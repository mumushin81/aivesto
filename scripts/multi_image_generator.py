#!/usr/bin/env python3
"""
Send 5+ prompts to Midjourney via Discord bot and upload results to Supabase.

Input : prompts JSON from contextual_prompt_generator.py
Output: images JSON with URLs + metadata (for injector)

Requires:
  - DISCORD_BOT_TOKEN
  - MIDJOURNEY_CHANNEL_ID
  - SUPABASE_URL + SUPABASE_KEY (or SUPABASE_SERVICE_ROLE_KEY)
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List

from dotenv import load_dotenv
from loguru import logger

from scripts.discord_midjourney_bot import MidjourneyDiscordBot

load_dotenv()


async def generate_images(prompts: Dict, article_id: str) -> List[Dict]:
    total = len(prompts)
    done_event = asyncio.Event()
    results: List[Dict] = []

    def on_result(payload):
        results.append(payload)
        if len(results) >= total:
            done_event.set()

    async def start_bot():
        async with bot:
            token = os.getenv("DISCORD_BOT_TOKEN")
            channel_id = int(os.getenv("MIDJOURNEY_CHANNEL_ID", "0"))
            if not token or not channel_id:
                raise RuntimeError("Set DISCORD_BOT_TOKEN and MIDJOURNEY_CHANNEL_ID in .env")

            bot.channel_id = channel_id

            for _, prompt_obj in prompts.items():
                await bot.enqueue_prompt(
                    symbol=prompt_obj.get("symbol", "NVDA"),
                    topic=prompt_obj.get("section_title"),
                    prompt=prompt_obj["prompt"],
                    article_id=article_id,
                    position=prompt_obj.get("position", 0),
                    section_title=prompt_obj.get("section_title"),
                    context_keywords=prompt_obj.get("keywords"),
                    image_type=prompt_obj.get("image_type"),
                    caption=prompt_obj.get("caption"),
                    image_slot_after_line=prompt_obj.get("image_slot_after_line"),
                )
            await bot.start(token)

    channel_id_env = int(os.getenv("MIDJOURNEY_CHANNEL_ID", "0"))
    bot = MidjourneyDiscordBot(
        channel_id=channel_id_env or 0,
        result_callback=on_result,
    )

    bot_task = asyncio.create_task(start_bot())
    await done_event.wait()
    await bot.close()
    await bot_task
    return results


def _write(results: List[Dict], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Saved {len(results)} image records to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate multiple Midjourney images via Discord.")
    parser.add_argument("prompts_json", type=Path)
    parser.add_argument("--article-id", required=True, help="Stable article identifier")
    parser.add_argument("--out", type=Path, default=Path("tmp") / "images.json")
    args = parser.parse_args()

    prompts = json.loads(args.prompts_json.read_text(encoding="utf-8"))
    results = asyncio.run(generate_images(prompts, args.article_id))
    _write(results, args.out)


if __name__ == "__main__":
    main()
