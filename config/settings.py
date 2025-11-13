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

# Article Generation Criteria (Analyzed: 2025-11-13)
# Tier 1: Primary (높은 중요도 뉴스 3개 이상) - Auto generation
ARTICLE_TIER_1_MIN_HIGH_IMPORTANCE = 3      # 높은 중요도 뉴스 최소 3개
ARTICLE_TIER_1_SYMBOLS = [                  # 13개 종목
    "MSFT", "NVDA", "AAPL", "GOOGL", "AMZN", "TSLA", "META",
    "GOOG", "NBIS", "BRK.B", "AMD", "WMT", "SPY"
]

# Tier 2: Secondary (뉴스 3개+ AND 점수 75+) - Semi-auto generation
ARTICLE_TIER_2_MIN_NEWS = 3
ARTICLE_TIER_2_MIN_SCORE = 75
ARTICLE_TIER_2_SYMBOLS = [                  # 추가 5개
    "AVGO", "TSM", "CORW", "INTC", "RGTI"
]

# Tier 3: Trend (상위 15개) - Monthly report
ARTICLE_TIER_3_TOP_N = 15                   # 월간 리포트 대상

# Article generation strategy
ARTICLE_GENERATION_STRATEGY = "tiered"      # "tiered" 또는 "dynamic"
ARTICLE_STRATEGY_CONFIG = {
    "tier_1": {
        "name": "Primary - Hot Issues",
        "criteria": "high_importance >= 3",
        "frequency": "weekly",
        "auto_generate": True
    },
    "tier_2": {
        "name": "Secondary - Deep Analysis",
        "criteria": "news_count >= 3 AND avg_score >= 75",
        "frequency": "semi-weekly",
        "auto_generate": True
    },
    "tier_3": {
        "name": "Trend - Monthly Report",
        "criteria": "top_15_symbols",
        "frequency": "monthly",
        "auto_generate": False
    }
}

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
