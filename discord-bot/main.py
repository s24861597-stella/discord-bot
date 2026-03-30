import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

COGS = [
    "cogs.general",
    "cogs.info",
    "cogs.fun",
]


@bot.event
async def on_ready():
    print(f"✅ Bot 已上線！登入身份：{bot.user} (ID: {bot.user.id})")
    print(f"📡 連接到 {len(bot.guilds)} 個伺服器")
    print("─" * 40)
    await bot.change_presence(
        activity=discord.Game(name=f"{PREFIX}help | Discord Bot")
    )


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ 找不到指令！輸入 `{PREFIX}help` 查看可用指令。")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ 缺少必要的參數！請檢查指令用法。")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ 你沒有執行此指令的權限！")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("❌ 機器人沒有執行此操作所需的權限！")
    else:
        print(f"發生錯誤：{error}")
        await ctx.send(f"❌ 發生了一個錯誤：{error}")


async def load_cogs():
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            print(f"✅ 載入模組：{cog}")
        except Exception as e:
            print(f"❌ 無法載入模組 {cog}：{e}")


async def main():
    if not TOKEN:
        print("❌ 錯誤：找不到 DISCORD_TOKEN！")
        print("請在 .env 檔案中設定 DISCORD_TOKEN=你的Bot Token")
        return

    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
