import requests
from datetime import datetime

BASE_URL = "https://api.spaceflightnewsapi.net/v4/articles/"


def fetch_space_articles(limit: int = 100) -> list:
    """
    Fetch latest space news articles from the Spaceflight News API (free, no key needed).
    Returns a list of article dicts.
    """
    articles = []
    offset = 0
    page_size = min(limit, 50)

    while len(articles) < limit:
        try:
            resp = requests.get(
                BASE_URL,
                params={"limit": page_size, "offset": offset},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[Fetch Error] {e}")
            break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            # Normalise published date
            pub = item.get("published_at", "")
            try:
                pub = datetime.fromisoformat(pub.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pub = None

            articles.append({
                "id":           item.get("id"),
                "title":        item.get("title", ""),
                "summary":      item.get("summary", ""),
                "news_site":    item.get("news_site", ""),
                "published_at": pub,
            })

        offset += page_size
        if offset >= limit:
            break

    return articles[:limit]
