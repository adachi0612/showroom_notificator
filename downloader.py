import asyncio
import os

import discord
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DOWNLOAD_DIR = "downloads"
SERVER_IP = os.getenv("SERVER_IP")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def download_video(url):
    ydl_opts = {
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    }
    loop = asyncio.get_running_loop()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await loop.run_in_executor(
            None, lambda: ydl.extract_info(url, download=True)
        )
        downloaded_file = ydl.prepare_filename(info)
        return downloaded_file


@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました。")
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    print(f"ダウンロードディレクトリ: {DOWNLOAD_DIR}")


@bot.command(name="dl")
async def download_command(ctx, url: str):
    try:
        processing_message = await ctx.send(
            f"🔄 `{url}` の処理を開始します。しばらくお待ちください..."
        )
        filepath = await download_video(url)
        filename = os.path.basename(filepath)
        base_url = f"https://{SERVER_IP.rstrip('/')}"
        download_url = f"{base_url}/{DOWNLOAD_DIR}/{filename}"
        # ダウンロードリンクをDiscordに返す
        await processing_message.edit(
            content=f"✅ ダウンロード準備が完了しました！\n\n**ファイル名:** `{filename}`\n**ダウンロードリンク:** {download_url}"
        )
    except Exception as e:
        await ctx.send(f"❌ エラーが発生しました: {e}")
        print(f"エラー: {e}")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
