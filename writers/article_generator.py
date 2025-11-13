from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import sys
from pathlib import Path

sys.path.append('..')
from database.supabase_client import SupabaseClient
from database.models import PublishedArticle

class ArticleGenerator:
    """Claude Code를 사용한 블로그 글 생성 (프롬프트 방식)"""

    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
        self.prompts_dir = Path("prompts")
        self.prompts_dir.mkdir(exist_ok=True)
        logger.info("Article generator initialized with Claude Code mode")

    def generate_article(self, symbol: str, max_news: int = 5) -> Optional[str]:
        """특정 종목에 대한 블로그 글 작성 프롬프트 생성"""
        try:
            # 해당 종목 관련 미발행 뉴스 가져오기
            news_items = self.db.get_unpublished_news_by_symbol(symbol, limit=max_news)

            if not news_items:
                logger.info(f"No unpublished news found for {symbol}")
                return None

            logger.info(f"📝 Generating article prompt for {symbol} with {len(news_items)} news items")

            # 프롬프트 생성
            prompt = self._build_article_prompt(symbol, news_items)

            # 프롬프트 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_file = f"{self.prompts_dir}/article_{symbol}_{timestamp}.md"

            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)

            logger.info(f"✅ Article prompt saved: {prompt_file}")
            logger.info(f"   → Claude Code에서 프롬프트를 복사하여 글을 작성하고")
            logger.info(f"   → 완성된 글을 articles/ 폴더에 저장하세요")

            return None  # 수동 작성이므로 None 반환

        except Exception as e:
            logger.error(f"Error generating article prompt for {symbol}: {e}")

        return None

    def load_article_from_file(self, article_file: str, news_items: List[Dict]) -> Optional[str]:
        """Claude Code에서 작성한 글을 데이터베이스에 저장"""
        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 제목과 본문 분리
            article_data = self._parse_article_response(content)

            if not article_data:
                return None

            # 데이터베이스에 저장
            analyzed_news_ids = [news['id'] for news in news_items]
            published_article = PublishedArticle(
                title=article_data['title'],
                content=article_data['content'],
                analyzed_news_ids=analyzed_news_ids,
                published_at=datetime.now()
            )

            article_id = self.db.insert_published_article(published_article)

            if article_id:
                logger.info(f"✅ Article saved: {article_data['title']}")
                return article_id

        except Exception as e:
            logger.error(f"Error loading article: {e}")

        return None

    def _build_article_prompt(self, symbol: str, news_items: List[Dict]) -> str:
        """블로그 글 작성 프롬프트"""
        # 뉴스 요약 구성
        news_summaries = []
        for i, news in enumerate(news_items, 1):
            raw_news = news['news_raw']
            analysis = news['analysis']

            summary = f"""
뉴스 {i}:
- 제목: {raw_news['title']}
- 출처: {raw_news['source']}
- 발행일: {raw_news['published_at']}
- 내용: {raw_news['content'][:500]}
- 관련성 점수: {news['relevance_score']}/100
- 주가 영향: {news['price_impact']}
- 분석: {analysis.get('reasoning', '')}
- 핵심 포인트:
{chr(10).join([f"  * {point}" for point in analysis.get('key_points', [])])}
"""
            news_summaries.append(summary)

        news_context = "\n".join(news_summaries)

        return f"""당신은 미국 주식 시장 전문 블로거입니다. 한국어로 글을 작성하며, 투자자들에게 유용한 정보를 제공합니다.

종목: {symbol}

관련 뉴스:
{news_context}

다음 구조로 블로그 글을 작성해주세요:

---
제목: [종목명] 관련 최신 뉴스 분석 - [핵심 키워드 3-5개]

## 📊 무엇이 일어났는가

[3-5개 뉴스를 종합하여 핵심 사건 요약. 각 뉴스의 핵심만 간결하게.]

## 🔄 어떻게 작동하는가

[메커니즘 설명: 이 뉴스들이 비즈니스/산업에 어떤 영향을 주는지]
- 공급망 변화
- 시장 점유율 변화
- 규제 영향
- 경쟁사 관계
등을 고려

## 💡 왜 주가에 영향을 주는가

[논리적 연결고리 설명]
1. 재무적 영향: 매출/이익에 어떻게 영향?
2. 시장 심리: 투자자들이 어떻게 반응할지?
3. 장단기 전망: 단기/중기/장기적 관점

## 📈 투자 시사점

투자자 관점에서 고려사항:

**긍정적 요소**
- [구체적 긍정 요인 3가지]

**리스크 요소**
- [구체적 리스크 3가지]

**투자 전략 제안**
- [단기 투자자를 위한 관점]
- [장기 투자자를 위한 관점]

## 🔗 참고 자료

[원본 뉴스 출처 링크들을 정리]

---

**작성 가이드라인:**
1. 글자 수: 1,500-2,000자 (SEO 최적화)
2. 톤: 전문적이지만 이해하기 쉽게
3. 데이터: 구체적인 숫자와 팩트 중심
4. 객관성: 과장 없이 균형잡힌 시각
5. SEO: 종목명과 관련 키워드를 자연스럽게 포함
6. 투자 조언 아님: "투자 판단은 본인의 책임" 명시

제목과 본문을 다음 형식으로 구분해서 작성:

TITLE:
[제목]

CONTENT:
[본문 전체]
"""

    def _parse_article_response(self, response_text: str) -> Optional[Dict]:
        """Claude 응답에서 제목과 본문 분리"""
        try:
            # TITLE: 과 CONTENT: 로 구분
            title_start = response_text.find("TITLE:")
            content_start = response_text.find("CONTENT:")

            if title_start == -1 or content_start == -1:
                # 구분자가 없으면 첫 줄을 제목으로
                lines = response_text.strip().split('\n')
                title = lines[0].strip()
                content = '\n'.join(lines[1:]).strip()
            else:
                title = response_text[title_start + 6:content_start].strip()
                content = response_text[content_start + 8:].strip()

            # 제목에서 마크다운 제거
            title = title.replace('#', '').strip()

            return {
                'title': title,
                'content': content
            }

        except Exception as e:
            logger.error(f"Error parsing article response: {e}")
            return None

    def generate_daily_articles(self, tier: str = "tier_1", criteria_override: Dict = None) -> List[str]:
        """
        분석 기준점에 따라 여러 글 생성 프롬프트

        Args:
            tier: "tier_1" (높은 중요도 3개+), "tier_2" (뉴스 3개+ AND 점수 75+), "tier_3" (상위 15개)
            criteria_override: 기준점 사용자 정의 (선택사항)
        """
        article_ids = []

        try:
            from config.settings import (
                ARTICLE_TIER_1_SYMBOLS, ARTICLE_TIER_2_SYMBOLS,
                ARTICLE_TIER_1_MIN_HIGH_IMPORTANCE,
                ARTICLE_TIER_2_MIN_NEWS, ARTICLE_TIER_2_MIN_SCORE,
                ARTICLE_TIER_3_TOP_N
            )
            from analyzers.analysis_pipeline import AnalysisPipeline

            pipeline = AnalysisPipeline(self.db)

            # 기준점별 종목 선택
            if tier == "tier_1":
                logger.info(f"🎯 Generating articles for Tier 1 (High Importance >= {ARTICLE_TIER_1_MIN_HIGH_IMPORTANCE})")
                target_symbols = ARTICLE_TIER_1_SYMBOLS
                logger.info(f"   Target symbols ({len(target_symbols)}): {', '.join(target_symbols)}")

            elif tier == "tier_2":
                logger.info(f"🎯 Generating articles for Tier 2 (News >= {ARTICLE_TIER_2_MIN_NEWS} AND Score >= {ARTICLE_TIER_2_MIN_SCORE})")
                target_symbols = ARTICLE_TIER_1_SYMBOLS + ARTICLE_TIER_2_SYMBOLS
                logger.info(f"   Target symbols ({len(target_symbols)}): {', '.join(target_symbols)}")

            elif tier == "tier_3":
                logger.info(f"🎯 Generating articles for Tier 3 (Top {ARTICLE_TIER_3_TOP_N} symbols)")
                trending_symbols = pipeline.get_trending_symbols()
                target_symbols = list(trending_symbols.keys())[:ARTICLE_TIER_3_TOP_N]
                logger.info(f"   Target symbols ({len(target_symbols)}): {', '.join(target_symbols)}")

            else:
                raise ValueError(f"Invalid tier: {tier}")

            # 글 생성
            logger.info(f"\n📝 Starting article generation for {len(target_symbols)} symbols...")
            for i, symbol in enumerate(target_symbols, 1):
                try:
                    result = self.generate_article(symbol)
                    logger.info(f"   [{i}/{len(target_symbols)}] {symbol}: {'Generated' if result else 'No data'}")
                    if result:
                        article_ids.append(result)
                except Exception as e:
                    logger.error(f"   [{i}/{len(target_symbols)}] {symbol}: Error - {str(e)[:50]}")

            logger.info(f"\n✅ Article generation completed: {len(article_ids)} articles generated")
            logger.info(f"   Tier: {tier}")
            logger.info(f"   Target symbols: {len(target_symbols)}")
            logger.info(f"   Generated: {len(article_ids)}")

        except Exception as e:
            logger.error(f"Error in daily article generation: {e}")

        return article_ids

    def export_for_wordpress(self, article_id: str) -> Dict:
        """WordPress 발행용 데이터 포맷"""
        try:
            articles = self.db.get_recent_articles(days=1, limit=100)
            article = next((a for a in articles if a['id'] == article_id), None)

            if not article:
                return None

            # WordPress XML-RPC 포맷
            wordpress_data = {
                'title': article['title'],
                'content': article['content'],
                'post_status': 'publish',
                'post_type': 'post',
                'comment_status': 'open',
                'categories': ['Stock Analysis', 'US Market'],
                'tags': self._extract_tags(article),
                'custom_fields': [
                    {'key': 'article_id', 'value': article_id},
                    {'key': 'generated_at', 'value': article['created_at']}
                ]
            }

            return wordpress_data

        except Exception as e:
            logger.error(f"Error exporting for WordPress: {e}")
            return None

    def _extract_tags(self, article: Dict) -> List[str]:
        """글에서 태그 추출"""
        # analyzed_news_ids를 통해 관련 종목 추출
        # 간단히 제목에서 추출
        tags = ['Stock News', 'US Market', 'Investment']
        return tags
