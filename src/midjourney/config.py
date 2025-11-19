"""Midjourney Discord 설정"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Load from environment variables
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
SERVER_ID = os.getenv("DISCORD_SERVER_ID", "1439322559026954324")
CHANNEL_ID_FASHION = os.getenv("DISCORD_CHANNEL_FASHION", "1088256235603767350")
CHANNEL_ID_WONDER = os.getenv("DISCORD_CHANNEL_WONDER", "1439345125074407608")
SALAI_TOKEN = os.getenv("SALAI_TOKEN")
discord_base_url = f"https://discord.com/channels/{SERVER_ID}/{CHANNEL_ID_WONDER}"

#boolean
USE_MESSAGED_CHANNEL = False

#don't edit the following variable
MID_JOURNEY_ID = "936929561302675456"  #midjourney bot id

# Discord API 상수 (F12 개발자 도구에서 확인 - 2025-11-16 업데이트)
APPLICATION_ID = "936929561302675456"
APPLICATION_DATA_VERSION = "1237876415471554623"
APPLICATION_DATA_ID = "938956540159881230"
SESSION_ID = "7b2f4cef2320c9ebf70a2fb7b136628c"  # Updated 2025-11-16

