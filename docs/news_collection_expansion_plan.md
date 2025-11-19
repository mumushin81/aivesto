# 미국 주식 투자 뉴스 수집 시스템 확장 계획

## 목표
6대 뉴스 카테고리 기반 자동 시그널 포착 시스템 구축

---

## 1. 거시경제(Macro) 뉴스 수집

### 수집 대상
- **CPI, PPI** (소비자/생산자 물가지수)
- **고용지표**: NFP (Non-Farm Payroll), 실업률
- **FOMC**: 의사록, 금리 결정
- **소매판매, 제조업 PMI**
- **GDP 성장률**
- **소비자신뢰지수**
- **미 재무부/연준 발언**: Yellen, Fed speakers

### 데이터 소스
- CNBC Economy API
- Bloomberg Markets
- Investing.com Economic Calendar API
- MarketWatch
- Reuters U.S. Economics API
- 미국 정부 공식 리포트: BEA, BLS

### 시그널 포인트
- ✅ 예상치 대비 강/약 (Consensus vs Actual)
- ✅ 위험선호/위험회피 전환
- ✅ 금리 전망 변화 → 성장주/가치주 흐름
- ✅ 장 시작 전 선행지표

### 자동매매 시그널 예시
```python
if CPI_actual > CPI_consensus:
    signal = "TECH_GROWTH_STOCK_SHORT_TERM_DOWN"
    affected_stocks = ["NVDA", "TSLA", "META", "GOOGL"]

if NFP_actual > NFP_consensus:
    signal = "DOLLAR_STRONG_NASDAQ_DOWN"
    affected_indices = ["QQQ", "TQQQ"]
```

---

## 2. 실적(Earnings) 관련 뉴스

### 수집 대상
- **Earnings Release**
- **Earnings Call Transcript** (SeekingAlpha)
- **EPS, Revenue 서프라이즈/쇼크**
- **가이던스 상향/하향**
- **애널리스트 Target Price 변경**

### 데이터 소스
- CNBC Earnings API
- NASDAQ Earnings Calendar
- Yahoo Finance Press Releases
- Bloomberg
- Seeking Alpha (Premium)

### 시그널 포인트
- ✅ EPS/매출 서프라이즈 → 단기 모멘텀
- ✅ 가이던스 상향 → 중기 상승
- ✅ 목표가 상향 → 강한 중기 시그널
- ✅ 악재 실적 → 갭다운 + 단기 하락

### 자동매매 시그널 예시
```python
if AAPL.EPS_beat and AAPL.revenue_beat:
    signal = "STRONG_BUY"
    expected_move = "+3% avg"

if TSLA.guidance == "DOWN":
    signal = "STRONG_SELL"
    expected_move = "gap_down + momentum_down"
```

---

## 3. 산업군(섹터)별 뉴스

### 수집 대상
- **미국 정부 정책**: 반도체법, IRA 보조금, EV 정책
- **지정학적 리스크**: 국제 분쟁
- **원자재 가격**: Oil, Copper, Lithium, Natural Gas
- **공급망 이슈**: 글로벌 반도체 공급
- **산업 리포트**: AI, 클라우드, 자동차, 방산

### 데이터 소스
- Reuters Sector News
- Bloomberg Industries
- WSJ Markets
- OilPrice.com (에너지)
- Semiconductor Engineering, TSMC Press
- TechCrunch (빅테크/스타트업)

### 시그널 포인트
- ✅ 정부 정책 → 섹터 단기 폭등
- ✅ 원자재 급등 → 제조기업 비용 증가 → 중기 하락
- ✅ 반도체 공급 이슈 → NVDA, AMD, TSM 강세

### 자동매매 시그널 예시
```python
if "CHIPS Act funding" in news:
    signal = "SEMICONDUCTOR_SECTOR_RALLY"
    affected = ["NVDA", "AMD", "INTC", "TSM"]

if oil_price_change > 5%:
    signal = "ENERGY_SECTOR_MOVE"
    affected = ["XOM", "CVX", "OXY"]
    reverse_affected = ["AIRLINES", "TRANSPORT"]
```

---

## 4. 기업 PR + 사고/이슈성 뉴스

### 수집 대상
- **M&A 발표**
- **SEC 조사, 소송**
- **CEO 교체**
- **제품 출시/리콜**
- **파산 신청/자금조달**
- **내부자 매매 (Insider Trading)**

### 데이터 소스
- SEC 8-K, 10-K 필링
- BusinessWire
- GlobeNewswire
- Reuters Company News
- MarketWatch "Company News"

### 시그널 포인트
- ✅ 제품 리콜 → 즉각 하락
- ✅ CEO 사임 → 단기 하락
- ✅ 빅테크 M&A → 피인수 급등 / 인수 기업 조정
- ✅ 내부자 대량 매수 → 중기 상승

### 자동매매 시그널 예시
```python
if "product recall" in news:
    signal = "IMMEDIATE_SELL"

if "CEO resignation" in news:
    signal = "SHORT_TERM_DOWN"

if insider_buying > threshold:
    signal = "MEDIUM_TERM_BUY"
```

---

## 5. AI·오픈소스·테크 트렌드 뉴스

### 수집 대상
- **AI 반도체 기술 발표**
- **기업 AI 서비스 추가/확장**
- **서버 GPU 수요 증가**
- **오픈소스 모델 발표**
- **빅테크 협력/파트너십**

### 데이터 소스
- TechCrunch
- The Verge
- Reuters Tech
- Bloomberg Tech
- NVIDIA 공식 블로그
- OpenAI, Anthropic, Google AI Blog

### 시그널 포인트
- ✅ "NVIDIA GPU 공급 부족" → NVDA 강세
- ✅ "MSFT 기업용 AI 유료화" → MSFT 단기 상승
- ✅ "중국 반도체 제재 확대" → 미국 AI 반도체 강세

### 자동매매 시그널 예시
```python
if "GPU shortage" in news:
    signal = "NVDA_STRONG_BUY"

if "Microsoft AI monetization" in news:
    signal = "MSFT_SHORT_TERM_UP"

if "China semiconductor ban" in news:
    signal = "US_AI_CHIP_RALLY"
    affected = ["NVDA", "AMD", "INTC"]
```

---

## 6. 국제 뉴스 & 지정학적 리스크

### 수집 대상
- **중국 경제 지표**
- **홍콩·상해 지수 급등락**
- **러시아-우크라이나 전쟁**
- **중동 분쟁**
- **국제유가 급등락**
- **환율 변동**

### 데이터 소스
- Reuters World
- Bloomberg Asia
- CNBC International
- Trading Economics
- OANDA (환율)
- OilPrice.com

### 시그널 포인트
- ✅ 중국 경기침체 → AAPL, TSLA, 반도체 하락
- ✅ 전쟁/분쟁 확대 → 방산 상승, 유가 상승
- ✅ 달러지수 강세 → 성장주 하락

### 자동매매 시그널 예시
```python
if china_gdp_growth < 4%:
    signal = "CHINA_EXPOSURE_DOWN"
    affected = ["AAPL", "TSLA", "NVDA"]

if war_escalation:
    signal = "DEFENSE_RALLY_OIL_UP"
    affected_up = ["LMT", "RTX", "GD", "XOM"]
    affected_down = ["TECH_GROWTH"]

if DXY > 105:
    signal = "GROWTH_STOCK_DOWN"
    affected = ["QQQ", "ARKK"]
```

---

## 기술 구현 계획

### Phase 1: 데이터 수집 인프라 (2주)
```python
# scripts/news_collectors/
├── macro_collector.py          # 거시경제
├── earnings_collector.py       # 실적
├── sector_collector.py         # 산업군
├── corporate_events_collector.py  # 기업 이슈
├── tech_trends_collector.py    # AI/테크
└── geopolitical_collector.py   # 국제 뉴스
```

### Phase 2: 시그널 분석 엔진 (2주)
```python
# scripts/signal_engine/
├── macro_signal_analyzer.py
├── earnings_signal_analyzer.py
├── sector_signal_analyzer.py
├── event_signal_analyzer.py
├── tech_signal_analyzer.py
└── geo_signal_analyzer.py
```

### Phase 3: 자동매매 시그널 생성 (1주)
```python
# scripts/trading_signals/
├── signal_aggregator.py        # 모든 시그널 통합
├── signal_ranker.py            # 시그널 우선순위
└── signal_publisher.py         # 블로그/알림 발행
```

### Phase 4: 블로그 자동 발행 (1주)
```python
# 실시간 시그널 → 블로그 자동 생성 → Vercel 배포
```

---

## 데이터베이스 스키마 확장

### 새 테이블

```sql
-- 거시경제 뉴스
CREATE TABLE macro_news (
    id UUID PRIMARY KEY,
    event_type TEXT,  -- 'CPI', 'NFP', 'FOMC' 등
    actual NUMERIC,
    consensus NUMERIC,
    previous NUMERIC,
    impact TEXT,  -- 'HIGH', 'MEDIUM', 'LOW'
    affected_sectors JSONB,
    created_at TIMESTAMP
);

-- 실적 뉴스
CREATE TABLE earnings_news (
    id UUID PRIMARY KEY,
    symbol TEXT,
    quarter TEXT,
    eps_actual NUMERIC,
    eps_consensus NUMERIC,
    revenue_actual NUMERIC,
    revenue_consensus NUMERIC,
    guidance TEXT,  -- 'UP', 'DOWN', 'MAINTAIN'
    signal_strength TEXT,
    created_at TIMESTAMP
);

-- 섹터 뉴스
CREATE TABLE sector_news (
    id UUID PRIMARY KEY,
    sector TEXT,  -- 'SEMICONDUCTOR', 'AI', 'ENERGY' 등
    event_type TEXT,
    impact_level TEXT,
    affected_stocks JSONB,
    signal TEXT,
    created_at TIMESTAMP
);

-- 기업 이슈 뉴스
CREATE TABLE corporate_events (
    id UUID PRIMARY KEY,
    symbol TEXT,
    event_type TEXT,  -- 'M&A', 'CEO_CHANGE', 'RECALL' 등
    event_description TEXT,
    signal TEXT,
    severity TEXT,
    created_at TIMESTAMP
);

-- AI/테크 트렌드
CREATE TABLE tech_trends (
    id UUID PRIMARY KEY,
    trend_type TEXT,  -- 'AI_CHIP', 'GPU_DEMAND', 'PARTNERSHIP' 등
    companies JSONB,
    signal TEXT,
    impact_score NUMERIC,
    created_at TIMESTAMP
);

-- 지정학적 뉴스
CREATE TABLE geopolitical_news (
    id UUID PRIMARY KEY,
    region TEXT,  -- 'CHINA', 'MIDDLE_EAST', 'RUSSIA' 등
    event_type TEXT,
    affected_sectors JSONB,
    signal TEXT,
    created_at TIMESTAMP
);
```

---

## 예상 효과

### 시그널 포착 수 증가
- **현재**: ~5-10개/일 (주요 기업 뉴스만)
- **확장 후**: ~50-100개/일 (6대 카테고리 전체)

### 매매 정확도 향상
- 거시경제 선행지표 포착 → 섹터 로테이션 예측
- 실적 시즌 자동 분석 → 서프라이즈 포착
- 지정학적 리스크 조기 감지 → 방어 포지션

### 블로그 콘텐츠 다양화
- 기업 뉴스뿐 아니라 매크로, 섹터, 테크 트렌드 분석 글 자동 생성
- 일일 시장 요약 리포트 자동 발행

---

## 다음 단계

1. ✅ 현재 이미지 생성 완료 대기
2. 🔄 6대 카테고리 뉴스 수집기 구현
3. 🔄 시그널 분석 엔진 개발
4. 🔄 자동매매 시그널 생성 시스템
5. 🔄 블로그 자동 발행 파이프라인
