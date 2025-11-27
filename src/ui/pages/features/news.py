"""
FinCA AI - News Page
Displays financial news with sentiment analysis from Alpha Vantage
"""
import streamlit as st
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.services.features_service import FeaturesService
from src.utils.session_manager import SessionManager


def show_news_page():
    """Display the news page with financial news and sentiment analysis"""

    st.title("📰 Financial News & Market Insights")

    # Check if user is logged in
    if not SessionManager.is_authenticated():
        st.warning("Please log in to access news features.")
        return

    user_id = SessionManager.get_user_id()
    service = FeaturesService()

    # News filters and controls
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader("📈 Market News Feed")

    with col2:
        # Sentiment filter
        sentiment_filter = st.selectbox(
            "Filter by Sentiment",
            ["All", "Bullish", "Bearish", "Neutral"],
            key="sentiment_filter"
        )

    with col3:
        # Time filter
        time_filter = st.selectbox(
            "Time Period",
            ["All Time", "Last 24h", "Last 7 days", "Last 30 days"],
            key="time_filter"
        )

    # Fetch news
    news_data = []
    try:
        news_data = service.get_latest_news()

        if news_data:
            # Apply filters
            filtered_news = filter_news(news_data, sentiment_filter, time_filter)

            if filtered_news:
                # Display news count
                st.info(f"Showing {len(filtered_news)} articles")

                # Display news articles
                for article in filtered_news:
                    display_news_article(article)
            else:
                st.info("No news articles match your filters. Try adjusting the filters.")
        else:
            st.warning("No news data available. The news fetching service might not be running.")

    except Exception as e:
        st.error(f"Error loading news: {str(e)}")

    # Always show manual refresh option
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh News", key="refresh_news"):
            with st.spinner("Fetching latest news..."):
                # Import and run the news fetching script
                import subprocess
                import sys
                try:
                    result = subprocess.run([
                        sys.executable,
                        str(Path(__file__).parent.parent.parent.parent.parent / "scripts" / "fetch_and_store_news.py")
                    ], capture_output=True, text=True, cwd=str(Path(__file__).parent.parent.parent.parent.parent))

                    if result.returncode == 0:
                        st.success("News refreshed successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to refresh news: {result.stderr}")
                except Exception as e:
                    st.error(f"Error refreshing news: {str(e)}")

    # News statistics
    st.markdown("---")
    show_news_statistics(news_data)


def filter_news(news_data, sentiment_filter, time_filter):
    """Filter news based on sentiment and time criteria"""
    filtered = news_data.copy()

    # Sentiment filter
    if sentiment_filter != "All":
        sentiment_map = {
            "Bullish": ["Bullish", "Somewhat-Bullish"],
            "Bearish": ["Bearish", "Somewhat-Bearish"],
            "Neutral": ["Neutral"]
        }
        allowed_sentiments = sentiment_map.get(sentiment_filter, [])
        filtered = [article for article in filtered if article.get('sentiment', '').replace('Somewhat-', '') in allowed_sentiments]

    # Time filter
    if time_filter != "All Time":
        now = datetime.now(timezone.utc)
        time_filters = {
            "Last 24h": timedelta(hours=24),
            "Last 7 days": timedelta(days=7),
            "Last 30 days": timedelta(days=30)
        }

        cutoff_time = now - time_filters[time_filter]
        filtered = [article for article in filtered if parse_datetime(article.get('published_at', '')) >= cutoff_time]

    return filtered


def parse_datetime(date_str):
    """Parse datetime string from various formats"""
    try:
        # Try different datetime formats
        formats = [
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d"
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # If the datetime doesn't have timezone info, assume UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue

        # If all formats fail, return old date
        return datetime.now(timezone.utc) - timedelta(days=365)
    except:
        return datetime.now(timezone.utc) - timedelta(days=365)


def display_news_article(article):
    """Display a single news article with sentiment analysis"""

    # Determine sentiment color
    sentiment = article.get('sentiment', 'Neutral')
    sentiment_color = get_sentiment_color(sentiment)

    # Create expander with colored title
    title = article.get('title', 'Untitled')
    with st.expander(f"📰 {title}", expanded=False):

        # Article metadata
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.caption(f"📅 {article.get('published_at', 'Unknown date')}")

        with col2:
            st.markdown(f"**Sentiment:** <span style='color:{sentiment_color}'>{sentiment}</span>", unsafe_allow_html=True)

        with col3:
            category = article.get('category', 'General')
            st.caption(f"🏷️ {category}")

        # Article summary
        summary = article.get('summary', 'No summary available')
        st.write(summary)

        # Article link
        if article.get('url'):
            st.markdown(f"[🔗 Read Full Article]({article.get('url')})")

        # Additional metadata if available
        if article.get('source'):
            st.caption(f"Source: {article.get('source')}")

        # Sentiment score if available
        if 'sentiment_score' in article:
            score = article['sentiment_score']
            st.progress(min(max(score + 1, 0), 1))  # Normalize to 0-1 range
            st.caption(f"Sentiment Score: {score:.3f}")


def get_sentiment_color(sentiment):
    """Get color for sentiment display"""
    sentiment_lower = sentiment.lower()
    if 'bullish' in sentiment_lower:
        return "#28a745"  # Green
    elif 'bearish' in sentiment_lower:
        return "#dc3545"  # Red
    else:
        return "#6c757d"  # Gray


def show_news_statistics(news_data):
    """Display news statistics and insights"""

    if not news_data:
        return

    st.subheader("📊 News Analytics")

    col1, col2, col3, col4 = st.columns(4)

    # Total articles
    with col1:
        st.metric("Total Articles", len(news_data))

    # Sentiment distribution
    sentiments = [article.get('sentiment', 'Neutral') for article in news_data]
    bullish_count = sum(1 for s in sentiments if 'bullish' in s.lower())
    bearish_count = sum(1 for s in sentiments if 'bearish' in s.lower())
    neutral_count = len(sentiments) - bullish_count - bearish_count

    with col2:
        st.metric("Bullish Articles", bullish_count)

    with col3:
        st.metric("Bearish Articles", bearish_count)

    with col4:
        st.metric("Neutral Articles", neutral_count)

    # Sentiment ratio chart
    if len(sentiments) > 0:
        st.subheader("📈 Sentiment Distribution")

        # Create a simple bar chart
        sentiment_counts = {
            'Bullish': bullish_count,
            'Bearish': bearish_count,
            'Neutral': neutral_count
        }

        st.bar_chart(sentiment_counts)

    # Recent articles timeline
    st.subheader("⏰ Recent Activity")
    recent_articles = sorted(news_data, key=lambda x: parse_datetime(x.get('published_at', '')), reverse=True)[:5]

    for article in recent_articles:
        time_ago = get_time_ago(parse_datetime(article.get('published_at', '')))
        st.write(f"• {article.get('title', 'Untitled')} - {time_ago}")


def get_time_ago(publish_time):
    """Get human-readable time ago string"""
    # Use UTC time for consistency
    now = datetime.now(timezone.utc)

    diff = now - publish_time

    if diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"