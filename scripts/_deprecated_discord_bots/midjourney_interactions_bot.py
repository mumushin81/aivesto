#!/usr/bin/env python3
"""
Discord Interactions API를 사용하여 Midjourney 슬래시 커맨드 트리거
"""
import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from loguru import logger
import discord
from discord import app_commands

load_dotenv()


class MidjourneyInteractionsBot(discord.Client):
    """Discord Interactions API를 사용한 Midjourney 봇"""

    def __init__(
        self,
        *,
        channel_id: int,
        midjourney_bot_id: int = 936929561302675456,
    ):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        super().__init__(intents=intents)

        self.channel_id = channel_id
        self.midjourney_bot_id = midjourney_bot_id
        self.tree = app_commands.CommandTree(self)
        self.pending_prompts: Dict[str, Dict] = {}

    async def setup_hook(self):
        """봇 시작 시 커맨드 트리 동기화"""
        logger.info("Setting up command tree...")

    async def on_ready(self):
        """봇 준비 완료"""
        logger.info(f"✅ Logged in as {self.user} (ID: {self.user.id})")

        # 채널 확인
        channel = self.get_channel(self.channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.channel_id)
        logger.info(f"✅ Channel: {channel.name}")

        # 길드 정보 확인
        for guild in self.guilds:
            logger.info(f"✅ Guild: {guild.name} (ID: {guild.id})")

            # Midjourney 봇이 이 길드에 있는지 확인
            midjourney_member = guild.get_member(self.midjourney_bot_id)
            if midjourney_member:
                logger.success(f"✅ Midjourney bot found: {midjourney_member.name}")
            else:
                logger.warning(f"⚠️ Midjourney bot not found in {guild.name}")

    async def trigger_imagine(
        self,
        prompt: str,
        article_id: str,
        position: int = 0,
        section_title: Optional[str] = None,
    ) -> Optional[str]:
        """
        Midjourney /imagine 커맨드 트리거 (Interactions API 사용)

        중요: Discord의 Interactions API는 봇이 다른 봇의 슬래시 커맨드를
        프로그래밍 방식으로 실행할 수 없습니다.

        대안:
        1. discord-py-interactions 라이브러리 사용
        2. Discord Gateway를 통한 INTERACTION_CREATE 이벤트 전송 (비공식, ToS 위반)
        3. Selenium/Playwright로 브라우저 자동화 (비권장)
        """
        channel = self.get_channel(self.channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.channel_id)

        # Midjourney 봇을 직접 호출할 수 없으므로,
        # 텍스트 메시지로 프롬프트 전송 (작동하지 않을 가능성 높음)
        try:
            # 방법 1: 멘션 + 커맨드 (작동하지 않음)
            message = await channel.send(f"<@{self.midjourney_bot_id}> /imagine prompt: {prompt}")
            logger.info(f"📨 Sent prompt via mention (msg id: {message.id})")

            # 추적을 위해 저장
            self.pending_prompts[str(message.id)] = {
                "prompt": prompt,
                "article_id": article_id,
                "position": position,
                "section_title": section_title,
                "sent_at": datetime.utcnow().isoformat(),
            }

            return str(message.id)

        except Exception as e:
            logger.error(f"❌ Failed to send prompt: {e}")
            return None

    async def on_message(self, message: discord.Message):
        """Midjourney 응답 모니터링"""
        # Midjourney 봇의 응답만 처리
        if message.author.id != self.midjourney_bot_id:
            return

        logger.info(f"🎨 Midjourney message: {message.content[:100]}")

        # 첨부파일(이미지) 확인
        if message.attachments:
            for attachment in message.attachments:
                logger.success(f"🖼️ Image generated: {attachment.url}")

                # 매칭되는 프롬프트 찾기
                for msg_id, prompt_data in self.pending_prompts.items():
                    if prompt_data["prompt"][:30] in message.content:
                        logger.success(f"✅ Matched prompt: {prompt_data['section_title']}")
                        # 여기서 이미지 다운로드 및 처리
                        return


async def test_single_imagine(prompt: str):
    """단일 이미지 생성 테스트"""
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))

    bot = MidjourneyInteractionsBot(channel_id=channel_id)

    @bot.event
    async def on_ready():
        """봇 준비 완료 후 테스트 실행"""
        logger.info("🚀 Bot ready, sending test prompt...")

        msg_id = await bot.trigger_imagine(
            prompt=prompt,
            article_id="test",
            position=0,
            section_title="Test Image",
        )

        if msg_id:
            logger.info(f"✅ Prompt sent successfully (msg_id: {msg_id})")
            logger.info("⏳ Waiting 60 seconds for Midjourney response...")
            await asyncio.sleep(60)
        else:
            logger.error("❌ Failed to send prompt")

        await bot.close()

    await bot.start(token)


if __name__ == "__main__":
    # 테스트용 프롬프트
    test_prompt = "Modern technology visualization, NVIDIA GPU with glowing green circuits, professional corporate style, dramatic lighting --ar 16:9 --quality 2"

    logger.info(f"🧪 Testing Midjourney Interactions API")
    logger.info(f"📝 Prompt: {test_prompt}")

    asyncio.run(test_single_imagine(test_prompt))
