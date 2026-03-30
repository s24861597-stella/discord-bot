import random
import discord
from discord.ext import commands


class Fun(commands.Cog):
    """趣味指令"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hello", aliases=["嗨", "哈囉", "hi"])
    async def hello(self, ctx):
        """Bot 打招呼"""
        greetings = [
            f"嗨嗨！{ctx.author.mention}，你好！😊",
            f"哈囉！{ctx.author.mention}，很高興見到你！🎉",
            f"嘿！{ctx.author.mention}，有什麼我能幫你的嗎？✨",
            f"你好！{ctx.author.mention}，今天過得怎麼樣？😄",
            f"Hi！{ctx.author.mention}！希望你今天愉快！🌟",
        ]
        await ctx.send(random.choice(greetings))

    @commands.command(name="roll", aliases=["骰子", "dice"])
    async def roll_dice(self, ctx, sides: int = 6):
        """擲骰子
        
        用法：!roll [面數]
        例：!roll 20（擲 20 面骰子）
        """
        if sides < 2:
            await ctx.send("❌ 骰子至少需要 2 面！")
            return
        if sides > 1000:
            await ctx.send("❌ 骰子面數最多 1000 面！")
            return

        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 擲骰子！",
            description=f"{ctx.author.mention} 擲了一個 **{sides}** 面骰子",
            color=discord.Color.orange(),
        )
        embed.add_field(name="結果", value=f"🎯 **{result}**")
        await ctx.send(embed=embed)

    @commands.command(name="flip", aliases=["硬幣", "coin"])
    async def flip_coin(self, ctx):
        """擲硬幣"""
        result = random.choice(["正面 🪙", "反面 🔄"])
        embed = discord.Embed(
            title="🪙 擲硬幣！",
            description=f"{ctx.author.mention} 擲了一枚硬幣",
            color=discord.Color.gold(),
        )
        embed.add_field(name="結果", value=f"**{result}**")
        await ctx.send(embed=embed)

    @commands.command(name="say", aliases=["說話", "repeat"])
    async def say(self, ctx, *, message: str):
        """讓 Bot 說出指定的訊息
        
        用法：!say <訊息>
        """
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="choose", aliases=["選擇", "pick"])
    async def choose(self, ctx, *options: str):
        """從多個選項中隨機選擇一個
        
        用法：!choose 選項1 選項2 選項3
        """
        if len(options) < 2:
            await ctx.send("❌ 請至少提供 2 個選項！\n用法：`!choose 選項1 選項2 選項3`")
            return

        chosen = random.choice(options)
        embed = discord.Embed(
            title="🤔 我的選擇是...",
            description=f"在 **{len(options)}** 個選項中，我選擇了：",
            color=discord.Color.purple(),
        )
        embed.add_field(name="✨ 結果", value=f"**{chosen}**")
        await ctx.send(embed=embed)

    @commands.command(name="8ball", aliases=["魔法球"])
    async def eight_ball(self, ctx, *, question: str):
        """問魔法 8 號球一個問題
        
        用法：!8ball <問題>
        """
        responses = [
            ("是的，當然！", discord.Color.green()),
            ("絕對是！", discord.Color.green()),
            ("毫無疑問！", discord.Color.green()),
            ("我認為是的！", discord.Color.green()),
            ("很可能是！", discord.Color.green()),
            ("前景不錯！", discord.Color.green()),
            ("是的！", discord.Color.green()),
            ("跡象表明是！", discord.Color.green()),
            ("目前不清楚，再試一次。", discord.Color.yellow()),
            ("稍後再問。", discord.Color.yellow()),
            ("現在不好說。", discord.Color.yellow()),
            ("現在無法預測。", discord.Color.yellow()),
            ("專注後再問。", discord.Color.yellow()),
            ("別指望了。", discord.Color.red()),
            ("我的回答是否定的。", discord.Color.red()),
            ("我的消息來源說不。", discord.Color.red()),
            ("前景不樂觀。", discord.Color.red()),
            ("非常懷疑。", discord.Color.red()),
        ]

        response, color = random.choice(responses)
        embed = discord.Embed(
            title="🎱 魔法 8 號球",
            color=color,
        )
        embed.add_field(name="❓ 問題", value=question, inline=False)
        embed.add_field(name="🔮 回答", value=f"**{response}**", inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
