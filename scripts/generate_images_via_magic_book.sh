#!/bin/bash
# magic_book을 사용하여 aivesto 블로그 이미지 생성

cd /Users/jinxin/dev/magic_book

python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.midjourney import generate_images_batch_and_save
from loguru import logger

# aivesto NVDA Blackwell 기사 프롬프트
PROMPTS = [
    "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting, floating semiconductor design, black background with subtle green accents, professional tech photography, 8k quality --ar 16:9 --quality 2 --stylize 500",
    "Technical architecture diagram of advanced GPU chip design, labeled components, clean white background, professional vector illustration, green and black color scheme, isometric perspective, enterprise presentation style --ar 16:9 --quality 1",
    "Professional technology concept visualization, modern digital innovation, green and black color palette, clean high-contrast design, corporate tech aesthetic, dramatic lighting --ar 16:9 --quality 1",
]

logger.info("=" * 60)
logger.info("🎨 aivesto 블로그 이미지 생성 (via magic_book)")
logger.info("=" * 60)

results = generate_images_batch_and_save(
    prompts=PROMPTS,
    auto_crop=False,
    save_locally=False,
    verbose=True
)

logger.success(f"\n✅ 완료: {len(results)}개 이미지 생성")

for idx, result in enumerate(results, 1):
    if result.success and result.supabase_image_ids:
        logger.info(f"{idx}. Image ID: {result.supabase_image_ids[0]}")
        logger.info(f"   URL: {result.image_url[:80]}...")
    else:
        logger.error(f"{idx}. 실패")

EOF
