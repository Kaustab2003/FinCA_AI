#!/usr/bin/env python3
"""
FinCA AI - Automated News Fetcher
This script runs periodically to fetch and store financial news
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/news_fetcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to fetch and store news"""
    try:
        logger.info("Starting automated news fetch...")

        # Import after path setup
        from scripts.fetch_and_store_news import fetch_news, store_news

        # Fetch news
        logger.info("Fetching news from Alpha Vantage...")
        articles = fetch_news()

        if articles:
            logger.info(f"Fetched {len(articles)} articles")

            # Store news
            logger.info("Storing news in database...")
            stored_count = store_news(articles)
            logger.info(f"Successfully stored {stored_count} articles")
        else:
            logger.warning("No articles fetched")

        logger.info("News fetch completed successfully")

    except Exception as e:
        logger.error(f"Error in automated news fetch: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    main()