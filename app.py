import os
import threading

from flask import Flask

from oonishi_aoi import main
from tiktok_random import main as tiktok_main

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


def start_monitor():
    t = threading.Thread(target=main, daemon=True)
    t.start()


def start_tiktok_dice():
    t = threading.Thread(target=tiktok_main, daemon=True)
    t.start()


start_monitor()
start_tiktok_dice()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
