# 블로그 자동 생성 가이드

뉴스 시그널을 기반으로 전문가 수준의 투자 분석 블로그 글을 자동 생성하는 방법입니다.

## ✨ 주요 업데이트 (2025-11-18)

**스토리텔링 형식으로 전환**:
- 실제 사례, 비교, 비유를 풍부하게 사용
- 감성적 스토리 + 이성적 데이터 균형
- 각 섹션마다 핵심 포인트 요약 박스 추가

**뉴스 출처 자동 표시**:
- 모든 블로그에 뉴스 출처와 시그널 정보 자동 삽입
- AI 알고리즘이 감지한 투자 시그널 명시
- Impact Score (0-100) 표시

---

## 📋 개요

### 전체 프로세스

```
뉴스 수집 → 시그널 분석 → 블로그 생성 → 이미지 삽입 → 웹사이트 배포
```

**소요 시간**: 약 5-10분 (이미지 생성 포함 시 20분)

---

## 🚀 블로그 생성 실행

### 기본 실행

```bash
cd /Users/jinxin/dev/aivesto
python scripts/generate_blog_from_signals.py
```

**기대 결과**:
```
=== Blog Generation from Signals Started ===
2025-11-17 22:44:35 | INFO | 📊 Fetching signals from database...
2025-11-17 22:44:36 | INFO | ✅ Found 2 signals to process

2025-11-17 22:44:37 | INFO | 📝 Generating blog: MSFT_AI_EXPANSION
2025-11-17 22:44:38 | INFO | ✅ Blog saved: article_msft_ai_copilot_expansion_20251117.html

2025-11-17 22:44:39 | INFO | 📝 Generating blog: GOOGL_AI_SEARCH
2025-11-17 22:44:40 | INFO | ✅ Blog saved: article_googl_ai_search_revolution_20251117.html

2025-11-17 22:44:41 | INFO | 📋 Updating blog.html...
2025-11-17 22:44:42 | INFO | ✅ Blog index updated (11 → 13 articles)

=== Blog Generation Completed ===
📊 Summary:
  Signals processed: 2
  Blogs generated: 2
  Total articles: 13
```

---

## 📝 블로그 글 구조

### 글쓰기 스타일: 스토리텔링 형식

**핵심 원칙**:
- 감성적인 스토리와 이성적인 데이터의 균형
- 실제 사례, 비교, 비유를 풍부하게 사용
- 각 섹션마다 핵심 포인트 요약 박스 포함
- 투자자가 이해하기 쉬운 언어 사용

### 생성되는 섹션

각 블로그 글은 다음 7개 섹션으로 구성됩니다:

#### 0. 📰 뉴스 출처 및 시그널 (자동 삽입)

**반드시 포함해야 하는 정보**:
- 뉴스 출처 (예: TechCrunch, NVIDIA Blog)
- 핵심 시그널 (예: MSFT_AI_EXPANSION)
- Impact Score (0-100 점수)

**예시**:
```markdown
---

> 📰 **이 분석의 근거가 된 뉴스**
>
> **출처**: NVIDIA Blog
>
> **핵심 시그널**: MSFT_AI_EXPANSION
> - 이 시그널은 AI 알고리즘이 자동으로 감지한 투자 기회입니다
> - Impact Score: 75/100 (높음)

---
```

#### 1. 📖 여는 이야기 (Opening Story)

**스토리텔링 필수 요소**:
- 구체적인 인물/회사 사례 (실명이나 가명)
- Before/After 비교
- 숫자로 증명된 변화
- 감정적 임팩트

**예시**:
```markdown
### 샌프란시스코의 작은 기적

샌프란시스코 다운타운의 한 스타트업, TechFlow의 CEO 제니퍼는 6개월 전만 해도
하루 평균 4시간을 회의에 소비했습니다...

**"마법 같았어요."** 제니퍼는 말합니다. TechFlow의 생산성은 38% 증가했습니다.

---

> 💡 **핵심 포인트**: Microsoft Copilot은 단순한 AI 도구가 아닙니다.
> 이것은 일하는 방식 자체를 바꾸는 플랫폼 혁명입니다.
```

#### 2. 📊 무슨 일이 일어났나 (What Happened)

**스토리텔링 요소**:
- 숫자 계산 과정 보여주기
- 비교 스토리 (다른 제품/회사와 비교)
- 비유 사용 (AI는 전기다, Microsoft는 발전소다)

**예시**:
```markdown
### 숫자로 보는 Microsoft의 AI 공세

**비교 스토리**: Instagram이 1억 명 달성하는 데 2.5년 걸렸습니다.
Copilot은 6개월 만에 해냈죠.

**계산 보여주기**:
- Microsoft 365 유료 구독자 4억 명
- 15%가 Copilot Pro 사용 = 6,000만 명
- 월 $30 × 6,000만 = **연간 $216억의 신규 매출**

**비유**: Microsoft는 AI라는 '전기'를 모든 제품에 공급하고 있습니다.

---

> 📊 **핵심 정리**:
> - **Copilot**: 연간 $200억+ 신규 매출 창출 가능
> - **Azure AI**: 42% 성장률로 클라우드 시장 재정의
```

#### 3. 💡 왜 중요한가 (Why Important)

**투자 논리 스토리텔링**:
- 실제 기업 사례 (ROI 계산)
- 시나리오 연습 ("당신이 Google CEO라면?")
- 워렌 버핏 같은 권위자 인용
- 시뮬레이션 (2년 후 예측)

**예시**:
```markdown
### 투자자 여러분, 왜 지금 주목해야 할까요?

**실제 사례**: 시애틀의 한 중견 기업은 Microsoft에 월 $30 더 내면서,
연간 $200만의 인건비를 절감했습니다. **200배 ROI**입니다.

**시나리오**: 당신이 Google의 CEO라면 어떻게 Microsoft를 따라잡겠습니까?

**시뮬레이션**:
- **현재**: 연매출 $2,400억 × AI 기여도 15% = $360억
- **2년 후**: 연매출 $3,000억 × AI 기여도 30% = $900억

---

> 🎯 **핵심 정리**:
> - **수익 모델**: 연간 $200억+ 신규 고마진 매출 창출 중
> - **경쟁 우위**: OpenAI 독점 + 기업 락인으로 해자 강화
```

#### 4. 📈 핵심 요약 (Summary)
- 1-2문장으로 투자 테마 요약
- 주가 영향도 간략 언급

**예시**:
```markdown
Microsoft가 AI 통합 오피스 제품군인 Copilot의 월간 활성 사용자 1억 명을 돌파하며,
기업용 생산성 소프트웨어 시장에서 독보적 지위를 공고히 하고 있습니다.
```

---

#### 5. 🎯 투자 포인트 (3가지)
- 핵심 강점 3가지
- 정량적 데이터 포함

**예시**:
```markdown
## 🎯 투자 포인트

### 1. Copilot 사용자 폭발적 성장
- 월간 활성 사용자 1억 명 돌파 (출시 6개월 만에)
- 기업용 Copilot 유료 구독자 200만 명 (전분기 대비 +85%)

### 2. Azure AI 서비스 강세
- Azure AI 매출 YoY +42% 성장
- OpenAI API 독점 공급으로 고마진 수익 창출

### 3. 오피스 제품군 가격 인상 효과
- Microsoft 365 구독 가격 평균 12% 인상
- AI 기능 추가로 가격 인상 저항 최소화
```

---

#### 6. 📊 재무 영향 분석
- 매출/영업이익 전망
- 애널리스트 의견
- 밸류에이션

**예시**:
```markdown
## 📊 재무 영향 분석

### 실적 전망
- **FY2025 Azure 성장률**: 28-30% (이전 전망: 25-27%)
- **오피스 365 매출**: YoY +18% (AI 프리미엄 효과)
- **영업이익률**: 42% → 44% 개선 (AI 서비스 고마진)

### 애널리스트 의견
- **Morgan Stanley**: 목표가 $520 상향 (이전 $480)
- **Goldman Sachs**: Strong Buy 유지, "AI 리더십 확대"
- **JP Morgan**: 목표가 $510, "Azure AI 독점 구조 장기 지속"

### 밸류에이션
- 현재 P/E: 32배 (S&P 500: 20배)
- PEG Ratio: 1.8 (AI 성장률 감안 시 합리적)
- EV/Sales: 10.5배 (클라우드 기업 평균 대비 -15%)
```

---

#### 7. 🚀 주가 전망 (3가지 시나리오)
- 강세 / 중립 / 약세 시나리오
- 각 시나리오별 확률 및 목표가

**예시**:
```markdown
## 🚀 주가 전망

### 강세 시나리오 (확률 65%)
**목표가**: $510-540
**조건**:
- Azure AI 성장률 30% 이상 지속
- Copilot 구독자 분기당 50% 이상 성장
- OpenAI 독점 관계 유지

**주요 촉매**:
- FY2025 Q1 실적 발표 (Copilot 매출 기여 가시화)
- AI 기능 추가로 Office 365 가격 추가 인상
- 기업 고객 AI 도입 가속화

### 중립 시나리오 (확률 25%)
**목표가**: $450-480
**조건**:
- Azure 성장률 25% 수준으로 둔화
- Copilot 성장세 점진적 둔화
- 경쟁 심화 (Google Workspace AI)

### 약세 시나리오 (확률 10%)
**목표가**: $380-420
**조건**:
- OpenAI 독점 계약 종료
- 규제 리스크 (EU AI Act)
- 거시 경기 둔화로 IT 지출 감소
```

---

#### 8. 💡 투자 전략
- 매수 타이밍
- 목표 수익률
- 손절가
- 리스크 관리

**예시**:
```markdown
## 💡 투자 전략

### 진입 전략
- **적극 매수**: $440 이하 (현재가 대비 -5%)
- **분할 매수**: $450-470 (3회 나눠 매수)
- **관망**: $480 이상 (조정 대기)

### 목표 수익률
- **단기 (3개월)**: +8-12% (실적 발표 전)
- **중기 (6개월)**: +15-20% (Copilot 성장 가시화)
- **장기 (12개월)**: +25-30% (AI 리더십 확립)

### 손절 전략
- **손절가**: $420 (지지선 붕괴 시)
- **손절 조건**: Azure 성장률 20% 하회 가이던스

### 리스크 관리
- 포트폴리오 비중: 15-20% (대형 성장주 포지션)
- 헤지: QQQ 풋옵션 (나스닥 급락 대비)
- 분산: GOOGL, AMZN 함께 보유 (클라우드 섹터 분산)
```

---

#### 9. ⚠️ 리스크 요인
- 주요 리스크 3-5가지
- 모니터링 포인트

**예시**:
```markdown
## ⚠️ 리스크 요인

### 1. OpenAI 독점 관계 종료 리스크
- OpenAI IPO 시 독립성 강화 가능성
- Azure 외 다른 클라우드 사용 확대 우려

### 2. 경쟁 심화
- Google Workspace AI 기능 빠르게 따라잡는 중
- Amazon CodeWhisperer 등 개발자 도구 경쟁

### 3. 규제 리스크
- EU AI Act 규제 강화
- 미국 반독점 조사 가능성

### 모니터링 포인트
- Azure 분기 성장률 (25% 이상 유지 여부)
- Copilot 구독자 수 공개 (분기 실적 발표)
- OpenAI와의 계약 갱신 여부 (2026년 만료)
```

---

#### 10. 🎯 결론
- 추천 등급 (Strong Buy / Buy / Hold / Sell)
- 목표가
- 한 줄 요약

**예시**:
```markdown
## 🎯 결론

**추천 등급**: Strong Buy ⭐⭐⭐⭐⭐

**목표가**: $520 (현재가 $440 기준, 상승 여력 +18%)

**한 줄 요약**: Microsoft는 AI 통합 오피스 제품으로 기업 생산성 시장을 재정의하고 있으며,
Azure AI와 Copilot의 폭발적 성장으로 향후 12개월간 25-30% 주가 상승이 기대됩니다.

---

**면책 조항**: 본 분석은 정보 제공 목적이며, 투자 권유가 아닙니다.
투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.
```

---

## 🎨 스타일링

### 브랜드 컬러

각 종목별로 고유한 브랜드 컬러가 적용됩니다:

```python
BRAND_COLORS = {
    'AAPL': '#000000',  # Apple Black
    'NVDA': '#76B900',  # NVIDIA Green
    'TSLA': '#CC0000',  # Tesla Red
    'MSFT': '#00A4EF',  # Microsoft Blue
    'GOOGL': '#4285F4', # Google Blue
    'META': '#0668E1',  # Meta Blue
    'AMZN': '#FF9900',  # Amazon Orange
    'NFLX': '#E50914',  # Netflix Red
    'ADBE': '#FF0000',  # Adobe Red
    'UBER': '#000000'   # Uber Black
}
```

### 헤더 스타일

```html
<div class="article-header" style="background: #00A4EF;">
    <div class="symbol-tag">MSFT</div>
    <h1>Microsoft, AI 오피스 통합으로 생산성 혁명 주도</h1>
</div>
```

---

## 🖼️ 이미지 생성 및 삽입

### 자동 이미지 생성

블로그 글 생성 후 이미지를 추가하려면:

```bash
python scripts/generate_images_for_new_articles.py
```

**생성 이미지**:
1. **Hero Image** (상단 배너)
   - 종목 테마 관련 이미지
   - 비율: 16:9
   - 예: "Microsoft office AI integration"

2. **Diagram Image** (본문 중간)
   - 차트, 인포그래픽 스타일
   - 비율: 16:9
   - 예: "Revenue growth chart"

---

## 📂 생성 파일 위치

### 블로그 HTML 파일

```
/public/article_{symbol}_{topic}_{date}.html
```

**예시**:
```
/public/article_msft_ai_copilot_expansion_20251117.html
/public/article_googl_ai_search_revolution_20251117.html
```

### 블로그 인덱스 업데이트

`/public/blog.html` 파일이 자동으로 업데이트됩니다:

```html
<!-- 새 글이 맨 위에 추가됨 -->
<div class="article-card" onclick="location.href='article_msft_ai_copilot_expansion_20251117.html'">
    <div class="article-header">
        <span class="symbol-tag">MSFT</span>
        <div class="article-date">📅 2025-11-17</div>
    </div>
    <h2 class="article-title">Microsoft, AI 오피스 통합으로 생산성 혁명 주도</h2>
</div>
```

---

## 🔍 생성 로직 상세

### 시그널 → 블로그 매핑

`generate_blog_from_signals.py` 스크립트는 다음 로직으로 작동합니다:

```python
# 1. 데이터베이스에서 시그널 조회
signals = supabase.table('all_trading_signals') \
    .select('*') \
    .gte('created_at', today) \
    .order('created_at', desc=True) \
    .execute()

# 2. 각 시그널을 블로그 글로 변환
for signal in signals.data:
    article_data = {
        'symbol': extract_symbol(signal['signal']),
        'signal': signal['signal'],
        'title': generate_title(signal),
        'content': generate_content(signal),
        'rating': calculate_rating(signal),
        'target_price': calculate_target(signal)
    }

    # 3. HTML 생성
    html = generate_blog_html(article_data)

    # 4. 파일 저장
    filename = f"article_{symbol}_{topic}_{date}.html"
    save_file(filename, html)

# 5. blog.html 업데이트
update_blog_index(new_articles)
```

---

### 투자 등급 계산

```python
def calculate_rating(signal):
    impact_score = signal.get('impact_score', 0)

    if impact_score >= 85:
        return "Strong Buy ⭐⭐⭐⭐⭐"
    elif impact_score >= 70:
        return "Buy ⭐⭐⭐⭐"
    elif impact_score >= 50:
        return "Hold ⭐⭐⭐"
    elif impact_score >= 30:
        return "Sell ⭐⭐"
    else:
        return "Strong Sell ⭐"
```

---

### 목표가 계산

```python
def calculate_target_price(symbol, signal):
    # 현재가 조회 (yfinance)
    import yfinance as yf
    ticker = yf.Ticker(symbol)
    current_price = ticker.history(period="1d")['Close'].iloc[-1]

    # Impact Score에 따른 상승률
    impact = signal.get('impact_score', 50)
    upside = impact / 5  # 85점 → 17% 상승

    target = current_price * (1 + upside / 100)
    return round(target, 2)
```

---

## 🔄 전체 파이프라인 자동화

### 원클릭 실행 스크립트

```bash
# scripts/run_full_pipeline.sh
#!/bin/bash
cd /Users/jinxin/dev/aivesto

echo "=== AI Investment Blog Pipeline ==="
echo ""

echo "Step 1/4: Collecting news..."
python scripts/news_collectors/tech_trends_collector.py
python scripts/news_collectors/macro_collector.py
python scripts/news_collectors/earnings_collector.py

echo ""
echo "Step 2/4: Generating blogs from signals..."
python scripts/generate_blog_from_signals.py

echo ""
echo "Step 3/4: Generating images..."
python scripts/generate_images_for_new_articles.py

echo ""
echo "Step 4/4: Deploying to web..."
echo "✅ Blog updated: http://localhost:8000/blog.html"

echo ""
echo "=== Pipeline Completed ==="
```

**실행**:
```bash
chmod +x scripts/run_full_pipeline.sh
./scripts/run_full_pipeline.sh
```

---

## 📊 성과 측정

### 블로그 글 품질 체크리스트

생성된 블로그 글이 다음 기준을 만족하는지 확인:

- [ ] 제목이 구체적이고 임팩트 있는가?
- [ ] 핵심 요약이 1-2문장으로 명확한가?
- [ ] 투자 포인트 3가지가 정량적 데이터를 포함하는가?
- [ ] 재무 영향 분석에 애널리스트 의견이 있는가?
- [ ] 주가 전망이 3가지 시나리오로 구성되었는가?
- [ ] 투자 전략에 진입가/목표가/손절가가 명시되었는가?
- [ ] 리스크 요인이 3개 이상 제시되었는가?
- [ ] 추천 등급과 목표가가 명확한가?

---

### 블로그 통계 확인

```python
# scripts/check_blog_stats.py
from pathlib import Path

blog_dir = Path("/Users/jinxin/dev/aivesto/public")
articles = list(blog_dir.glob("article_*.html"))

print(f"Total articles: {len(articles)}")
print()

# 종목별 분류
from collections import Counter
symbols = [a.stem.split('_')[1].upper() for a in articles]
symbol_counts = Counter(symbols)

print("Articles by symbol:")
for symbol, count in symbol_counts.most_common():
    print(f"  {symbol}: {count}")

# 날짜별 분류
dates = [a.stem.split('_')[-1] for a in articles]
date_counts = Counter(dates)

print()
print("Articles by date:")
for date, count in sorted(date_counts.items(), reverse=True)[:5]:
    print(f"  {date}: {count}")
```

---

## 🚨 문제 해결

### 문제 1: 시그널 없음

**증상**: `Found 0 signals to process`

**원인**:
- 뉴스 수집기가 실행되지 않았음
- 또는 시그널 조건을 만족하는 뉴스가 없음

**해결**:
```bash
# 뉴스 수집기 먼저 실행
python scripts/news_collectors/tech_trends_collector.py

# 시그널 확인
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
result = supabase.table('all_trading_signals').select('*').execute()
print(f'Total signals: {len(result.data)}')
"
```

---

### 문제 2: yfinance 오류

**증상**: `yfinance Ticker data not available`

**원인**: Yahoo Finance API 일시적 오류

**해결**:
```python
# 목표가를 수동으로 설정
FALLBACK_PRICES = {
    'MSFT': 440,
    'GOOGL': 165,
    'NVDA': 875,
    'AAPL': 195
}
```

---

### 문제 3: 이미지 생성 실패

**증상**: `ModuleNotFoundError: No module named 'src.midjourney'`

**원인**: magic_book 프로젝트 경로 문제

**해결**:
이미지 없이 블로그 배포 (나중에 수동 추가 가능)

---

## 📈 고급 기능

### 사용자 정의 템플릿

다른 스타일의 블로그 글을 원한다면 템플릿을 수정:

```python
# scripts/templates/blog_template.py
CUSTOM_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <title>{title}</title>
    <style>
        /* 사용자 정의 CSS */
    </style>
</head>
<body>
    <!-- 사용자 정의 HTML 구조 -->
</body>
</html>
"""
```

---

### A/B 테스팅

두 가지 버전의 블로그를 생성하여 비교:

```bash
# 버전 A: 보수적 투자 전략
python scripts/generate_blog_from_signals.py --style conservative

# 버전 B: 공격적 투자 전략
python scripts/generate_blog_from_signals.py --style aggressive
```

---

## 📚 추가 문서

- [뉴스 수집기 가이드](./NEWS_COLLECTORS_GUIDE.md)
- [데이터베이스 스키마 배포](./DATABASE_SCHEMA_DEPLOYMENT.md)
- [API 키 설정 가이드](./API_KEYS_SETUP_GUIDE.md)
- [빠른 시작 체크리스트](./QUICK_START_CHECKLIST.md)

---

## 🎉 완료!

이제 뉴스 시그널에서 전문가 수준의 투자 분석 블로그를 자동으로 생성할 수 있습니다!

**다음 실행**:
```bash
# 전체 파이프라인 실행
./scripts/run_full_pipeline.sh

# 또는 개별 단계별 실행
python scripts/news_collectors/tech_trends_collector.py
python scripts/generate_blog_from_signals.py
```

**로컬에서 확인**:
```bash
cd public
python -m http.server 8000
# 브라우저: http://localhost:8000/blog.html
```
