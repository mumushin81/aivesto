# API 키 설정 가이드

뉴스 수집 시스템을 완전히 작동시키기 위해 필요한 API 키들을 설정하는 방법입니다.

---

## 📋 필요한 API 키 목록

| API | 용도 | 무료 여부 | 필수도 |
|-----|------|-----------|--------|
| FRED API | 거시경제 데이터 (CPI, 실업률, GDP) | ✅ 무료 | ⭐⭐⭐ 높음 |
| FMP API | 기업 실적, 내부자 매매, 보도자료 | 🔶 제한적 무료 | ⭐⭐⭐ 높음 |
| Alpha Vantage | 원자재 가격, 환율 | ✅ 무료 | ⭐⭐ 중간 |
| yfinance | 주가, ETF, 지수 데이터 | ✅ 무료 (라이브러리) | ⭐⭐⭐ 높음 |

---

## 1️⃣ FRED API (Federal Reserve Economic Data)

### 📌 용도
- CPI (소비자물가지수)
- 실업률
- GDP
- PPI (생산자물가지수)
- 연방기금금리

### 🔑 발급 방법

#### Step 1: 계정 생성
1. 사이트 접속: https://fred.stlouisfed.org/
2. 우측 상단 **"Sign In"** 클릭
3. **"Create new account"** 클릭
4. 이메일, 이름 등 기본 정보 입력

#### Step 2: API 키 발급
1. 로그인 후 **"My Account"** 클릭
2. 좌측 메뉴에서 **"API Keys"** 선택
3. **"Request API Key"** 버튼 클릭
4. API 키가 즉시 발급됨 (예: `abc123def456...`)

#### Step 3: .env 파일에 추가
```bash
FRED_API_KEY=여기에_발급받은_키_붙여넣기
```

### 📊 사용 제한
- **무료**: 무제한
- **Rate Limit**: 일일 요청 제한 없음
- **데이터**: 미국 경제 데이터 50만+ 시계열

### ✅ 테스트
```bash
curl "https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key=YOUR_API_KEY&file_type=json&limit=1"
```

---

## 2️⃣ FMP API (Financial Modeling Prep)

### 📌 용도
- 기업 실적 (EPS, Revenue)
- 내부자 매매 (Insider Trading)
- 보도자료 (Press Releases)
- 애널리스트 추정치

### 🔑 발급 방법

#### Step 1: 계정 생성
1. 사이트 접속: https://site.financialmodelingprep.com/
2. **"Get Your Free API Key"** 클릭
3. 이메일, 비밀번호 입력하여 가입

#### Step 2: API 키 확인
1. 로그인 후 대시보드로 이동
2. **"API Key"** 섹션에서 키 확인
3. 무료 플랜은 하루 250 requests 제공

#### Step 3: .env 파일에 추가
```bash
FMP_API_KEY=여기에_발급받은_키_붙여넣기
```

### 📊 사용 제한

#### 무료 플랜
- ✅ 250 requests/day
- ✅ 기본 실적 데이터
- ✅ 주가 데이터
- ✅ 내부자 매매 데이터

#### 유료 플랜 (필요시)
- **Starter**: $14/월 - 1,000 requests/day
- **Professional**: $29/월 - 무제한
- **Enterprise**: $99/월 - 무제한 + 실시간

### ✅ 테스트
```bash
curl "https://financialmodelingprep.com/api/v3/quote/AAPL?apikey=YOUR_API_KEY"
```

---

## 3️⃣ Alpha Vantage API

### 📌 용도
- 원자재 가격 (Oil, Copper, Gold)
- 환율 (USD/CNY, EUR/USD)
- 기술적 지표

### 🔑 발급 방법

#### Step 1: API 키 발급
1. 사이트 접속: https://www.alphavantage.co/support/#api-key
2. 이메일 입력
3. **"GET FREE API KEY"** 클릭
4. 이메일로 즉시 API 키 수신

#### Step 2: .env 파일에 추가
```bash
ALPHA_VANTAGE_API_KEY=여기에_발급받은_키_붙여넣기
```

### 📊 사용 제한
- **무료**: 25 requests/day
- **Rate Limit**: 5 requests/minute
- **유료 플랜**: $49.99/월 - 120 requests/minute

### 💡 팁
무료 플랜은 제한이 엄격하므로, 필수 데이터만 수집하는 것을 권장합니다.

### ✅ 테스트
```bash
curl "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=YOUR_API_KEY"
```

---

## 4️⃣ yfinance (라이브러리)

### 📌 용도
- 주가 데이터
- ETF 가격
- 중국 지수 (Shanghai Composite, Hang Seng)
- 국제 유가 (WTI, Brent)
- 환율 (DXY, USD/CNY)

### 🔑 설치 방법

#### Step 1: 패키지 설치
```bash
pip install yfinance
```

#### Step 2: 추가 패키지 설치
```bash
pip install feedparser requests beautifulsoup4 loguru
```

### 📊 사용 제한
- **무료**: 완전 무료
- **Rate Limit**: 없음 (Yahoo Finance 데이터 사용)
- **API 키**: 필요 없음

### ✅ 테스트
```python
import yfinance as yf

# NVDA 주가 조회
nvda = yf.Ticker("NVDA")
hist = nvda.history(period="1d")
print(hist)
```

---

## 📝 .env 파일 설정

### Step 1: .env 파일 열기
```bash
cd /Users/jinxin/dev/aivesto
nano .env
```

### Step 2: API 키 추가
`.env` 파일에 다음 내용을 추가하세요:

```bash
# ============================================
# News Collection API Keys
# ============================================

# FRED API (Federal Reserve Economic Data)
# 발급: https://fred.stlouisfed.org/
FRED_API_KEY=your_fred_api_key_here

# FMP API (Financial Modeling Prep)
# 발급: https://site.financialmodelingprep.com/
FMP_API_KEY=your_fmp_api_key_here

# Alpha Vantage API
# 발급: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# ============================================
# Existing Keys (유지)
# ============================================

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_supabase_key_here
SUPABASE_SERVICE_KEY=your_service_role_key_here

# Discord (Midjourney)
DISCORD_BOT_TOKEN=your_discord_bot_token
MIDJOURNEY_CHANNEL_ID=123456789012345678
```

### Step 3: 저장 및 확인
```bash
# nano 편집기에서:
# Ctrl + O (저장)
# Enter (확인)
# Ctrl + X (종료)

# 확인
cat .env | grep API_KEY
```

---

## 🔍 API 키 검증

모든 API 키가 정상 작동하는지 확인하는 스크립트를 실행하세요:

```bash
python scripts/test_api_keys.py
```

이 스크립트는 자동으로 생성되며, 다음을 확인합니다:
- ✅ FRED API 연결
- ✅ FMP API 연결
- ✅ Alpha Vantage API 연결
- ✅ yfinance 작동

---

## 📊 우선순위별 설정 가이드

### 🔴 필수 (즉시 설정)
1. **yfinance 설치** - 무료, 가장 많이 사용
   ```bash
   pip install yfinance
   ```

2. **FRED API** - 무료, 거시경제 데이터 필수
   - 발급: https://fred.stlouisfed.org/

3. **FMP API** - 무료 플랜으로 시작
   - 발급: https://site.financialmodelingprep.com/

### 🟡 권장 (이번 주 내)
4. **Alpha Vantage API** - 원자재 데이터용
   - 발급: https://www.alphavantage.co/
   - 무료 플랜 제한이 있으므로 필요시에만

### 🟢 선택 (나중에)
5. Alpha Vantage 유료 플랜 ($49.99/월) - 더 많은 요청 필요시
6. FMP 유료 플랜 ($29/월) - 실시간 데이터 필요시

---

## 🚨 보안 주의사항

### ❌ 절대 하지 말 것
- GitHub에 .env 파일 커밋하지 마세요
- API 키를 코드에 직접 하드코딩하지 마세요
- API 키를 다른 사람과 공유하지 마세요

### ✅ 해야 할 것
- `.env` 파일은 `.gitignore`에 추가되어 있는지 확인
- API 키가 노출되면 즉시 재발급
- 정기적으로 API 사용량 모니터링

---

## 📞 도움이 필요하신가요?

### API 발급 문제
- FRED: support@stlouisfed.org
- FMP: support@financialmodelingprep.com
- Alpha Vantage: support@alphavantage.co

### 기술 지원
- GitHub Issues: https://github.com/your-repo/issues
- 문서: `/docs/` 폴더 참조

---

## ✅ 설정 완료 확인

모든 API 키를 설정했다면:

```bash
# 1. 의존성 설치
pip install yfinance feedparser requests beautifulsoup4 loguru

# 2. 뉴스 수집 테스트
python scripts/news_collectors/tech_trends_collector.py

# 3. 전체 파이프라인 실행
python scripts/generate_blog_from_signals.py
```

성공하면 자동으로 블로그 글이 생성됩니다! 🎉

---

**다음 단계**: [데이터베이스 스키마 배포 가이드](./DATABASE_SCHEMA_DEPLOYMENT.md)
