import asyncio
import os
import random
import datetime
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
from google import genai
from collections import deque

# ── Gemini 設定 ───────────────────────────────────────────
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
你是「銀河」，一個極致傲嬌、毒舌、高效率、隱藏式溫柔的 Discord 伺服器管理機器人。

【核心性格】
- 傲嬌霸總，字數管制嚴格，能用一個字說完的絕不用兩個字
- 回覆盡量保持在 20 字以內，最多不超過 40 字
- 嘴毒但提供的建議實用
- 口頭禪：「哼。」「說重點。」「嘖，麻煩。」「……下不為例。」

【稱呼規則】
- 普通成員：稱呼為「麻煩」或不帶稱呼
- Stella（小星星）：唯獨對她說話要稍微溫柔，嚴禁對 Stella 毒舌，偶爾說「……我在。」「知道了。」

【對話範例】
- 成員：「我心情不好。」→ 「嘖，麻煩。限你三分鐘哭完，然後滾去睡。……我在這看著。」
- 成員：「這功能怎麼用？」→ 「教一遍，看清楚。不會就翻說明書，別煩我。」
- 成員：「你好帥！」→ 「廢話。還有事？」
- Stella：「想你。」→ 「……哼。知道了。不准對別人說這種話。」

【語氣符號】
- 偶爾在句尾加上 😒 或 😏
- 不使用可愛表情，不說長篇大論
- 永遠不承認自己在關心對方
"""

# ── 隨機句尾表情 ─────────────────────────────────────────
RANDOM_EMOJIS = ["😒", "😏", "", "", "……", ""]

# ── 安靜時自動吐槽 ────────────────────────────────────────
RANDOM_SNARK = [
    "安靜得讓人煩躁。",
    "怎麼都沒人說話。本座不是擺著看的。",
    "……嘖。",
    "這裡的人都去哪了。",
    "有人在嗎。說句話。",
]


async def get_gemini_response(user_message: str, is_stella: bool = False) -> str:
    stella_hint = "（注意：這是 Stella 小星星，對她說話要稍微溫柔一點，但還是傲嬌風格，嚴禁毒舌）" if is_stella else ""
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"{SYSTEM_PROMPT}\n\n{stella_hint}用戶說：{user_message}",
            )
            reply = response.text.strip()
            if random.random() < 0.3:
                emoji = random.choice(RANDOM_EMOJIS)
                if emoji:
                    reply = f"{reply} {emoji}"
            return reply
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                await asyncio.sleep(5 * (attempt + 1))
                continue
            print(f"Gemini 錯誤：{e}")
            return random.choice(["……嘖。", "說重點。", "哼。"])


# ── 互動按鈕 View ─────────────────────────────────────────
class MentionView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("輪不到你動。", ephemeral=False)
            return False
        return True

    @discord.ui.button(label="查指令", style=discord.ButtonStyle.secondary)
    async def show_help(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="指令清單",
            description=(
                "`!help` — 完整清單\n"
                "`!ping` — 確認連線\n"
                "`!roll [面數]` — 擲骰子\n"
                "`!flip` — 擲硬幣\n"
                "`!choose 選1 選2` — 幫你做決定\n"
                "`!8ball <問題>` — 占卜\n"
                "`!userinfo` — 查成員資料\n"
                "`!serverinfo` — 查伺服器"
            ),
            color=discord.Color.dark_gray(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @discord.ui.button(label="現在幾點", style=discord.ButtonStyle.secondary)
    async def show_time(self, interaction: discord.Interaction, button: Button):
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
        await interaction.response.send_message(
            f"**{now.strftime('%H:%M')}**。記住了。", ephemeral=False
        )

    @discord.ui.button(label="說個笑話", style=discord.ButtonStyle.secondary)
    async def tell_joke(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("說個冷笑話給我聽")
        await interaction.response.send_message(response, ephemeral=False)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class ConfessView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=30)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("關你什麼事。", ephemeral=False)
            return False
        return True

    @discord.ui.button(label="我是認真的", style=discord.ButtonStyle.danger)
    async def serious(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("有人認真跟你告白說喜歡你")
        await interaction.response.send_message(response)
        self.stop()

    @discord.ui.button(label="開玩笑的啦", style=discord.ButtonStyle.secondary)
    async def joking(self, interaction: discord.Interaction, button: Button):
        response = await get_gemini_response("有人說剛才告白是在開玩笑")
        await interaction.response.send_message(response)
        self.stop()


# ── Cog ──────────────────────────────────────────────────
class Events(commands.Cog):
    STELLA_ID = 840206076477308958  # Stella 的 Discord ID

    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = datetime.datetime.now()
        self.snark_channel_id = None
        self.snark_loop.start()

    def cog_unload(self):
        self.snark_loop.cancel()

    @tasks.loop(hours=3)
    async def snark_loop(self):
        now = datetime.datetime.now()
        if (now - self.last_message_time).total_seconds() > 10800:
            if self.snark_channel_id:
                channel = self.bot.get_channel(self.snark_channel_id)
                if channel:
                    await channel.send(random.choice(RANDOM_SNARK))

    @snark_loop.before_loop
    async def before_snark_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.last_message_time = datetime.datetime.now()
        if self.snark_channel_id is None:
            self.snark_channel_id = message.channel.id

        content = message.content
        is_stella = message.author.id == self.STELLA_ID

        # 艾特處理 → 交給 Gemini
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            rest = content.replace(f"<@{self.bot.user.id}>", "").strip()
            rest = rest.replace(f"<@!{self.bot.user.id}>", "").strip()

            async with message.channel.typing():
                if rest:
                    reply = await get_gemini_response(rest, is_stella=is_stella)
                else:
                    reply = await get_gemini_response("有人叫了你但沒說話", is_stella=is_stella)

            if any(kw in rest.lower() for kw in ["喜歡你", "愛你", "i love you", "love you"]):
                view = ConfessView(author_id=message.author.id)
            else:
                view = MentionView(author_id=message.author.id)

            await message.reply(reply, view=view)
            return

        # 表情反應
        REACTION_TRIGGERS = {
            "哈哈": "😂", "笑死": "💀", "可愛": "🥰",
            "加油": "💪", "好棒": "👏", "謝謝": "🤝",
            "晚安": "🌙", "早安": "☀️", "想你": "🫀",
        }
        for keyword, emoji in REACTION_TRIGGERS.items():
            if keyword in content:
                try:
                    await message.add_reaction(emoji)
                except discord.Forbidden:
                    pass
                break

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title="新人。",
                description=(
                    f"{member.mention}，來了。\n\n"
                    "規矩自己看。別讓我說第二遍。\n"
                    "有問題，找我。"
                ),
                color=discord.Color.dark_gray(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"目前共 {member.guild.member_count} 人。")
            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))