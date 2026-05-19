from flask import Flask, render_template, jsonify, send_file
import io
import threading
import time

from db import init_db, save_articles, get_all_text
from space_fetcher import fetch_space_articles
from wordcloud_gen import generate_wordcloud

app = Flask(__name__)

# --- background refresh every 30 minutes ---
def background_refresh():
    while True:
        try:
            articles = fetch_space_articles(limit=100)
            save_articles(articles)
            print(f"[Refresh] Saved {len(articles)} articles to DB")
        except Exception as e:
            print(f"[Refresh Error] {e}")
        time.sleep(1800)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/wordcloud.png")
def wordcloud_image():
    text = get_all_text()
    img_bytes = generate_wordcloud(text)
    return send_file(io.BytesIO(img_bytes), mimetype="image/png")


@app.route("/api/stats")
def stats():
    from db import get_stats
    return jsonify(get_stats())


@app.route("/api/refresh", methods=["POST"])
def manual_refresh():
    articles = fetch_space_articles(limit=100)
    count = save_articles(articles)
    return jsonify({"refreshed": count})


if __name__ == "__main__":
    init_db()
    # initial fetch
    try:
        articles = fetch_space_articles(limit=100)
        save_articles(articles)
        print(f"Initial load: {len(articles)} articles")
    except Exception as e:
        print(f"Initial fetch error: {e}")

    t = threading.Thread(target=background_refresh, daemon=True)
    t.start()

    app.run(debug=True, port=5000)
