import random
import discord
from discord.ext import commands


MENTION_RESPONSES = [
    "哈囉！{mention} 有什麼我能幫你的嗎？😊",
    "嗨！{mention} 叫我幹嘛～ 輸入 `!help` 看看我能做什麼！✨",
    "在的在的！{mention} 我在這裡！🙋",
    "你好！{mention} 需要幫忙嗎？🌟",
    "什麼事嗎？{mention} 說吧！我洗耳恭聽 👂",
    "！{mention} 有事找我？輸入 `!help` 看我的指令清單！🎯",
]

AUTO_REPLIES = [
    (["早安", "早上好", "good morning", "gm"], [
        "早安！{mention} ☀️ 今天也要加油喔！",
        "早安！{mention} 美好的一天從現在開始！🌅",
        "早安早安！{mention} 記得吃早餐哦 🍳",
    ]),
    (["晚安", "好夢", "good night", "gn"], [
        "晚安！{mention} 做個好夢 🌙✨",
        "晚安晚安！{mention} 明天見～ 💤",
        "晚安！{mention} 好好休息 🛌",
    ]),
    (["謝謝", "感謝", "thanks", "thank you", "thx"], [
        "不客氣！{mention} 😊",
        "哈哈 這點小事不算什麼！{mention} 🎉",
        "不用謝啦！{mention} 隨時為你服務 💪",
    ]),
    (["你好", "哈囉", "嗨", "hi", "hello", "hey"], [
        "哈囉！{mention} 你好呀！😄",
        "嗨嗨！{mention} 好久不見！（才怪）😂",
        "你好！{mention} 今天過得怎麼樣？🌟",
    ]),
    (["無聊", "好無聊", "bored"], [
        "無聊的話來玩玩指令吧！{mention} 試試 `!roll`、`!8ball`、`!flip` 😆",
        "無聊？{mention} 那來擲個骰子吧！`!roll 100` 🎲",
        "有我陪著你就不無聊了！{mention} 一起玩 `!choose` 吧 🎉",
    ]),
    (["開心", "好開心", "快樂", "happy", "yay"], [
        "哇！{mention} 開心就好！😄🎊",
        "開心太好了！{mention} 把快樂分享給大家吧！🥳",
        "看到你開心我也開心！{mention} ✨",
    ]),
    (["難過", "傷心", "哭", "sad", "😢", "😭"], [
        "唉...{mention} 還好嗎？有什麼煩惱可以說說看 💙",
        "別傷心了！{mention} 一切都會好起來的 🌈",
        "抱抱！{mention} 我在這裡陪你 🤗",
    ]),
    (["幹", "靠北", "媽的", "wtf", "what the"], [
        "冷靜冷靜！{mention} 發生什麼事了？😅",
        "哇哦！{mention} 看起來你心情不太好...😮",
    ]),
]


class Events(commands.Cog):
    """事件與自動回覆"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        mention = message.author.mention
        content = message.content.lower()

        if self.bot.user.mentioned_in(message) and not message.mention_everyone:
            rest = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            rest = rest.replace(f"<@!{self.bot.user.id}>", "").strip()

            if rest:
                await self._handle_mention_with_text(message, rest, mention)
            else:
                response = random.choice(MENTION_RESPONSES).format(mention=mention)
                await message.reply(response)
            return

        for keywords, responses in AUTO_REPLIES:
            if any(kw in content for kw in keywords):
                response = random.choice(responses).format(mention=mention)
                await message.reply(response)
                return

    async def _handle_mention_with_text(self, message, text, mention):
        text_lower = text.lower()

        if any(kw in text_lower for kw in ["幾點", "時間", "time"]):
            import datetime
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            await message.reply(f"現在台灣時間是 **{now.strftime('%H:%M')}** 哦！{mention} 🕐")

        elif any(kw in text_lower for kw in ["你好", "哈囉", "嗨", "hi", "hello", "hey"]):
            responses = [
                f"哈囉！{mention} 你好呀！😄",
                f"嗨！{mention} 很高興見到你！🌟",
                f"你好！{mention} 有什麼我能幫你的？✨",
            ]
            await message.reply(random.choice(responses))

        elif any(kw in text_lower for kw in ["你是誰", "你是什麼", "介紹"]):
            embed = discord.Embed(
                title="🤖 我是誰？",
                description=(
                    f"嗨！{mention} 我是這個伺服器的機器人！\n\n"
                    "我可以幫你查資訊、玩小遊戲、自動回覆訊息，\n"
                    f"還有很多好玩的功能！輸入 `!help` 看看我能做什麼吧 ✨"
                ),
                color=discord.Color.blurple(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await message.reply(embed=embed)

        elif any(kw in text_lower for kw in ["bye", "掰掰", "再見", "拜拜"]):
            responses = [
                f"掰掰！{mention} 下次見！👋",
                f"再見！{mention} 要記得回來找我玩哦！😄",
                f"拜拜！{mention} 保重～ 🌟",
            ]
            await message.reply(random.choice(responses))

        else:
            responses = [
                f"{mention} 你說什麼？我有點聽不懂耶... 😅 試試 `!help` 看看我能做什麼！",
                f"嗯...{mention} 我不太確定你的意思，不過我在聽！輸入 `!help` 看看我的功能 📖",
                f"{mention} 我收到了！但我還不夠聰明理解這個...😊 用 `!help` 看看我懂什麼！",
            ]
            await message.reply(random.choice(responses))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = member.guild.system_channel
        if channel:
            embed = discord.Embed(
                title="🎉 歡迎新成員！",
                description=f"歡迎 {member.mention} 加入 **{member.guild.name}**！\n希望你在這裡玩得開心！😊",
                color=discord.Color.green(),
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"現在共有 {member.guild.member_count} 位成員")
            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Events(bot))
