#!/usr/bin/env python3
"""
One-shot pipeline:
 1) Analyze Markdown → sections/keywords/slots
 2) Generate Midjourney prompts (GPT-backed)
 3) Submit prompts to Midjourney via Discord; upload to Supabase
 4) Inject resulting image URLs back into Markdown

Environment: requires same .env variables as discord_midjourney_bot + Supabase + OpenAI.
"""

import argparse
import json
import os
import sys
import asyncio
from pathlib import Path

from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.blog_content_analyzer import analyze_markdown
from scripts.contextual_prompt_generator import build_prompts, DEFAULT_BRAND
from scripts.multi_image_generator import generate_images
from scripts.smart_image_injector import inject


def run(markdown_path: Path, article_id: str, working_dir: Path):
    working_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: analysis
    analysis = analyze_markdown(markdown_path, min_images=5)
    analysis_path = working_dir / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Analysis saved to {analysis_path}")

    # Step 2: prompts
    prompts = build_prompts(analysis, DEFAULT_BRAND)
    prompts_path = working_dir / "prompts.json"
    prompts_path.write_text(json.dumps(prompts, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Prompts saved to {prompts_path}")

    # Step 3: images
    results = []
    try:
        results = asyncio.run(generate_images(prompts, article_id))
    except Exception as exc:
        logger.error(f"Image generation failed: {exc}")
        raise

    images_path = working_dir / "images.json"
    images_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Images saved to {images_path}")

    # Step 4: inject into markdown
    injected_path = working_dir / f"{Path(markdown_path).stem}_with_images.md"
    inject(markdown_path, results, injected_path)
    logger.info(f"Final article ready at {injected_path}")

    return {
        "analysis": str(analysis_path),
        "prompts": str(prompts_path),
        "images": str(images_path),
        "output_markdown": str(injected_path),
    }


def main():
    parser = argparse.ArgumentParser(description="End-to-end blog image pipeline")
    parser.add_argument("markdown_path", type=Path, help="Path to source Markdown")
    parser.add_argument("--article-id", required=True, help="Stable identifier (e.g., slug or DB id)")
    parser.add_argument("--workdir", type=Path, default=Path("tmp") / "pipeline")
    args = parser.parse_args()

    run(args.markdown_path, args.article_id, args.workdir)


if __name__ == "__main__":
    main()
