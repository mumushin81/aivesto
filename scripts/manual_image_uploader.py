#!/usr/bin/env python3
"""
수동으로 제작한 이미지를 Supabase에 업로드하고 메타데이터를 저장하는 스크립트

Usage:
    python scripts/manual_image_uploader.py image.jpg \
        --article-id nvda_blackwell_20251113 \
        --section-index 0 \
        --section-title "NVIDIA Blackwell GPU 출시" \
        --image-type hero \
        --keywords "nvidia,blackwell,gpu"
"""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.supabase_image_uploader import SupabaseImageUploader

load_dotenv()

def upload_manual_image(
    image_path: Path,
    article_id: str,
    section_index: int,
    section_title: str,
    image_type: str = "concept",
    keywords: list = None,
    caption: str = None,
    prompt: str = "Manually created image",
):
    """수동 제작 이미지를 Supabase에 업로드"""
    
    if not image_path.exists():
        logger.error(f"❌ Image not found: {image_path}")
        return None

    # Extract symbol from article_id (e.g., nvda_blackwell_20251113 -> NVDA)
    symbol = article_id.split('_')[0].upper() if '_' in article_id else article_id.upper()
    topic = article_id

    uploader = SupabaseImageUploader()

    try:
        image_id, public_url = uploader.upload_and_record(
            file_path=image_path,
            symbol=symbol,
            topic=topic,
            prompt=prompt,
            article_id=article_id,
            position=section_index,
            section_title=section_title,
            context_keywords=keywords or [],
            image_type=image_type,
            caption=caption,
        )

        logger.success(f"✅ Uploaded: {public_url}")
        logger.info(f"📝 Image ID: {image_id}")
        logger.info(f"📊 Article: {article_id}")
        logger.info(f"📍 Section: {section_index} - {section_title}")

        return {
            "image_id": image_id,
            "image_url": public_url,
            "article_id": article_id,
            "section_index": section_index,
            "section_title": section_title,
            "image_type": image_type,
        }

    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(
        description="수동 제작 이미지를 Supabase에 업로드"
    )
    parser.add_argument("image_path", type=Path, help="이미지 파일 경로")
    parser.add_argument("--article-id", required=True, help="기사 ID (예: nvda_blackwell_20251113)")
    parser.add_argument("--section-index", type=int, required=True, help="섹션 인덱스 (0부터 시작)")
    parser.add_argument("--section-title", required=True, help="섹션 제목")
    parser.add_argument("--image-type", default="concept", help="이미지 타입 (hero/diagram/chart/concept)")
    parser.add_argument("--keywords", help="키워드 (쉼표로 구분)")
    parser.add_argument("--caption", help="이미지 캡션")
    parser.add_argument("--prompt", default="Manually created with Midjourney", help="생성 프롬프트 설명")

    args = parser.parse_args()

    keywords = args.keywords.split(',') if args.keywords else []

    result = upload_manual_image(
        image_path=args.image_path,
        article_id=args.article_id,
        section_index=args.section_index,
        section_title=args.section_title,
        image_type=args.image_type,
        keywords=keywords,
        caption=args.caption,
        prompt=args.prompt,
    )

    if result:
        logger.success("🎉 업로드 완료!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
