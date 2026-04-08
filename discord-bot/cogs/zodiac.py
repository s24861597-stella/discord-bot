import datetime
import discord
import os
import random
from discord.ext import commands
from discord.ui import View, Select
from google import genai

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
    """叫 Gemini 穿上星際斗篷，給出最中二的即時預言"""
    today = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime("%Y/%m/%d")
    prompt = f"""
    你是「銀河」，一個極度中二沙雕、自稱「本宇宙最強管理員」的 Discord 機器人。
    現在請為你的「凡人信徒」提供 {today} 的 {zodiac} 運勢預言。
    
    回覆規範：
    1. 語氣必須中二沙雕，充滿「本座」、「星河之力」、「凡人」等字眼。
    2. 第一行必須是一句浮誇的今日短評。
    3. 必須包含：綜合運勢、戀愛運、財運、事業運（皆用 1-5 顆 ★ 表示）。
    4. 必須包含：幸運顏色、幸運數字。
    5. 最後是一段約 80 字的「星河指引」，以傲嬌中二但溫柔的口吻給予建議。
    6. 不要使用 Markdown 代碼區塊，直接回覆純文字內容。
    """
    try:
        # 使用穩定版模型
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"（星圖震動）宇宙意志受到了干擾！本座暫時無法窺探天機，妳等等再來吧。錯誤：{e}"

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
        super().__init__(placeholder="選擇你的星座，讓本座為妳觀星…", options=options)

    async def callback(self, interaction: discord.Interaction):
        zodiac = self.values[0]
        # 先回應讓選單不卡住，因為 Gemini 需要時間思考
        await interaction.response.defer()
        
        # 呼叫 Gemini 獲取占卜內容
        horoscope_content = await get_gemini_horoscope(zodiac)

        embed = discord.Embed(
            title=f"{ZODIACS[zodiac]['emoji']} {zodiac} · 星河預言報告",
            description=horoscope_content,
            color=discord.Color.dark_purple(),
        )
        embed.set_footer(text="本座已言盡於此。星河見證。")
        
        # 使用 followup 發送，因為剛才用了 defer
        await interaction.followup.send(embed=embed)

class ZodiacView(View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ZodiacSelect())

class Zodiac(commands.Cog):
    """星座運勢（Gemini AI 版）"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="星座", aliases=["運勢", "zodiac"])
    async def zodiac(self, ctx):
        """查詢星座今日運勢"""
        view = ZodiacView()
        await ctx.send("（展開星際斗篷）凡人，選妳的星座吧。本座將跨越光年為妳窺探天機。", view=view)

async def setup(bot):
    await bot.add_cog(Zodiac(bot))
