#!/usr/bin/env python3
"""
Midjourney로 aivesto 블로그 이미지 생성
magic_book 모듈 사용
"""
import sys
from pathlib import Path

# aivesto 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.midjourney import generate_images_batch_and_save
from loguru import logger

# NVDA Blackwell 기사 프롬프트
NVDA_PROMPTS = [
    "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting, floating semiconductor design, black background with subtle green accents, professional tech photography, 8k quality --ar 16:9 --quality 2 --stylize 500",
    "Technical architecture diagram of advanced GPU chip design, labeled components, clean white background, professional vector illustration, green and black color scheme, isometric perspective, enterprise presentation style --ar 16:9 --quality 1",
    "Professional technology concept visualization, modern digital innovation, green (#16B31E) and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1",
]

def main():
    logger.info("=" * 60)
    logger.info("🎨 Midjourney 블로그 이미지 생성")
    logger.info("=" * 60)
    
    logger.info(f"📝 {len(NVDA_PROMPTS)}개 이미지 생성 시작...")
    
    results = generate_images_batch_and_save(
        prompts=NVDA_PROMPTS,
        auto_crop=False,
        save_locally=False,
        verbose=True
    )
    
    logger.success(f"✅ 완료: {len(results)}개")
    
    for idx, result in enumerate(results, 1):
        if result.success:
            logger.info(f"{idx}. URL: {result.image_url[:80]}...")
        else:
            logger.error(f"{idx}. 실패: {result.error if hasattr(result, 'error') else 'Unknown'}")

if __name__ == "__main__":
    main()
