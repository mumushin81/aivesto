#!/usr/bin/env python3
"""
Simple Discord bot test to verify connection and channel access
"""
import os
import asyncio
import discord
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

async def test_connection():
    token = os.getenv("DISCORD_BOT_TOKEN")
    channel_id = int(os.getenv("MIDJOURNEY_CHANNEL_ID"))

    if not token or not channel_id:
        logger.error("Missing DISCORD_BOT_TOKEN or MIDJOURNEY_CHANNEL_ID")
        return

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"✅ Logged in as {client.user} (ID: {client.user.id})")

        # Get channel
        channel = client.get_channel(channel_id)
        if not channel:
            try:
                channel = await client.fetch_channel(channel_id)
            except Exception as e:
                logger.error(f"❌ Cannot access channel {channel_id}: {e}")
                await client.close()
                return

        logger.info(f"✅ Found channel: {channel.name} (ID: {channel.id})")

        # Send test message
        try:
            test_msg = await channel.send("🤖 Discord bot test - connection successful!")
            logger.success(f"✅ Test message sent: {test_msg.id}")

            # Try to trigger Midjourney with /imagine
            imagine_msg = await channel.send("/imagine prompt: a simple test image --ar 16:9")
            logger.info(f"📨 Sent imagine command: {imagine_msg.id}")

        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")

        # Wait a bit then close
        await asyncio.sleep(5)
        await client.close()

    try:
        await client.start(token)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
