import os
import requests
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_BASE_URL = os.getenv("ALPHAVANTAGE_BASE_URL", "https://www.alphavantage.co/query")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_news():
    """Fetch financial news from Alpha Vantage NEWS_SENTIMENT API"""
    url = ALPHAVANTAGE_BASE_URL
    params = {
        "function": "NEWS_SENTIMENT",
        "sort": "LATEST",
        "limit": 50,  # Get up to 50 articles
        "apikey": ALPHAVANTAGE_API_KEY
    }

    print(f"Making request to: {url}")
    print(f"Parameters: {params}")

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    data = resp.json()
    print(f"API Response keys: {list(data.keys())}")

    # Alpha Vantage returns 'feed' array with articles
    articles = data.get("feed", [])
    print(f"Found {len(articles)} articles in response")

    return articles

def store_news(articles):
    """Store news articles in Supabase news_cache table"""
    stored_count = 0

    for article in articles:
        try:
            # Map Alpha Vantage response to our schema
            data = {
                "title": article.get("title", "No Title"),
                "url": article.get("url", ""),
                "summary": article.get("summary", "")[:1000],  # Limit summary length
                "published_at": article.get("time_published", datetime.utcnow().isoformat()),
                "category": article.get("topics", ["General"])[0] if article.get("topics") else "General",
                "sentiment": article.get("overall_sentiment_label", "neutral"),
                "fetched_at": datetime.utcnow().isoformat()
            }

            # Skip articles without URLs
            if not data["url"]:
                print(f"Skipping article without URL: {data['title']}")
                continue

            # Convert published_at to proper format if needed
            if data["published_at"] and len(data["published_at"]) > 10:
                # Alpha Vantage format: "20231201T123000" -> convert to ISO
                try:
                    dt = datetime.strptime(data["published_at"], "%Y%m%dT%H%M%S")
                    data["published_at"] = dt.isoformat()
                except ValueError:
                    # If parsing fails, use current time
                    data["published_at"] = datetime.utcnow().isoformat()

            print(f"Storing article: {data['title'][:50]}...")

            # Upsert by URL to avoid duplicates
            result = supabase.table("news_cache").upsert(data, on_conflict=["url"]).execute()
            stored_count += 1

        except Exception as e:
            print(f"Error storing article: {e}")
            continue

    print(f"Successfully stored {stored_count} articles")

if __name__ == "__main__":
    print("Fetching financial news from Alpha Vantage...")
    try:
        articles = fetch_news()
        print(f"Fetched {len(articles)} articles. Storing in Supabase...")
        store_news(articles)
        print("Done.")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
