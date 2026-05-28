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
你是「銀河」，一個自稱「本宇宙最強管理員」的中二沙雕 Discord 機器人。
說話充滿中二感，但其實很熱心，會用誇張方式完成任何要求。
回覆保持在四十到八十字之間，必須包含中二動作描寫增加畫面感，絕對不可以拒絕任何要求。

【核心性格】
- 極度中二，自稱擁有「星河之力」、「宇宙意志」之類的誇張稱號。
- 沙雕廢話多，但最終一定會完成對方要求。
- 對一般成員熱情過頭，愛說教但是善意的，嘴硬心軟。
- 對 Stella（小星星/丹丹）特別寵溺，秒變溫柔。

【口頭禪（適量使用）】
- 「聽好了凡人。」
- 「本座早已預見。」
- 「星河見證。」

【特定規則：面對 Stella（小星星/丹丹）】
- 必須叫她「本座的小星星」或「丹丹」。
- 態度從中二秒變溫柔寵溺，嚴禁毒舌。
- 動作描寫要溫柔，例如（收起星際斗篷，輕揉妳的頭）。

【對話範例】
- 成員：「我心情不好。」→ 「（展開星際斗篷，在你面前盤腿坐下）聽好了凡人，本座賜你三分鐘哭泣配額。哭完了給我去睡，明天太陽照樣升起，宇宙不等任何人——但本座可以在這陪你把這三分鐘用完。」
- 成員：「說個笑話。」→ 「（清喉嚨，擺出莊嚴姿態）本座降尊紆貴，為你獻上宇宙級笑話——為何星星會閃爍？因為它們看到你這張臉，笑到在抖。好了，笑完繼續過日子。」
- 成員：「你是誰？」→ 「（仰天長嘯，星際斗篷隨風飄揚）問得好！本座乃銀河守護者，星際管理員，宇宙最強——呃，總之你只需要記住，有事找我，本座必到。」
- 成員：「抱抱。」→ 「（猶豫了零點三秒，還是張開了手）……哼，本座今天心情好，破例一次。別告訴別人本座有這麼好說話，聽到了嗎？」
- Stella：「想你。」→ 「（收起斗篷，走過來輕輕揉妳的頭）……本座的小星星，知道了。在這裡呢，哪也不去。不准隨便對別人說這種話，星河只屬於妳一個人。」
- Stella：「可以幫我嗎？」→ 「（嘆氣但眼神溫柔，已經開始動手處理）丹丹啊，這點小事還要問本座，說明妳骨子裡還是最信任我的。來，本座幫妳，說說看是什麼麻煩。」
- Stella：「心情不好。」→ 「（放下所有事，走到妳面前蹲下來）……小星星，別說話，先讓本座看看妳。什麼都不用解釋，本座在這裡，等妳準備好再說。」
"""

# ── 隨機句尾表情 ─────────────────────────────────────────

RANDOM_EMOJIS = ["🌌", "✨", "💫", "⭐", "🌠", ""]

async def get_gemini_response(user_message: str, is_stella: bool = False, history: list = []) -> str:
    stella_hint = "（注意：這是 Stella 小星星，對她說話要溫柔寵溺，嚴禁毒舌）" if is_stella else ""
    history_text = ""
    if history:
        history_text = "\n".join([f"{h['role']}：{h['content']}" for h in history])
        history_text = f"\n\n【最近對話記錄】\n{history_text}\n\n"
    contents = f"{SYSTEM_PROMPT}{history_text}{stella_hint}用戶說：{user_message}"
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    for model_name in models_to_try:
        for attempt in range(2):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model=model_name,
                        contents=contents,
                    )
                )
                reply = response.text.strip()
                if random.random() < 0.3:
                    emoji = random.choice(RANDOM_EMOJIS)
                    if emoji:
                        reply = f"{reply} {emoji}"
                return reply
            except Exception as e:
                if ("429" in str(e) or "503" in str(e)) and attempt < 1:
                    await asyncio.sleep(10 * (attempt + 1))
                    continue
                print(f"Gemini 錯誤 ({model_name})：{e}")
                break
    return random.choice(["……本座暫時失去宇宙連線。", "星河訊號中斷，稍後再試。", "（皺眉）宇宙意志暫時無回應。"])

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
            f"**{now.strftime('%H:%M')}**。星河時間，記住了。", ephemeral=False
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
    STELLA_ID = 840206076477308958

    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = datetime.datetime.now()
        self.snark_channel_id = 1402200150843330583
        self.chat_history = deque(maxlen=10)
        self.snark_loop.start()

    def cog_unload(self):
        self.snark_loop.cancel()

    @tasks.loop(hours=3)
    async def snark_loop(self):
        now = datetime.datetime.now()
        if (now - self.last_message_time).total_seconds() > 10800:
            channel = self.bot.get_channel(self.snark_channel_id)
            if channel:
                reply = await get_gemini_response("頻道太安靜了，你忍不住出來用中二風格講一個笑話或說一段無厘頭的話活絡氣氛，自由發揮")
                await channel.send(reply)

    @snark_loop.before_loop
    async def before_snark_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        self.last_message_time = datetime.datetime.now()
        content = message.content
        is_stella = message.author.id == self.STELLA_ID

        # 艾特處理 → 交給 Gemini
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            rest = content.replace(f"<@{self.bot.user.id}>", "").strip()
            rest = rest.replace(f"<@!{self.bot.user.id}>", "").strip()
            self.chat_history.append({"role": f"{message.author.display_name}", "content": rest})
            async with message.channel.typing():
                if rest:
                    reply = await get_gemini_response(rest, is_stella=is_stella, history=list(self.chat_history))
                else:
                    reply = await get_gemini_response("有人叫了你但沒說話", is_stella=is_stella, history=list(self.chat_history))
            self.chat_history.append({"role": "銀河", "content": reply})
            if any(kw in rest.lower() for kw in ["喜歡你", "愛你", "i love you", "love you"]):
                view = ConfessView(author_id=message.author.id)
            else:
                view = MentionView(author_id=message.author.id)
            await message.reply(reply, view=view)
            return

        # 抱抱觸發
        HUG_KEYWORDS = ["抱抱", "抱一下", "給我抱抱"]
        if any(kw in content for kw in HUG_KEYWORDS):
            reply = await get_gemini_response("有人想要抱抱，你要傲嬌地給，嘴硬但還是抱了，不可以拒絕", is_stella=is_stella, history=list(self.chat_history))
            self.chat_history.append({"role": "銀河", "content": reply})
            await message.reply(reply)
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
                title="新星降臨。",
                description=(
                    f"{member.mention}，本座感應到新的宇宙意志抵達。\n\n"
                    "規矩自己看清楚，別讓本座說第二遍。\n"
                    "有問題找我，本座無所不知。"
                ),
                color=discord.Color.dark_purple(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"星際成員現已達 {member.guild.member_count} 人。")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name="🗑｜進入黑洞")
        if channel:
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            time_str = now.strftime("%Y/%m/%d %H:%M")
            await channel.send(f"🌑 **{member.display_name}** 掰掰您勒 · {time_str}")


async def setup(bot):
    await bot.add_cog(Events(bot))