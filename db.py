import pymysql
import os
from pathlib import Path


def _load_local_env() -> None:
    """Load key/value pairs from .env into process env if not already set."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


_load_local_env()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",   "localhost"),
    "port":     int(os.getenv("DB_PORT", 3307)),
    "user":     os.getenv("DB_USER",   "space_user"),
    "password": os.getenv("DB_PASS",   "change_me"),
    "database": os.getenv("DB_NAME",   "space_wordcloud"),
    "charset":  "utf8mb4",
}


def get_conn():
    return pymysql.connect(**DB_CONFIG)


def init_db():
    """Create the database/table if they don't exist."""
    cfg = {**DB_CONFIG}
    db_name = cfg.pop("database")
    conn = pymysql.connect(**cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
    finally:
        conn.close()

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    external_id INT UNIQUE,
                    title       TEXT,
                    summary     TEXT,
                    source      VARCHAR(255),
                    published   DATETIME,
                    fetched_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        print("[DB] Table ready.")
    finally:
        conn.close()


def save_articles(articles: list) -> int:
    """Insert new articles, ignore duplicates. Returns count inserted."""
    if not articles:
        return 0
    conn = get_conn()
    inserted = 0
    try:
        with conn.cursor() as cur:
            for a in articles:
                try:
                    cur.execute("""
                        INSERT IGNORE INTO articles (external_id, title, summary, source, published)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (a["id"], a["title"], a["summary"], a["news_site"], a["published_at"]))
                    inserted += cur.rowcount
                except Exception:
                    pass
        conn.commit()
    finally:
        conn.close()
    return inserted


def get_all_text() -> str:
    """Return all titles + summaries as one big string."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT title, summary FROM articles")
            rows = cur.fetchall()
        return " ".join(f"{r[0]} {r[1] or ''}" for r in rows)
    finally:
        conn.close()


def get_stats() -> dict:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM articles")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(DISTINCT source) FROM articles")
            sources = cur.fetchone()[0]
            cur.execute("SELECT MAX(fetched_at) FROM articles")
            last = cur.fetchone()[0]
        return {
            "total_articles": total,
            "unique_sources": sources,
            "last_updated": str(last) if last else "Never",
        }
    finally:
        conn.close()
