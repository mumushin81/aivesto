#!/usr/bin/env python3
"""
Test Supabase Connection
"""

import sys
sys.path.append('.')

from database.supabase_client import SupabaseClient
from loguru import logger

def test_connection():
    """Test Supabase connection"""
    try:
        logger.info("Testing Supabase connection...")

        # Initialize client
        client = SupabaseClient()
        logger.success("✓ Supabase client initialized successfully")

        # Test dashboard stats
        logger.info("Testing dashboard stats query...")
        stats = client.get_dashboard_stats()
        logger.success(f"✓ Dashboard stats retrieved: {stats}")

        # Test trending symbols
        logger.info("Testing trending symbols query...")
        trending = client.get_trending_symbols(hours=24, limit=5)
        logger.success(f"✓ Trending symbols retrieved: {len(trending)} symbols")

        # Test articles for dashboard
        logger.info("Testing articles query...")
        articles = client.get_articles_for_dashboard(limit=10)
        logger.success(f"✓ Articles retrieved: {len(articles)} articles")

        logger.success("\n🎉 All tests passed! Supabase connection is working.")
        return True

    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
