"""
이메일 알림 시스템
Email Alert System for Investment Signals
"""

import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from loguru import logger

sys.path.append('..')
from config.settings import ANTHROPIC_API_KEY  # 향후 이메일 설정 추가 예정
from dashboard.signal_api import SignalAPI


class EmailAlertService:
    """이메일 알림 서비스"""

    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 sender_email: str = None, sender_password: str = None):
        """
        Args:
            smtp_server: SMTP 서버 주소
            smtp_port: SMTP 포트
            sender_email: 발신자 이메일
            sender_password: 발신자 비밀번호
        """
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.sender_email = sender_email or "noreply@aivesto.com"
        self.sender_password = sender_password

        self.signal_api = SignalAPI()
        logger.info(f"Email alert service initialized with {self.smtp_server}:{self.smtp_port}")

    def send_urgent_alert(self, signal_data: dict, recipient_emails: List[str]) -> bool:
        """긴급 알림 전송 (Level 1 신호)"""
        try:
            subject = f"🔴 URGENT: {signal_data['title'][:60]}"
            body = self._format_urgent_email(signal_data)

            return self._send_email(subject, body, recipient_emails, priority="high")

        except Exception as e:
            logger.error(f"Error sending urgent alert: {e}")
            return False

    def send_daily_digest(self, recipient_emails: List[str], hours: int = 24) -> bool:
        """일일 요약 이메일 전송"""
        try:
            summary = self.signal_api.get_dashboard_summary(hours=hours)

            subject = f"📊 Investment Signal Summary - {datetime.now().strftime('%Y-%m-%d')}"
            body = self._format_daily_digest(summary, hours)

            return self._send_email(subject, body, recipient_emails, priority="normal")

        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            return False

    def send_high_priority_alert(self, recipient_emails: List[str], hours: int = 24) -> bool:
        """높은 우선순위 시그널 알림 (Level 1-2)"""
        try:
            signals = self.signal_api.get_high_priority_signals(hours=hours, limit=50)

            if not signals:
                logger.info("No high-priority signals to send")
                return False

            subject = f"🟠 High Priority Signals - {len(signals)} alerts"
            body = self._format_high_priority_email(signals)

            return self._send_email(subject, body, recipient_emails, priority="high")

        except Exception as e:
            logger.error(f"Error sending high-priority alert: {e}")
            return False

    def send_symbol_alert(self, symbol: str, recipient_emails: List[str],
                         hours: int = 24) -> bool:
        """특정 종목 신호 알림"""
        try:
            signals = self.signal_api.get_signals_by_symbol(symbol, hours=hours, limit=20)

            if not signals:
                logger.info(f"No signals for {symbol} to send")
                return False

            subject = f"📈 {symbol} Alerts - {len(signals)} signals"
            body = self._format_symbol_alert(symbol, signals)

            return self._send_email(subject, body, recipient_emails, priority="normal")

        except Exception as e:
            logger.error(f"Error sending symbol alert: {e}")
            return False

    def _format_urgent_email(self, signal_data: dict) -> str:
        """긴급 알림 이메일 포맷"""
        symbols = ", ".join(signal_data.get('affected_symbols', []))
        impact = signal_data.get('price_impact', 'unknown').upper()
        importance = signal_data.get('importance', 'unknown').upper()

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .urgent {{ background-color: #ff4444; color: white; padding: 15px; border-radius: 5px; }}
                    .signal-title {{ font-size: 18px; font-weight: bold; margin: 15px 0; }}
                    .signal-info {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #ff4444; }}
                    .score {{ font-size: 24px; font-weight: bold; color: #ff4444; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="urgent">
                        <h1>🔴 URGENT SIGNAL ALERT</h1>
                        <p>Immediate action may be required</p>
                    </div>

                    <div class="signal-title">{signal_data.get('title', 'Unknown')}</div>

                    <div class="signal-info">
                        <strong>Affected Symbols:</strong> {symbols}
                    </div>

                    <div class="signal-info">
                        <strong>Relevance Score:</strong> <span class="score">{signal_data.get('relevance_score', 'N/A')}/100</span>
                    </div>

                    <div class="signal-info">
                        <strong>Price Impact:</strong> {impact}<br>
                        <strong>Importance:</strong> {importance}<br>
                        <strong>Signal Level:</strong> Level {signal_data.get('signal_level', '?')} (URGENT)
                    </div>

                    <div class="signal-info">
                        <strong>Analysis:</strong><br>
                        {signal_data.get('analysis', {}).get('reasoning', 'N/A')}
                    </div>

                    <div class="signal-info">
                        <strong>Key Points:</strong>
                        <ul>
                            {''.join([f'<li>{point}</li>' for point in signal_data.get('analysis', {}).get('key_points', [])])}
                        </ul>
                    </div>

                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Alert sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                        Investment Signal Dashboard | Real-time Monitoring
                    </p>
                </div>
            </body>
        </html>
        """
        return html

    def _format_daily_digest(self, summary: dict, hours: int) -> str:
        """일일 요약 이메일 포맷"""
        trending = summary.get('trending_symbols', [])[:5]
        trending_html = "".join([
            f"<li><strong>{s['symbol']}</strong> - {s['count']} signals, Score: {s['avg_score']:.1f}</li>"
            for s in trending
        ])

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: #1e40af; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
                    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; }}
                    .stat-box {{ background-color: #e0e7ff; padding: 15px; border-radius: 5px; text-align: center; }}
                    .stat-number {{ font-size: 24px; font-weight: bold; color: #1e40af; }}
                    .stat-label {{ color: #666; font-size: 12px; margin-top: 5px; }}
                    .trending {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 Daily Investment Signal Summary</h1>
                        <p>{datetime.now().strftime('%Y-%m-%d')}</p>
                    </div>

                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number" style="color: #ff4444;">{summary.get('urgent_count', 0)}</div>
                            <div class="stat-label">URGENT (Level 1)</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number" style="color: #ff8800;">{summary.get('high_count', 0)}</div>
                            <div class="stat-label">HIGH (Level 2)</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number" style="color: #ffbb00;">{summary.get('medium_count', 0)}</div>
                            <div class="stat-label">MEDIUM (Level 3)</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number" style="color: #00aa00;">{summary.get('low_count', 0)}</div>
                            <div class="stat-label">LOW (Level 4)</div>
                        </div>
                    </div>

                    <div class="section trending">
                        <h3>📈 Trending Symbols</h3>
                        <ul>
                            {trending_html or '<li>No signals in this period</li>'}
                        </ul>
                    </div>

                    <div class="section">
                        <h3>⚡ Latest Urgent Signals</h3>
                        <p><strong>{summary.get('latest_signals', [])}</strong></p>
                    </div>

                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        Summary period: Last {hours} hours<br>
                        Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                        <a href="http://localhost:5000/api/dashboard">View Full Dashboard</a>
                    </p>
                </div>
            </body>
        </html>
        """
        return html

    def _format_high_priority_email(self, signals: List[dict]) -> str:
        """높은 우선순위 시그널 이메일 포맷"""
        signals_html = "".join([
            f"""
            <tr>
                <td style="border-bottom: 1px solid #ddd; padding: 10px;">
                    <strong>{s.get('title', 'Unknown')[:60]}</strong><br>
                    <small>{', '.join(s.get('affected_symbols', []))}</small>
                </td>
                <td style="border-bottom: 1px solid #ddd; padding: 10px; text-align: center;">
                    <strong style="color: {'#ff4444' if s.get('signal_level') == 1 else '#ff8800'};">
                        {s.get('relevance_score', 'N/A')}/100
                    </strong>
                </td>
                <td style="border-bottom: 1px solid #ddd; padding: 10px; text-align: center;">
                    Level {s.get('signal_level', '?')}
                </td>
            </tr>
            """
            for s in signals[:20]
        ])

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 700px; margin: 0 auto; }}
                    .header {{ background-color: #ff8800; color: white; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th {{ background-color: #f5f5f5; padding: 10px; text-align: left; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🟠 High Priority Signals - {len(signals)} Alerts</h2>
                        <p>Level 1 (Urgent) and Level 2 (High) Signals</p>
                    </div>

                    <table>
                        <tr>
                            <th>Signal</th>
                            <th>Score</th>
                            <th>Level</th>
                        </tr>
                        {signals_html}
                    </table>

                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                        <a href="http://localhost:5000/api/signals/high-priority">View All Signals</a>
                    </p>
                </div>
            </body>
        </html>
        """
        return html

    def _format_symbol_alert(self, symbol: str, signals: List[dict]) -> str:
        """종목별 알림 이메일 포맷"""
        signals_html = "".join([
            f"""
            <div style="background-color: #f9f9f9; padding: 10px; margin: 10px 0; border-left: 3px solid #1e40af;">
                <strong>{s.get('title', 'Unknown')}</strong><br>
                <small>Score: {s.get('relevance_score', 'N/A')}/100 | Level {s.get('signal_level', '?')}</small>
            </div>
            """
            for s in signals[:10]
        ])

        html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; }}
                    .header {{ background-color: #1e40af; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                    .symbol {{ font-size: 32px; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="symbol">{symbol}</div>
                        <h2 style="margin: 10px 0 0 0;">Signal Alert - {len(signals)} Updates</h2>
                    </div>

                    {signals_html}

                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                        <a href="http://localhost:5000/api/signals/by-symbol/{symbol}">View Details</a>
                    </p>
                </div>
            </body>
        </html>
        """
        return html

    def _send_email(self, subject: str, body: str, recipient_emails: List[str],
                    priority: str = "normal") -> bool:
        """이메일 전송"""
        if not self.sender_password:
            logger.warning("Email service not configured (no sender password)")
            return False

        try:
            # 이메일 구성
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(recipient_emails)
            message["X-Priority"] = "1" if priority == "high" else "3"

            # HTML 본문 추가
            part = MIMEText(body, "html")
            message.attach(part)

            # 이메일 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_emails, message.as_string())

            logger.info(f"Email sent to {recipient_emails}: {subject[:50]}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def schedule_daily_digest(self, recipient_emails: List[str], hour: int = 9):
        """일일 요약 스케줄 설정 (job scheduler에서 사용)"""
        logger.info(f"Daily digest scheduled for {hour}:00 UTC to {recipient_emails}")
        # 실제 스케줄링은 scheduler/jobs.py에서 처리
