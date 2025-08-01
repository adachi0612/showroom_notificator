import asyncio
import os
import random
import time  # timeライブラリをインポート

import discord
import pyktok as pyk
from discord.ext import commands
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()


# --- 設定項目 ---
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TIKTOK_USERNAMES = [
    "nearlyequal_joy",
    "notequal_me",
    "notequal_me_hana",
    "notequal_me_miyuki",
]
RANDOM_VIDEO_COUNT = 1  # !randomコマンドで取得する動画数
VIDEOS_PER_USER_TO_FETCH = 42  # 1回の取得で試みる動画数
# --- 設定項目はここまで ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


# 【変更点】cursorを引数に追加
def get_videos_sync(username, cursor):
    """
    【同期的】pyktokを使って指定ユーザーの動画リストを取得する関数。
    cursorで指定された時点から動画を取得する。
    """
    try:
        print(f"📄 [{username}] から動画を取得開始 (cursor: {cursor})...")
        videos = pyk.get_user_videos(
            username, count=VIDEOS_PER_USER_TO_FETCH, cursor=cursor  # cursorを指定
        )
        print(f"✅ [{username}] から動画を{len(videos)}件取得完了。")
        return videos
    except Exception as e:
        print(f"❌ [{username}] 動画の取得に失敗: {e}")
        return []


def create_video_embed(video):
    """取得した動画情報からDiscordの埋め込みメッセージを作成する"""
    author_name = video["author"]["uniqueId"]
    video_id = video["id"]
    video_url = f"https://www.tiktok.com/@{author_name}/video/{video_id}"
    video_desc = video.get("desc") or "（説明なし）"

    stats = video.get("stats", {})
    stats_text = (
        f"❤️ **いいね:** {stats.get('diggCount', 0):,}\n"
        f"💬 **コメント:** {stats.get('commentCount', 0):,}\n"
        f"🔗 **シェア:** {stats.get('shareCount', 0):,}"
    )

    embed = discord.Embed(
        title=video_desc, url=video_url, description=stats_text, color=0xFF0050
    )
    embed.set_author(
        name=f"@{author_name}",
        url=f"https://www.tiktok.com/@{author_name}",
        icon_url=video["author"].get("avatarThumb"),
    )
    embed.set_footer(
        text="Random TikTok Finder",
        icon_url="https://sf-cdn.co/images/tiktok-logo-24.png",
    )
    if video.get("video", {}).get("cover"):
        embed.set_image(url=video["video"]["cover"])

    return embed


@bot.event
async def on_ready():
    """ボットが起動したときに実行されるイベント"""
    print("---")
    print(f"🚀 ボットが起動しました: {bot.user}")
    print(f'👀 監視対象アカウント: {", ".join(TIKTOK_USERNAMES)}')
    print(f"💬 コマンド「!random」でランダムに動画を{RANDOM_VIDEO_COUNT}件取得します。")
    print("---")


@bot.command(name="random")
async def get_random_tiktoks(ctx):
    """!randomコマンドを受け取ったときに実行される関数"""
    await ctx.send(
        f"**⏳ TikTokからランダムな動画を探しています...**\n対象: `{', '.join(TIKTOK_USERNAMES)}`"
    )

    all_videos = []

    # 【変更点】ランダムなcursorを生成し、各ユーザーの取得タスクに渡す
    # 2020年〜現在までのUnixタイムスタンプの範囲でランダムな値を生成
    current_time = int(time.time())
    start_time = 1577836800  # 2020-01-01

    tasks = []
    for username in TIKTOK_USERNAMES:
        # ユーザーごとに違う時点から取得を開始する
        random_cursor = random.randint(start_time, current_time) * 1000
        tasks.append(asyncio.to_thread(get_videos_sync, username, random_cursor))

    results = await asyncio.gather(*tasks)

    for video_list in results:
        all_videos.extend(video_list)

    if not all_videos:
        await ctx.send(
            "❌ 動画を1件も見つけられませんでした。時間をおいて再度お試しください。"
        )
        return

    sample_count = min(RANDOM_VIDEO_COUNT, len(all_videos))
    random_videos = random.sample(all_videos, k=sample_count)

    await ctx.send(f"**🎉 見つかった動画の中から {sample_count}件をお届けします！**")

    for video in random_videos:
        embed = create_video_embed(video)
        await ctx.send(embed=embed)
        await asyncio.sleep(1)


def main():
    if not DISCORD_BOT_TOKEN:
        print("❌ 環境変数 'DISCORD_BOT_TOKEN' を.envファイルに設定してください。")
        return
    if not TIKTOK_USERNAMES:
        print(
            "❌ 'TIKTOK_USERNAMES' リストに少なくとも1つのユーザー名を設定してください。"
        )
        return

    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
