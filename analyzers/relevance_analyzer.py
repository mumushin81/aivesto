from typing import Dict, List, Tuple
import json
from loguru import logger
import sys
from datetime import datetime
from pathlib import Path

sys.path.append('..')
from config.settings import MIN_RELEVANCE_SCORE
from database.models import AnalyzedNews, PriceImpact, Importance

class RelevanceAnalyzer:
    """뉴스 관련성 분석 (프롬프트 기반 - Claude Code 사용)"""

    def __init__(self):
        self.prompts_dir = Path("prompts/analysis")
        self.results_dir = Path("prompts/results")
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Relevance analyzer initialized (Prompt-based mode - Claude Code)")

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

    def batch_analyze(self, news_list: List[Dict], batch_size: int = 5) -> List[Dict]:
        """📝 뉴스 분석 프롬프트 일괄 생성 (Claude Code가 분석)"""
        logger.info(f"📝 Generating analysis prompts for {len(news_list)} news items...")

        prompt_files = []
        for i, news in enumerate(news_list, 1):
            try:
                prompt_file = self.analyze_news(news)
                if prompt_file:
                    prompt_files.append(prompt_file)
                logger.info(f"   [{i}/{len(news_list)}] {news.get('title', 'Unknown')[:50]}")
            except Exception as e:
                logger.error(f"Error generating prompt: {e}")

        logger.info(f"✅ Generated {len(prompt_files)} analysis prompts")
        logger.info(f"📂 Location: {self.prompts_dir}/")
        logger.info(f"\n💡 Next step: 각 프롬프트를 Claude Code에 입력하세요")
        logger.info(f"   명령어: cat prompts/analysis/*.md | wc -l")

        return []  # 프롬프트 기반이므로 즉시 결과 없음
