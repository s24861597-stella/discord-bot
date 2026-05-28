import discord
from discord.ext import commands
from discord import app_commands
import datetime

# ── 設定區 ──────────────────────────────────────────
ADMIN_ROLE_NAME     = "🛰୨୧．管理員"
HYPEN_ID            = 776078980968742944  # Hypen 的 Discord ID
# ────────────────────────────────────────────────────

class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── 斜線指令：開放給所有人！一般成員輸入後直接開私人串 ──
    @app_commands.command(
        name="驗證設置",
        description="開啟妳的專屬玩家驗證通道（直接建立私人討論串）"
    )
    async def setup_verify(self, interaction: discord.Interaction):
        guild   = interaction.guild
        member  = interaction.user
        channel = interaction.channel

        # 1. 防重複：檢查該玩家在目前頻道是否已有開著的驗證串
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

        # 2. 直接建立私人討論串（不需要按鈕了！）
        thread = await channel.create_thread(
            name=f"玩家驗證－{member.display_name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        # 3. 把申請的成員自己拉進去
        await thread.add_member(member)

        # 4. 把君君（Hypen）也拉進去
        hypen = guild.get_member(HYPEN_ID)
        if hypen:
            await thread.add_member(hypen)

        # 5. 找管理身分組來通知
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        admin_mention = admin_role.mention if admin_role else "管理員"

        # 6. 私人串裡的說明訊息（維持妳的精美設定）
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

        # 在私人討論串發送通知與說明
        await thread.send(content=f"{admin_mention} 新驗證申請！")
        await thread.send(embed=embed)

        # 7. 回覆點擊指令的成員（ephemeral=True，只有他自己看得到提示）
        await interaction.response.send_message(
            f"已為你開啟驗證通道 {thread.mention}，請前往上傳截圖 🌟",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))