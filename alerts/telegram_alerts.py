"""
텔레그램 알림 시스템
Telegram Alert System for Investment Signals
"""

import requests
import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional
from loguru import logger

sys.path.append('..')
from dashboard.signal_api import SignalAPI


class TelegramAlertService:
    """텔레그램 알림 서비스"""

    def __init__(self, bot_token: str = None, chat_ids: List[str] = None):
        """
        Args:
            bot_token: 텔레그램 봇 토큰 (BotFather에서 발급)
            chat_ids: 텔레그램 채팅 ID 리스트 (채팅하고 /start 명령어로 확인)
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_ids = chat_ids or (os.getenv("TELEGRAM_CHAT_IDS", "").split(",") if os.getenv("TELEGRAM_CHAT_IDS") else [])
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        self.signal_api = SignalAPI()

        if self.bot_token:
            logger.info(f"Telegram alert service initialized (Token: {self.bot_token[:10]}...)")
        else:
            logger.warning("Telegram service not configured (no bot token)")

    def send_urgent_alert(self, signal_data: dict, chat_ids: List[str] = None) -> bool:
        """긴급 알림 전송 (Level 1 신호)"""
        if not chat_ids:
            chat_ids = self.chat_ids

        try:
            message = self._format_urgent_message(signal_data)
            return self._send_message(message, chat_ids, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error sending urgent alert: {e}")
            return False

    def send_daily_digest(self, chat_ids: List[str] = None, hours: int = 24) -> bool:
        """일일 요약 텔레그램 메시지 전송"""
        if not chat_ids:
            chat_ids = self.chat_ids

        try:
            summary = self.signal_api.get_dashboard_summary(hours=hours)
            message = self._format_daily_digest(summary, hours)
            return self._send_message(message, chat_ids, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            return False

    def send_high_priority_alert(self, chat_ids: List[str] = None, hours: int = 24) -> bool:
        """높은 우선순위 시그널 알림 (Level 1-2)"""
        if not chat_ids:
            chat_ids = self.chat_ids

        try:
            signals = self.signal_api.get_high_priority_signals(hours=hours, limit=50)

            if not signals:
                logger.info("No high-priority signals to send")
                return False

            message = self._format_high_priority_message(signals)
            return self._send_message(message, chat_ids, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error sending high-priority alert: {e}")
            return False

    def send_symbol_alert(self, symbol: str, chat_ids: List[str] = None, hours: int = 24) -> bool:
        """특정 종목 신호 알림"""
        if not chat_ids:
            chat_ids = self.chat_ids

        try:
            signals = self.signal_api.get_signals_by_symbol(symbol, hours=hours, limit=20)

            if not signals:
                logger.info(f"No signals for {symbol} to send")
                return False

            message = self._format_symbol_message(symbol, signals)
            return self._send_message(message, chat_ids, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Error sending symbol alert: {e}")
            return False

    def _format_urgent_message(self, signal_data: dict) -> str:
        """긴급 알림 메시지 포맷"""
        symbols = ", ".join(signal_data.get('affected_symbols', []))
        impact = signal_data.get('price_impact', 'unknown').upper()
        importance = signal_data.get('importance', 'unknown').upper()
        score = signal_data.get('relevance_score', 'N/A')

        message = f"""
🔴 <b>긴급 신호 알림!</b>

<b>제목:</b>
{signal_data.get('title', 'Unknown')[:100]}

<b>영향 종목:</b>
{symbols}

<b>관련성 점수:</b>
<b style="color: #ff4444;">{score}/100</b>

<b>주가 영향:</b> {impact}
<b>중요도:</b> {importance}
<b>신호 레벨:</b> Level {signal_data.get('signal_level', '?')} (🔴 URGENT)

<b>분석 요약:</b>
{signal_data.get('analysis', {}).get('reasoning', 'N/A')[:200]}

<b>핵심 포인트:</b>
"""
        for point in signal_data.get('analysis', {}).get('key_points', [])[:3]:
            message += f"\n• {point[:100]}"

        message += f"\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"

        return message

    def _format_daily_digest(self, summary: dict, hours: int) -> str:
        """일일 요약 메시지 포맷"""
        trending = summary.get('trending_symbols', [])[:5]

        message = f"""
📊 <b>일일 투자 신호 요약</b>

<b>📅 {datetime.now().strftime('%Y-%m-%d')}</b>

<b>신호 통계:</b>
🔴 긴급 (Level 1): {summary.get('urgent_count', 0)}
🟠 높음 (Level 2): {summary.get('high_count', 0)}
🟡 중간 (Level 3): {summary.get('medium_count', 0)}
🟢 낮음 (Level 4): {summary.get('low_count', 0)}

<b>📈 트렌딩 종목 (상위 5):</b>
"""
        for i, s in enumerate(trending, 1):
            message += f"\n{i}. <b>{s['symbol']}</b> - {s['count']}개 신호, 평균 점수: {s['avg_score']:.1f}"

        message += f"""

<b>조회 기간:</b> 최근 {hours}시간
⏰ 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🌐 <a href="http://localhost:5000">대시보드 보기</a>
"""
        return message

    def _format_high_priority_message(self, signals: List[dict]) -> str:
        """높은 우선순위 시그널 메시지 포맷"""
        message = f"""
🟠 <b>높은 우선순위 신호</b> - {len(signals)}개 알림

<b>Level 1 (긴급) 및 Level 2 (높음) 신호</b>

"""
        for i, s in enumerate(signals[:10], 1):
            level_emoji = "🔴" if s.get('signal_level') == 1 else "🟠"
            message += f"{i}. {level_emoji} <b>{s.get('title', 'Unknown')[:60]}</b>\n"
            message += f"   종목: {', '.join(s.get('affected_symbols', []))}\n"
            message += f"   점수: {s.get('relevance_score', 'N/A')}/100\n\n"

        if len(signals) > 10:
            message += f"... 그 외 {len(signals) - 10}개 신호\n\n"

        message += f"""⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🔗 <a href="http://localhost:5000/api/signals/high-priority">모든 신호 보기</a>
"""
        return message

    def _format_symbol_message(self, symbol: str, signals: List[dict]) -> str:
        """종목별 알림 메시지 포맷"""
        message = f"""
📈 <b>{symbol} 신호 알림</b> - {len(signals)}개 업데이트

"""
        for i, s in enumerate(signals[:8], 1):
            message += f"{i}. <b>{s.get('title', 'Unknown')[:70]}</b>\n"
            message += f"   점수: {s.get('relevance_score', 'N/A')}/100 | Level {s.get('signal_level', '?')}\n\n"

        if len(signals) > 8:
            message += f"... 그 외 {len(signals) - 8}개 신호\n\n"

        message += f"""⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🔗 <a href="http://localhost:5000/api/signals/by-symbol/{symbol}">상세 보기</a>
"""
        return message

    def _send_message(self, text: str, chat_ids: List[str], parse_mode: str = "HTML") -> bool:
        """텔레그램 메시지 전송"""
        if not self.bot_token:
            logger.warning("Telegram service not configured")
            return False

        if not chat_ids:
            logger.warning("No chat IDs configured")
            return False

        success_count = 0

        for chat_id in chat_ids:
            try:
                # 메시지 길이 제한: 4096자
                if len(text) > 4096:
                    logger.warning(f"Message too long ({len(text)} chars), truncating")
                    text = text[:4093] + "..."

                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True
                }

                response = requests.post(
                    f"{self.base_url}/sendMessage",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info(f"Telegram message sent to {chat_id}")
                    success_count += 1
                else:
                    logger.error(f"Failed to send message to {chat_id}: {response.text}")

            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")

        return success_count == len(chat_ids)

    def send_test_message(self, chat_id: str = None) -> bool:
        """테스트 메시지 전송"""
        test_chat_id = chat_id or (self.chat_ids[0] if self.chat_ids else None)

        if not test_chat_id:
            logger.error("No chat ID provided for test")
            return False

        message = """
✅ <b>텔레그램 알림 설정 성공!</b>

이제 다음과 같은 알림을 받게 됩니다:
🔴 긴급 신호 (Level 1)
🟠 높은 우선순위 신호 (Level 2)
📊 일일 요약
📈 종목별 알림

<b>테스트 정보:</b>
• Bot Token: {self.bot_token[:10]}...
• Chat ID: {test_chat_id}
• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

질문이나 문제가 있으시면 로그를 확인하세요.
"""
        return self._send_message(message, [test_chat_id], parse_mode="HTML")

    def validate_config(self) -> bool:
        """텔레그램 설정 검증"""
        if not self.bot_token:
            logger.error("Bot token not configured")
            return False

        if not self.chat_ids:
            logger.error("Chat IDs not configured")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/getMe",
                timeout=5
            )
            if response.status_code == 200:
                bot_info = response.json()
                logger.info(f"Telegram bot validated: @{bot_info['result']['username']}")
                return True
            else:
                logger.error(f"Invalid bot token: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to validate bot token: {e}")
            return False

    def schedule_daily_digest(self, chat_ids: List[str], hour: int = 9):
        """일일 요약 스케줄 설정 (job scheduler에서 사용)"""
        logger.info(f"Daily digest scheduled for {hour}:00 UTC to {chat_ids}")
        # 실제 스케줄링은 scheduler/jobs.py에서 처리
