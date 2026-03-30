import discord
from discord.ext import commands


class Info(commands.Cog):
    """資訊查詢指令"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["使用者", "user"])
    async def user_info(self, ctx, member: discord.Member = None):
        """查看成員資訊"""
        member = member or ctx.author

        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        roles_str = " ".join(roles) if roles else "無"

        embed = discord.Embed(
            title=f"👤 {member.display_name} 的資訊",
            color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="🏷️ 使用者名稱", value=str(member), inline=True)
        embed.add_field(name="🆔 使用者 ID", value=member.id, inline=True)
        embed.add_field(name="🤖 是否為機器人", value="是" if member.bot else "否", inline=True)

        embed.add_field(
            name="📅 帳號建立時間",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=False,
        )
        embed.add_field(
            name="📥 加入伺服器時間",
            value=discord.utils.format_dt(member.joined_at, style="F") if member.joined_at else "未知",
            inline=False,
        )
        embed.add_field(
            name=f"🎭 身分組（{len(roles)} 個）",
            value=roles_str if len(roles_str) < 1024 else f"共 {len(roles)} 個身分組",
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.command(name="serverinfo", aliases=["伺服器", "server"])
    async def server_info(self, ctx):
        """查看伺服器資訊"""
        guild = ctx.guild

        embed = discord.Embed(
            title=f"🏰 {guild.name} 的資訊",
            color=discord.Color.gold(),
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="🆔 伺服器 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 伺服器擁有者", value=guild.owner.mention if guild.owner else "未知", inline=True)
        embed.add_field(name="🌍 地區", value=str(guild.preferred_locale), inline=True)

        embed.add_field(name="👥 成員總數", value=guild.member_count, inline=True)
        embed.add_field(name="💬 頻道數", value=len(guild.channels), inline=True)
        embed.add_field(name="🎭 身分組數", value=len(guild.roles), inline=True)

        embed.add_field(name="😀 表情符號數", value=len(guild.emojis), inline=True)
        embed.add_field(name="🚀 Boost 等級", value=f"等級 {guild.premium_tier}", inline=True)
        embed.add_field(name="💎 Boost 數量", value=guild.premium_subscription_count, inline=True)

        embed.add_field(
            name="📅 建立時間",
            value=discord.utils.format_dt(guild.created_at, style="F"),
            inline=False,
        )

        if guild.description:
            embed.add_field(name="📝 伺服器描述", value=guild.description, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="avatar", aliases=["頭像", "av"])
    async def avatar(self, ctx, member: discord.Member = None):
        """查看成員頭像"""
        member = member or ctx.author

        embed = discord.Embed(
            title=f"🖼️ {member.display_name} 的頭像",
            color=discord.Color.blue(),
        )
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(
            name="連結",
            value=f"[點擊查看原圖]({member.display_avatar.url})",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))
