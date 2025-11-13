"""
Telegram 알림 테스트 스크립트
Test Telegram Alert Service
"""

import sys
import os
from datetime import datetime
from loguru import logger

sys.path.append('..')
from alerts.telegram_alerts import TelegramAlertService


def test_telegram_service():
    """텔레그램 서비스 테스트"""

    print("\n" + "=" * 70)
    print("📱 Telegram 알림 시스템 테스트")
    print("=" * 70)

    # 서비스 초기화
    service = TelegramAlertService()

    # 1. 설정 검증
    print("\n1️⃣ 설정 검증 중...")

    if not service.bot_token:
        print("❌ Bot Token 없음")
        print("   → .env 파일에 TELEGRAM_BOT_TOKEN=YOUR_TOKEN 추가")
        return False
    else:
        print(f"✅ Bot Token: {service.bot_token[:10]}...{service.bot_token[-10:]}")

    if not service.chat_ids:
        print("❌ Chat ID 없음")
        print("   → .env 파일에 TELEGRAM_CHAT_IDS=YOUR_ID 추가")
        return False
    else:
        print(f"✅ Chat IDs: {', '.join(service.chat_ids)}")

    # 2. 봇 토큰 검증
    print("\n2️⃣ 봇 연결 검증 중...")

    if not service.validate_config():
        print("❌ 봇 연결 실패")
        print("   → Bot Token이 유효한지 확인")
        print("   → 인터넷 연결 확인")
        return False
    else:
        print("✅ 봇 연결 성공")

    # 3. 테스트 메시지
    print("\n3️⃣ 테스트 메시지 전송 중...")

    test_result = service.send_test_message(service.chat_ids[0] if service.chat_ids else None)

    if test_result:
        print("✅ 테스트 메시지 전송 성공")
        print("   → Telegram 앱에서 메시지 확인해주세요")
    else:
        print("❌ 테스트 메시지 전송 실패")
        print("   → Chat ID가 유효한지 확인")
        return False

    # 4. 긴급 신호 테스트
    print("\n4️⃣ 긴급 신호 테스트 중...")

    test_signal = {
        "title": "[테스트] Apple Q4 earnings beat expectations",
        "affected_symbols": ["AAPL", "MSFT"],
        "relevance_score": 95,
        "price_impact": "up",
        "importance": "high",
        "signal_level": 1,
        "analysis": {
            "reasoning": "Apple이 Q4 실적에서 기대치를 15% 초과 달성했습니다. 이는 iPhone 판매량 증가로 인한 것으로, 주가 상승이 예상됩니다.",
            "key_points": [
                "Q4 매출: $123.5B (+10% YoY)",
                "iPhone 판매 25% 증가",
                "서비스 부문 역대 최고 매출"
            ]
        }
    }

    if service.send_urgent_alert(test_signal, service.chat_ids):
        print("✅ 긴급 신호 테스트 성공")
    else:
        print("⚠️ 긴급 신호 테스트 실패 (무시 가능)")

    # 5. 일일 요약 테스트
    print("\n5️⃣ 일일 요약 테스트 중...")

    if service.send_daily_digest(service.chat_ids):
        print("✅ 일일 요약 테스트 성공")
    else:
        print("⚠️ 일일 요약 테스트 실패 (무시 가능)")

    # 6. 높은 우선순위 테스트
    print("\n6️⃣ 높은 우선순위 테스트 중...")

    if service.send_high_priority_alert(service.chat_ids):
        print("✅ 높은 우선순위 테스트 성공")
    else:
        print("⚠️ 높은 우선순위 테스트 실패 (신호 없음 - 정상)")

    # 7. 종목별 테스트
    print("\n7️⃣ 종목별 알림 테스트 중...")

    if service.send_symbol_alert("MSFT", service.chat_ids):
        print("✅ 종목별 알림 테스트 성공")
    else:
        print("⚠️ 종목별 알림 테스트 실패 (신호 없음 - 정상)")

    # 최종 결과
    print("\n" + "=" * 70)
    print("✅ 테스트 완료!")
    print("=" * 70)
    print("""
다음 단계:
1. ✅ Telegram에서 메시지 확인
2. ✅ 메시지 포맷 확인 (이모지, 링크 등)
3. ✅ 대시보드 시작: python main.py --mode run
4. ✅ 실시간 알림 수신 대기

설정 정보:
- Bot Token: TELEGRAM_BOT_TOKEN (환경 변수)
- Chat IDs: TELEGRAM_CHAT_IDS (환경 변수)

스케줄러 통합:
- 긴급 신호: 즉시 전송 (트리거 기반)
- 일일 요약: 매일 09:00 UTC
- 높은 우선순위: 매시간
- 종목별: 감지 시

더 많은 정보: TELEGRAM_SETUP_GUIDE.md
""")
    print("=" * 70)

    return True


def main():
    """메인 함수"""
    try:
        success = test_telegram_service()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
