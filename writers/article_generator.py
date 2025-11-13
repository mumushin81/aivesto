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
        """SEO 최적화 글 작성 프롬프트 (구글 & AI 검색 노출 최우선)"""
        # 뉴스 요약 구성 (상세 정보 포함)
        news_summaries = []
        for i, news in enumerate(news_items, 1):
            raw_news = news['news_raw']
            analysis = news['analysis']
            published_date = raw_news['published_at'].split('T')[0] if 'T' in raw_news['published_at'] else raw_news['published_at']

            summary = f"""
[뉴스 {i}]
제목: {raw_news['title']}
출처: {raw_news['source']}
발행일: {published_date}
내용: {raw_news['content'][:600]}

분석 결과:
- 관련성 점수: {news['relevance_score']}/100
- 주가 영향: {news['price_impact']}
- 중요도: {analysis.get('importance', 'medium')}
- 분석: {analysis.get('reasoning', '')}
- 핵심 포인트:
  {chr(10).join([f"• {point}" for point in analysis.get('key_points', [])])}
"""
            news_summaries.append(summary)

        news_context = "\n".join(news_summaries)

        return f"""당신은 미국 주식 시장 분석 전문가입니다.
다음 기준으로 구글 및 AI 검색 엔진(Claude, ChatGPT, Gemini)에 노출되기 좋은 글을 한국어로 작성해주세요.

📊 작성 대상: {symbol}

분석 대상 뉴스:
{news_context}

================================================================================
🎯 글 작성 가이드 (SEO 최적화)
================================================================================

## ✅ 필수 구성 (이 순서대로)

### 1️⃣ 제목 (60자 이내, 검색 클릭률 극대화)
- 규칙: 종목명 + 핵심 이슈 + 수치 또는 질문
- 약함: "{symbol} 최신 뉴스"
- 강함: "{symbol} 비즈니스 전환점 + 구체적 수치 (시간)"

### 2️⃣ 10초 판독 요약 (AI 검색 최우선, 필수)
다음 정확한 형식으로 작성:

## 📌 핵심 요약 (AI 검색 엔진용)

**상황**: 1줄 - 방금 있은 구체적 뉴스 이벤트
**영향**: 1-2줄 - 시장이나 실적에 미치는 영향 (수치 포함)
**투자자 관점**:
- 긍정: [구체적 이유 1-2개]
- 위험: [구체적 이유 1-2개]
- 시사점: [구체적 액션]

### 3️⃣ 📊 무엇이 일어났는가 (뉴스)
- 명확한 헤드라인 (한 문장)
- 언제: 정확한 날짜 명시
- 누가: 회사명, 경영진
- 뭐: 구체적 액션과 수치
- 출처: 공식 발표, 링크 명시

### 4️⃣ 🔧 어떻게 작동하는가 (비즈니스 로직)
- 이 뉴스가 비즈니스에 미치는 메커니즘 설명
- 업계 배경지식 (신규 독자 고려)
- 경쟁 구도 변화 (비교 포함)
- 시장 트렌드와의 연결

### 5️⃣ 💰 왜 주가에 영향을 주는가 (투자 로직)
1. 재무 임팩트
   - 수익성 개선: [구체적 메커니즘]
   - 성장성: [구체적 데이터]
   - 실제 수치: [정확한 숫자]

2. 투자자 심리
   - 시장 선호도: [기관투자자 움직임]
   - 분석가 평가: [전문가 의견]
   - 밸류에이션: [P/E, PEG 등]

3. 단기 vs 장기 전망
   - 3-6개월: [신호]
   - 6-12개월: [기대]
   - 1-3년: [장기 추세]

### 6️⃣ 📈 수치로 보는 분석 (표 형식)
마크다운 표를 사용하여 비교 정보 제시:
- {symbol} vs 경쟁사 비교
- 실적 추이 (3년)
- 위험 요소 평가

### 7️⃣ 🏢 경쟁사 비교 (차별성)
- vs 주요 경쟁사: [강점 및 약점]
- 시장 위치: [{symbol}의 차별성]
- 결론: [객관적 평가]

### 8️⃣ ❓ 자주 묻는 질문 (FAQ - 반드시 포함)
Q&A 형식으로 5-7개 질문에 답변:
- Q: "{symbol}을 지금 사야 하나?"
- Q: "{symbol} vs 경쟁사 비교"
- Q: "이 산업은 정말 성장할까?"
- Q: "{symbol}의 위험은?"
- Q: "주가 전망은?"

각 답변은 150-300자, 명확하고 근거 있게.

### 9️⃣ 📰 전문가 의견 및 출처 (신뢰도)
- 주요 분석가 등급 (Goldman Sachs, Morgan Stanley 등)
- 목표가 및 근거
- 공식 공시 및 투자자 문서 링크
- 신뢰할 수 있는 정보원

### 🔟 ⚡ 단계별 전망 분석
단기(3-6개월), 중기(6-12개월), 장기(1-3년)별로:
- 강세/중립/약세 시나리오
- 각 시나리오의 확률
- 트리거와 목표가
- 최악의 경우까지 고려

### 1️⃣1️⃣ 🔐 결론 및 투자 고려사항
- ✅ 좋은 이유 (체크리스트)
- ⚠️ 위험 요소 (체크리스트)
- 📋 투자 결정 가이드 (투자자별)
- ⚖️ 법적 고지 (투자 조언 아님 명시)

================================================================================
🔑 SEO 키워드 배치 규칙
================================================================================

1차 키워드 (종목명): 제목 1회, 첫 100자 1회, 본문 1회 이상
2차 키워드 (주제): 자연스럽게 3-5회 분산 배치
3차 키워드 (Long-tail): "~하는 이유", "~전망", "vs 비교" 포함
4차 키워드 (의도): "매수 기회", "투자 시점", "위험 요소" 자연스럽게 포함

규칙: 키워드를 강제로 반복하지 말고, 문맥에 자연스럽게 녹이기

================================================================================
✍️ 작성 스타일
================================================================================

- 글자 수: 2,500-3,500자 (기존 1,500-2,000에서 증가 - 깊이 추가)
- 톤: 전문적이지만 이해하기 쉽게 (학술적 언어 제거)
- 단락: 200자 이내 (AI가 파싱하기 쉽게)
- 구조: H2(##), H3(###)로 계층화
- 리스트: 불릿(•) 또는 숫자로 명확화
- 표: 데이터 비교는 마크다운 표 사용
- 링크: 모든 출처에 명확한 링크 포함
- 수치: 추정치(~)가 아닌 정확한 숫자 사용
- 면책: "투자 조언이 아닙니다" 반드시 포함

================================================================================
📋 최종 형식
================================================================================

TITLE:
[클릭 유도적인 제목 60자 이내]

CONTENT:
[전체 본문 - 위의 필수 구성 1-11 포함, 마크다운 형식]

================================================================================
⚠️ 금지 사항
================================================================================

❌ 하지 말 것:
- "~에 투자하세요", "지금 사세요" 같은 직접적 권고
- 과장된 수치 ("확실히 2배 올라갈", "무조건 성공")
- 출처 없는 주장
- 너무 긴 단락 (200자 초과)
- 단조로운 문장 (표, 리스트, 강조로 시각화)
- 정치, 종교, 윤리 논쟁 (투자 글에만 집중)

================================================================================

지금 시작하세요. 글을 작성한 후 위의 형식 (TITLE: / CONTENT:)로 결과를 제시해주세요.

참고: 이 글은 구글, Claude, ChatGPT, Gemini 등 모든 검색 엔진에서 최상위에
노출되도록 설계되었습니다. 각 부분의 역할을 이해하고 신중하게 작성해주세요.
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
