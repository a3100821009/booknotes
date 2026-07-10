"""Shared config: paths, env vars, .env loader."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

# Load .env for local development (GitHub Actions uses secrets directly)
_env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_file):
    with open(_env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

TOKEN = os.environ.get("NOTION_TOKEN", "")
BOOKS_DB_ID = os.environ.get("NOTION_BOOKS_DB_ID", "")
RECORDS_DB_ID = os.environ.get("NOTION_RECORDS_DB_ID", "")

COVERS_DIR = os.path.join(DIST_DIR, "covers")
DATA_FILE = os.path.join(DIST_DIR, "books_data_full.json")
RECORDS_FILE = os.path.join(DIST_DIR, "reading_records.json")
HTML_FILE = os.path.join(DIST_DIR, "index.html")

os.makedirs(DIST_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

if not TOKEN:
    print("WARNING: NOTION_TOKEN not set. Create .env file or set env var.")
