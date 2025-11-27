import os
import requests
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_BASE = os.getenv("NEWS_API_BASE", "https://newsapi.org/v2")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_news():
    url = f"{NEWS_API_BASE}/top-headlines"
    params = {
        "country": "in",  # India news
        "apiKey": NEWS_API_KEY,
        "pageSize": 10
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("articles", [])

def store_news(articles):
    for article in articles:
        data = {
            "title": article.get("title"),
            "url": article.get("url"),
            "summary": article.get("description"),
            "published_at": article.get("publishedAt", datetime.utcnow().isoformat()),
            "category": article.get("source", {}).get("name", "General"),
            "sentiment": "neutral",  # Placeholder, can be improved
            "fetched_at": datetime.utcnow().isoformat()
        }
        # Upsert by URL to avoid duplicates
        supabase.table("news_cache").upsert(data, on_conflict=["url"]).execute()

if __name__ == "__main__":
    print("Fetching news from NewsAPI...")
    articles = fetch_news()
    print(f"Fetched {len(articles)} articles. Storing in Supabase...")
    store_news(articles)
    print("Done.")
