#!/usr/bin/env python3
"""
Connect recently generated Midjourney images to blog articles

This script fixes the issue where images were generated successfully
but failed to be inserted into the blog_images junction table.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from pathlib import Path

load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)


def get_all_blog_articles():
    """Get all blog article IDs from HTML files"""
    blog_dir = Path("/Users/jinxin/dev/aivesto/public")
    html_files = list(blog_dir.glob("article_*.html"))

    articles = []
    for html_file in html_files:
        filename = html_file.stem
        parts = filename.replace('article_', '').split('_')
        symbol = parts[0].lower()
        topic = '_'.join(parts[1:-1])
        date = parts[-1]
        article_id = f"{symbol}_{topic}_{date}"

        articles.append({
            "article_id": article_id,
            "symbol": symbol.upper(),
            "topic": topic,
            "date": date
        })

    logger.info(f"Found {len(articles)} blog articles")
    return sorted(articles, key=lambda x: x['article_id'])


def get_recent_midjourney_images():
    """Get images generated in the last 24 hours from midjourney_images table"""

    # Get images from last 24 hours, only cropped images (position 0-3)
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()

    try:
        result = supabase.table('midjourney_images') \
            .select('*') \
            .gte('created_at', yesterday) \
            .not_.is_('crop_position', 'null') \
            .order('created_at', desc=False) \
            .execute()

        images = result.data
        logger.info(f"Found {len(images)} cropped images from last 24 hours")

        return images

    except Exception as e:
        logger.error(f"Failed to get midjourney images: {e}")
        return []


def group_images_by_article(images, articles):
    """
    Group images by article based on generation order
    Each article should have 2 original images = 8 cropped images (4 crops each)
    """

    grouped = {}

    # Group by original_image_url (each original has 4 crops)
    originals = {}
    for img in images:
        original_url = img.get('original_image_url') or img.get('image_url')
        if original_url not in originals:
            originals[original_url] = []
        originals[original_url].append(img)

    logger.info(f"Found {len(originals)} original images with crops")

    # Each article needs 2 original images (hero + diagram)
    # So we need to group every 2 originals
    original_list = list(originals.keys())

    article_index = 0
    for i in range(0, len(original_list), 2):
        if article_index >= len(articles):
            break

        article = articles[article_index]
        article_id = article['article_id']

        # Get the 2 originals for this article
        hero_original = original_list[i] if i < len(original_list) else None
        diagram_original = original_list[i + 1] if i + 1 < len(original_list) else None

        grouped[article_id] = {
            "article": article,
            "hero_images": originals.get(hero_original, []) if hero_original else [],
            "diagram_images": originals.get(diagram_original, []) if diagram_original else []
        }

        article_index += 1

    logger.info(f"Grouped images for {len(grouped)} articles")
    return grouped


def save_image_to_aivesto(image_data, symbol, topic, image_type):
    """Save image metadata to aivesto images table"""

    try:
        data = {
            "symbol": symbol,
            "topic": topic,
            "image_type": image_type,
            "image_url": image_data.get('image_url'),
            "original_image_url": image_data.get('original_image_url'),
            "crop_position": image_data.get('crop_position'),
            "prompt": image_data.get('prompt'),
            "midjourney_id": image_data.get('midjourney_id'),
            "created_at": image_data.get('created_at')
        }

        result = supabase.table('images').insert(data).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]['id']
        else:
            logger.error(f"Failed to insert image: {result}")
            return None

    except Exception as e:
        logger.error(f"Error saving image to aivesto: {e}")
        return None


def connect_images_to_blog(article_id, image_id, position):
    """Connect image to blog article via blog_images junction table"""

    try:
        data = {
            "article_id": article_id,
            "image_id": image_id,
            "position": position
        }

        result = supabase.table('blog_images').insert(data).execute()

        if result.data and len(result.data) > 0:
            return True
        else:
            logger.error(f"Failed to connect image to blog: {result}")
            return False

    except Exception as e:
        logger.error(f"Error connecting image to blog: {e}")
        return False


def process_article_images(article_id, article_data):
    """Process and connect all images for one article"""

    article = article_data['article']
    hero_images = article_data['hero_images']
    diagram_images = article_data['diagram_images']

    logger.info(f"\nProcessing {article_id}")
    logger.info(f"  Hero images: {len(hero_images)}, Diagram images: {len(diagram_images)}")

    success_count = 0

    # Process hero images (position 0)
    for hero_img in hero_images:
        image_id = save_image_to_aivesto(
            hero_img,
            article['symbol'],
            article['topic'],
            'hero'
        )

        if image_id:
            if connect_images_to_blog(article_id, image_id, 0):
                success_count += 1
                logger.success(f"  ✅ Connected hero image (crop {hero_img.get('crop_position')})")
            else:
                logger.error(f"  ❌ Failed to connect hero image")
        else:
            logger.error(f"  ❌ Failed to save hero image")

    # Process diagram images (position 1)
    for diagram_img in diagram_images:
        image_id = save_image_to_aivesto(
            diagram_img,
            article['symbol'],
            article['topic'],
            'diagram'
        )

        if image_id:
            if connect_images_to_blog(article_id, image_id, 1):
                success_count += 1
                logger.success(f"  ✅ Connected diagram image (crop {diagram_img.get('crop_position')})")
            else:
                logger.error(f"  ❌ Failed to connect diagram image")
        else:
            logger.error(f"  ❌ Failed to save diagram image")

    return success_count


def verify_blog_images():
    """Verify all blog articles now have images"""

    logger.info("\n" + "=" * 60)
    logger.info("Verifying blog images...")
    logger.info("=" * 60)

    articles = get_all_blog_articles()

    for article in articles:
        article_id = article['article_id']

        result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', article_id) \
            .execute()

        image_count = len(result.data) if result.data else 0

        if image_count > 0:
            logger.success(f"  ✅ {article_id}: {image_count} images")
        else:
            logger.error(f"  ❌ {article_id}: NO IMAGES")

    logger.info("=" * 60)


def main():
    """Main execution"""

    logger.info("=" * 60)
    logger.info("🔗 Connecting Generated Images to Blog Articles")
    logger.info("=" * 60)

    # 1. Get all blog articles
    articles = get_all_blog_articles()

    if not articles:
        logger.error("No blog articles found!")
        return

    # 2. Get recent Midjourney images
    images = get_recent_midjourney_images()

    if not images:
        logger.error("No recent images found!")
        return

    # 3. Group images by article
    grouped = group_images_by_article(images, articles)

    # 4. Process each article
    total_success = 0
    total_failed = 0

    for article_id, article_data in grouped.items():
        try:
            success = process_article_images(article_id, article_data)
            total_success += success
        except Exception as e:
            logger.error(f"Failed to process {article_id}: {e}")
            total_failed += 1

    # 5. Verify results
    verify_blog_images()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.success(f"✅ Successfully connected: {total_success} images")
    if total_failed > 0:
        logger.error(f"❌ Failed: {total_failed} articles")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
