import discord
from discord.ext import commands


class General(commands.Cog):
    """一般指令"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["幫助", "h"])
    async def help_command(self, ctx):
        """顯示所有可用指令"""
        prefix = self.bot.command_prefix

        embed = discord.Embed(
            title="📖 指令幫助",
            description=f"使用 `{prefix}<指令名稱>` 來執行指令",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="🔧 一般指令",
            value=(
                f"`{prefix}help` — 顯示此幫助選單\n"
                f"`{prefix}ping` — 查看 Bot 的延遲\n"
                f"`{prefix}invite` — 取得 Bot 邀請連結"
            ),
            inline=False,
        )

        embed.add_field(
            name="ℹ️ 資訊指令",
            value=(
                f"`{prefix}userinfo [成員]` — 查看成員資訊\n"
                f"`{prefix}serverinfo` — 查看伺服器資訊\n"
                f"`{prefix}avatar [成員]` — 查看成員頭像"
            ),
            inline=False,
        )

        embed.add_field(
            name="🎉 趣味指令",
            value=(
                f"`{prefix}hello` — 打招呼\n"
                f"`{prefix}roll [骰子面數]` — 擲骰子（預設 6 面）\n"
                f"`{prefix}flip` — 擲硬幣\n"
                f"`{prefix}say <訊息>` — 讓 Bot 說話"
            ),
            inline=False,
        )

        embed.set_footer(text=f"由 {self.bot.user.name} 提供服務")
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """查看 Bot 的延遲"""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot 延遲：**{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.yellow(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="invite")
    async def invite(self, ctx):
        """取得 Bot 邀請連結"""
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            manage_messages=True,
        )
        url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        embed = discord.Embed(
            title="📨 邀請 Bot",
            description=f"[點擊這裡邀請 {self.bot.user.name} 到你的伺服器]({url})",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
