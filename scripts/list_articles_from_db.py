#!/usr/bin/env python3
"""
List all articles from database to understand article_id structure
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Try to find articles table
try:
    result = supabase.table('articles').select('*').execute()
    logger.info(f"Found {len(result.data)} articles in 'articles' table")
    for article in result.data[:5]:
        logger.info(f"  {article}")
except Exception as e:
    logger.error(f"'articles' table query failed: {e}")

# Check if there's a blog_posts table
try:
    result = supabase.table('blog_posts').select('*').execute()
    logger.info(f"Found {len(result.data)} articles in 'blog_posts' table")
    for post in result.data[:5]:
        logger.info(f"  {post}")
except Exception as e:
    logger.error(f"'blog_posts' table query failed: {e}")

# Check blog_images to see what article_ids exist there
try:
    result = supabase.table('blog_images').select('article_id').execute()
    if result.data:
        article_ids = set(img['article_id'] for img in result.data)
        logger.info(f"Found {len(article_ids)} unique article_ids in blog_images:")
        for aid in sorted(article_ids):
            logger.info(f"  {aid}")
    else:
        logger.info("blog_images table is empty")
except Exception as e:
    logger.error(f"'blog_images' table query failed: {e}")

# Check midjourney_images for recent images
try:
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    result = supabase.table('midjourney_images').select('*').gte('created_at', yesterday).limit(5).execute()
    logger.info(f"\nRecent midjourney_images (last 24h): {len(result.data)} total")
    for img in result.data[:5]:
        logger.info(f"  {img.get('prompt', '')[:80]}...")
        logger.info(f"    crop_position: {img.get('crop_position')}, created: {img.get('created_at')}")
except Exception as e:
    logger.error(f"'midjourney_images' table query failed: {e}")
