#!/usr/bin/env python3
"""
Simple test: Send a single Midjourney prompt and wait for result
"""
import os
import asyncio
import discord
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def test_midjourney():
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))
    midjourney_bot_id = int(os.getenv("MIDJOURNEY_BOT_ID", "936929561302675456"))

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"✅ Logged in as {client.user}")

        channel = await client.fetch_channel(channel_id)
        logger.info(f"✅ Channel: {channel.name}")

        # Test prompt
        test_prompt = "Futuristic NVIDIA GPU chip with glowing green circuits, ultra-detailed 3D render, dramatic studio lighting --ar 16:9 --quality 2"

        # Method 1: Try mentioning Midjourney bot
        msg = await channel.send(f"<@{midjourney_bot_id}> /imagine prompt: {test_prompt}")
        logger.info(f"📨 Sent prompt via mention: {msg.id}")

        # Wait to see if Midjourney responds
        logger.info("⏳ Waiting 30 seconds for Midjourney response...")
        await asyncio.sleep(30)
        await client.close()

    @client.event
    async def on_message(message):
        # Check for Midjourney responses
        if message.author.id == midjourney_bot_id:
            logger.success(f"🎨 Midjourney responded: {message.content[:100]}")
            if message.attachments:
                logger.success(f"🖼️  Image attached: {message.attachments[0].url}")

    await client.start(token)

if __name__ == "__main__":
    asyncio.run(test_midjourney())
