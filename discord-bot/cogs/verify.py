import discord
from discord.ext import commands
from discord import app_commands

# ── 設定區 ──────────────────────────────────────────
HYPEN_ID = 776078980968742944  # 君君 Discord ID
# ────────────────────────────────────────────────────


class Verify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="驗證設置",
        description="開啟你的專屬玩家驗證通道"
    )
    async def setup_verify(self, interaction: discord.Interaction):

        guild = interaction.guild
        member = interaction.user
        channel = interaction.channel

        # 防止重複開串
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

        # Discord 必須先回應
        await interaction.response.send_message(
            "正在為你開啟驗證通道，請稍候…🌟",
            ephemeral=True
        )

        # 建立私人討論串
        thread = await channel.create_thread(
            name=f"玩家驗證－{member.display_name}",
            type=discord.ChannelType.private_thread,
            invitable=False
        )

        # 加入開票者
        await thread.add_user(member)

        # 加入君君
        hypen = guild.get_member(HYPEN_ID)
        if hypen:
            await thread.add_user(hypen)

        # 驗證說明 Embed
        embed = discord.Embed(
            title="⭐ 玩家身分驗證",
            description=(
                f"{member.mention} 你好呀～🌙\n\n"
                "請提供妳的遊戲截圖（75需要戀人以上，其他平台需自證 p.300 以上，"
                "有問題請直接留言，比如說不喜歡資訊欄所以沒頁數，則按情況酌情提供）。\n\n"
                "通過後會私訊提供你，可作為生圖或其他衍生二創使用～感謝大家。\n\n"
                "有可能我提供的資料與你所玩到的、角色提供給你的不同。"
                "若有需要以自己的窗所獲得的個人資料製作 CP 衍生二創，"
                "不需要過問我這邊，謝謝！"
            ),
            color=0xb39ddb
        )

        embed.set_footer(text="Powered by 銀河 🌌")

        # Ping 君君
        await thread.send(
            content=f"<@{HYPEN_ID}> 新驗證申請！"
        )

        # 發送說明
        await thread.send(embed=embed)

        # 更新原始回覆
        await interaction.edit_original_response(
            content=f"已為你開啟驗證通道 {thread.mention}，請前往上傳截圖 🌟"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))