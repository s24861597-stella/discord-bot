import random
import discord
from discord.ext import commands
from google import genai
import os
import asyncio

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


class Fun(commands.Cog):
    """互動指令"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello", aliases=["嗨", "哈囉", "hi"])
    async def hello(self, ctx):
        """打招呼"""
        greetings = [
            f"{ctx.author.mention} 嗯。",
            f"來了，{ctx.author.mention}。",
            f"{ctx.author.mention}。有事？",
            f"嗯，{ctx.author.mention}。說。",
            f"{ctx.author.mention}。",
        ]
        await ctx.send(random.choice(greetings))

    @commands.command(name="roll", aliases=["骰子", "dice"])
    async def roll_dice(self, ctx, sides: int = 6):
        """擲骰子"""
        if sides < 2:
            await ctx.send("骰子至少兩面。別鬧。")
            return
        if sides > 1000:
            await ctx.send("最多 1000 面。要求太多了。")
            return

        result = random.randint(1, sides)
        embed = discord.Embed(
            description=f"{ctx.author.mention} 擲 {sides} 面骰。結果：**{result}**。",
            color=discord.Color.dark_gray(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="flip", aliases=["硬幣", "coin"])
    async def flip_coin(self, ctx):
        """擲硬幣"""
        result = random.choice(["正面", "反面"])
        embed = discord.Embed(
            description=f"{ctx.author.mention} 擲硬幣。**{result}**。",
            color=discord.Color.dark_gray(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="say", aliases=["說話", "repeat"])
    async def say(self, ctx, *, message: str):
        """代為傳話"""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="choose", aliases=["選擇", "pick"])
    async def choose(self, ctx, *options: str):
        """替你做決定"""
        if len(options) < 2:
            await ctx.send("至少給兩個選項。自己想清楚再來。")
            return

        chosen = random.choice(options)
        embed = discord.Embed(
            description=f"**{chosen}**。就這個。不用再猶豫了。",
            color=discord.Color.dark_gray(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="8ball", aliases=["魔法球"])
    async def eight_ball(self, ctx, *, question: str):
        """占卜"""
        responses = [
            ("星河之力已給出答案——是的，本座確認。", "✅", discord.Color.dark_green()),
            ("宇宙意志明確指示：當然可以。毋庸置疑。", "✅", discord.Color.dark_green()),
            ("（閉目感應三秒）毫無疑問。本座的預言從不出錯。", "✅", discord.Color.dark_green()),
            ("（展開星圖）確定。就照這個方向走，別猶豫。", "✅", discord.Color.dark_green()),
            ("（微微點頭）可能吧。宇宙偏向於是，但變數仍在。", "✅", discord.Color.dark_green()),
            ("（皺眉凝視星河）……暫時看不清，宇宙迷霧太濃。", "🔮", discord.Color.dark_gray()),
            ("（搖頭）時機未到，再想想。本座無法妄下定論。", "🔮", discord.Color.dark_gray()),
            ("（星圖模糊）說不準。宇宙此刻態度曖昧，本座也沒辦法。", "🔮", discord.Color.dark_gray()),
            ("（放下星圖）現在問不對時機。換個時間再來。", "🔮", discord.Color.dark_gray()),
            ("（冷靜搖頭）不。星河明確拒絕了這個可能性。", "❌", discord.Color.dark_red()),
            ("（嘆氣）別抱希望了。宇宙意志已經給出答案，接受吧。", "❌", discord.Color.dark_red()),
            ("（斬釘截鐵）不可能。本座在星河中找不到任何支持的跡象。", "❌", discord.Color.dark_red()),
            ("（闔上星圖）想都不用想。這條路宇宙不允許。", "❌", discord.Color.dark_red()),
            ("（輕拍你肩膀）放棄吧。本座說這話不是殘忍，是為你好。", "❌", discord.Color.dark_red()),
        ]

        response, icon, color = random.choice(responses)
        embed = discord.Embed(
            description=f"「{question}」\n\n{icon} {response}",
            color=color,
        )
        embed.set_footer(text="本座已言盡於此。星河見證。")
        await ctx.send(embed=embed)

    @commands.command(name="吃什麼", aliases=["eat", "今天吃什麼", "晚餐吃什麼", "午餐吃什麼"])
    async def what_to_eat(self, ctx):
        """今天吃什麼"""
        for attempt in range(3):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents="你是中二沙雕管理員銀河，用戶問今天要吃什麼，用中二風格推薦一樣具體的食物，只能說一樣，四十字以內，要有動作描寫。",
                    )
                )
                reply = response.text.strip()
                embed = discord.Embed(
                    description=reply,
                    color=discord.Color.dark_purple(),
                )
                embed.set_footer(text="本座的宇宙食譜，不接受反駁。")
                await ctx.send(embed=embed)
                return
            except Exception as e:
                if ("429" in str(e) or "503" in str(e)) and attempt < 2:
                    await asyncio.sleep(10 * (attempt + 1))
                    continue
                await ctx.send("（皺眉）宇宙訊號中斷，本座暫時無法存取食譜。稍後再試。")
                return


async def setup(bot):
    await bot.add_cog(Fun(bot))