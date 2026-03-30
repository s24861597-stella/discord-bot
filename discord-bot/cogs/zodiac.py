import random
import datetime
import discord
from discord.ext import commands
from discord.ui import View, Select


ZODIACS = {
    "牡羊座": {"emoji": "♈", "date": "3/21–4/19"},
    "金牛座": {"emoji": "♉", "date": "4/20–5/20"},
    "雙子座": {"emoji": "♊", "date": "5/21–6/21"},
    "巨蟹座": {"emoji": "♋", "date": "6/22–7/22"},
    "獅子座": {"emoji": "♌", "date": "7/23–8/22"},
    "處女座": {"emoji": "♍", "date": "8/23–9/22"},
    "天秤座": {"emoji": "♎", "date": "9/23–10/23"},
    "天蠍座": {"emoji": "♏", "date": "10/24–11/22"},
    "射手座": {"emoji": "♐", "date": "11/23–12/21"},
    "摩羯座": {"emoji": "♑", "date": "12/22–1/19"},
    "水瓶座": {"emoji": "♒", "date": "1/20–2/18"},
    "雙魚座": {"emoji": "♓", "date": "2/19–3/20"},
}

FORTUNE_TEMPLATES = [
    "今天適合主動出擊，猶豫只是在浪費時間。",
    "收斂一點。今天不是你表現的日子。",
    "運勢平穩。平穩不等於無聊，好好把握。",
    "有貴人出現，但你得先讓自己值得被幫助。",
    "今天的阻礙是明天的養分。記住這句話。",
    "別把精力花在無謂的爭論上。",
    "靜下來，答案自然會出現。",
    "機會有，但需要你自己走出去拿。",
    "今天適合整理思緒，別急著行動。",
    "小心言多必失。今天少說多做。",
    "一件被你拖延的事，今天去解決它。",
    "今天的你比昨天更強。繼續。",
    "有些人不值得你付出，看清楚。",
    "別高估別人，也別低估自己。",
    "今天適合休息。充電不是懈怠。",
]

LOVE_TEMPLATES = [
    "感情上，說清楚比猜測有用得多。",
    "對方在等你開口，但你還在等什麼。",
    "感情稍有波動，冷靜處理即可。",
    "舊情緒別帶進新關係。",
    "主動一點，不會少塊肉。",
    "暗戀的事，今天或許能有突破。",
    "感情平順，珍惜眼前人。",
    "別把沉默誤解為冷漠。",
    "今天不適合衝動表白，再等等。",
    "關係需要經營，不是等著對方猜你的心。",
]

MONEY_TEMPLATES = [
    "財運不差，但別亂花。",
    "今天不宜衝動消費。忍住。",
    "有意外收穫的可能，保持開放。",
    "理財要趁早，今天可以做個計畫。",
    "花錢要花在刀口上。",
    "財運平穩，守住就好。",
    "今天有破財跡象，錢包看緊一點。",
    "投資前先做功課，別衝動。",
]

WORK_TEMPLATES = [
    "工作上遇到困難，正面迎擊。",
    "今天效率高，把該做的做完。",
    "同事關係需要留意，別讓小事變大事。",
    "有新機會，但需要你自己去爭取。",
    "專注在重要的事，別被雜務牽著走。",
    "今天適合提案或溝通，說清楚你的想法。",
    "工作進度超前，但別鬆懈。",
    "遇到卡關的事，換個角度想。",
]

LUCKY = {
    "顏色": ["暗紅", "墨藍", "深灰", "純白", "森林綠", "酒紅", "黑", "金", "銀", "靛藍", "玫瑰金", "炭灰"],
    "數字": list(range(1, 100)),
}

STARS = ["★★★★★", "★★★★☆", "★★★☆☆", "★★☆☆☆", "★☆☆☆☆"]
STAR_WEIGHTS = [10, 30, 35, 20, 5]


def get_today_seed(zodiac: str) -> random.Random:
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y%m%d")
    seed = int(today) + sum(ord(c) for c in zodiac)
    return random.Random(seed)


def build_fortune_embed(zodiac: str) -> discord.Embed:
    info = ZODIACS[zodiac]
    rng = get_today_seed(zodiac)

    overall = rng.choices(STARS, weights=STAR_WEIGHTS, k=1)[0]
    love    = rng.choices(STARS, weights=STAR_WEIGHTS, k=1)[0]
    money   = rng.choices(STARS, weights=STAR_WEIGHTS, k=1)[0]
    work    = rng.choices(STARS, weights=STAR_WEIGHTS, k=1)[0]

    fortune_text = rng.choice(FORTUNE_TEMPLATES)
    love_text    = rng.choice(LOVE_TEMPLATES)
    money_text   = rng.choice(MONEY_TEMPLATES)
    work_text    = rng.choice(WORK_TEMPLATES)
    lucky_color  = rng.choice(LUCKY["顏色"])
    lucky_number = rng.choice(LUCKY["數字"])

    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y/%m/%d")

    embed = discord.Embed(
        title=f"{info['emoji']} {zodiac}  今日運勢",
        description=f"*{today}　{info['date']}*\n\n「{fortune_text}」",
        color=discord.Color.dark_gold(),
    )
    embed.add_field(name="綜合運勢", value=overall, inline=True)
    embed.add_field(name="戀愛運",   value=love,    inline=True)
    embed.add_field(name="財運",     value=money,   inline=True)
    embed.add_field(name="事業運",   value=work,    inline=True)
    embed.add_field(name="幸運顏色", value=f"**{lucky_color}**", inline=True)
    embed.add_field(name="幸運數字", value=f"**{lucky_number}**", inline=True)
    embed.add_field(name="戀愛提示", value=love_text,  inline=False)
    embed.add_field(name="財運提示", value=money_text, inline=False)
    embed.add_field(name="事業提示", value=work_text,  inline=False)
    embed.set_footer(text="本座已言盡於此。信不信由你。")
    return embed


class ZodiacSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=name,
                value=name,
                emoji=info["emoji"],
                description=info["date"],
            )
            for name, info in ZODIACS.items()
        ]
        super().__init__(placeholder="選擇你的星座…", options=options)

    async def callback(self, interaction: discord.Interaction):
        zodiac = self.values[0]
        embed = build_fortune_embed(zodiac)
        await interaction.response.send_message(embed=embed, ephemeral=False)


class ZodiacView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ZodiacSelect())


class Zodiac(commands.Cog):
    """星座運勢"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="星座", aliases=["zodiac", "運勢", "horoscope"])
    async def zodiac(self, ctx, *, sign: str = None):
        """查詢星座今日運勢

        用法：
          !星座          → 顯示選單讓你選
          !星座 獅子座   → 直接查詢指定星座
        """
        if sign:
            sign = sign.strip()
            if sign not in ZODIACS:
                names = "　".join(ZODIACS.keys())
                await ctx.send(f"找不到「{sign}」。\n可用星座：{names}")
                return
            embed = build_fortune_embed(sign)
            await ctx.send(embed=embed)
        else:
            view = ZodiacView()
            await ctx.send("選你的星座。", view=view)


async def setup(bot):
    await bot.add_cog(Zodiac(bot))
