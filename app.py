import os
import threading

from flask import Flask, send_from_directory

from oonishi_aoi import main as showroom_main

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


def start_showroom_monitor():
    t = threading.Thread(target=showroom_main, daemon=True)
    t.start()


# サーバー起動時に両方の監視・ボットを開始
start_showroom_monitor()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
