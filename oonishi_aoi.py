import os
import time

from dotenv import load_dotenv

load_dotenv()  # .envファイルから環境変数を読み込む

import requests

# --- 設定項目 ---
# 監視したい配信者のルームURLの末尾部分 (例: https://www.showroom-live.com/r/some_performer の場合は 'some_performer')
ROOM_URL_KEYS = [
    "nearlyequal_joy_official",
    "JOY_AOI_ONISHI",
    "JOY_OZAWA_AIMI",
    "ME_HANA_OGI",
    "ME_NATSUNE_KAWAGUCHI",
    "ME_MIYUKI_HONDA",
]

# DiscordのWebhook URL (絶対に公開しないこと)
# 環境変数から読み込むことを推奨 (例: os.getenv('DISCORD_WEBHOOK_URL'))
os.environ.setdefault("DISCORD_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    raise ValueError(
        "DISCORD_WEBHOOK_URL is not set. Please set it in your environment variables."
    )

# チェック間隔（秒）APIに負荷をかけすぎないよう60秒以上を推奨
CHECK_INTERVAL_SECONDS = 61
# --- 設定項目はここまで ---


def get_room_status(room_url_key):
    """
    【更新】/api/room/status APIを使い、ルームの全情報を一度に取得する
    """
    api_url = (
        f"https://www.showroom-live.com/api/room/status?room_url_key={room_url_key}"
    )
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ APIへのアクセスに失敗しました: {e}")
        return None
    except requests.exceptions.JSONDecodeError:
        print("❌ APIからの応答がJSON形式ではありませんでした。")
        return None


def send_discord_notification(webhook_url, status_data):
    """Discordに配信開始の通知を送信する"""
    # APIの出力から必要な情報を取得
    room_name = status_data.get("room_name", "配信")
    room_url_key = status_data.get("room_url_key")
    room_url = f"https://www.showroom-live.com/r/{room_url_key}"
    # サムネイル画像は "image_s" キーから取得
    thumbnail_url = status_data.get("image_s")

    message = {
        "content": f"**📢 {room_name}が配信を開始しました！**",
        "embeds": [
            {
                "title": f"🎬 {room_name}",
                "url": room_url,
                "description": "配信が始まりました。今すぐ視聴しましょう！",
                "color": 15258703,  # 赤系の色
                "thumbnail": {"url": thumbnail_url},
                "footer": {
                    "text": "Showroom Notifier",
                    "icon_url": "https://www.showroom-live.com/favicon.ico",
                },
            }
        ],
    }
    try:
        response = requests.post(webhook_url, json=message)
        response.raise_for_status()
        print("✅ Discordへ通知を送信しました。")
    except requests.exceptions.RequestException as e:
        print(f"❌ Discordへの通知送信に失敗しました: {e}")


def main():
    """メインの処理"""
    print("🚀 Showroom 配信監視ボットを起動します...")
    print(f"👀 監視対象: {ROOM_URL_KEYS}")
    print(f"🕒 {CHECK_INTERVAL_SECONDS}秒ごとにチェックします。")

    # 各配信者ごとに前回の配信ステータスを管理
    is_streaming_before = {key: False for key in ROOM_URL_KEYS}

    while True:
        for room_url_key in ROOM_URL_KEYS:
            status_data = get_room_status(room_url_key)

            if status_data:
                # "is_live" キーの値 (true/false) で現在の配信状況を判断
                is_streaming_now = status_data.get("is_live", False)

                # 配信が開始された瞬間を検知 (前回はOFF → 今回はON)
                if is_streaming_now and not is_streaming_before[room_url_key]:
                    print(f"🎉 {status_data.get('room_name')} の配信が開始されました！")
                    send_discord_notification(DISCORD_WEBHOOK_URL, status_data)

                # 配信が終了したことをログに記録
                elif not is_streaming_now and is_streaming_before[room_url_key]:
                    print(f"💤 {status_data.get('room_name')} の配信が終了しました。")

                elif not is_streaming_now:
                    print(
                        f"{status_data.get('room_name')}：現在配信は行われていません。"
                    )

                # 次のチェックのためにステータスを更新
                is_streaming_before[room_url_key] = is_streaming_now

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
