import random
import datetime
import discord
from discord.ext import commands
from discord.ui import View, Button
from discord.ext import tasks


# ── 艾特但沒說話 ──────────────────────────────────────────
MENTION_RESPONSES = [
    "叫我？說重點。",
    "本座在。有事說事。",
    "{mention} 找我何事。",
    "嗯。說。",
    "不是讓你站在這裡發呆的。",
    "有話直說，我時間寶貴。",
    "說。",
]

# ── 自動回覆關鍵字 ────────────────────────────────────────
AUTO_REPLIES = [
    (["早安", "早上好", "good morning", "gm"], [
        "起這麼早。",
        "{mention} 早。",
        "嗯。",
        "今天的事今天做完。",
    ]),
    (["晚安", "好夢", "good night", "gn"], [
        "去睡吧。明天還要上線。",
        "{mention} 早點休息。",
        "嗯。",
        "別熬夜。",
    ]),
    (["謝謝", "感謝", "thanks", "thank you", "thx"], [
        "不必謝。",
        "這是應該的。",
        "嗯。",
        "記住就好。",
    ]),
    (["你好", "哈囉", "嗨", "hi", "hello", "hey"], [
        "嗯。",
        "{mention} 有事？",
        "說。",
    ]),
    (["無聊", "好無聊", "bored"], [
        "無聊？那就去做點有意義的事。",
        "時間是自己的。別浪費。",
        "去玩 `!roll` 或 `!8ball`，別在這裡虛度。",
    ]),
    (["開心", "好開心", "快樂", "happy", "yay"], [
        "嗯。",
        "高興就好。別太鬧。",
    ]),
    (["難過", "傷心", "哭", "sad", "😢", "😭"], [
        "哭什麼。擦乾眼淚站起來。",
        "{mention} 說說看發生什麼事了。",
        "……過去了就過去了。",
        "我在。說。",
    ]),
    (["好帥", "好厲害", "你好棒", "你最棒", "讚"], [
        "我知道。",
        "這是基本。",
        "嗯。",
    ]),
    (["想你", "miss you", "想念", "好想你", "思念"], [
        "……嗯。",
        "知道了。",
        "……少說這種話。",
        "哼。",
        "……我也——算了。",
    ]),
    (["喜歡你", "愛你", "你好可愛", "愛你喔", "i love you", "love you"], [
        "……少說這種話。",
        "不准亂說。",
        "哼。",
        "……知道了。",
    ]),
    (["幹", "靠北", "媽的", "wtf", "what the", "怎樣", "煩死"], [
        "冷靜。",
        "說清楚。",
        "發生什麼事了。",
    ]),
    (["餓", "好餓", "吃飯", "沒吃飯"], [
        "去吃。別讓自己餓著。",
        "吃飯比什麼都重要。快去。",
        "還坐在這裡？去吃飯。",
    ]),
    (["累", "好累", "疲憊", "累死了", "tired"], [
        "累了就休息。沒什麼大不了的。",
        "撐著幹什麼。去躺一下。",
        "……去休息。",
    ]),
    (["下雨", "天氣", "好熱", "好冷", "颱風"], [
        "照顧好自己。",
        "多加件衣服。",
        "天氣這種事，適應就好。",
    ]),
]

# ── 會觸發表情反應的關鍵字 ────────────────────────────────
REACTION_TRIGGERS = {
    "哈哈": "😂",
    "笑死": "💀",
    "可愛": "🥰",
    "加油": "💪",
    "好棒": "👏",
    "謝謝": "🤝",
    "晚安": "🌙",
    "早安": "☀️",
    "想你": "🫀",
}

# ── 主動吐槽（安靜時自動發） ──────────────────────────────
RANDOM_SNARK = [
    "安靜得讓人煩躁。",
    "怎麼都沒人說話。本座不是擺著看的。",
    "……嘖。",
    "這裡的人都去哪了。",
    "沉默是金？本座不這麼認為。",
    "有人在嗎。說句話。",
]

# ── Stella 專屬回覆 ────────────────────────────────────────
STELLA_RESPONSES = [
    "嗯，我在。",
    "說吧，我聽著。",
    "累了就過來。",
    "……是妳啊。",
    "有話直說。",
]


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
        jokes = [
            "笑話？……你本人就是。",
            "有個人問我笑話是什麼。我給他看了鏡子。",
            "……本座不說笑話。",
            "笑話：有人以為叫我一聲我就會陪他聊天。",
            "哼。",
        ]
        await interaction.response.send_message(random.choice(jokes), ephemeral=False)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class ConfessView(View):
    """告白後的互動按鈕"""
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
        responses = [
            "……我知道。",
            "哼。不准反悔。",
            "……算你有眼光。",
            "知道了。別再說了。",
        ]
        await interaction.response.send_message(random.choice(responses))
        self.stop()

    @discord.ui.button(label="開玩笑的啦", style=discord.ButtonStyle.secondary)
    async def joking(self, interaction: discord.Interaction, button: Button):
        responses = [
            "我就知道。",
            "哼。無聊。",
            "浪費我時間。",
            "……早說是開玩笑的。",
        ]
        await interaction.response.send_message(random.choice(responses))
        self.stop()


# ── Cog ──────────────────────────────────────────────────
class Events(commands.Cog):
    """事件與自動回覆"""

    STELLA_ID = 840206076477308958  # Stella 的 Discord ID

    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = datetime.datetime.now()
        self.snark_channel_id = None  # 會自動記錄第一個有人說話的頻道
        self.snark_loop.start()

    def cog_unload(self):
        self.snark_loop.cancel()

    @tasks.loop(hours=3)
    async def snark_loop(self):
        """每3小時如果沒人說話就主動吐槽"""
        now = datetime.datetime.now()
        if (now - self.last_message_time).total_seconds() > 10800:  # 3小時
            if self.snark_channel_id:
                channel = self.bot.get_channel(self.snark_channel_id)
                if channel:
                    await channel.send(random.choice(RANDOM_SNARK))

    @snark_loop.before_loop
    async def before_snark_loop(self):
        await self.bot.wait_until_ready()

    async def _get_response(self, message, base_responses):
        """根據是否為 Stella 決定回覆內容"""
        is_stella = message.author.id == self.STELLA_ID
        chance = random.random()

        if is_stella and chance < 0.3:
            return f"……{random.choice(STELLA_RESPONSES)}"

        # 5% 機率對一般人主動吐槽
        if not is_stella and chance < 0.05:
            return random.choice(["嘖，話真多。", "……本座沒空理你。", "說這麼多幹嘛。"])

        return random.choice(base_responses)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # 記錄最後說話時間和頻道
        self.last_message_time = datetime.datetime.now()
        if self.snark_channel_id is None:
            self.snark_channel_id = message.channel.id

        mention = message.author.mention
        content = message.content.lower()

        # 表情反應
        for keyword, emoji in REACTION_TRIGGERS.items():
            if keyword in content:
                try:
                    await message.add_reaction(emoji)
                except discord.Forbidden:
                    pass
                break

        # 艾特處理
        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            rest = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            rest = rest.replace(f"<@!{self.bot.user.id}>", "").strip()

            if rest:
                await self._handle_mention_with_text(message, rest, mention)
            else:
                base = random.choice(MENTION_RESPONSES).format(mention=mention)
                response = await self._get_response(message, MENTION_RESPONSES)
                response = response.format(mention=mention)
                view = MentionView(author_id=message.author.id)
                await message.reply(response, view=view)
            return

        # 自動回覆
        for keywords, responses in AUTO_REPLIES:
            if any(kw in content for kw in keywords):
                response = await self._get_response(message, responses)
                response = response.format(mention=mention)
                if any(kw in content for kw in ["喜歡你", "愛你", "i love you", "love you"]):
                    view = ConfessView(author_id=message.author.id)
                    await message.reply(response, view=view)
                else:
                    await message.reply(response)
                return

    async def _handle_mention_with_text(self, message, text, mention):
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["幾點", "時間", "time"]):
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            await message.reply(f"**{now.strftime('%H:%M')}**。記住了。")

        elif any(kw in text_lower for kw in ["你好", "哈囉", "嗨", "hi", "hello", "hey"]):
            view = MentionView(author_id=message.author.id)
            response = await self._get_response(message, ["嗯。", "有事？", "說。"])
            await message.reply(response, view=view)

        elif any(kw in text_lower for kw in ["你是誰", "你是什麼", "介紹", "自我介紹"]):
            embed = discord.Embed(
                title="我是誰？",
                description=(
                    "問這種問題。\n\n"
                    "我是這個伺服器的管理者。\n"
                    "查資訊、協助群務——這些都是我的職責。\n\n"
                    f"輸入 `!help` 自己看。我不重複說兩遍。"
                ),
                color=discord.Color.dark_gray(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await message.reply(embed=embed)

        elif any(kw in text_lower for kw in ["bye", "掰掰", "再見", "拜拜"]):
            await message.reply(random.choice(["嗯。去吧。", "。", "明天還要上線。"]))

        elif any(kw in text_lower for kw in ["謝謝", "感謝", "thanks", "thx"]):
            await message.reply(random.choice(["不必謝。", "這是應該的。", "嗯。"]))

        elif any(kw in text_lower for kw in ["想你", "miss", "思念", "好想"]):
            await message.reply(random.choice(["……嗯。", "……我也——算了。", "知道了。"]))

        elif any(kw in text_lower for kw in ["喜歡", "愛你", "love", "可愛", "帥"]):
            view = ConfessView(author_id=message.author.id)
            response = await self._get_response(message, ["……少說這種話。", "哼。", "不准亂說。"])
            await message.reply(response, view=view)

        elif any(kw in text_lower for kw in ["幫幫我", "幫我", "help me", "救我"]):
            view = MentionView(author_id=message.author.id)
            response = await self._get_response(message, [f"{mention} 說清楚，什麼事。", "說。我在聽。", "講重點。"])
            await message.reply(response, view=view)

        elif any(kw in text_lower for kw in ["無聊", "bored"]):
            view = MentionView(author_id=message.author.id)
            await message.reply("無聊？自己找事做。", view=view)

        else:
            view = MentionView(author_id=message.author.id)
            response = await self._get_response(message, ["說清楚一點。", "沒聽懂。再說一次。", "……說重點。"])
            await message.reply(response, view=view)

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
