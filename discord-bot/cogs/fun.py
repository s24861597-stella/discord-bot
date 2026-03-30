import random
import discord
from discord.ext import commands


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
            ("是。",          discord.Color.dark_green()),
            ("當然。",        discord.Color.dark_green()),
            ("毫無疑問。",    discord.Color.dark_green()),
            ("確定。",        discord.Color.dark_green()),
            ("可能吧。",      discord.Color.dark_green()),
            ("暫時不明。",    discord.Color.dark_gray()),
            ("再想想。",      discord.Color.dark_gray()),
            ("說不準。",      discord.Color.dark_gray()),
            ("現在問不對。",  discord.Color.dark_gray()),
            ("不。",          discord.Color.dark_red()),
            ("別抱希望了。",  discord.Color.dark_red()),
            ("不可能。",      discord.Color.dark_red()),
            ("想都不用想。",  discord.Color.dark_red()),
            ("放棄吧。",      discord.Color.dark_red()),
        ]

        response, color = random.choice(responses)
        embed = discord.Embed(color=color)
        embed.add_field(name="問題", value=question, inline=False)
        embed.add_field(name="答覆", value=f"**{response}**", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
