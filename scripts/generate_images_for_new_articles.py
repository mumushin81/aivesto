#!/usr/bin/env python3
"""
신규 블로그 글에 이미지 생성 및 연결
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# magic_book 경로 추가
magic_book_path = Path("/Users/jinxin/dev/magic_book")
sys.path.insert(0, str(magic_book_path))

load_dotenv('/Users/jinxin/dev/aivesto/.env')

from loguru import logger
from supabase import create_client

# magic_book 이미지 생성 함수 import
from src.midjourney.batch import process_batch_generation

BRAND_COLORS = {
    'MSFT': '#00A4EF',
    'GOOGL': '#4285F4',
}

NEW_ARTICLES = [
    {
        "article_id": "msft_ai_copilot_expansion_20251117",
        "symbol": "MSFT",
        "topic": "ai_copilot_expansion",
        "title": "Microsoft AI Copilot 확장"
    },
    {
        "article_id": "googl_ai_search_revolution_20251117",
        "symbol": "GOOGL",
        "topic": "ai_search_revolution",
        "title": "Google AI 검색 혁명"
    }
]


def generate_image_prompts(article):
    """각 블로그 글에 맞는 2개 이미지 프롬프트 생성"""

    symbol = article['symbol']
    topic = article['topic']
    color = BRAND_COLORS.get(symbol, '#667eea')

    base_style = f"professional tech photography, corporate presentation style, clean high-contrast design, dramatic lighting, {color} brand color accent"

    prompts = [
        {
            "prompt": f"{symbol} company visualization: modern technology innovation, {topic.replace('_', ' ')}, {base_style}, hero image, 8k quality --ar 16:9 --quality 2 --stylize 500",
            "position": 0,
            "image_type": "hero"
        },
        {
            "prompt": f"Professional business concept: {topic.replace('_', ' ')}, clean infographic style, data visualization, {color} color scheme, white background, corporate aesthetic --ar 16:9 --quality 1",
            "position": 1,
            "image_type": "diagram"
        }
    ]

    return prompts


def generate_images_for_article(article):
    """한 블로그 글에 이미지 생성"""

    logger.info(f"\n{'='*60}")
    logger.info(f"🎨 {article['symbol']}: {article['title']}")
    logger.info(f"{'='*60}")

    article_id = article['article_id']
    prompts_data = generate_image_prompts(article)

    logger.info(f"  Article ID: {article_id}")
    logger.info(f"  생성할 이미지: {len(prompts_data)}개")

    # 프롬프트만 추출
    prompts = [p['prompt'] for p in prompts_data]

    try:
        # magic_book 배치 생성 실행
        result = process_batch_generation(
            prompts=prompts,
            timeout_per_image=300,
            download_images=False  # Supabase에만 저장
        )

        if result and 'image_urls' in result:
            logger.success(f"  ✅ magic_book 생성 완료: {len(result['image_urls'])}개")
            return result['image_urls']
        else:
            logger.error(f"  ❌ 이미지 생성 실패")
            return []

    except Exception as e:
        logger.error(f"  ❌ 예외 발생: {e}")
        return []


def connect_images_to_blog(article_id, symbol, topic, image_urls):
    """생성된 이미지를 blog_images에 연결"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase = create_client(supabase_url, supabase_key)

    logger.info(f"\n💾 {article_id} 이미지 연결 중...")

    for position, image_url in enumerate(image_urls[:2]):  # 최대 2개
        try:
            # images 테이블에 저장
            image_data = {
                "symbol": symbol,
                "topic": topic,
                "image_url": image_url,
                "prompt": f"AI generated image for {topic}"
            }

            result = supabase.table('images').insert(image_data).execute()

            if result.data and len(result.data) > 0:
                image_id = result.data[0]['id']

                # blog_images에 연결
                blog_image_data = {
                    "article_id": article_id,
                    "image_id": image_id,
                    "position": position
                }

                supabase.table('blog_images').insert(blog_image_data).execute()
                logger.success(f"  ✅ Position {position} 연결 완료: {image_id}")

        except Exception as e:
            logger.error(f"  ❌ Position {position} 연결 실패: {e}")


def main():
    """메인 실행"""

    logger.info("=" * 60)
    logger.info("🚀 신규 블로그 이미지 생성 시작")
    logger.info("=" * 60)

    total_success = 0
    total_failed = 0

    for article in NEW_ARTICLES:
        try:
            image_urls = generate_images_for_article(article)

            if image_urls:
                connect_images_to_blog(
                    article['article_id'],
                    article['symbol'],
                    article['topic'],
                    image_urls
                )
                total_success += 1
            else:
                total_failed += 1

        except Exception as e:
            logger.error(f"❌ {article['article_id']} 처리 실패: {e}")
            total_failed += 1

    logger.info("\n" + "=" * 60)
    logger.success(f"✅ 성공: {total_success}개")
    logger.error(f"❌ 실패: {total_failed}개")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
