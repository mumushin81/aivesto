"""
Telegram Chat ID 조회 스크립트
Get Telegram Chat ID from bot token
"""

import requests
import sys
import argparse
from loguru import logger


def get_chat_id(bot_token: str):
    """
    Telegram 봇에서 Chat ID 조회

    Args:
        bot_token: Telegram 봇 토큰
    """
    try:
        base_url = f"https://api.telegram.org/bot{bot_token}"

        # 봇 정보 확인
        logger.info("🤖 Telegram 봇 정보 조회 중...")
        bot_response = requests.get(
            f"{base_url}/getMe",
            timeout=10
        )

        if bot_response.status_code != 200:
            logger.error(f"❌ 봇 토큰 오류: {bot_response.text}")
            return False

        bot_info = bot_response.json()
        if bot_info['ok']:
            bot_username = bot_info['result']['username']
            bot_name = bot_info['result']['first_name']
            logger.info(f"✅ 봇 확인: @{bot_username} ({bot_name})")
        else:
            logger.error(f"❌ 봇 조회 실패: {bot_info}")
            return False

        # 최근 업데이트 확인
        logger.info("\n📩 최근 메시지 확인 중...")
        logger.info("(봇과 상호작용한 메시지가 있는지 확인)")

        updates_response = requests.get(
            f"{base_url}/getUpdates",
            timeout=10
        )

        if updates_response.status_code != 200:
            logger.error(f"❌ 업데이트 조회 실패: {updates_response.text}")
            return False

        updates = updates_response.json()

        if not updates['ok'] or not updates['result']:
            logger.error("""
❌ 메시지 없음!

다음 단계를 수행하세요:
1. Telegram 앱 열기
2. 검색에서 @{} 찾기
3. /start 또는 아무 메시지 보내기
4. 이 스크립트 다시 실행

또는 다음 URL에서 Chat ID 확인:
https://api.telegram.org/bot{}/getUpdates
            """.format(bot_username, bot_token))
            return False

        # Chat ID 추출
        chat_ids = {}
        for update in updates['result']:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                first_name = chat.get('first_name', 'Unknown')

                if chat_id not in chat_ids:
                    chat_ids[chat_id] = first_name

        if not chat_ids:
            logger.error("❌ Chat ID를 찾을 수 없습니다")
            return False

        # 결과 표시
        print("\n" + "=" * 60)
        print("✅ Chat ID 조회 성공!")
        print("=" * 60)
        print(f"\n봇: @{bot_username}")
        print(f"\n발견된 Chat ID:")
        for chat_id, name in chat_ids.items():
            print(f"  • {chat_id} ({name})")

        # .env 형식으로 출력
        chat_id_list = ",".join(str(id) for id in chat_ids.keys())
        print(f"\n📝 .env 파일에 다음을 추가하세요:")
        print(f"TELEGRAM_BOT_TOKEN={bot_token}")
        print(f"TELEGRAM_CHAT_IDS={chat_id_list}")

        print("\n" + "=" * 60)
        return True

    except requests.exceptions.Timeout:
        logger.error("❌ 요청 타임아웃 - 인터넷 연결 확인")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 요청 실패: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 오류: {e}")
        return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="Telegram Chat ID 조회"
    )
    parser.add_argument(
        "--token",
        required=True,
        help="Telegram 봇 토큰 (BotFather에서 발급)"
    )

    args = parser.parse_args()

    success = get_chat_id(args.token)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
