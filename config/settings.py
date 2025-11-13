import os
from dotenv import load_dotenv

load_dotenv()

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# News APIs
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# AI APIs
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# WordPress
WORDPRESS_URL = os.getenv("WORDPRESS_URL")
WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD")

# Intervals (in seconds)
NEWS_COLLECTION_INTERVAL = int(os.getenv("NEWS_COLLECTION_INTERVAL", 900))
ANALYSIS_INTERVAL = int(os.getenv("ANALYSIS_INTERVAL", 1800))
ARTICLE_GENERATION_INTERVAL = int(os.getenv("ARTICLE_GENERATION_INTERVAL", 3600))

# Thresholds
MIN_RELEVANCE_SCORE = int(os.getenv("MIN_RELEVANCE_SCORE", 70))

# RSS Feeds
RSS_FEEDS = [
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/rss/",
        "category": "general"
    },
    {
        "name": "Reuters Business",
        "url": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
        "category": "business"
    },
    {
        "name": "MarketWatch",
        "url": "https://www.marketwatch.com/rss/",
        "category": "markets"
    },
    {
        "name": "Seeking Alpha",
        "url": "https://seekingalpha.com/feed.xml",
        "category": "analysis"
    }
]

# Stock Symbols to Track (can be expanded)
TRACKED_SYMBOLS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT",
    "JNJ", "PG", "UNH", "HD", "BAC", "DIS", "ADBE", "NFLX", "CRM", "PYPL"
]
