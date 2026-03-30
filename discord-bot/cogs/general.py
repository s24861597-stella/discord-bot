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
            title="指令清單",
            description=f"前綴：`{prefix}` ── 看清楚，別問我兩遍。",
            color=discord.Color.dark_gray(),
        )

        embed.add_field(
            name="基本",
            value=(
                f"`{prefix}help` — 這份清單\n"
                f"`{prefix}ping` — 確認連線\n"
                f"`{prefix}invite` — 邀請連結"
            ),
            inline=False,
        )

        embed.add_field(
            name="查詢",
            value=(
                f"`{prefix}userinfo [@成員]` — 成員資料\n"
                f"`{prefix}serverinfo` — 伺服器資料\n"
                f"`{prefix}avatar [@成員]` — 查看頭像"
            ),
            inline=False,
        )

        embed.add_field(
            name="趣味",
            value=(
                f"`{prefix}hello` — 打招呼\n"
                f"`{prefix}roll [面數]` — 擲骰子\n"
                f"`{prefix}flip` — 擲硬幣\n"
                f"`{prefix}choose 選1 選2` — 做決定\n"
                f"`{prefix}8ball <問題>` — 占卜\n"
                f"`{prefix}say <內容>` — 代為傳話"
            ),
            inline=False,
        )

        embed.add_field(
            name="♎ 星座運勢",
            value=(
                f"`{prefix}星座` — 開選單選星座\n"
                f"`{prefix}星座 獅子座` — 直接查指定星座\n"
                f"每天結果固定，同天問同答。"
            ),
            inline=False,
        )

        embed.set_footer(text="沒有下一次提醒了。")
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        """查看延遲"""
        latency = round(ctx.bot.latency * 1000)
        status = "正常。" if latency < 100 else "有點慢。"
        embed = discord.Embed(
            description=f"延遲 **{latency}ms**。{status}",
            color=discord.Color.dark_gray(),
        )
        await ctx.send(embed=embed)

    @commands.command(name="invite")
    async def invite(self, ctx):
        """取得邀請連結"""
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            manage_messages=True,
        )
        url = discord.utils.oauth_url(ctx.bot.user.id, permissions=permissions)
        embed = discord.Embed(
            description=f"[邀請連結]({url})。用好。",
            color=discord.Color.dark_gray(),
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))
