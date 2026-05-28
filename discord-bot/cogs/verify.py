import discord
from discord.ext import commands
from discord import app_commands

# ── 設定區 ──────────────────────────────────────────
VERIFY_CHANNEL_NAME = "🎟｜發票中心"   # 放按鈕的頻道名稱
ADMIN_ROLE_NAME     = "🛰୨୧．管理員"   # 要通知的管理身分組名稱
# ────────────────────────────────────────────────────


class VerifyButton(discord.ui.View):
    """頻道裡常駐的「申請驗證」按鈕，timeout=None 讓它重啟後依然有效"""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✉️ 開啟驗證",
        style=discord.ButtonStyle.primary,
        custom_id="verify_open"          # 固定 custom_id，重啟後仍可響應
    )
    async def open_verify(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild   = interaction.guild
        member  = interaction.user
        channel = interaction.channel

        # 防重複：檢查該玩家是否已有開著的驗證串
        existing = discord.utils.get(
            channel.threads,
            name=f"玩家驗證－{member.display_name}"
        )
        if existing:
            await interaction.response.send_message(
                f"✨ 你已經有一個進行中的驗證通道囉：{existing.mention}",
                ephemeral=True
            )
            return

        # 建立私人討論串（private thread）
        thread = await channel.create_thread(
            name=f"玩家驗證－{member.display_name}",
            type=discord.ChannelType.private_thread,
            invitable=False          # 只有管理員可以邀請其他人進來
        )

        # 把申請玩家加入串
        await thread.add_member(member)

        # 找管理身分組
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        admin_mention = admin_role.mention if admin_role else "管理員"

        # 歡迎訊息（銀河語氣）
        embed = discord.Embed(
            title="⭐ 玩家身分驗證",
            description=(
                f"{member.mention} 你好呀～🌙\n\n"
                "這裡是只有你和管理員能看到的私人驗證通道。\n\n"
                "**請直接在下方上傳一張遊玩截圖**，管理員審核通過後就會給你身分組囉！\n\n"
                "> 截圖能清楚看到遊戲畫面就可以，不限平台 ✨"
            ),
            color=0xb39ddb
        )
        embed.set_footer(text="Powered by 銀河 🌌")

        # 通知管理 + 歡迎玩家
        await thread.send(content=f"{admin_mention}", embed=embed)

        # 回覆按鈕點擊（ephemeral，只有玩家看到）
        await interaction.response.send_message(
            f"已為你開啟驗證通道 {thread.mention}，請前往上傳截圖 🌟",
            ephemeral=True
        )


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # 讓 persistent view 在重啟後依然有效
        bot.add_view(VerifyButton())

    # ── 斜線指令：管理員用來在頻道發送驗證按鈕 ──────────
    @app_commands.command(
        name="驗證設置",
        description="在目前頻道發送玩家驗證按鈕（管理員專用）"
    )
    @app_commands.checks.has_role("🛰୨୧．管理員")
    async def setup_verify(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎟 玩家身分驗證",
            description=(
                "請點擊下方按鈕，開啟你的專屬驗證通道。\n\n"
                "• 請準備好一張遊玩截圖\n"
                "• 截圖會在私人通道中上傳\n"
                "• 每次只能開啟一個驗證"
            ),
            color=0xb39ddb
        )
        embed.set_footer(text="Powered by 銀河 🌌")

        await interaction.channel.send(embed=embed, view=VerifyButton())
        await interaction.response.send_message("✅ 驗證按鈕已發送！", ephemeral=True)

    @setup_verify.error
    async def setup_verify_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(
                "❌ 只有管理員才能使用這個指令喔！", ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))