#!/usr/bin/env python3
"""
AI·오픈소스·테크 트렌드 뉴스 수집기

수집 대상:
- AI 반도체 기술 발표
- 기업 AI 서비스 추가/확장
- 서버 GPU 수요 증가 보고
- 오픈소스 모델 발표
- 빅테크 협력/파트너십

데이터 소스:
- TechCrunch RSS
- The Verge RSS
- Reuters Tech
- Bloomberg Tech
- NVIDIA, OpenAI, Anthropic 공식 블로그
"""

import os
import requests
import feedparser
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client
from typing import List, Dict, Any

load_dotenv()


class TechTrendsCollector:
    """AI/테크 트렌드 뉴스 수집기"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # RSS 피드 URL
        self.rss_feeds = {
            "TechCrunch": "https://techcrunch.com/feed/",
            "TheVerge": "https://www.theverge.com/rss/index.xml",
            "Reuters_Tech": "https://www.reutersagency.com/feed/?taxonomy=best-topics&post_type=best",
            "Ars_Technica": "https://feeds.arstechnica.com/arstechnica/index"
        }

        # AI/테크 관련 키워드
        self.ai_keywords = [
            "AI", "artificial intelligence", "GPU", "NVIDIA", "AMD",
            "ChatGPT", "OpenAI", "Anthropic", "Claude", "Gemini",
            "machine learning", "deep learning", "LLM", "transformer",
            "semiconductor", "chip", "server", "cloud computing",
            "partnership", "collaboration", "acquisition", "M&A"
        ]

        # 관련 종목
        self.tech_stocks = {
            "AI_CHIP": ["NVDA", "AMD", "INTC"],
            "AI_SOFTWARE": ["MSFT", "GOOGL", "META"],
            "CLOUD": ["MSFT", "AMZN", "GOOGL"]
        }

    def collect_rss_news(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """RSS 피드에서 뉴스 수집"""
        logger.info(f"📊 {source_name} RSS 수집 중...")

        try:
            feed = feedparser.parse(feed_url)

            news_items = []
            for entry in feed.entries[:20]:  # 최근 20개
                # AI/테크 관련 키워드 필터링
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()

                is_relevant = any(keyword.lower() in title or keyword.lower() in summary
                                for keyword in self.ai_keywords)

                if is_relevant:
                    news_items.append({
                        "source": source_name,
                        "title": entry.get('title', ''),
                        "link": entry.get('link', ''),
                        "published": entry.get('published', ''),
                        "summary": entry.get('summary', '')[:500]
                    })

            logger.success(f"  ✅ {source_name}: AI/테크 뉴스 {len(news_items)}개 수집")
            return news_items

        except Exception as e:
            logger.error(f"  ❌ {source_name} RSS 수집 실패: {e}")
            return []

    def collect_nvidia_blog(self) -> List[Dict[str, Any]]:
        """
        NVIDIA 공식 블로그에서 기술 발표 수집
        Source: NVIDIA Blog RSS or API
        """
        logger.info("📊 NVIDIA 블로그 수집 중...")

        try:
            # NVIDIA Developer Blog RSS
            nvidia_rss = "https://blogs.nvidia.com/feed/"
            feed = feedparser.parse(nvidia_rss)

            nvidia_news = []
            for entry in feed.entries[:10]:
                nvidia_news.append({
                    "source": "NVIDIA Blog",
                    "title": entry.get('title', ''),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "category": "AI_CHIP"
                })

            logger.success(f"  ✅ NVIDIA 블로그: {len(nvidia_news)}개 수집")
            return nvidia_news

        except Exception as e:
            logger.error(f"  ❌ NVIDIA 블로그 수집 실패: {e}")
            return []

    def analyze_tech_trend_signal(self, news: Dict[str, Any]) -> Dict[str, Any]:
        """
        테크 트렌드 뉴스에서 시그널 분석

        시그널 포인트:
        - "GPU shortage" → NVDA 강세
        - "Microsoft AI monetization" → MSFT 상승
        - "China semiconductor ban" → 미국 AI 칩 강세
        """

        title = news.get("title", "").lower()
        summary = news.get("summary", "").lower()
        full_text = f"{title} {summary}"

        # 뉴스 원본 데이터 포함
        signal = {
            "source": news.get("source"),
            "title": news.get("title"),
            "summary": news.get("summary", ""),  # 요약 추가
            "link": news.get("link", ""),  # 링크 추가
            "signal": None,
            "affected_stocks": [],
            "impact_score": 0,
            "trend_type": "GENERAL"  # 기본값
        }

        # GPU 공급 부족 시그널
        if "gpu shortage" in full_text or "gpu supply" in full_text:
            signal["signal"] = "NVDA_STRONG_BUY"
            signal["affected_stocks"] = ["NVDA"]
            signal["impact_score"] = 85
            signal["trend_type"] = "AI_CHIP"

        # Microsoft AI 시그널
        elif "microsoft" in full_text and ("ai" in full_text or "copilot" in full_text):
            signal["signal"] = "MSFT_AI_EXPANSION"
            signal["affected_stocks"] = ["MSFT"]
            signal["impact_score"] = 75
            signal["trend_type"] = "AI_SOFTWARE"

        # 중국 반도체 제재
        elif "china" in full_text and ("semiconductor" in full_text or "chip ban" in full_text):
            signal["signal"] = "US_AI_CHIP_RALLY"
            signal["affected_stocks"] = ["NVDA", "AMD", "INTC"]
            signal["impact_score"] = 80

        # OpenAI/Claude 신모델 발표
        elif "gpt-5" in full_text or "claude" in full_text or "gemini" in full_text:
            signal["signal"] = "NEW_AI_MODEL_RELEASE"
            signal["affected_stocks"] = ["MSFT", "GOOGL", "NVDA"]
            signal["impact_score"] = 70

        # 빅테크 파트너십
        elif ("partnership" in full_text or "collaboration" in full_text) and \
             any(company in full_text for company in ["microsoft", "google", "amazon", "nvidia"]):
            signal["signal"] = "BIGTECH_PARTNERSHIP"
            signal["affected_stocks"] = self.extract_companies(full_text)
            signal["impact_score"] = 65

        return signal

    def extract_companies(self, text: str) -> List[str]:
        """텍스트에서 회사명 추출"""
        companies = []
        company_map = {
            "nvidia": "NVDA",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "amazon": "AMZN",
            "meta": "META",
            "apple": "AAPL",
            "amd": "AMD",
            "intel": "INTC"
        }

        for company_name, ticker in company_map.items():
            if company_name in text.lower():
                companies.append(ticker)

        return companies

    def save_to_database(self, data: List[Dict[str, Any]]):
        """수집한 데이터를 Supabase에 저장"""

        logger.info("💾 Supabase에 저장 중...")

        for item in data:
            try:
                # 뉴스 원본 데이터 포함하여 저장
                # summary는 title과 합쳐서 저장 (스키마에 summary 필드 없음)
                result = self.supabase.table('tech_trends').insert({
                    "trend_type": item.get("trend_type", "GENERAL"),
                    "title": item.get("title", "") + (f" - {item.get('summary', '')[:200]}" if item.get('summary') else ""),  # 제목 + 요약
                    "source": item.get("source", ""),  # 뉴스 출처
                    "source_url": item.get("link", ""),  # 뉴스 링크 (link → source_url)
                    "companies": item.get("affected_stocks", []),
                    "signal": item.get("signal", ""),
                    "impact_score": item.get("impact_score", 0)
                }).execute()

                logger.success(f"  ✅ 저장 완료: {item.get('title', 'No title')[:50]}")

            except Exception as e:
                logger.error(f"  ❌ 저장 실패: {e}")

    def run(self):
        """테크 트렌드 수집 실행"""

        logger.info("=" * 60)
        logger.info("🚀 AI/테크 트렌드 뉴스 수집 시작")
        logger.info("=" * 60)

        all_news = []

        # 1. RSS 피드 수집
        for source_name, feed_url in self.rss_feeds.items():
            news = self.collect_rss_news(feed_url, source_name)
            all_news.extend(news)

        # 2. NVIDIA 블로그
        nvidia_news = self.collect_nvidia_blog()
        all_news.extend(nvidia_news)

        # 3. 시그널 분석
        signals = []
        for news in all_news:
            signal = self.analyze_tech_trend_signal(news)
            if signal.get("signal"):
                signals.append(signal)
                logger.info(f"  📈 시그널: {signal['signal']} - {', '.join(signal['affected_stocks'])}")

        # 4. 데이터베이스 저장
        if signals:
            self.save_to_database(signals)

        logger.info("\n" + "=" * 60)
        logger.success(f"✅ AI/테크 뉴스 수집: {len(all_news)}개")
        logger.success(f"✅ 시그널 발견: {len(signals)}개")
        logger.info("=" * 60)

        return {
            "news": all_news,
            "signals": signals
        }


def main():
    """메인 함수"""
    collector = TechTrendsCollector()
    result = collector.run()


if __name__ == "__main__":
    main()
