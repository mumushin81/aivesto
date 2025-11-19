#!/usr/bin/env python3
"""
모든 블로그 글에 이미지 생성 및 배치
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# magic_book 경로 추가
magic_book_path = Path("/Users/jinxin/dev/magic_book")
sys.path.insert(0, str(magic_book_path))

# aivesto .env 로드
load_dotenv('/Users/jinxin/dev/aivesto/.env')

from loguru import logger
from supabase import create_client

# 각 종목별 브랜드 색상
BRAND_COLORS = {
    'AAPL': '#000000',  # Apple Black
    'ADBE': '#ED1C24',  # Adobe Red
    'AMZN': '#FF9900',  # Amazon Orange
    'GOOGL': '#4285F4', # Google Blue
    'META': '#0668E1',  # Meta Blue
    'MSFT': '#00A4EF',  # Microsoft Blue
    'NFLX': '#E50914',  # Netflix Red
    'NVDA': '#76B900',  # NVIDIA Green
    'TSLA': '#CC0000',  # Tesla Red
    'UBER': '#000000',  # Uber Black
}

def extract_article_info(html_file: Path):
    """HTML 파일에서 article_id, symbol, 제목 추출"""

    # 파일명에서 정보 추출
    filename = html_file.stem  # article_NVDA_blackwell_gpu_20251113
    parts = filename.replace('article_', '').split('_')

    if len(parts) < 3:
        return None

    symbol = parts[0].upper()
    topic = '_'.join(parts[1:-1])
    date = parts[-1]
    article_id = f"{parts[0].lower()}_{topic}_{date}"

    # HTML에서 제목 추출
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            title_tag = soup.find('h1')
            title = title_tag.text.strip() if title_tag else "No title"
    except Exception as e:
        logger.warning(f"제목 추출 실패 ({html_file.name}): {e}")
        title = topic.replace('_', ' ').title()

    return {
        'article_id': article_id,
        'symbol': symbol,
        'topic': topic,
        'date': date,
        'title': title,
        'html_file': html_file,
        'brand_color': BRAND_COLORS.get(symbol, '#667eea')
    }


def generate_image_prompts(article_info):
    """각 블로그 글에 맞는 2개 이미지 프롬프트 생성"""

    symbol = article_info['symbol']
    topic = article_info['topic']
    title = article_info['title']
    color = article_info['brand_color']

    # 기본 스타일
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


def check_existing_images(article_id):
    """이미 이미지가 있는지 확인"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase = create_client(supabase_url, supabase_key)

    try:
        result = supabase.table('blog_images') \
            .select('*') \
            .eq('article_id', article_id) \
            .execute()

        return len(result.data) > 0

    except:
        return False


def generate_images_for_article(article_info):
    """한 블로그 글의 이미지 생성"""

    from src.midjourney import generate_images_batch_and_save

    article_id = article_info['article_id']
    symbol = article_info['symbol']

    logger.info(f"\n{'=' * 60}")
    logger.info(f"🎨 {symbol}: {article_info['title'][:50]}...")
    logger.info(f"{'=' * 60}")

    # 프롬프트 생성
    prompts_data = generate_image_prompts(article_info)
    prompt_texts = [p["prompt"] for p in prompts_data]

    logger.info(f"  Article ID: {article_id}")
    logger.info(f"  생성할 이미지: {len(prompt_texts)}개")

    # magic_book으로 이미지 생성
    try:
        results = generate_images_batch_and_save(
            prompts=prompt_texts,
            auto_crop=True,  # 크롭 버전 생성
            save_locally=False,
            verbose=True
        )

        logger.success(f"  ✅ magic_book 생성 완료: {len(results)}개")

        # aivesto Supabase에 저장
        generated_images = []
        for idx, result in enumerate(results):
            if result.success and result.image_urls:
                # 크롭된 첫 번째 이미지 사용
                image_url = result.image_urls[0] if result.image_urls else None
                supabase_id = result.supabase_image_ids[0] if result.supabase_image_ids else None

                if image_url and '/cropped/' in image_url:
                    generated_images.append({
                        **prompts_data[idx],
                        "image_url": image_url,
                        "midjourney_id": supabase_id
                    })
                    logger.info(f"    {idx+1}. Position {prompts_data[idx]['position']}: {image_url[:60]}...")

        return generated_images

    except Exception as e:
        logger.error(f"  ❌ 이미지 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_images_to_blog(article_id, symbol, images):
    """생성된 이미지를 blog_images에 저장"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase = create_client(supabase_url, supabase_key)

    logger.info(f"\n  💾 blog_images 저장 중...")

    for img in images:
        try:
            # images 테이블에 저장
            image_data = {
                "symbol": symbol,
                "topic": article_id.split('_', 1)[1].rsplit('_', 1)[0],  # 중간 topic 부분
                "prompt": img["prompt"],
                "image_url": img["image_url"]
            }

            result = supabase.table('images').insert(image_data).execute()

            if result.data:
                image_id = result.data[0]['id']

                # blog_images 테이블에 연결
                blog_image_data = {
                    "article_id": article_id,
                    "image_id": image_id,
                    "position": img["position"]
                }

                supabase.table('blog_images').insert(blog_image_data).execute()
                logger.success(f"    ✅ Position {img['position']}: {image_id}")

        except Exception as e:
            logger.error(f"    ❌ 저장 실패 (Position {img['position']}): {e}")


def main():
    """메인 함수"""

    logger.info("=" * 60)
    logger.info("🚀 모든 블로그 글 이미지 생성 시작")
    logger.info("=" * 60)

    # 모든 HTML 파일 검색
    articles_dir = Path("/Users/jinxin/dev/aivesto/public/articles")
    html_files = sorted(articles_dir.glob("article_*.html"))

    logger.info(f"\n📝 총 {len(html_files)}개 블로그 글 발견")

    # article_id 정보 추출
    articles = []
    for html_file in html_files:
        info = extract_article_info(html_file)
        if info:
            articles.append(info)

    logger.info(f"  ✅ {len(articles)}개 article 정보 추출 완료")

    # 이미 이미지가 있는 블로그 제외
    articles_to_generate = []
    for article in articles:
        if check_existing_images(article['article_id']):
            logger.info(f"  ⏭️  {article['symbol']}: 이미 이미지 있음 - 스킵")
        else:
            articles_to_generate.append(article)

    if not articles_to_generate:
        logger.success("\n✅ 모든 블로그 글에 이미 이미지가 있습니다!")
        return

    logger.info(f"\n🎨 {len(articles_to_generate)}개 블로그 글에 이미지 생성 시작...")

    # 각 블로그 글에 이미지 생성
    success_count = 0
    fail_count = 0

    for article in articles_to_generate:
        try:
            images = generate_images_for_article(article)

            if images:
                save_images_to_blog(article['article_id'], article['symbol'], images)
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            logger.error(f"\n❌ {article['symbol']} 처리 실패: {e}")
            fail_count += 1

    # 최종 요약
    logger.info("\n" + "=" * 60)
    logger.info("📊 최종 결과")
    logger.info("=" * 60)
    logger.success(f"✅ 성공: {success_count}개")
    logger.error(f"❌ 실패: {fail_count}개")
    logger.info(f"📝 전체: {len(articles_to_generate)}개")


if __name__ == "__main__":
    main()
