import datetime
import discord
import os
from discord.ext import commands
from discord.ui import View, Select
from google import genai  # 記得確保 events.py 也有用這個

# ── Gemini 設定 ───────────────────────────────────────────
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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

async def get_gemini_horoscope(zodiac: str):
    """叫 Gemini 真的去根據當天星象算命"""
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y/%m/%d")
    prompt = f"""
    你是銀河守護者，請根據 {today} 的星象，為 {zodiac} 提供今日運勢。
    請嚴格遵守以下格式回覆，不要有額外廢話，各項評分給 1~5 顆星（★）：
    
    綜合短評：(20字以內)
    綜合運勢：(例如：★★★★☆)
    戀愛運：(例如：★★★☆☆)
    財運：(例如：★★★★★)
    事業運：(例如：★★☆☆☆)
    幸運顏色：(顏色名稱)
    幸運數字：(1-99)
    詳細提示：(包含戀愛、財運、事業的綜合中二風建議，約 60 字)
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except:
        return "（星圖模糊）宇宙迷霧太濃，本座暫時看不清。妳待會再問一次。"

class ZodiacSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=name, emoji=info["emoji"], description=info["date"])
            for name, info in ZODIACS.items()
        ]
        super().__init__(placeholder="選擇你的星座，由本座為你觀星…", options=options)

    async def callback(self, interaction: discord.Interaction):
        zodiac = self.values[0]
        await interaction.response.defer() # 讓它轉圈圈等 Gemini 回覆
        
        raw_text = await get_gemini_horoscope(zodiac)
        
        # 解析 Gemini 的回覆 (簡單解析)
        data = {}
        for line in raw_text.split('\n'):
            if '：' in line:
                key, val = line.split('：', 1)
                data[key.strip()] = val.strip()

        embed = discord.Embed(
            title=f"{ZODIACS[zodiac]['emoji']} {zodiac}  今日星象預言",
            description=f"*{datetime.datetime.now().strftime('%Y/%m/%d')}*\n\n「{data.get('綜合短評', '星河流轉，命運已定。')}」",
            color=discord.Color.dark_purple(),
        )
        embed.add_field(name="綜合運勢", value=data.get('綜合運勢', '★★★☆☆'), inline=True)
        embed.add_field(name="戀愛運",   value=data.get('戀愛運', '★★★☆☆'), inline=True)
        embed.add_field(name="財運",     value=data.get('財運', '★★★☆☆'), inline=True)
        embed.add_field(name="事業運",   value=data.get('事業運', '★★★☆☆'), inline=True)
        embed.add_field(name="幸運顏色", value=f"**{data.get('幸運顏色', '星辰紫')}**", inline=True)
        embed.add_field(name="幸運數字", value=f"**{data.get('幸運數字', '7')}**", inline=True)
        embed.add_field(name="星河指引", value=data.get('詳細提示', '這片宇宙，始終有光指引著妳。'), inline=False)
        embed.set_footer(text="本座已言盡於此。星河見證。")
        
        await interaction.followup.send(embed=embed)

class ZodiacView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ZodiacSelect())

class Zodiac(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="星座", aliases=["運勢"])
    async def zodiac(self, ctx):
        await ctx.send("（展開星圖）凡人，選妳的星座吧。讓本座看看妳今天的命運。", view=ZodiacView())

async def setup(bot):
    await bot.add_cog(Zodiac(bot))
