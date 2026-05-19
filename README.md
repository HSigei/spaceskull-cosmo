# 🌌 Cosmos Word Cloud

A live space-news word cloud website built with Python (Flask) + MariaDB.

## What it does

- **Fetches** the latest space news articles from the free [Spaceflight News API](https://api.spaceflightnewsapi.net) (NASA, SpaceX, ESA, etc.)
- **Stores** titles & summaries in MariaDB (no duplicates, upsert-safe)
- **Generates** a beautiful skull-shaped word cloud using the Python `wordcloud` library
- **Serves** a dark space-themed website with live stats, auto-refresh, and PNG download
- **Auto-refreshes** the data every 30 minutes in the background

---

## Project Structure

```
space-wordcloud/
├── app.py            # Flask routes + background refresh thread
├── db.py             # MariaDB connection, schema, queries
├── space_fetcher.py  # Spaceflight News API client
├── wordcloud_gen.py  # Word cloud image generator
├── requirements.txt  # Python dependencies
├── setup.sql         # MariaDB one-time setup script
└── templates/
    └── index.html    # Frontend (starfield, stats, cloud, controls)
```

---

## Setup

### 1. MariaDB — one-time setup

```bash
sudo mariadb -u root -p < setup.sql
```

Or run manually in the MariaDB shell:

```sql
CREATE DATABASE space_wordcloud CHARACTER SET utf8mb4;
CREATE USER 'space_user'@'localhost' IDENTIFIED BY 'space_pass';
GRANT ALL PRIVILEGES ON space_wordcloud.* TO 'space_user'@'localhost';
FLUSH PRIVILEGES;
```

> **Change the password** — update `setup.sql` and `db.py` (or use env vars below).

---

### 2. Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

### 3. Configure (optional — env vars override defaults)

| Variable   | Default          | Description             |
|------------|-----------------|-------------------------|
| `DB_HOST`  | `localhost`     | MariaDB host            |
| `DB_PORT`  | `3306`          | MariaDB port            |
| `DB_USER`  | `space_user`    | DB username             |
| `DB_PASS`  | `space_pass`    | DB password             |
| `DB_NAME`  | `space_wordcloud` | Database name          |

Example:
```bash
export DB_PASS="my_secure_password"
```

---

### 4. Run

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## API Endpoints

| Endpoint             | Method | Description                           |
|----------------------|--------|---------------------------------------|
| `/`                  | GET    | Main page                             |
| `/wordcloud.png`     | GET    | Live word cloud image                 |
| `/api/stats`         | GET    | JSON stats (article count, sources)   |
| `/api/refresh`       | POST   | Manually fetch new articles           |

---

## Customisation

- **More words / pages**: Change `limit=100` in `app.py` to fetch more articles.
- **Colours**: Edit `COLORS` list in `wordcloud_gen.py`.
- **Stopwords**: Add terms to `CUSTOM_STOPWORDS` in `wordcloud_gen.py`.
- **Refresh interval**: Change `time.sleep(1800)` in `app.py` (seconds).
- **Data source**: Swap `space_fetcher.py` to use the NASA APOD API, Open Notify, or any RSS feed.

---

## Data Source

Articles are pulled from the **Spaceflight News API** — completely free, no API key required.
Coverage includes NASA, SpaceX, ESA, Roscosmos, Blue Origin, and dozens of space news outlets.
