import discord
import random
import urllib.parse
from discord.ext import commands


class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pt")
    async def generate_image(self, ctx, *, prompt: str):
        encoded = urllib.parse.quote(prompt)
        seed = random.randint(1, 99999)
        url = f"https://image.pollinations.ai/prompt/{encoded}?nologo=true&seed={seed}"
        await ctx.send(f"（展開星際斗篷）正在召喚宇宙意志，為你繪製——")
        await ctx.send(url)


async def setup(bot):
    await bot.add_cog(Image(bot))