#!/usr/bin/env python3
"""
Extract article IDs from the generated images based on prompts
and connect them to blog_images table
"""
import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Article mapping from prompts
ARTICLE_MAPPING = {
    "iphone sales": "aapl_iphone_sales_20251113",
    "creative ai": "adbe_creative_ai_20251113",
    "aws ai services": "amzn_aws_ai_services_20251113",
    "search ai": "googl_search_ai_20251113",
    "enterprise ai": "meta_enterprise_ai_20251113",
    "ai office integration": "msft_copilot_revenue_20251113",
    "subscriber growth": "nflx_subscriber_growth_20251113",
    "blackwell gpu": "nvda_blackwell_20251113",
    "foxconn ai server": "nvda_foxconn_factory_20251113",
    "robotaxi fleet": "tsla_robotaxi_20251113",
    "profitability expansion": "uber_profitability_expansion_20251113"
}

SYMBOL_MAPPING = {
    "iphone sales": "AAPL",
    "creative ai": "ADBE",
    "aws ai services": "AMZN",
    "search ai": "GOOGL",
    "enterprise ai": "META",
    "ai office integration": "MSFT",
    "subscriber growth": "NFLX",
    "blackwell gpu": "NVDA",
    "foxconn ai server": "NVDA",
    "robotaxi fleet": "TSLA",
    "profitability expansion": "UBER"
}

def get_today_midjourney_images():
    """Get all midjourney images from today"""

    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()

    try:
        # Get all images from yesterday
        result = supabase.table('midjourney_images') \
            .select('*') \
            .gte('created_at', yesterday) \
            .order('created_at', desc=False) \
            .execute()

        # Filter for originals only (crop_position is None)
        originals = [img for img in result.data if img.get('crop_position') is None]

        logger.info(f"Found {len(result.data)} total images, {len(originals)} originals from last 8 hours")
        return originals

    except Exception as e:
        logger.error(f"Failed to query midjourney_images: {e}")
        return []


def identify_article_from_prompt(prompt):
    """Identify article_id and symbol from image prompt"""

    prompt_lower = prompt.lower()

    for topic_key, article_id in ARTICLE_MAPPING.items():
        if topic_key in prompt_lower:
            symbol = SYMBOL_MAPPING.get(topic_key, "UNKNOWN")
            return article_id, symbol, topic_key

    return None, None, None


def save_image_to_images_table(image_data, article_id, symbol, topic, position):
    """Save image to images table"""

    try:
        # midjourney_images uses 'public_url', not 'image_url'
        image_url = image_data.get('public_url') or image_data.get('original_url') or image_data.get('image_url')

        data = {
            "symbol": symbol,
            "topic": topic,
            "image_url": image_url,
            "prompt": image_data.get('prompt')
        }

        result = supabase.table('images').insert(data).execute()

        if result.data and len(result.data) > 0:
            image_id = result.data[0]['id']
            logger.success(f"  ✅ Saved to images table: {image_id} (position {position})")
            return image_id
        else:
            logger.error(f"  ❌ Failed to save to images table")
            return None

    except Exception as e:
        logger.error(f"  ❌ Error saving to images table: {e}")
        return None


def connect_to_blog_images(article_id, image_id, position):
    """Connect image to blog via blog_images junction table"""

    try:
        data = {
            "article_id": article_id,
            "image_id": image_id,
            "position": position
        }

        result = supabase.table('blog_images').insert(data).execute()

        if result.data and len(result.data) > 0:
            logger.success(f"  ✅ Connected to blog_images: position {position}")
            return True
        else:
            logger.error(f"  ❌ Failed to connect to blog_images")
            return False

    except Exception as e:
        logger.error(f"  ❌ Error connecting to blog_images: {e}")
        return False


def main():
    """Main execution"""

    logger.info("=" * 60)
    logger.info("🔗 Connecting Generated Images to Blog Articles")
    logger.info("=" * 60)

    # Get today's images
    images = get_today_midjourney_images()

    if not images:
        logger.error("No images found!")
        return

    # Group images by article
    article_images = {}

    for img in images:
        prompt = img.get('prompt', '')
        article_id, symbol, topic = identify_article_from_prompt(prompt)

        if not article_id:
            logger.warning(f"Could not identify article from prompt: {prompt[:50]}...")
            continue

        if article_id not in article_images:
            article_images[article_id] = {
                'symbol': symbol,
                'topic': topic,
                'images': []
            }

        article_images[article_id]['images'].append(img)

    logger.info(f"\nFound {len(article_images)} articles with images:")
    for aid in sorted(article_images.keys()):
        logger.info(f"  {aid}: {len(article_images[aid]['images'])} images")

    # Process each article
    success_count = 0
    failed_count = 0

    for article_id, data in sorted(article_images.items()):
        logger.info(f"\nProcessing {article_id}")
        logger.info(f"  Symbol: {data['symbol']}, Topic: {data['topic']}")
        logger.info(f"  Images: {len(data['images'])}")

        images_list = sorted(data['images'], key=lambda x: x['created_at'])

        for position, img in enumerate(images_list[:2]):  # Only take first 2 images
            # Save to images table
            image_id = save_image_to_images_table(
                img,
                article_id,
                data['symbol'],
                data['topic'],
                position
            )

            if image_id:
                # Connect to blog_images
                if connect_to_blog_images(article_id, image_id, position):
                    success_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1

    # Verify
    logger.info("\n" + "=" * 60)
    logger.info("Verification:")
    logger.info("=" * 60)

    for article_id in sorted(article_images.keys()):
        result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', article_id) \
            .execute()

        count = len(result.data) if result.data else 0
        if count > 0:
            logger.success(f"  ✅ {article_id}: {count} images")
        else:
            logger.error(f"  ❌ {article_id}: NO IMAGES")

    logger.info("\n" + "=" * 60)
    logger.success(f"✅ Successfully connected: {success_count} images")
    logger.error(f"❌ Failed: {failed_count} images")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
