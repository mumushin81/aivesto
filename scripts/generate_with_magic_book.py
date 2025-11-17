#!/usr/bin/env python3
"""
magic_book을 사용하여 이미지 생성 후 aivesto Supabase에 저장
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

def generate_blog_images():
    """NVDA Blackwell 기사용 5개 이미지 생성"""
    
    # magic_book의 Midjourney 모듈 임포트
    try:
        from src.midjourney import generate_images_batch_and_save
    except ImportError as e:
        logger.error(f"magic_book 모듈 로드 실패: {e}")
        logger.info("magic_book 프로젝트 경로를 확인하세요: /Users/jinxin/dev/magic_book")
        return []
    
    # NVDA Blackwell 기사 프롬프트 (tmp/test_pipeline/prompts.json에서 가져옴)
    prompts = [
        {
            "prompt": "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting, floating semiconductor design, black background with subtle green accents, professional tech photography, 8k quality --ar 16:9 --quality 2 --stylize 500",
            "section_title": "TITLE:",
            "section_index": 0,
            "image_type": "hero"
        },
        {
            "prompt": "Technical architecture diagram of advanced GPU chip design, labeled components, clean white background, professional vector illustration, green and black color scheme, isometric perspective, enterprise presentation style --ar 16:9 --quality 1",
            "section_title": "시그널",
            "section_index": 1,
            "image_type": "diagram"
        },
        {
            "prompt": "Professional technology concept visualization, modern digital innovation, green (#16B31E) and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1",
            "section_title": "Supplemental Visual 3",
            "section_index": 2,
            "image_type": "concept"
        },
        {
            "prompt": "Professional technology concept visualization, modern digital innovation, green (#16B31E) and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1",
            "section_title": "Supplemental Visual 4",
            "section_index": 3,
            "image_type": "concept"
        },
        {
            "prompt": "Professional technology concept visualization, modern digital innovation, green (#16B31E) and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1",
            "section_title": "Supplemental Visual 5",
            "section_index": 4,
            "image_type": "concept"
        }
    ]
    
    logger.info(f"🎨 {len(prompts)}개 이미지 생성 시작...")
    
    # magic_book으로 배치 생성
    prompt_texts = [p["prompt"] for p in prompts]
    
    try:
        results = generate_images_batch_and_save(
            prompts=prompt_texts,
            auto_crop=False,  # 원본만 필요
            save_locally=False,
            verbose=True
        )
        
        logger.success(f"✅ magic_book 생성 완료: {len(results)}개")
        
        # 결과 정리
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
        
        return generated_images
        
    except Exception as e:
        logger.error(f"❌ 이미지 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_to_aivesto_supabase(images: list):
    """생성된 이미지를 aivesto Supabase에 저장"""
    from supabase import create_client
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("❌ aivesto SUPABASE_URL/KEY가 설정되지 않았습니다")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    logger.info("💾 aivesto Supabase에 저장 중...")
    
    article_id = "nvda_blackwell_20251113"
    
    for img in images:
        try:
            # images 테이블에 저장 (실제 스키마: symbol, topic, prompt, image_url만 존재)
            image_data = {
                "symbol": "NVDA",
                "topic": "blackwell_gpu",
                "prompt": img["prompt"],
                "image_url": img["image_url"]
            }

            result = supabase.table('images').insert(image_data).execute()

            if result.data:
                image_id = result.data[0]['id']
                logger.success(f"  ✅ {img['section_title']}: {image_id}")

                # blog_images 테이블에 연결 (실제 스키마: article_id, image_id, position만 존재)
                blog_image_data = {
                    "article_id": article_id,
                    "image_id": image_id,
                    "position": img["section_index"]
                }

                supabase.table('blog_images').insert(blog_image_data).execute()
                
        except Exception as e:
            logger.error(f"  ❌ 저장 실패 ({img['section_title']}): {e}")
    
    logger.success(f"✅ aivesto Supabase 저장 완료!")
    return True


def main():
    logger.info("=" * 60)
    logger.info("🚀 magic_book → aivesto 블로그 이미지 생성 파이프라인")
    logger.info("=" * 60)
    
    # 1. magic_book으로 이미지 생성
    images = generate_blog_images()
    
    if not images:
        logger.error("❌ 이미지 생성 실패")
        sys.exit(1)
    
    # 2. aivesto Supabase에 저장
    success = save_to_aivesto_supabase(images)
    
    if success:
        logger.success("🎉 완료! 이제 블로그에 표시할 수 있습니다:")
        logger.info("  python scripts/fetch_images_from_supabase.py")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
