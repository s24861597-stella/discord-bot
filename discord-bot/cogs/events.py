import random
import datetime
import discord
from discord.ext import commands


MENTION_RESPONSES = [
    "叫我？說重點。",
    "本座在。有事說事。",
    "{mention} 找我何事。",
    "嗯。說。",
    "不是讓你站在這裡發呆的。",
    "有話直說，我時間寶貴。",
    "說。",
]

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
        "。",
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
        "。",
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
        "不用誇。做好是本分。",
    ]),
    (["喜歡你", "愛你", "你好可愛", "愛你喔"], [
        "……少說這種話。",
        "不准亂說。",
        "哼。",
        "……知道了。",
    ]),
    (["幹", "靠北", "媽的", "wtf", "what the", "幹嘛", "怎樣"], [
        "冷靜。",
        "說清楚。",
        "發生什麼事了。",
    ]),
    (["餓", "好餓", "吃飯", "沒吃飯"], [
        "去吃。別讓自己餓著。",
        "吃飯比什麼都重要。快去。",
        "還坐在這裡？去吃飯。",
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
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
            await message.reply(f"**{now.strftime('%H:%M')}**。記住了。")

        elif any(kw in text_lower for kw in ["你好", "哈囉", "嗨", "hi", "hello", "hey"]):
            responses = [
                "嗯。",
                "有事說事。",
                f"{mention} 說。",
            ]
            await message.reply(random.choice(responses))

        elif any(kw in text_lower for kw in ["你是誰", "你是什麼", "介紹", "自我介紹"]):
            embed = discord.Embed(
                title="我是誰？",
                description=(
                    "問這種問題。\n\n"
                    "我是這個伺服器的管理者。\n"
                    "查資訊、查指令、協助群務——這些都是我的職責。\n\n"
                    f"輸入 `!help` 自己看。我不重複說兩遍。"
                ),
                color=discord.Color.dark_gray(),
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await message.reply(embed=embed)

        elif any(kw in text_lower for kw in ["bye", "掰掰", "再見", "拜拜"]):
            responses = [
                "嗯。去吧。",
                "。",
                "明天還要上線。",
                "去吧。",
            ]
            await message.reply(random.choice(responses))

        elif any(kw in text_lower for kw in ["謝謝", "感謝", "thanks", "thx"]):
            responses = [
                "不必謝。",
                "這是應該的。",
                "嗯。",
            ]
            await message.reply(random.choice(responses))

        elif any(kw in text_lower for kw in ["喜歡", "愛你", "可愛", "帥"]):
            responses = [
                "……少說這種話。",
                "哼。",
                "不准亂說。",
                "……知道了。",
            ]
            await message.reply(random.choice(responses))

        elif any(kw in text_lower for kw in ["幫幫我", "幫我", "help me", "救我"]):
            responses = [
                f"{mention} 說清楚，什麼事。",
                "說。我在聽。",
                "講重點。",
            ]
            await message.reply(random.choice(responses))

        else:
            responses = [
                "說清楚一點。",
                "沒聽懂。再說一次。",
                f"輸入 `!help` 看指令。別讓我重複。",
                "……說重點。",
            ]
            await message.reply(random.choice(responses))

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
