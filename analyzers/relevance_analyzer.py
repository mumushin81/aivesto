from typing import Dict, List, Tuple
import json
from loguru import logger
import sys
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

sys.path.append('..')
from config.settings import MIN_RELEVANCE_SCORE, ANTHROPIC_API_KEY
from database.models import AnalyzedNews, PriceImpact, Importance

try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False
    logger.warning("Anthropic API not available - falling back to prompt generation mode")

class RelevanceAnalyzer:
    """자동 뉴스 분석 및 투자 시그널 분류 시스템"""

    def __init__(self):
        self.prompts_dir = Path("prompts")
        self.prompts_dir.mkdir(exist_ok=True)

        # Claude API 초기화
        if CLAUDE_AVAILABLE and ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            self.auto_analyze = True
            logger.info("Relevance analyzer initialized with Claude API (automatic mode)")
        else:
            self.client = None
            self.auto_analyze = False
            logger.info("Relevance analyzer initialized with prompt generation mode (manual analysis)")

    def analyze_news(self, news_data: Dict) -> Dict:
        """뉴스 분석 프롬프트 생성 (수동 분석용)"""
        try:
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            existing_symbols = news_data.get('symbols', [])
            news_id = news_data.get('id', 'unknown')

            # 프롬프트 생성
            prompt = self._build_analysis_prompt(title, content, existing_symbols)

            # 프롬프트 파일 저장
            prompt_file = self._save_prompt(news_id, prompt)
            logger.info(f"📝 분석 프롬프트 생성: {prompt_file}")
            logger.info(f"   뉴스: {title[:60]}")
            logger.info(f"   → Claude Code에서 다음을 실행하세요:")
            logger.info(f"   cat {prompt_file}")

            return None  # 수동 분석이므로 None 반환

        except Exception as e:
            logger.error(f"Error generating analysis prompt: {e}")
            return None

    def load_manual_analysis(self, json_response: str) -> Dict:
        """Claude Code에서 수동으로 분석한 JSON 결과 로드"""
        try:
            result = self._parse_response(json_response)
            return result
        except Exception as e:
            logger.error(f"Error loading manual analysis: {e}")
            return None

    def _save_prompt(self, news_id: str, prompt: str) -> str:
        """프롬프트를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.prompts_dir}/analysis_{news_id}_{timestamp}.md"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)

        return filename

    def _build_analysis_prompt(self, title: str, content: str, existing_symbols: List[str]) -> str:
        """Claude에게 보낼 프롬프트 구성"""
        return f"""당신은 미국 주식 시장 전문 애널리스트입니다. 다음 뉴스를 분석하여 주식 투자자에게 얼마나 유용한지 평가해주세요.

뉴스 제목: {title}

뉴스 내용:
{content[:2000]}

기존 추출된 심볼: {', '.join(existing_symbols) if existing_symbols else '없음'}

다음 항목을 JSON 형식으로 분석해주세요:

1. relevance_score (0-100): 주식 투자자에게 얼마나 관련성이 높은지
   - 0-30: 무관한 뉴스 (일반 뉴스, 정치, 스포츠 등)
   - 31-60: 간접 관련 (경제 일반, 업계 트렌드)
   - 61-80: 직접 관련 (특정 기업/섹터 뉴스)
   - 81-100: 매우 중요 (실적, M&A, 규제 변화, 중대 사건)

2. affected_symbols: 영향을 받는 주식 심볼 리스트 (최대 5개)
   - 기존 심볼 검증 및 추가 심볼 발견
   - 직접 언급된 기업만 포함

3. price_impact: 주가 영향 예측
   - "up": 긍정적 영향 (매출 증가, 신제품, 호실적)
   - "down": 부정적 영향 (손실, 소송, 규제)
   - "neutral": 중립 또는 혼재

4. importance: 중요도
   - "high": 즉각적 주가 영향 예상
   - "medium": 중기적 영향
   - "low": 장기적/간접적 영향

5. reasoning: 분석 근거 (2-3문장)
   - 왜 이 점수인지
   - 주가에 어떤 영향을 줄지
   - 핵심 팩트

6. key_points: 핵심 포인트 (3-5개 bullet points)
   - 투자자가 알아야 할 핵심 정보

응답 형식 (JSON만 반환):
{{
  "relevance_score": 85,
  "affected_symbols": ["AAPL", "MSFT"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "...",
  "key_points": ["...", "...", "..."]
}}"""

    def _parse_response(self, response_text: str) -> Dict:
        """Claude Code 응답 파싱"""
        try:
            # JSON 추출 시도
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                # 유효성 검증
                required_fields = ['relevance_score', 'affected_symbols', 'price_impact', 'importance']
                if not all(field in data for field in required_fields):
                    logger.error("Missing required fields in response")
                    return None

                # 관련성 점수가 임계값 이하면 필터링
                if int(data['relevance_score']) < MIN_RELEVANCE_SCORE:
                    logger.info(f"Filtered out (score: {data['relevance_score']})")
                    return None

                # 타입 변환
                result = {
                    'relevance_score': int(data['relevance_score']),
                    'affected_symbols': data['affected_symbols'],
                    'price_impact': PriceImpact(data['price_impact']),
                    'importance': Importance(data['importance']),
                    'reasoning': data.get('reasoning', ''),
                    'key_points': data.get('key_points', [])
                }

                logger.info(f"✅ Analysis loaded: score {result['relevance_score']}")
                return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
        except Exception as e:
            logger.error(f"Response parsing error: {e}")

        return None

    def batch_analyze(self, news_list: List[Dict], batch_size: int = 10, max_workers: int = 5) -> List[Dict]:
        """여러 뉴스 자동 분석 (Claude API 활용)"""
        if not self.auto_analyze:
            logger.info(f"📝 Generating analysis prompts for {len(news_list)} news items (manual mode)...")
            for news in news_list:
                self.analyze_news(news)
            logger.info(f"✅ All prompts generated in prompts/ directory")
            return []

        logger.info(f"🤖 Starting automated analysis for {len(news_list)} news items...")
        results = []

        try:
            # 병렬 처리를 위한 ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_news = {
                    executor.submit(self._analyze_single_news_auto, news): news
                    for news in news_list
                }

                completed = 0
                for future in as_completed(future_to_news):
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                            completed += 1
                    except Exception as e:
                        logger.error(f"Error analyzing news: {e}")

                logger.info(f"✅ Automated analysis completed: {completed}/{len(news_list)} items analyzed")

        except Exception as e:
            logger.error(f"Batch analysis error: {e}")

        return results

    def _analyze_single_news_auto(self, news_data: Dict) -> Dict:
        """개별 뉴스 자동 분석"""
        try:
            title = news_data.get('title', '')
            content = news_data.get('content', '')
            existing_symbols = news_data.get('symbols', [])
            news_id = news_data.get('id', 'unknown')

            prompt = self._build_analysis_prompt(title, content, existing_symbols)

            # Claude API로 분석
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # 분석 결과 파싱
            result = self._parse_response(response_text)
            if result:
                result['news_id'] = news_id
                # 신호 레벨 계산
                result['signal_level'] = self._calculate_signal_level(result)
                return result

            return None

        except Exception as e:
            logger.error(f"Error analyzing news {news_data.get('id')}: {e}")
            return None

    def _calculate_signal_level(self, analysis_result: Dict) -> int:
        """투자 시그널 레벨 계산 (1-4)
        Level 1: 매우 중요 (90+점) - 즉시 실행
        Level 2: 높음 (80-89점) - 고려 필요
        Level 3: 중간 (70-79점) - 모니터링
        Level 4: 낮음 (70점 미만) - 참고용
        """
        score = analysis_result.get('relevance_score', 0)
        importance = analysis_result.get('importance', 'low')

        # 중요도와 점수 조합으로 레벨 결정
        if score >= 90 or (score >= 85 and importance == 'high'):
            return 1
        elif score >= 80 or (score >= 75 and importance == 'high'):
            return 2
        elif score >= 70:
            return 3
        else:
            return 4
