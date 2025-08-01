import os
import threading

from flask import Flask

from oonishi_aoi import main

app = Flask(__name__)


@app.route("/")
def index():
    return "OK"


def start_monitor():
    t = threading.Thread(target=main, daemon=True)
    t.start()


start_monitor()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
