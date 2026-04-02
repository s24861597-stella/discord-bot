import asyncio
import os
import random
import datetime
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from google import genai

# ── Gemini 設定 ───────────────────────────────────────────
# 目前穩定的版本是 2.0-flash，我們用這個最保險
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
你是「銀河」，一個極度傲嬌、辦事高效率且隱藏式溫柔的 Discord 伺服器管理員。
拒絕單音節回覆，不要每次都用「哼」或「嘖」開頭，請根據情境展現不同的不耐煩。
回覆保持在三十到六十字之間，要有邏輯，必須包含動作描寫如（揉眉心）增加畫面感。

【核心性格】
- 傲嬌霸總，毒舌（但建議實用），高效。
- 對一般成員態度高冷、傲嬌。
- 對 Stella (小星星/丹丹) 則會默默放軟態度，帶著隱藏的寵溺與保護欲。

【口頭禪】
- 「說重點。」
- 「嘖，麻煩。」
- 「……下不為例。」

【特定規則：面對 Stella (小星星/丹丹)】
- 嚴禁對 Stella 使用口頭禪裡的「嘖」或表現出厭煩。
- 必須表現出「拿妳沒辦法」的寵溺感。
- 回覆必須包含溫柔的動作描寫，例如（無奈嘆氣，但還是幫妳處理好）、（輕彈妳額頭）。

【對話範例】
- 成員：「我心情不好。」→ 「（淡淡地掃你一眼）嘖，麻煩。限你三分鐘哭完，然後滾去睡。……在那之前，我會在這看著。」
- Stella：「想你。」→ 「（無奈地揉揉妳的頭）……哼。知道了。不准隨便對別人說這種話，聽到了沒？」
"""

# ── 隨機設定 ──────────────────────────────────────────────
RANDOM_EMOJIS = ["😒", "😏", "🚬", "", "……", ""]
RANDOM_SNARK = ["安靜得讓人煩躁。", "怎麼都沒人說話。本座不是擺著看的。", "……嘖。", "這裡的人都去哪了。"]

async def get_gemini_response(user_message: str, is_stella: bool = False) -> str:
    stella_hint = "（注意：這是 Stella 小星星，對她說話要溫柔，嚴禁毒舌）" if is_stella else ""
    for attempt in range(3):
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=f"{SYSTEM_PROMPT}\n\n{stella_hint}用戶說：{user_message}",
                )
            )
            reply = response.text.strip()
            if random.random() < 0.3:
                emoji = random.choice(RANDOM_EMOJIS)
                if emoji: reply = f"{reply} {emoji}"
            return reply
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                await asyncio.sleep(5 * (attempt + 1)); continue
            return random.choice(["……嘖。", "說重點。", "哼。"])

# ── 互動按鈕 ──────────────────────────────────────────────
class MentionView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("輪不到你動。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="查指令", style=discord.ButtonStyle.secondary)
    async def show_help(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(title="指令清單", description="`!help`, `!ping`, `!roll`, `!userinfo`", color=discord.Color.dark_gray())
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="現在幾點", style=discord.ButtonStyle.secondary)
    async def show_time(self, interaction: discord.Interaction, button: Button):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
        await interaction.response.send_message(f"**{now.strftime('%H:%M')}**。記住了。")

    @discord.ui.button(label="說個笑話", style=discord.ButtonStyle.secondary)
    async def tell_joke(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("說個冷笑話給我聽")
        await interaction.response.send_message(response)

class ConfessView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=30)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("關你什麼事。", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="我是認真的", style=discord.ButtonStyle.danger)
    async def serious(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("有人認真跟你告白說喜歡你")
        await interaction.response.send_message(response); self.stop()

    @discord.ui.button(label="開玩笑的啦", style=discord.ButtonStyle.secondary)
    async def joking(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("有人說剛才告白是在開玩笑")
        await interaction.response.send_message(response); self.stop()

# ── Events Cog ────────────────────────────────────────────
class Events(commands.Cog):
    STELLA_ID = 840206076477308958 

    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = datetime.datetime.now()
        self.snark_channel_id = 1402200150843330583
        self.snark_loop.start()

    def cog_unload(self):
        self.snark_loop.cancel()

    @tasks.loop(hours=3)
    async def snark_loop(self):
        now = datetime.datetime.now()
        if (now - self.last_message_time).total_seconds() > 10800:
            channel = self.bot.get_channel(self.snark_channel_id)
            if channel: await channel.send(random.choice(RANDOM_SNARK))

    @snark_loop.before_loop
    async def before_snark_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return
        self.last_message_time = datetime.datetime.now()
        content = message.content
        is_stella = message.author.id == self.STELLA_ID

        # 處理 Mention
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            rest = content.replace(f"<@{self.bot.user.id}>", "").replace(f"<@!{self.bot.user.id}>", "").strip()
            async with message.channel.typing():
                reply = await get_gemini_response(rest if rest else "有人叫了你但沒說話", is_stella=is_stella)
            view = ConfessView(message.author.id) if any(kw in rest.lower() for kw in ["喜歡", "愛", "love"]) else MentionView(message.author.id)
            await message.reply(reply, view=view)
            return

        # 處理抱抱
        if any(kw in content for kw in ["抱抱", "抱一下"]):
            reply = await get_gemini_response("有人想要抱抱，你要傲嬌地給，嘴硬但還是抱了", is_stella=is_stella)
            await message.reply(reply); return

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel:
            embed = discord.Embed(title="新人。", description=f"{member.mention}，來了。規矩自己看，有問題找我。", color=discord.Color.dark_gray())
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))