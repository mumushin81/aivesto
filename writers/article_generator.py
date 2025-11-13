import anthropic
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger
import sys

sys.path.append('..')
from config.settings import ANTHROPIC_API_KEY
from database.supabase_client import SupabaseClient
from database.models import PublishedArticle

class ArticleGenerator:
    """Claude AI를 사용한 블로그 글 자동 생성"""

    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-3-5-sonnet-20241022"
        logger.info("Article generator initialized")

    def generate_article(self, symbol: str, max_news: int = 5) -> Optional[str]:
        """특정 종목에 대한 블로그 글 생성"""
        try:
            # 해당 종목 관련 미발행 뉴스 가져오기
            news_items = self.db.get_unpublished_news_by_symbol(symbol, limit=max_news)

            if not news_items:
                logger.info(f"No unpublished news found for {symbol}")
                return None

            logger.info(f"Generating article for {symbol} with {len(news_items)} news items")

            # Claude에게 글 작성 요청
            article_data = self._create_article_with_claude(symbol, news_items)

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
                logger.info(f"Article generated and saved: {article_data['title']}")
                return article_id

        except Exception as e:
            logger.error(f"Error generating article for {symbol}: {e}")

        return None

    def _create_article_with_claude(self, symbol: str, news_items: List[Dict]) -> Optional[Dict]:
        """Claude를 사용하여 블로그 글 작성"""
        try:
            prompt = self._build_article_prompt(symbol, news_items)

            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text

            # 제목과 본문 분리
            article_data = self._parse_article_response(response_text)
            return article_data

        except Exception as e:
            logger.error(f"Claude article generation error: {e}")
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

    def generate_daily_articles(self, top_n_symbols: int = 5) -> List[str]:
        """일일 인기 종목 기준으로 여러 글 생성"""
        article_ids = []

        try:
            # 최근 트렌딩 종목 가져오기
            from analyzers.analysis_pipeline import AnalysisPipeline
            pipeline = AnalysisPipeline(self.db)
            trending_symbols = pipeline.get_trending_symbols()

            # 상위 N개 종목
            top_symbols = list(trending_symbols.keys())[:top_n_symbols]

            logger.info(f"Generating articles for top {len(top_symbols)} symbols: {top_symbols}")

            for symbol in top_symbols:
                article_id = self.generate_article(symbol)
                if article_id:
                    article_ids.append(article_id)

            logger.info(f"Daily article generation completed: {len(article_ids)} articles created")

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
