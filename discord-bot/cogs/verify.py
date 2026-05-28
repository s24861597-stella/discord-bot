import discord
from discord.ext import commands
from discord import app_commands

# ── 設定區 ──────────────────────────────────────────
VERIFY_CHANNEL_NAME = "🎟｜發票中心"   # 放按鈕的頻道名稱
ADMIN_ROLE_NAME     = "🛰୨୧．管理員"   # 要通知的管理身分組名稱
# ────────────────────────────────────────────────────


class VerifyButton(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✉️ 開啟驗證",
        style=discord.ButtonStyle.primary,
        custom_id="verify_open_v2"
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

        # 建立私人討論串
        thread = await channel.create_thread(
            name=f"玩家驗證－{member.display_name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        # 把申請玩家加入串
        await thread.add_member(member)

        # 找管理身分組
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        admin_mention = admin_role.mention if admin_role else "管理員"

        # 說明訊息
        embed = discord.Embed(
            title="⭐ 玩家身分驗證",
            description=(
                f"{member.mention} 你好呀～🌙\n\n"
                "請提供妳的遊戲截圖（75需要戀人以上，其他平台需自證p.300以上，"
                "有問題請直接留言，比如說不喜歡資訊欄所以沒頁數，則按情況酌情提供），"
                "會私訊提供你，可作為生圖或是其他衍生二創使用～感謝大家。\n\n"
                "有可能我提供的資料與你所玩到的、角色提供給你的不同，"
                "若有需要以自己的窗所獲得的個人資料，製作CP衍生二創，"
                "不需要過問我這邊，謝謝！"
            ),
            color=0xb39ddb
        )
        embed.set_footer(text="Powered by 銀河 🌌")

        # tag 管理員 + 發說明
        await thread.send(content=f"{admin_mention} 新驗證申請！")
        await thread.send(embed=embed)

        # 回覆玩家
        await interaction.response.send_message(
            f"已為你開啟驗證通道 {thread.mention}，請前往上傳截圖 🌟",
            ephemeral=True
        )


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(VerifyButton())

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
