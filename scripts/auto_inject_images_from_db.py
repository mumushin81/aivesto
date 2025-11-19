#!/usr/bin/env python3
"""
Supabase DB에서 이미지 정보를 가져와서 자동으로 블로그 기사에 삽입

Usage:
    python scripts/auto_inject_images_from_db.py \
        --article-id nvda_blackwell_20251113 \
        --input articles/article_NVDA_blackwell_gpu_20251113.md \
        --output articles_with_images/article_NVDA_blackwell_gpu_20251113.md
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client

load_dotenv()

def get_images_from_db(article_id: str) -> list:
    """Supabase DB에서 article_id에 해당하는 이미지 가져오기"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL or SUPABASE_KEY not set")
        return []

    supabase: Client = create_client(supabase_url, supabase_key)

    try:
        # Query images for this article from blog_images join images
        result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', article_id) \
            .order('position') \
            .execute()

        images = []
        for row in result.data:
            img_data = row.get('images', {})
            images.append({
                'image_url': img_data.get('image_url'),
                'section_title': img_data.get('section_title'),
                'caption': img_data.get('caption'),
                'image_type': img_data.get('image_type'),
                'position': row.get('position', 0),
                'section_index': row.get('section_index'),
            })

        logger.info(f"✅ Found {len(images)} images for article: {article_id}")
        return images

    except Exception as e:
        logger.error(f"❌ Failed to fetch images: {e}")
        return []


def inject_images_to_markdown(
    input_path: Path,
    output_path: Path,
    images: list,
):
    """마크다운 파일에 이미지 삽입"""
    
    if not input_path.exists():
        logger.error(f"❌ Input file not found: {input_path}")
        return False

    content = input_path.read_text(encoding='utf-8')
    lines = content.split('\n')

    # TODO: 실제 섹션 매칭 로직 구현
    # 지금은 간단히 파일 맨 위에 이미지 리스트 추가
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 이미지를 markdown에 삽입
    image_markdown = []
    for img in images:
        if img['image_url']:
            image_markdown.append(f"\n![{img.get('caption', img.get('section_title', 'Image'))}]({img['image_url']})")
            image_markdown.append(f"*{img.get('caption', img.get('section_title', ''))}*\n")

    # 원본 내용 + 이미지 결합
    final_content = '\n'.join(image_markdown) + '\n\n' + content

    output_path.write_text(final_content, encoding='utf-8')
    logger.success(f"✅ Images injected: {output_path}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Supabase DB에서 이미지를 가져와 블로그에 자동 배치"
    )
    parser.add_argument("--article-id", required=True, help="기사 ID")
    parser.add_argument("--input", type=Path, required=True, help="입력 마크다운 파일")
    parser.add_argument("--output", type=Path, required=True, help="출력 마크다운 파일")

    args = parser.parse_args()

    images = get_images_from_db(args.article_id)
    
    if not images:
        logger.warning("⚠️ No images found in DB")
        return

    success = inject_images_to_markdown(args.input, args.output, images)

    if success:
        logger.success("🎉 완료!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
