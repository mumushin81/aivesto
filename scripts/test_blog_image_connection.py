#!/usr/bin/env python3
"""
수정된 워크플로우 테스트: 이미지 생성 → blog_images 연결 검증
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# magic_book 경로 추가
magic_book_path = Path("/Users/jinxin/dev/magic_book")
sys.path.insert(0, str(magic_book_path))

# aivesto .env 로드
load_dotenv('/Users/jinxin/dev/aivesto/.env')

from loguru import logger

def test_single_blog_image():
    """단일 이미지로 전체 워크플로우 테스트"""

    # magic_book의 Midjourney 모듈 임포트
    try:
        from src.midjourney import generate_images_batch_and_save
    except ImportError as e:
        logger.error(f"magic_book 모듈 로드 실패: {e}")
        return False

    # 테스트 프롬프트 (1개만)
    prompts = [
        {
            "prompt": "Professional business analytics dashboard, clean modern infographic with rising trend lines, minimal grid design, green (#16B31E) data visualization bars, dark background, corporate presentation style, clear typography --ar 16:9 --quality 1",
            "section_title": "시그널",
            "section_index": 1,
            "image_type": "diagram"
        }
    ]

    logger.info("=" * 60)
    logger.info("🧪 블로그 이미지 연결 워크플로우 테스트")
    logger.info("=" * 60)

    # 1단계: magic_book으로 이미지 생성
    logger.info("📝 1단계: 이미지 생성 중...")
    prompt_texts = [p["prompt"] for p in prompts]

    try:
        results = generate_images_batch_and_save(
            prompts=prompt_texts,
            auto_crop=False,
            save_locally=False,
            verbose=True
        )

        logger.success(f"✅ magic_book 생성 완료: {len(results)}개")

        # 결과 정리 (수정된 코드)
        generated_images = []
        for idx, result in enumerate(results):
            if result.success and result.image_urls:
                # image_urls는 리스트이므로 첫 번째 URL 사용
                image_url = result.image_urls[0] if result.image_urls else None
                supabase_id = result.supabase_image_ids[0] if result.supabase_image_ids else None

                if image_url:
                    generated_images.append({
                        **prompts[idx],
                        "image_url": image_url,
                        "midjourney_id": supabase_id
                    })
                    logger.info(f"  {idx+1}. {prompts[idx]['section_title']}: {image_url[:60]}...")

        if not generated_images:
            logger.error("❌ 이미지 URL 추출 실패")
            return False

    except Exception as e:
        logger.error(f"❌ 이미지 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2단계: aivesto Supabase에 연결
    logger.info("\n📝 2단계: aivesto Supabase에 연결 중...")

    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return False

    supabase = create_client(supabase_url, supabase_key)

    article_id = "test_nvda_blackwell_20251113"

    for img in generated_images:
        try:
            # images 테이블에 저장 (실제 스키마: symbol, topic, prompt, image_url만 존재)
            image_data = {
                "symbol": "NVDA",
                "topic": "blackwell_gpu_test",
                "prompt": img["prompt"],
                "image_url": img["image_url"]
            }

            result = supabase.table('images').insert(image_data).execute()

            if result.data:
                image_id = result.data[0]['id']
                logger.success(f"  ✅ images 테이블 저장: {image_id}")

                # blog_images 테이블에 연결 (실제 스키마: article_id, image_id, position만 존재)
                blog_image_data = {
                    "article_id": article_id,
                    "image_id": image_id,
                    "position": img["section_index"]
                }

                blog_result = supabase.table('blog_images').insert(blog_image_data).execute()

                if blog_result.data:
                    logger.success(f"  ✅ blog_images 연결 완료!")
                    logger.info(f"     Article: {article_id}")
                    logger.info(f"     Image: {image_id}")
                    logger.info(f"     Position: {img['section_index']}")
                else:
                    logger.error(f"  ❌ blog_images 연결 실패")

        except Exception as e:
            logger.error(f"  ❌ 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    # 3단계: 검증
    logger.info("\n📝 3단계: blog_images 테이블 검증 중...")

    try:
        verify_result = supabase.table('blog_images') \
            .select('*') \
            .eq('article_id', article_id) \
            .execute()

        if verify_result.data:
            logger.success(f"✅ 검증 완료! blog_images에 {len(verify_result.data)}개 레코드 존재")
            for record in verify_result.data:
                logger.info(f"   - Image ID: {record.get('image_id')}, Position: {record.get('position')}")
            return True
        else:
            logger.error("❌ blog_images 테이블이 여전히 비어있음")
            return False

    except Exception as e:
        logger.error(f"❌ 검증 실패: {e}")
        return False


if __name__ == "__main__":
    success = test_single_blog_image()

    if success:
        logger.success("\n" + "=" * 60)
        logger.success("🎉 워크플로우 테스트 성공!")
        logger.success("=" * 60)
        sys.exit(0)
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ 워크플로우 테스트 실패")
        logger.error("=" * 60)
        sys.exit(1)
