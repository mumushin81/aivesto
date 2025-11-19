"""End-to-end runner: prompts -> Midjourney via Discord -> Supabase -> blog HTML."""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from scripts.blog_image_injector import BlogImageInjector, build_card
from scripts.discord_midjourney_bot import MidjourneyDiscordBot, load_prompts


load_dotenv()


async def run_pipeline(
    prompts_file: str = "scripts/ai_image_prompts.json",
    blog_html: str = "public/blog.html",
    article_id_prefix: str = "auto",
):
    prompts = load_prompts(Path(prompts_file))
    total = len(prompts)
    done_event = asyncio.Event()
    results = []

    def on_result(payload):
        results.append(payload)
        if len(results) >= total:
            done_event.set()

    channel_id = int(os.getenv("MIDJOURNEY_CHANNEL_ID", "0"))
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or not channel_id:
        raise RuntimeError("Set DISCORD_BOT_TOKEN and MIDJOURNEY_CHANNEL_ID in .env")

    bot = MidjourneyDiscordBot(channel_id=channel_id, result_callback=on_result)

    async def start_bot():
        async with bot:
            for idx, (key, prompt_obj) in enumerate(prompts.items()):
                await bot.enqueue_prompt(
                    symbol=prompt_obj.get("symbol") or key.split("_")[0].upper(),
                    topic=prompt_obj.get("topic") or key.replace("_", " "),
                    prompt=prompt_obj["midjourney_prompt"],
                    article_id=f"{article_id_prefix}_{key}",
                    position=idx,
                )
            await bot.start(token)

    bot_task = asyncio.create_task(start_bot())

    await done_event.wait()
    logger.info("All prompts completed, shutting down bot")
    await bot.close()
    await bot_task

    # Inject into blog
    injector = BlogImageInjector(Path(blog_html))
    cards = [
        build_card(
            article_id=payload["article_id"],
            image_url=payload["image_url"],
            symbol=payload["symbol"],
            topic=payload["topic"],
            date=datetime.utcnow().date().isoformat(),
        )
        for payload in results
    ]
    injector.inject_cards(cards)
    logger.info(f"Pipeline finished. Updated {blog_html}")


def main():
    asyncio.run(run_pipeline())


if __name__ == "__main__":
    main()

