"""
투자 시그널 대시보드 API
Investment Signal Dashboard API
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger

sys.path.append('..')
from database.supabase_client import SupabaseClient


class SignalAPI:
    """투자 시그널 API"""

    def __init__(self):
        try:
            self.db = SupabaseClient()
        except Exception as e:
            logger.warning(f"Supabase client initialization failed: {e}. Article features will still work.")
            self.db = None

        self.articles_dir = os.path.join(os.path.dirname(__file__), '..', 'articles')
        logger.info("Signal API initialized")

    def _extract_article_metadata(self, content: str) -> Dict:
        """기사 내용에서 메타데이터 추출"""
        metadata = {
            'title': '',
            'summary': '',
            'symbol': '',
            'timestamp': datetime.now().isoformat()
        }

        # TITLE 추출
        title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', content)
        if title_match:
            metadata['title'] = title_match.group(1).strip()

        # 핵심 요약 추출
        summary_match = re.search(r'## 📌 핵심 요약\s*\n\n(.*?)\n\n---', content, re.DOTALL)
        if summary_match:
            summary_text = summary_match.group(1)
            # 첫 300자만 추출
            metadata['summary'] = summary_text.replace('\n', ' ')[:300]

        # 심볼 추출 (파일명에서)
        return metadata

    def _get_article_score(self, filename: str) -> Dict:
        """validation_report.json에서 기사 점수 조회"""
        try:
            report_path = os.path.join(os.path.dirname(__file__), '..', 'validation_report.json')
            if os.path.exists(report_path):
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    for result in report.get('results', []):
                        if result.get('file') == filename:
                            return {
                                'score': result.get('score', 0),
                                'completion_rate': result.get('completion_rate', '0%'),
                                'sections_passed': result.get('sections_passed', 0),
                                'total_sections': result.get('total_sections', 0)
                            }
        except Exception as e:
            logger.error(f"Error reading validation report: {e}")

        return {'score': 0, 'completion_rate': '0%', 'sections_passed': 0, 'total_sections': 0}

    def get_signals_by_level(
        self,
        level: int,
        hours: int = 24,
        limit: int = 50
    ) -> List[Dict]:
        """레벨별 시그널 조회

        Args:
            level: 신호 레벨 (1-4)
            hours: 최근 N시간 데이터
            limit: 최대 개수

        Returns:
            신호 리스트
        """
        try:
            if self.db is None:
                logger.warning("Supabase client not available")
                return []

            # Supabase 쿼리로 데이터 조회
            # 실제 구현은 database 연결에 따라 수정 필요
            signals = self.db.get_signals_by_level(level, hours=hours, limit=limit)
            logger.info(f"Fetched {len(signals)} Level {level} signals")
            return signals

        except Exception as e:
            logger.error(f"Error fetching signals by level: {e}")
            return []

    def get_urgent_signals(self, hours: int = 24, limit: int = 20) -> List[Dict]:
        """긴급 시그널 (Level 1) 조회"""
        return self.get_signals_by_level(1, hours=hours, limit=limit)

    def get_high_priority_signals(self, hours: int = 24, limit: int = 30) -> List[Dict]:
        """높은 우선순위 시그널 (Level 1-2) 조회"""
        signals = []
        signals.extend(self.get_signals_by_level(1, hours=hours, limit=limit))
        signals.extend(self.get_signals_by_level(2, hours=hours, limit=limit))
        return signals

    def get_signals_by_symbol(
        self,
        symbol: str,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict]:
        """종목별 시그널 조회"""
        try:
            if self.db is None:
                return []
            signals = self.db.get_signals_by_symbol(symbol, hours=hours, limit=limit)
            logger.info(f"Fetched {len(signals)} signals for {symbol}")
            return signals

        except Exception as e:
            logger.error(f"Error fetching signals for {symbol}: {e}")
            return []

    def get_trending_symbols(self, hours: int = 24, limit: int = 15) -> List[Dict]:
        """트렌딩 종목 조회 (가장 많은 시그널 나온 종목)"""
        try:
            if self.db is None:
                return []
            symbols = self.db.get_trending_symbols(hours=hours, limit=limit)
            logger.info(f"Fetched {len(symbols)} trending symbols")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching trending symbols: {e}")
            return []

    def get_dashboard_summary(self, hours: int = 24) -> Dict:
        """대시보드 요약 정보"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "period_hours": hours,
                "urgent_count": len(self.get_signals_by_level(1, hours=hours)),
                "high_count": len(self.get_signals_by_level(2, hours=hours)),
                "medium_count": len(self.get_signals_by_level(3, hours=hours)),
                "low_count": len(self.get_signals_by_level(4, hours=hours)),
                "trending_symbols": self.get_trending_symbols(hours=hours, limit=10),
                "latest_signals": self.get_signals_by_level(1, hours=hours, limit=5)
            }

        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return {"timestamp": datetime.now().isoformat(), "period_hours": hours, "urgent_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0, "trending_symbols": [], "latest_signals": []}

    def get_price_impact_summary(self, hours: int = 24) -> Dict:
        """가격 영향 요약"""
        try:
            if self.db is None:
                return {"up": 0, "down": 0, "neutral": 0}
            # 양수/음수/중립 시그널 비율 계산
            return self.db.get_price_impact_summary(hours=hours)

        except Exception as e:
            logger.error(f"Error getting price impact summary: {e}")
            return {"up": 0, "down": 0, "neutral": 0}

    def get_important_symbols_today(self) -> List[Dict]:
        """오늘 주목할 종목"""
        try:
            if self.db is None:
                return []
            return self.db.get_important_symbols_today()

        except Exception as e:
            logger.error(f"Error getting important symbols: {e}")
            return []

    def mark_signal_as_processed(self, signal_id: str) -> bool:
        """시그널을 처리됨으로 표시"""
        try:
            if self.db is None:
                return False
            # 이 기능은 블로거 큐에서 선택한 시그널을 표시
            return self.db.mark_signal_as_processed(signal_id)

        except Exception as e:
            logger.error(f"Error marking signal as processed: {e}")
            return False

    def get_signals_for_article(
        self,
        tier: str = "tier_1",
        hours: int = 24
    ) -> List[Dict]:
        """글 작성용 시그널 조회"""
        try:
            if self.db is None:
                return []

            if tier == "tier_1":
                # 긴급 + 높음 시그널만
                signals = self.get_signals_by_level(1, hours=hours, limit=30)
                signals.extend(self.get_signals_by_level(2, hours=hours, limit=20))
            elif tier == "tier_2":
                # 높음 + 중간 시그널
                signals = self.get_signals_by_level(2, hours=hours, limit=30)
                signals.extend(self.get_signals_by_level(3, hours=hours, limit=20))
            else:  # tier_3
                # 모든 시그널
                signals = []
                for level in [1, 2, 3, 4]:
                    signals.extend(self.get_signals_by_level(level, hours=hours*7, limit=50))

            return signals

        except Exception as e:
            logger.error(f"Error getting signals for article: {e}")
            return []

    def get_all_articles(self) -> List[Dict]:
        """생성된 모든 기사 조회"""
        articles = []

        if not os.path.exists(self.articles_dir):
            logger.warning(f"Articles directory not found: {self.articles_dir}")
            return articles

        try:
            article_files = sorted(Path(self.articles_dir).glob('article_*.md'))

            for article_file in article_files:
                try:
                    with open(article_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 메타데이터 추출
                    metadata = self._extract_article_metadata(content)

                    # 점수 조회
                    score_info = self._get_article_score(article_file.name)

                    # 파일명에서 심볼 추출
                    symbol_match = re.search(r'article_([A-Z]+)_', article_file.name)
                    symbol = symbol_match.group(1) if symbol_match else 'UNKNOWN'

                    article = {
                        'filename': article_file.name,
                        'symbol': symbol,
                        'title': metadata['title'],
                        'summary': metadata['summary'],
                        'score': score_info['score'],
                        'completion_rate': score_info['completion_rate'],
                        'sections_passed': score_info['sections_passed'],
                        'total_sections': score_info['total_sections'],
                        'created_date': datetime.fromtimestamp(article_file.stat().st_mtime).isoformat(),
                        'content_length': len(content),
                        'word_count': len(content.split())
                    }

                    articles.append(article)

                except Exception as e:
                    logger.error(f"Error processing article {article_file.name}: {e}")

            logger.info(f"Loaded {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Error loading articles: {e}")
            return articles

    def get_article_by_symbol(self, symbol: str) -> Optional[Dict]:
        """심볼별 기사 조회"""
        try:
            articles = self.get_all_articles()
            for article in articles:
                if article['symbol'].upper() == symbol.upper():
                    # 전체 내용 로드
                    article_path = os.path.join(self.articles_dir, article['filename'])
                    with open(article_path, 'r', encoding='utf-8') as f:
                        article['full_content'] = f.read()
                    return article

            return None

        except Exception as e:
            logger.error(f"Error getting article for {symbol}: {e}")
            return None

    def get_articles_stats(self) -> Dict:
        """기사 통계"""
        try:
            articles = self.get_all_articles()

            if not articles:
                return {
                    'total': 0,
                    'average_score': 0,
                    'high_quality': 0,
                    'symbols': []
                }

            scores = [a['score'] for a in articles]
            average_score = sum(scores) / len(scores) if scores else 0
            high_quality = len([a for a in articles if a['score'] >= 90])

            symbols = sorted(set([a['symbol'] for a in articles]))

            return {
                'total': len(articles),
                'average_score': round(average_score, 1),
                'high_quality': high_quality,
                'symbols': symbols,
                'total_words': sum([a['word_count'] for a in articles])
            }

        except Exception as e:
            logger.error(f"Error calculating article stats: {e}")
            return {'total': 0, 'average_score': 0, 'high_quality': 0, 'symbols': []}
