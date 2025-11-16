# Aivesto 개발 가이드

**프로젝트 목적**: 미국 주식 뉴스에서 투자 시그널을 발굴하고 SEO 최적화된 분석 기사 작성
**배포 URL**: https://aivesto-dashboard-f30hi3pct-mumushin81-gmailcoms-projects.vercel.app
**최종 업데이트**: 2025-11-14

---

## 프로젝트 개요

### 핵심 가치 제안

미국 주식 뉴스를 자동 수집하여:
1. **투자 시그널 발굴** - 주가 변동 가능성이 높은 뉴스 식별
2. **종목 추출** - 시그널과 관련된 주식 종목 자동 추출
3. **영향 분석** - 왜 해당 종목 가격이 상승/하락할지 분석
4. **SEO 기사 작성** - 2000-3500자 AI 검색 최적화 콘텐츠 생성

### 시그널이란?

**투자 시그널** = 주가에 영향을 줄 수 있는 중요한 뉴스 또는 이벤트

**시그널 유형** (우선순위 순):
- 🔥 **정책 변화 시그널**: 정부 정책 신설/폐지/변경 (최우선!)
  - 신규: IRA, CHIPS Act, AI 규제법, 관세 부과, 탄소세
  - 폐지: 규제 완화, 관세 철폐, 금수 조치 해제
  - 변경: 금리, 법인세율, 보조금, FDA 승인/거부
- 📈 **상승 시그널**: 신제품 출시, 실적 호조, 전략적 파트너십
- 📉 **하락 시그널**: 경쟁 심화, 실적 악화, 소송
- ⚖️ **중립 시그널**: 일반 업데이트, 시장 전반 동향

**시그널 레벨**:
- **Level 1 (긴급)**: 관련성 90+ → 즉시 기사 작성
- **Level 2 (높음)**: 관련성 80-89 → 우선 기사 작성
- **Level 3 (중간)**: 관련성 70-79 → 주간 리포트
- **Level 4 (낮음)**: 관련성 70 미만 → 무시

---

## 기술 스택

- **Backend**: Python 3.9+ / Flask
- **Frontend**: HTML/CSS/JavaScript (템플릿 기반)
- **Database**: Supabase (PostgreSQL)
- **AI Analysis**: Claude Code (로컬, 무료)
- **News Collection**: 3계층 전략
  - Layer 1: Bloomberg, Reuters, WSJ (RSS)
  - Layer 2: Fox News, CNN, Yahoo Finance (RSS)
  - Layer 3: Reddit, 지역 뉴스 (선택)
- **Sentiment Analysis**: FinBERT (ONNX), VADER, spaCy
- **Deployment**: Vercel (정적 사이트)
- **Alerts**: Telegram Bot

---

## 환경 설정

### 1. 의존성 설치

```bash
cd /Users/jinxin/dev/aivesto

# 가상환경
python3 -m venv venv
source venv/bin/activate

# 패키지
pip install -r requirements.txt
```

### 2. 필수 API 키 발급

| API | 가입 URL | 무료 제한 | 용도 |
|-----|----------|-----------|------|
| **Finnhub** | https://finnhub.io/register | 60 req/분 | 뉴스 수집 |
| **Supabase** | https://supabase.com | 500MB DB | 데이터 저장 |
| **Telegram** | @BotFather | 무제한 | 시그널 알림 |
| Alpha Vantage | https://www.alphavantage.co | 25 req/일 | 보조 뉴스 (선택) |

### 3. .env 설정

```bash
cp .env.example .env
nano .env
```

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key

# News APIs
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_key  # 선택

# Telegram
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_IDS=your_chat_id

# 시그널 설정
MIN_RELEVANCE_SCORE=70          # 최소 관련성 점수
NEWS_COLLECTION_INTERVAL=900    # 15분마다 수집
```

### 4. Supabase 데이터베이스 설정

```bash
# 1. Supabase 대시보드 > SQL Editor
# 2. database/schema.sql 복사 → 붙여넣기 → RUN
cat database/schema.sql
```

**생성 테이블**:
- `news_raw` - 수집된 원본 뉴스
- `analyzed_news` - 분석된 시그널 (관련성, 영향 종목, 가격 예측)
- `published_articles` - 발행된 블로그 기사

---

## 시스템 워크플로우

### 전체 프로세스 (현재: 수동 시그널 분석 방식)

```
0. 24시간 지난 뉴스 자동 삭제 (자동)
   ↓ 뉴스 수집 전 실행
   ↓ DB 정리 및 최적화

1. 뉴스 수집 (자동)
   ↓ Finnhub API - 필요시 수동 실행
   ↓ python main.py --mode collect

2. 시그널 분석 프롬프트 생성 (자동)
   ↓ python scripts/generate_daily_workflow.py
   ↓ prompts/analysis/*.md 파일 생성

3. Claude Code에서 수동 분석 ⭐ (당신이 직접)
   ↓ 각 프롬프트를 Claude Code에 복사
   ↓ JSON 결과 받기
   ↓ 관련성 90+ 시그널 선별

4. 시그널 기반 기사 작성 (수동 - Claude Code)
   ↓ 선별된 시그널로 기사 작성
   ↓ 2000-3500자 SEO 최적화
   ↓ articles/*.md로 저장

5. 발행 및 배포 (자동)
   ↓ git push → Vercel 자동 배포

⚠️ 향후: Phase 1-3 완료 후 완전 자동화 예정
```

### 시그널 분석 8가지 기준 (업데이트)

Claude Code가 각 뉴스를 다음 기준으로 평가:

1. **관련성 점수 (0-100)**: 투자 결정에 얼마나 중요한가?
2. **영향받는 종목 (1-5개)**: 어떤 주식이 영향을 받는가?
3. **가격 영향 방향**: UP (상승) / DOWN (하락) / NEUTRAL (중립)
4. **중요도**: HIGH / MEDIUM / LOW
5. **분석 근거 (2-3문장)**: 왜 이 점수를 줬는가?
6. **핵심 포인트 (3-5개)**: 투자자가 알아야 할 내용

**🆕 7. 정부 정책/정치 이슈 (CRITICAL)**: ⭐⭐⭐
   - **신규 정책**: 존재하지 않던 것이 새로 생김
     - 예: IRA(인플레이션 감축법), CHIPS Act, AI 규제법, 탄소세 도입
     - 예: FDA 신약 승인, FTC 반독점 조사 개시
   - **폐지/완화**: 존재하던 것이 없어짐
     - 예: 암호화폐 규제 완화, 석유 수출 금지 해제
     - 예: 관세 철폐, 환경 규제 완화
   - **변경**: 기존 정책 수정
     - 예: 금리 인상/인하, 법인세율 변경, 보조금 규모 조정

**🆕 8. 규제 변화 타입**:
   - `new_policy`: 신규 정책/규제 도입 (→ 섹터 전체 영향)
   - `policy_removed`: 기존 정책 폐지 (→ 규제 완화 수혜)
   - `policy_changed`: 정책 변경 (→ 승자/패자 명확)
   - `none`: 정책 무관

---

## 일일 수동 워크플로우 (현재 방식)

### Step 1: 뉴스 수집 (필요시)

```bash
# Finnhub에서 최신 뉴스 수집
python main.py --mode collect
```

**확인**:
```bash
# 수집된 뉴스 개수 확인
python -c "from database.supabase_client import SupabaseClient; db = SupabaseClient(); print(f'최근 24시간 뉴스: {len(db.get_recent_news(24))}개')"
```

### Step 2: Claude Code에서 직접 시그널 분석 ⭐

**방법 A: 개별 뉴스 분석**

```bash
# 1. 최근 뉴스 조회
python -c "
from database.supabase_client import SupabaseClient
db = SupabaseClient()
news_list = db.get_recent_news(24)

for i, news in enumerate(news_list[:10], 1):
    print(f'{i}. [{news.get(\"symbols\", [])}] {news.get(\"title\", \"No title\")[:80]}')
"

# 2. Claude Code에서 직접 분석 요청
```

**Claude Code에 붙여넣을 프롬프트 (최신 버전)**:
```
다음 뉴스를 투자 시그널 관점에서 분석해줘:

제목: [뉴스 제목]
내용: [뉴스 본문]
기존 심볼: [추출된 종목]

다음 형식으로 JSON 응답:
{
  "relevance_score": 0-100,
  "affected_symbols": ["AAPL", "MSFT"],
  "price_impact": "up/down/neutral",
  "importance": "high/medium/low",
  "reasoning": "2-3문장 분석",
  "key_points": ["포인트1", "포인트2", "포인트3"],

  // 🆕 정부 정책/정치 이슈 (매우 중요!)
  "policy_impact": {
    "has_policy_change": true/false,
    "change_type": "new_policy/policy_removed/policy_changed/none",
    "policy_description": "어떤 정책이 생겼거나 없어졌는지",
    "affected_sectors": ["Technology", "Energy"],
    "policy_catalyst": "왜 이 정책이 주가에 영향을 주는가"
  }
}

점수 기준:
- 0-60: 일반 뉴스, 투자 무관
- 61-80: 특정 기업/섹터 관련
- 81-89: 실적, M&A 등 중요 이벤트
- 90-100: ⭐ 정부 정책 변화, 규제 신설/폐지, FDA 승인, FTC 조사 등

⚠️ 정책 변화는 자동으로 90점 이상!
- 신규 정책 도입 (IRA, CHIPS Act, AI 규제법) → 95-100점
- 기존 정책 폐지 (규제 완화, 관세 철폐) → 95-100점
- 정책 변경 (금리, 세율, 보조금) → 90-95점
- FDA 승인/거부, FTC 반독점 조사 → 90-95점

90점 이상이면 즉시 기사 작성 대상!
```

**방법 B: 배치 분석 (권장)**

```bash
# 상위 10개 뉴스를 하나의 프롬프트로
python scripts/generate_batch_prompt.py --limit 10
# → prompts/batch_analysis_YYYYMMDD.md 생성

# Claude Code에 붙여넣기
cat prompts/batch_analysis_20251115.md
```

### Step 3: 긴급 시그널(90+) 확인

Claude Code 분석 결과에서 **relevance_score 90 이상**만 선별:

```json
// 예시 1: 정책 변화 시그널 (최우선!)
{
  "title": "바이든, AI 칩 대중국 수출 전면 금지 행정명령 발표",
  "relevance_score": 98,
  "symbols": ["NVDA", "AMD", "INTC"],
  "price_impact": "down",
  "importance": "high",
  "reasoning": "NVIDIA 매출의 20%가 중국 시장. 수출 금지로 연 $50억 매출 손실 예상",
  "key_points": [
    "A100/H100 GPU 중국 수출 완전 차단",
    "NVIDIA 주가 즉각 -8% 하락 전망",
    "AMD, Intel도 동일 규제 적용"
  ],
  "policy_impact": {
    "has_policy_change": true,
    "change_type": "new_policy",
    "policy_description": "첨단 AI 칩 대중국 수출 전면 금지",
    "affected_sectors": ["Technology", "Semiconductors"],
    "policy_catalyst": "중국 AI 군사 활용 차단. 반도체 기업 매출 타격"
  }
}

// 예시 2: 규제 완화 시그널
{
  "title": "SEC, 암호화폐 현물 ETF 전면 승인",
  "relevance_score": 96,
  "symbols": ["COIN", "MSTR", "RIOT"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "기관 투자자 자금 유입으로 암호화폐 거래량 폭증 예상",
  "key_points": [
    "Coinbase 거래 수수료 3배 증가 전망",
    "비트코인 가격 +25% 급등",
    "규제 불확실성 해소로 섹터 전체 상승"
  ],
  "policy_impact": {
    "has_policy_change": true,
    "change_type": "policy_removed",
    "policy_description": "암호화폐 ETF 승인 거부 정책 폐지",
    "affected_sectors": ["Cryptocurrency", "FinTech"],
    "policy_catalyst": "기관 자금 유입 가능. 거래소 수익 급증"
  }
}

// 예시 3: 일반 기업 뉴스 (정책 무관)
{
  "title": "NVIDIA Blackwell GPU 출시",
  "relevance_score": 95,
  "symbols": ["NVDA"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "AI 인프라 시장 지배력 강화. 2025년 매출 30% 증가 전망",
  "key_points": [
    "전세대 대비 30배 성능 향상",
    "Microsoft, Meta 대규모 선주문",
    "시장 점유율 85% 목표"
  ],
  "policy_impact": {
    "has_policy_change": false,
    "change_type": "none"
  }
}
```

**우선순위**:
1. 🔥 **정책 변화** (98-100점) → 즉시 기사 작성
2. ⚡ **규제 변화** (95-97점) → 당일 기사 작성
3. ⭐ **기업 이벤트** (90-94점) → 2-3일 내 작성

### Afternoon (30-60분) - 기사 작성

#### Step 1: 트렌딩 종목 확인

```bash
python scripts/get_trending.py
```

**출력 예시**:
```
📈 Top 10 Trending Symbols (24h)

1. NVDA   - 5 signals (avg: 88/100)
2. AAPL   - 4 signals (avg: 82/100)
3. MSFT   - 3 signals (avg: 85/100)

💡 Recommended: NVDA (Blackwell GPU 출시)
```

#### Step 2: 기사 작성 프롬프트 생성

```bash
python scripts/generate_article_prompts.py NVDA
```

**생성 파일**: `prompts/article_NVDA_20251114_1400.md`

**프롬프트 구조**:
```markdown
당신은 미국 주식 시장 분석 전문가입니다.
다음 뉴스 시그널을 바탕으로 SEO 최적화된 블로그 기사를 작성하세요.

📊 종목: NVDA (NVIDIA)
🔔 시그널 레벨: Level 1 (긴급)
📈 가격 영향: UP (상승)

=== 관련 뉴스 시그널 ===

[시그널 1]
제목: NVIDIA Blackwell GPU 출시
관련성: 92/100
핵심 포인트:
- Blackwell GPU 30배 성능 향상
- Microsoft, Meta 주요 고객
- 2025년 시장 점유율 50% 목표

[시그널 2]
제목: AI 서버 수요 급증, NVIDIA 수혜
관련성: 85/100
핵심 포인트:
- 글로벌 AI 인프라 투자 증가
- NVIDIA H100/H200 공급 부족
- 경쟁사 AMD 대비 기술 우위

=== 기사 작성 가이드 ===

📝 자세한 블로그 글 작성 가이드는 `BLOG_WRITING_GUIDE.md` 참조

✅ 핵심 원칙:

- 스토리텔링 형식 (구조화된 섹션 제목 사용 금지)
- 2000-3500자 분량
- 첫 줄에 [출처 + 날짜] + 핵심 내용
- 자연스러운 문단 전환
- 데이터 테이블 1-2개 포함
- 투자 전략 및 리스크 명시

형식:
TITLE:
[제목]

CONTENT:
[출처] (날짜) - 핵심 내용 한 문장

[본문 - 스토리텔링 형식으로 2000-3500자]

**투자 전략**: ...
**모니터링 포인트**: ...
**관련 종목**: ...

---
**출처**: ...
**작성일**: ...
**면책**: 본 기사는 정보 제공 목적이며, 투자 권유가 아닙니다.

지금 시작하세요!
```

#### Step 3: Claude Code에서 기사 작성

```bash
cat prompts/article_NVDA_20251114_1400.md
```

1. 프롬프트 전체 복사
2. Claude Code에 붙여넣기
3. Claude가 2000-3500자 기사 작성
4. `articles/article_NVDA_blackwell_gpu_20251114.md` 저장

#### Step 4: 기사 품질 검증

```bash
python scripts/validate_article_quality.py --file articles/article_NVDA_blackwell_gpu_20251114.md
```

**품질 체크리스트** (10가지):
- ✅ 파일 형식: `TITLE:` / `CONTENT:` 구조
- ✅ 내용 길이: 2000-3500자
- ✅ 11단계 구조: 모든 필수 섹션 포함
- ✅ SEO 규칙: 키워드, 제목, 헤딩
- ✅ 한국어 비율: 70% 이상
- ✅ 문장 길이: 40-80자 권장
- ✅ 불릿 포인트: 3개 이상
- ✅ 이모지: 2-10개
- ✅ 내부 링크: 2-5개
- ✅ 결론/CTA: 명확한 마무리

**점수 계산**:
- 100점: 완벽 (즉시 발행 가능)
- 90-99점: 우수 (소폭 수정)
- 80-89점: 양호 (일부 보완)
- 70-79점: 보통 (재작성 권장)
- 70점 미만: 미달 (재작성 필수)

#### Step 5: 자동 수정 (옵션)

```bash
# 품질 점수가 낮으면 자동 수정
python scripts/improve_article.py articles/article_NVDA_*.md
```

**자동 수정 항목**:
- 형식 보정: `# 제목` → `TITLE:\n제목\n\nCONTENT:\n`
- 필수 섹션 추가: 누락된 섹션 자동 생성
- 한국어 비율 개선: `AI` → `AI(인공지능)`
- 내부 링크 추가: 관련 기사 자동 연결

---

## 기사 작성 예시

### 시그널 정보

- **종목**: NVDA (NVIDIA)
- **시그널**: Blackwell GPU 출시
- **관련성**: 92/100
- **가격 영향**: UP (상승)
- **영향 종목**: NVDA (직접), AMD (경쟁), MSFT/META (고객)

### 최종 기사 구조

```markdown
TITLE:
NVIDIA Blackwell GPU 출시, AI 시장 지배력 강화 - 주가 전망 분석

CONTENT:

## 📌 핵심 요약 (10초 판독)

**상황**: NVIDIA가 차세대 Blackwell GPU를 공식 출시하며 AI 칩 시장 지배력을 강화했습니다.
**영향**: 전세대 대비 30배 성능 향상으로 Microsoft, Meta 등 주요 고객을 확보하며 2025년 시장 점유율 50% 달성 전망입니다.
**전망**: 애널리스트들은 목표주가를 $130-150로 상향 조정하며 AI 인프라 수혜주로 장기 보유를 권고하고 있습니다.

## 📰 무엇이 일어났나 - Blackwell GPU 시대 개막

NVIDIA(NVDA)는 2024년 11월 13일 차세대 AI GPU인 **Blackwell 아키텍처** 기반 제품을 공식 출시했습니다. 이번 출시는 단순한 제품 업데이트가 아닌, AI 인프라 시장의 판도를 바꿀 수 있는 게임 체인저로 평가받고 있습니다.

**주요 발표 내용**:
- ✅ **성능**: 전세대 H100 대비 30배 향상된 AI 훈련 속도
- ✅ **고객**: Microsoft, Meta, OpenAI 등 주요 기업 선주문 확보
- ✅ **생산**: 2025년 1분기부터 대량 생산 개시
- ✅ **목표**: 2025년 AI 서버 GPU 시장 점유율 50% 달성

이 발표 직후 NVIDIA 주가는 장중 8% 상승하며 시가총액 $1.2조를 기록했습니다.

## 🔍 어떻게 작동하는가 - Blackwell의 기술 우위

Blackwell GPU가 시장을 지배할 수 있는 이유는 3가지 핵심 기술에 있습니다.

### 1. 아키텍처 혁신
- **트랜지스터**: 208억 개 (H100 대비 2.5배)
- **메모리**: 192GB HBM3E (대역폭 8TB/s)
- **연산 능력**: FP8 정밀도에서 20 petaFLOPS

### 2. 에너지 효율
- **전력 소비**: 동일 성능 기준 40% 절감
- **TCO 개선**: 데이터센터 운영 비용 30% 감소

### 3. 소프트웨어 생태계
- **CUDA 12.0**: AI 프레임워크 완벽 지원
- **NVLink**: GPU 간 576GB/s 통신 속도

이러한 기술 우위는 경쟁사 AMD나 Intel이 단기간에 따라잡기 어려운 격차를 만들어냅니다.

## 💰 왜 주가에 영향을 주는가 - 투자 로직

### 매출 성장 가속화

| 항목 | 2024 (예상) | 2025 (전망) | 증가율 |
|------|-------------|-------------|--------|
| **데이터센터 매출** | $48B | $72B | +50% |
| **AI GPU 점유율** | 80% | 85% | +5%p |
| **영업 이익률** | 55% | 58% | +3%p |
| **EPS** | $12.50 | $18.00 | +44% |

### 시장 확대 수혜

글로벌 AI 인프라 투자는 2025년 $200B을 돌파할 전망입니다:
- 📊 **클라우드 3사** (AWS, Azure, GCP): $80B 투자 확대
- 🤖 **생성 AI 기업** (OpenAI, Anthropic): $40B GPU 구매
- 🏢 **엔터프라이즈**: $30B 온프레미스 AI 구축

NVIDIA는 이 중 50% 이상을 차지할 것으로 예상됩니다.

### 경쟁 우위 지속

- ✅ **기술 격차**: AMD 대비 2년 선행
- ✅ **고객 락인**: CUDA 생태계 의존도 높음
- ✅ **공급망**: TSMC CoWoS 패키징 독점 계약

## 📊 경쟁사 비교 - NVIDIA vs AMD vs Intel

| 항목 | NVIDIA | AMD | Intel |
|------|--------|-----|-------|
| **AI GPU 점유율** | 80% | 15% | 5% |
| **최신 제품** | Blackwell | MI300X | Gaudi 3 |
| **성능 (상대)** | 100% | 60% | 40% |
| **출시 시기** | 2024 Q4 | 2024 Q2 | 2025 Q1 |
| **소프트웨어** | CUDA (성숙) | ROCm (성장) | oneAPI (초기) |

**결론**: NVIDIA의 독과점은 최소 2-3년 지속될 전망입니다.

## ❓ 자주 묻는 질문

**Q1. Blackwell GPU는 언제 구매 가능한가요?**
A. 2025년 1분기부터 대량 생산되지만, 주요 고객(Microsoft, Meta 등) 선주문으로 인해 일반 기업은 2025년 하반기에 구매 가능할 전망입니다.

**Q2. 지금이 NVIDIA 매수 적기인가요?**
A. 장기 투자 관점(3-5년)에서는 여전히 매력적입니다. 단, 단기적으로 실적 발표 전 변동성이 클 수 있으니 분할 매수를 권장합니다.

**Q3. AI 버블 우려는 없나요?**
A. AI 인프라 투자는 실제 수요에 기반하고 있으며, NVIDIA는 이미 매출로 입증 중입니다. 다만 밸류에이션이 높아 조정 가능성은 존재합니다.

**Q4. AMD가 따라잡을 수 있나요?**
A. 기술적으로는 가능하지만, CUDA 생태계와 고객 락인 효과로 인해 시장 점유율 역전은 어려울 전망입니다.

## 💡 전문가 의견 및 목표가

### 주요 증권사 전망

- **모건스탠리**: 목표가 $150, "AI 인프라의 절대 강자"
- **골드만삭스**: 목표가 $145, "Blackwell 사이클 3년 지속"
- **JP모건**: 목표가 $140, "데이터센터 매출 50% 성장"

### 평균 목표가
- 📈 **상승 여력**: 현재가 대비 +15-20%
- 🎯 **컨센서스**: $142 (29개 증권사 평균)

**출처**: Bloomberg Terminal, 2024년 11월 13일 기준

## 🔮 단계별 전망 분석

### 낙관적 시나리오 (확률 40%)
**목표가 $150 (+25%)**
- Blackwell 수요 예상 초과
- AI 투자 2025년 30% 증가
- 영업이익률 60% 달성

### 중립적 시나리오 (확률 50%)
**목표가 $130 (+8%)**
- 계획대로 시장 점유율 85% 유지
- AI 투자 20% 증가
- 경쟁 심화로 마진 소폭 하락

### 비관적 시나리오 (확률 10%)
**목표가 $110 (-8%)**
- 글로벌 경기 침체로 AI 투자 감소
- AMD 시장 점유율 확대
- 미중 갈등으로 중국 수출 제한

## 📝 결론 및 투자 고려사항

### 투자 전략

**장기 투자자 (3-5년)**:
- ✅ **추천**: AI 인프라 성장은 구조적 트렌드
- ⚠️ **주의**: 현재 P/E 45배로 밸류에이션 부담

**단기 투자자 (6-12개월)**:
- ⚖️ **중립**: 실적 발표 변동성 고려
- 💡 **전략**: 분할 매수 또는 옵션 활용

### 리스크 요인

1. **규제 리스크**: 미국 반독점 조사 가능성
2. **경쟁 리스크**: AMD, Intel 기술 추격
3. **거시 리스크**: 금리 인상, 경기 침체
4. **지정학 리스크**: 대만(TSMC) 불안정성

### 모니터링 포인트

- 📅 **2025년 1월**: 4분기 실적 발표
- 📊 **Blackwell 출하량**: 분기별 업데이트
- 🏢 **고객사 CAPEX**: Microsoft, Meta AI 투자 규모
- 🌐 **시장 점유율**: AMD 대비 추이

---

### 관련 기사

- [MSFT AI Office 통합 전략 분석](articles/article_MSFT_AI_office_integration_20251113.md)
- [AMD MI300X vs NVIDIA H100 성능 비교](articles/article_AMD_vs_NVIDIA.md)
- [2025 AI 인프라 투자 전망](articles/article_AI_infrastructure_2025.md)

---

**면책 조항**: 본 기사는 투자 권유가 아닌 정보 제공 목적입니다. 투자 결정은 본인 책임 하에 신중히 하시기 바랍니다.

**작성일**: 2024년 11월 14일
**출처**: Finnhub, Bloomberg, 각 증권사 리서치 보고서
```

**통계**:
- 단어 수: 2,847자 ✅
- 한국어 비율: 72% ✅
- 필수 섹션: 11/11 ✅
- 내부 링크: 3개 ✅
- SEO 키워드 밀도: 최적 ✅

---

## 배포

### Vercel 배포 (자동)

```bash
# 1. GitHub 푸시
git add articles/
git commit -m "Add NVDA Blackwell GPU analysis"
git push origin main

# 2. Vercel 자동 배포 (GitHub 연동됨)
# 약 30초 후 배포 완료
```

### 로컬 미리보기

```bash
# Flask 서버 실행
python web/app.py

# 브라우저
open http://localhost:5000
```

---

## 디렉토리 구조

```
aivesto/
├── alerts/
│   ├── telegram_alerts.py     # Telegram 시그널 알림
│   └── email_alerts.py         # 이메일 알림
│
├── writers/
│   ├── article_generator.py   # 기사 프롬프트 생성
│   └── article_formatter.py   # 기사 품질 검증
│
├── scripts/
│   ├── generate_daily_workflow.py    # 일일 프롬프트 생성
│   ├── save_analysis.py              # 분석 결과 저장
│   ├── get_trending.py               # 트렌딩 종목 조회
│   ├── generate_article_prompts.py   # 기사 프롬프트 생성
│   ├── validate_article_quality.py   # 품질 검증
│   ├── improve_article.py            # 자동 수정
│   └── convert_to_seo_format.py      # SEO 최적화
│
├── articles/                   # 발행된 기사
│   ├── article_NVDA_blackwell_gpu_20251113.md
│   ├── article_MSFT_AI_office_integration_20251113.md
│   └── ...
│
├── prompts/                    # Claude Code 프롬프트
│   ├── analysis/              # 뉴스 분석 프롬프트
│   ├── results/               # 분석 결과 JSON
│   └── articles/              # 기사 작성 프롬프트
│
├── templates/                  # HTML 템플릿
│   ├── index.html             # 메인 대시보드
│   └── article.html           # 기사 상세 페이지
│
├── web/
│   └── app.py                 # Flask 웹 서버
│
├── database/
│   ├── schema.sql             # DB 스키마
│   ├── models.py              # 데이터 모델
│   └── supabase_client.py     # DB 클라이언트
│
├── vercel.json                # Vercel 설정
└── .env                       # 환경 변수
```

---

## 유용한 명령어

### 시스템 운영

```bash
# 뉴스 수집 (자동화)
python main.py --mode collect

# 1회 테스트
python main.py --mode once

# 24/7 실행 (백그라운드)
nohup python main.py --mode run > logs/system.log 2>&1 &
```

### 시그널 확인

```bash
# 긴급 시그널 (Level 1)
curl http://localhost:5000/api/signals/urgent

# 트렌딩 종목
python scripts/get_trending.py

# Supabase 쿼리
# SELECT * FROM analyzed_news WHERE relevance_score >= 90;
```

### 기사 관리

```bash
# 품질 검증
python scripts/validate_article_quality.py --file articles/YOUR.md

# 모든 기사 검증
python scripts/validate_article_quality.py --dir articles/

# 자동 수정
python scripts/improve_article.py articles/YOUR.md
```

### 로그 확인

```bash
# 실시간 로그
tail -f logs/stock_news_$(date +%Y-%m-%d).log

# 에러만 확인
grep "ERROR" logs/stock_news_*.log
```

---

## 문제 해결

### Q: 시그널이 발견되지 않습니다

```bash
# 뉴스 수집 확인
python main.py --mode collect

# Supabase 확인
SELECT COUNT(*) FROM news_raw
WHERE created_at > NOW() - INTERVAL '24 hours';

# MIN_RELEVANCE_SCORE 조정 (.env)
MIN_RELEVANCE_SCORE=60  # 70 → 60으로 낮춤
```

### Q: 기사 품질 점수가 낮습니다

**체크리스트**:
- [ ] `TITLE:` / `CONTENT:` 형식 사용
- [ ] 2000-3500자
- [ ] 11단계 구조 완성
- [ ] 한국어 비율 70% 이상
- [ ] 표, FAQ, 수치 포함

```bash
# 상세 리포트
python scripts/validate_article_quality.py --file articles/YOUR.md --verbose
```

### Q: Telegram 알림이 안 옵니다

```bash
# Bot 테스트
python scripts/test_telegram_alerts.py

# 로그 확인
tail -f logs/stock_news_*.log | grep Telegram
```

### Q: Vercel 배포 실패

```bash
# 로그 확인
vercel logs

# 체크포인트
# 1. templates/index.html 존재 확인
# 2. vercel.json 설정 확인
# 3. .vercelignore에 불필요한 파일 제외
```

---

## 성과 지표

### 시그널 발굴 성공률

- **Level 1 시그널**: 90% 이상 주가 영향 (±5% 이상)
- **Level 2 시그널**: 70% 주가 영향 (±3% 이상)

### 기사 SEO 성과

- **AI 검색 노출**: 상위 10위권 목표
- **Google 색인**: 24시간 내 색인
- **평균 체류 시간**: 3분 이상

### 운영 효율

| 작업 | 소요 시간 | 빈도 |
|------|-----------|------|
| 뉴스 수집 | 자동 | 15분마다 |
| 시그널 분석 | 30-45분 | 매일 |
| 기사 작성 | 30-60분 | 주 3-5회 |
| **총계** | **60-105분/일** | - |

---

**배포 URL**: https://aivesto-dashboard-f30hi3pct-mumushin81-gmailcoms-projects.vercel.app
**GitHub**: https://github.com/mumushin81/aivesto
**최종 업데이트**: 2025-11-14

---

## Phase 4: 엔드투엔드 뉴스 파이프라인 (NEW!)

### 자동화된 수집 및 분석 시스템

Phase 4에서는 Layer 1/2 뉴스 수집부터 NER, 감성 분석, 정책 감지, 증폭 감지까지 전체 워크플로우를 자동화했습니다.

#### 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                  NEWS PIPELINE (E2E)                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 1 (Core Signal)      Layer 2 (Sentiment)         │
│  ├─ Bloomberg               ├─ Fox News                 │
│  ├─ Reuters                 ├─ CNN                       │
│  └─ WSJ ✅                  └─ Yahoo Finance ✅          │
│         │                           │                    │
│         └───────────┬───────────────┘                    │
│                     ▼                                    │
│         ┌───────────────────────┐                        │
│         │  ANALYSIS PIPELINE    │                        │
│         ├───────────────────────┤                        │
│         │ 1. NER (심볼 추출)     │                        │
│         │ 2. Sentiment (VADER)   │                        │
│         │ 3. Policy 감지         │                        │
│         │ 4. Priority 스코어링   │                        │
│         └───────────────────────┘                        │
│                     ▼                                    │
│         ┌───────────────────────┐                        │
│         │ AMPLIFICATION         │                        │
│         │ Layer 1→2 증폭 감지   │                        │
│         └───────────────────────┘                        │
│                     ▼                                    │
│         ┌───────────────────────┐                        │
│         │  SUPABASE (옵션)      │                        │
│         │  자동 저장            │                        │
│         └───────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

#### 빠른 시작

```bash
# 1. 필수 패키지 설치
pip install vaderSentiment feedparser httpx beautifulsoup4

# 2. E2E 파이프라인 실행
python test_e2e_pipeline.py
```

**실행 결과 예시**:
```
============================================================
🚀 Starting News Pipeline
============================================================

📰 Collecting Layer 1 (Bloomberg, Reuters, WSJ)...
  WSJCollector: 60 articles
✅ Layer 1 collected: 60 articles

📺 Collecting Layer 2 (Fox, CNN, Yahoo)...
  FoxCollector: 100 articles
  CNNCollector: 167 articles
  YahooCollector: 87 articles
✅ Layer 2 collected: 354 articles

🔬 Analyzing articles...
✅ Analysis complete: 414 articles

🔊 Detecting amplification...
✅ Amplification detection complete

📊 Pipeline Stats:
  Total Articles: 414
  Layer 1: 60, Layer 2: 354
  High Priority (80+): 174 (42%)
  Policy Signals: 4
  Amplification Ratio: 5.9x
  Duration: 19.2s
```

#### 구성 요소

**1. Layer 1 수집기** (`collectors/`)
- `bloomberg_collector.py` - Bloomberg RSS
- `reuters_collector.py` - Reuters RSS
- `wsj_collector.py` - Wall Street Journal RSS ✅

**2. Layer 2 수집기** (`collectors/`)
- `fox_collector.py` - Fox News RSS (보수 성향)
- `cnn_collector.py` - CNN RSS (진보 성향)
- `yahoo_collector.py` - Yahoo Finance RSS

**3. 분석 엔진** (`analyzers/`)
- `ner_extractor.py` - 종목 심볼 추출 (regex + spaCy)
- `sentiment_analyzer.py` - 감성 분석 (VADER + FinBERT)
- `policy_detector.py` - 정책 변화 감지
- `amplification_detector.py` - 여론 증폭 감지

**4. 통합 파이프라인** (`pipeline/`)
- `news_pipeline.py` - E2E 오케스트레이터

#### 주요 기능

**1. NER (Named Entity Recognition)**
```python
from analyzers.ner_extractor import NERExtractor

ner = NERExtractor(use_spacy=False)  # Regex만 (빠름)
symbols = ner.extract_symbols("Apple (AAPL) and Microsoft (MSFT) partner")
# → ['AAPL', 'MSFT']
```

**2. Sentiment Analysis**
```python
from analyzers.sentiment_analyzer import SentimentAnalyzer

sentiment = SentimentAnalyzer(use_finbert=False)  # VADER만
result = sentiment.analyze("Tesla stock plummeted after CEO resignation")
# → {'sentiment': 'negative', 'score': -0.7, 'confidence': 0.7}
```

**3. Policy Detection**
```python
from analyzers.policy_detector import PolicyDetector

policy = PolicyDetector()
result = policy.detect("SEC introduces new cryptocurrency regulation")
# → {
#   'has_policy_change': True,
#   'change_type': 'new_policy',
#   'affected_sectors': ['Finance'],
#   'confidence': 1.0
# }
```

**4. Amplification Detection**
```python
from analyzers.amplification_detector import AmplificationDetector

amp = AmplificationDetector(time_window_hours=24)
result = amp.detect_amplification(layer1_articles, layer2_articles)
# → {
#   'has_amplification': True,
#   'amplification_ratio': 5.9,  # Layer 2 / Layer 1
#   'amplification_level': 'high',
#   'sentiment_shift': 'neutral_to_negative'
# }
```

#### 우선순위 스코어링 시스템

자동으로 각 기사에 0-100점 우선순위 점수를 부여합니다:

```python
# 점수 계산 로직
score = 50  # 기본

# 1. 정책 변화 (최우선!)
if policy['has_policy_change']:
    if policy['change_type'] == 'new_policy':     # 신규 정책
        score = 95
    elif policy['change_type'] == 'policy_removed':  # 폐지
        score = 95
    elif policy['change_type'] == 'policy_changed':  # 변경
        score = 90

# 2. 감성 강도
if abs(sentiment_score) > 0.5:
    score += 30
elif abs(sentiment_score) > 0.3:
    score += 20

# 3. 심볼 수 (관련성)
if symbol_count > 0:
    score += min(symbol_count * 5, 20)

# 최종: min(score, 100)
```

**결과**:
- **90-100점**: 정책 시그널, 즉시 기사 작성 대상
- **80-89점**: High-priority, 당일 기사 작성
- **70-79점**: Medium-priority, 주간 리포트
- **70점 미만**: Low-priority, 무시

#### 실전 예시

**High-Priority 기사 샘플**:

```
1. [85점] Target Drops DEI Goals and Ends Program
   Source: WSJ (Layer 1)
   Symbols: ['TGT']
   Sentiment: positive (0.68)

2. [85점] Google to Put Warnings on U.K. Businesses
   Source: WSJ (Layer 1)
   Symbols: ['GOOGL']
   Sentiment: negative (-0.85)

3. [95점] SEC Announces New Cryptocurrency Trading Rules
   Source: Reuters (Layer 1)
   Symbols: ['COIN', 'MSTR']
   Sentiment: negative (-0.8)
   Policy: new_policy - 암호화폐 거래 규제 강화
```

#### 테스트 스크립트

```bash
# Phase 1: Layer 1 수집 테스트
python test_layer1_collectors.py
# → WSJ 60개 기사 수집 확인

# Phase 2: 분석 엔진 테스트
python test_phase2_analyzers.py
# → NER, Sentiment, Policy 분석 확인

# Phase 3: Layer 2 + 증폭 테스트
python test_layer2_collectors.py
python test_phase3_amplification.py
# → Fox/CNN/Yahoo 354개 수집, 증폭 비율 확인

# Phase 4: 전체 E2E 테스트
python test_e2e_pipeline.py
# → 414개 기사 수집 → 분석 → 증폭 감지 (19초)
```

#### 성능

- **수집 속도**: ~400개/분 (병렬 처리)
- **분석 속도**: ~1,300개/분
- **전체 파이프라인**: 19초 (414개 기사)
- **메모리 사용**: ~200MB

#### Supabase 자동 저장

```python
from pipeline.news_pipeline import NewsPipeline
from database.supabase_client import SupabaseClient

# DB 연결
db = SupabaseClient()

# 파이프라인 실행 (자동 저장)
pipeline = NewsPipeline(db_client=db, use_finbert=False)
results = pipeline.run(save_to_db=True)

print(f"Saved {results['stats']['saved_count']} articles to Supabase")
```

#### 다음 단계

**Phase 5: 스케줄러 (예정)**
```bash
# Cron job 설정
# 매시간 뉴스 수집 및 분석
0 * * * * cd /path/to/aivesto && python test_e2e_pipeline.py >> logs/pipeline.log 2>&1
```

**Phase 6: 대시보드 연동 (예정)**
- High-priority 기사 자동 표시
- 실시간 통계 업데이트
- 증폭 감지 알림

---

## 다음 단계

- [x] Phase 1: Layer 1 수집기 (WSJ 성공)
- [x] Phase 2: 분석 엔진 (NER, Sentiment, Policy)
- [x] Phase 3: Layer 2 수집기 + 증폭 감지
- [x] Phase 4: E2E 파이프라인
- [ ] Phase 5: 스케줄러 (Cron/APScheduler)
- [ ] Phase 6: 대시보드 실시간 연동
- [ ] 백테스팅 시스템 (시그널 정확도 검증)
- [ ] 모바일 앱 (실시간 시그널 알림)
