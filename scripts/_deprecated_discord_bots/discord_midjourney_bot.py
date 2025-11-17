"""
Discord bot that automates Midjourney prompts, downloads the resulting image,
pushes it to Supabase storage/DB, and emits callbacks for downstream steps.

⚠️ Midjourney/Discord ToS: automated use of Midjourney via self-bots or
programmatic slash-command triggering may violate their terms. Keep this bot in
private servers you own, respect Midjourney's rate limits, and prefer the
official API/commercial plan when available. Use at your own risk.
"""

import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, Optional

import aiohttp
import discord
from dotenv import load_dotenv
from loguru import logger

from scripts.supabase_image_uploader import SupabaseImageUploader


load_dotenv()


class MidjourneyDiscordBot(discord.Client):
    def __init__(
        self,
        *,
        channel_id: int,
        midjourney_bot_id: int = 936929561302675456,
        result_callback: Optional[Callable[[Dict], None]] = None,
        rate_limit_per_min: int = 10,
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

        self.channel_id = channel_id
        self.midjourney_bot_id = midjourney_bot_id
        self.rate_limit_per_min = rate_limit_per_min
        self.result_callback = result_callback

        self.queue: asyncio.Queue[Dict] = asyncio.Queue()
        self.pending_messages: Dict[str, Dict] = {}
        self.last_minute: datetime = datetime.utcnow()
        self.sent_this_minute = 0

        self.session = aiohttp.ClientSession()
        self.uploader = SupabaseImageUploader()

    # ---------------- Discord lifecycle ----------------
    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        self.loop.create_task(self.worker())

    async def close(self):
        await self.session.close()
        await super().close()

    # ---------------- Public API ----------------
    async def enqueue_prompt(
        self,
        *,
        symbol: str,
        topic: str,
        prompt: str,
        article_id: str,
        position: int = 0,
        section_title: str | None = None,
        context_keywords: list | None = None,
        image_type: str | None = None,
        caption: str | None = None,
        image_slot_after_line: int | None = None,
    ):
        await self.queue.put({
            "symbol": symbol,
            "topic": topic,
            "prompt": prompt,
            "article_id": article_id,
            "position": position,
            "section_title": section_title,
            "context_keywords": context_keywords,
            "image_type": image_type,
            "caption": caption,
            "image_slot_after_line": image_slot_after_line,
        })

    # ---------------- Worker ----------------
    async def worker(self):
        channel = self.get_channel(self.channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.channel_id)

        while True:
            job = await self.queue.get()
            await self._respect_rate_limit()

            # Send /imagine command to Midjourney bot
            content = f"/imagine prompt: {job['prompt']}"
            message = await channel.send(content)
            logger.info(f"Sent prompt for {job['symbol']} (msg id {message.id})")

            # Track for correlation
            self.pending_messages[str(message.id)] = {
                **job,
                "sent_at": datetime.utcnow(),
                "message_id": message.id,
            }

            # Timeout cleanup
            self.loop.create_task(self._timeout_job(message.id, timeout=900))

    async def _respect_rate_limit(self):
        # 60초 간격으로 하나씩 전송
        if self.sent_this_minute > 0:
            logger.info(f"Rate limit: sleeping 60s before next prompt")
            await asyncio.sleep(60)
        self.sent_this_minute += 1

    async def _timeout_job(self, message_id: int, timeout: int):
        await asyncio.sleep(timeout)
        job = self.pending_messages.pop(str(message_id), None)
        if job:
            logger.error(f"Midjourney response timeout for prompt: {job['prompt']}")

    # ---------------- Message handler ----------------
    async def on_message(self, message: discord.Message):
        # Only care about Midjourney bot responses.
        if message.author.id != self.midjourney_bot_id:
            return

        if not message.attachments:
            return

        # Heuristic: check if this response matches the latest pending prompt substring
        matching_job = None
        for job in self.pending_messages.values():
            if job["prompt"][:30] in message.content:
                matching_job = job
                break

        if not matching_job:
            logger.warning("Received Midjourney image but no matching job")
            return

        attachment = message.attachments[0]
        tmpdir = Path(tempfile.mkdtemp())
        local_path = tmpdir / attachment.filename
        await attachment.save(local_path)
        logger.info(f"Downloaded image to {local_path}")

        # Upload & record
        image_id, public_url = self.uploader.upload_and_record(
            file_path=local_path,
            symbol=matching_job["symbol"],
            topic=matching_job["topic"],
            prompt=matching_job["prompt"],
            article_id=matching_job.get("article_id"),
            position=matching_job.get("position", 0),
            section_title=matching_job.get("section_title"),
            context_keywords=matching_job.get("context_keywords"),
            image_type=matching_job.get("image_type"),
            caption=matching_job.get("caption"),
        )

        # Callback to pipeline
        payload = {
            **matching_job,
            "image_id": image_id,
            "image_url": public_url,
            "midjourney_message_url": message.jump_url,
        }
        if self.result_callback:
            try:
                self.result_callback(payload)
            except Exception as exc:
                logger.error(f"Result callback failed: {exc}")

        self.pending_messages.pop(str(matching_job["message_id"]), None)
        logger.info(f"Job complete for {matching_job['symbol']} -> {public_url}")


def load_prompts(path: Path) -> Dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


async def main(prompts_path: str, article_id_prefix: str = "auto", channel_id: Optional[int] = None):
    token = os.getenv("DISCORD_BOT_TOKEN")
    mj_channel_id = channel_id or int(os.getenv("MIDJOURNEY_CHANNEL_ID", "0"))
    if not token or not mj_channel_id:
        raise RuntimeError("DISCORD_BOT_TOKEN or MIDJOURNEY_CHANNEL_ID missing")

    prompts = load_prompts(Path(prompts_path))

    injector_payloads = []

    def on_complete(payload: Dict):
        injector_payloads.append(payload)

    bot = MidjourneyDiscordBot(channel_id=mj_channel_id, result_callback=on_complete)

    async with bot:
        # enqueue jobs
        for idx, (key, prompt_obj) in enumerate(prompts.items()):
            await bot.enqueue_prompt(
                symbol=prompt_obj.get("symbol") or key.split("_")[0].upper(),
                topic=prompt_obj.get("topic") or key.replace("_", " "),
                prompt=prompt_obj["midjourney_prompt"],
                article_id=f"{article_id_prefix}_{key}",
                position=idx,
            )
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main("scripts/ai_image_prompts.json"))
