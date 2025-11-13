"""
Claude Code를 활용한 프롬프트 생성기
API 없이 사용자가 Claude Code에서 직접 분석/작성할 수 있도록 프롬프트 생성
"""

from typing import List, Dict
from datetime import datetime
from loguru import logger
import sys

sys.path.append('..')
from database.supabase_client import SupabaseClient

class PromptGenerator:
    """뉴스 분석 및 글 작성을 위한 프롬프트 자동 생성"""

    def __init__(self, db_client: SupabaseClient):
        self.db = db_client
        logger.info("Prompt generator initialized")

    def generate_analysis_prompt(self, news_batch: List[Dict], output_file: str = None) -> str:
        """뉴스 분석을 위한 프롬프트 생성"""

        prompt = f"""# 미국 주식 뉴스 분석 작업

총 {len(news_batch)}개의 뉴스를 분석해주세요.

## 분석 방법

각 뉴스에 대해 다음을 JSON 형식으로 분석:

1. **relevance_score** (0-100): 주식 투자자 관련성
   - 0-30: 무관 (일반 뉴스, 정치, 스포츠)
   - 31-60: 간접 관련 (경제 일반)
   - 61-80: 직접 관련 (특정 기업/섹터)
   - 81-100: 매우 중요 (실적, M&A, 규제)

2. **affected_symbols**: 영향받는 주식 심볼 (최대 5개)

3. **price_impact**: "up", "down", "neutral"

4. **importance**: "high", "medium", "low"

5. **reasoning**: 분석 근거 (2-3문장)

6. **key_points**: 핵심 포인트 (3-5개)

---

"""

        for i, news in enumerate(news_batch, 1):
            prompt += f"""
## 뉴스 #{i}

**ID**: {news['id']}
**출처**: {news['source']}
**제목**: {news['title']}
**발행일**: {news['published_at']}

**내용**:
{news.get('content', '')[:1000]}

**URL**: {news['url']}

---

"""

        prompt += """
## 출력 형식

각 뉴스에 대해 다음 JSON 형식으로 작성:

```json
{
  "news_id": "uuid",
  "relevance_score": 85,
  "affected_symbols": ["AAPL", "MSFT"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "애플이 신제품을 발표하여 매출 증가 예상. 마이크로소프트와의 파트너십도 긍정적.",
  "key_points": [
    "신제품 발표로 매출 증가 전망",
    "시장 점유율 확대 가능성",
    "MS와의 협력으로 시너지 기대"
  ]
}
```

**관련성 점수 70 이상인 뉴스만 분석 결과를 작성하세요.**

분석 결과를 `analysis_results.json` 파일에 JSON 배열로 저장하세요.
"""

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            logger.info(f"Analysis prompt saved to {output_file}")

        return prompt

    def generate_article_prompt(self, symbol: str, news_items: List[Dict], output_file: str = None) -> str:
        """블로그 글 작성을 위한 프롬프트 생성"""

        prompt = f"""# {symbol} 종목 관련 블로그 글 작성

{len(news_items)}개의 관련 뉴스를 종합하여 한국어 블로그 글을 작성해주세요.

---

"""

        for i, news in enumerate(news_items, 1):
            raw_news = news['news_raw']
            analysis = news.get('analysis', {})

            prompt += f"""
## 뉴스 #{i}

**제목**: {raw_news['title']}
**출처**: {raw_news['source']}
**발행일**: {raw_news['published_at']}

**내용**:
{raw_news.get('content', '')[:800]}

**관련성 점수**: {news.get('relevance_score', 'N/A')}/100
**주가 영향**: {news.get('price_impact', 'N/A')}
**중요도**: {news.get('importance', 'N/A')}

**분석**:
{analysis.get('reasoning', '')}

**핵심 포인트**:
{chr(10).join([f'- {point}' for point in analysis.get('key_points', [])])}

**출처**: {raw_news['url']}

---

"""

        prompt += f"""
## 작성 가이드

다음 구조로 블로그 글을 작성하세요:

### 제목 형식
`[{symbol}] 관련 최신 뉴스 분석 - [핵심 키워드 3-5개]`

예: "AAPL 관련 최신 뉴스 분석 - 신제품 출시, 실적 호조, AI 투자"

### 본문 구조

```markdown
# [제목]

## 📊 무엇이 일어났는가

[3-5개 뉴스를 종합하여 핵심 사건 요약. 각 뉴스의 핵심만 간결하게.]

## 🔄 어떻게 작동하는가

[메커니즘 설명: 이 뉴스들이 비즈니스/산업에 어떤 영향을 주는지]

- 공급망 변화
- 시장 점유율 변화
- 규제 영향
- 경쟁사 관계

등을 고려하여 설명

## 💡 왜 주가에 영향을 주는가

[논리적 연결고리 설명]

**1. 재무적 영향**
- 매출/이익에 어떻게 영향?

**2. 시장 심리**
- 투자자들이 어떻게 반응할지?

**3. 장단기 전망**
- 단기/중기/장기적 관점

## 📈 투자 시사점

투자자 관점에서 고려사항:

**긍정적 요소**
- [구체적 긍정 요인 3가지]

**리스크 요소**
- [구체적 리스크 3가지]

**투자 전략 제안**
- 단기 투자자: [관점]
- 장기 투자자: [관점]

## 🔗 참고 자료

[원본 뉴스 출처 링크들을 정리]

---

**면책 조항**: 본 글은 정보 제공 목적이며 투자 조언이 아닙니다. 투자 결정은 본인의 책임 하에 신중히 하시기 바랍니다.
```

### 작성 요구사항

1. **글자 수**: 1,500-2,000자 (SEO 최적화)
2. **톤**: 전문적이지만 이해하기 쉽게
3. **데이터**: 구체적인 숫자와 팩트 중심
4. **객관성**: 과장 없이 균형잡힌 시각
5. **SEO**: {symbol} 종목명과 관련 키워드를 자연스럽게 포함
6. **한국어**: 투자자 친화적 문체

작성한 글을 `article_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md` 파일로 저장하세요.
"""

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            logger.info(f"Article prompt saved to {output_file}")

        return prompt

    def generate_daily_workflow_prompt(self, output_dir: str = "prompts") -> str:
        """일일 워크플로우 프롬프트 생성"""

        # 미분석 뉴스 가져오기
        unanalyzed_news = self.db.get_unanalyzed_news(limit=50)

        if not unanalyzed_news:
            logger.info("No unanalyzed news found")
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')

        # 1. 분석 프롬프트 생성
        analysis_prompt_file = f"{output_dir}/analysis_{timestamp}.md"
        self.generate_analysis_prompt(unanalyzed_news, analysis_prompt_file)

        # 워크플로우 가이드
        workflow_prompt = f"""# 일일 뉴스 분석 및 블로그 글 작성 워크플로우

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 🔄 작업 순서

### 1단계: 뉴스 분석 ({len(unanalyzed_news)}개)

프롬프트 파일: `{analysis_prompt_file}`

**작업**:
1. 위 파일을 열어서 뉴스 분석 프롬프트 확인
2. Claude Code에서 각 뉴스 분석
3. 분석 결과를 `{output_dir}/analysis_results_{timestamp}.json`에 저장

**다음 명령으로 결과 저장**:
```bash
python scripts/save_analysis.py {output_dir}/analysis_results_{timestamp}.json
```

---

### 2단계: 인기 종목 확인

분석 완료 후, 다음 스크립트로 트렌딩 종목 확인:

```bash
python scripts/get_trending.py
```

---

### 3단계: 블로그 글 작성

트렌딩 종목(예: AAPL, TSLA, NVDA 등)에 대해 글 작성 프롬프트 생성:

```bash
python scripts/generate_article_prompts.py AAPL TSLA NVDA
```

생성된 프롬프트 파일들:
- `{output_dir}/article_AAPL_{timestamp}.md`
- `{output_dir}/article_TSLA_{timestamp}.md`
- `{output_dir}/article_NVDA_{timestamp}.md`

각 프롬프트를 열어서 블로그 글 작성 후, 결과를 지정된 파일명으로 저장.

---

### 4단계: 글 발행

작성한 글을 데이터베이스에 저장:

```bash
python scripts/publish_articles.py articles/article_AAPL_{timestamp}.md
```

---

## 📝 요약

**오늘의 작업**:
- [ ] {len(unanalyzed_news)}개 뉴스 분석
- [ ] 분석 결과 저장
- [ ] 트렌딩 종목 확인
- [ ] 상위 3-5개 종목 글 작성
- [ ] 작성한 글 발행

**예상 소요 시간**: 30-60분

**완전 무료**: API 비용 $0
"""

        workflow_file = f"{output_dir}/workflow_{timestamp}.md"
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_prompt)

        logger.info(f"Daily workflow prompt saved to {workflow_file}")
        return workflow_file
