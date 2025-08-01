import os
import threading

from flask import Flask

from oonishi_aoi import main

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


if __name__ == "__main__":
    t = threading.Thread(target=main, daemon=True)
    t.start()
    # Herokuが指定するポート番号を取得。なければ5000をデフォルトにする
    port = int(os.environ.get("PORT", 5000))

    # Flask Webサーバーを起動
    app.run(host="0.0.0.0", port=port)
