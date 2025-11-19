# 뉴스 수집기 실행 가이드

6개 카테고리의 뉴스를 수집하고 투자 시그널을 생성하는 방법입니다.

---

## 📋 수집기 목록

| 수집기 | 데이터 소스 | 주요 시그널 | 실행 빈도 권장 |
|--------|------------|-----------|---------------|
| `macro_collector.py` | FRED API, CNBC RSS | 인플레이션, 금리, 실업률 | 매일 1회 (오전 9시) |
| `earnings_collector.py` | yfinance, FMP API | 실적 발표, 가이던스 | 매일 2회 (오전 9시, 오후 5시) |
| `sector_collector.py` | Alpha Vantage, RSS | 원자재, 섹터 ETF | 매일 1회 (오전 9시) |
| `corporate_events_collector.py` | SEC EDGAR, FMP | M&A, 내부자 매매 | 매일 1회 (오전 10시) |
| `tech_trends_collector.py` | TechCrunch, TheVerge, NVIDIA 블로그 | AI 트렌드, GPU | 매일 3회 (오전 9시, 오후 2시, 오후 8시) |
| `geopolitical_collector.py` | Reuters, yfinance | 중국 경제, 환율, 유가 | 매일 1회 (오전 9시) |

---

## 🚀 개별 수집기 실행

### 1️⃣ Tech Trends Collector (AI/테크 뉴스)

**가장 안정적이며 시그널 발견 확률이 높습니다.**

```bash
cd /Users/jinxin/dev/aivesto
python scripts/news_collectors/tech_trends_collector.py
```

**기대 결과**:
```
=== Tech Trends News Collector Started ===
2025-11-17 22:44:12 | INFO | 📰 Fetching TechCrunch RSS...
2025-11-17 22:44:13 | INFO | ✅ TechCrunch: 12 articles collected
2025-11-17 22:44:14 | INFO | 📰 Fetching TheVerge RSS...
2025-11-17 22:44:15 | INFO | ✅ TheVerge: 6 articles collected
2025-11-17 22:44:16 | INFO | 📰 Fetching NVIDIA Blog...
2025-11-17 22:44:18 | INFO | ✅ NVIDIA Blog: 10 articles collected

📊 Summary:
  Total articles: 28
  Signals found: 2
    - MSFT_AI_EXPANSION (impact: 75)
    - NVDA_DATACENTER_DEMAND (impact: 82)

✅ Data saved to Supabase: tech_trends table
```

**시그널 예시**:
- `MSFT_AI_EXPANSION`: Microsoft Copilot 사용자 급증
- `NVDA_DATACENTER_DEMAND`: AI 데이터센터 GPU 수요 증가
- `GOOGL_AI_SEARCH`: Google Gemini 검색 통합
- `META_LLAMA_ADOPTION`: Meta Llama 오픈소스 확산

---

### 2️⃣ Earnings Collector (실적 뉴스)

**실적 발표 시즌(1월, 4월, 7월, 10월)에 가장 유용합니다.**

```bash
python scripts/news_collectors/earnings_collector.py
```

**필요 조건**:
- ✅ `yfinance` 설치됨
- ✅ `FMP_API_KEY` 설정됨

**기대 결과**:
```
=== Earnings News Collector Started ===
2025-11-17 22:45:01 | INFO | 📊 Checking earnings calendar...
2025-11-17 22:45:03 | INFO | ✅ NVDA earnings: EPS $5.20 (beat by 8%)
2025-11-17 22:45:04 | INFO | 🚨 Signal: NVDA_EARNINGS_BEAT (strength: 85)
2025-11-17 22:45:05 | INFO | ✅ AAPL earnings: EPS $1.52 (in-line)
2025-11-17 22:45:06 | INFO | ℹ️  No signal generated (met expectations)

📊 Summary:
  Earnings checked: 30 stocks
  Signals found: 3
    - NVDA_EARNINGS_BEAT (strength: 85)
    - MSFT_REVENUE_GUIDANCE_RAISED (strength: 78)
    - TSLA_MISS_WARNING (strength: -65)
```

**시그널 예시**:
- `NVDA_EARNINGS_BEAT`: 실적 예상치 상회
- `MSFT_REVENUE_GUIDANCE_RAISED`: 가이던스 상향
- `TSLA_MISS_WARNING`: 실적 예상치 하회

---

### 3️⃣ Macro Collector (거시경제)

**경제 지표 발표일에 중요합니다.**

```bash
python scripts/news_collectors/macro_collector.py
```

**필요 조건**:
- ✅ `FRED_API_KEY` 설정됨

**기대 결과**:
```
=== Macro Economic News Collector Started ===
2025-11-17 22:46:01 | INFO | 📈 Fetching CPI data from FRED...
2025-11-17 22:46:02 | INFO | ✅ CPI: 3.7% (consensus: 3.6%, previous: 3.5%)
2025-11-17 22:46:03 | INFO | 🚨 Signal: INFLATION_RISING (impact: HIGH)
2025-11-17 22:46:04 | INFO | 📊 Affected sectors: 금리민감주, 부동산, 금융
2025-11-17 22:46:05 | INFO | 📅 Fetching FOMC schedule...
2025-11-17 22:46:06 | INFO | ✅ Next FOMC meeting: 2025-12-18

📊 Summary:
  Events collected: 4
  Signals found: 1
    - INFLATION_RISING (impact: HIGH)
```

**시그널 예시**:
- `INFLATION_RISING`: CPI 상승 → 금리민감주 약세
- `UNEMPLOYMENT_SPIKE`: 실업률 급등 → 경기 둔화 우려
- `FOMC_HAWKISH`: 연준 매파 발언 → 금리 인상 시그널

---

### 4️⃣ Sector Collector (섹터별 뉴스)

```bash
python scripts/news_collectors/sector_collector.py
```

**필요 조건**:
- ✅ `ALPHA_VANTAGE_API_KEY` 설정됨
- ✅ `yfinance` 설치됨

**기대 결과**:
```
=== Sector News Collector Started ===
2025-11-17 22:47:01 | INFO | 🛢️  Fetching commodity prices...
2025-11-17 22:47:03 | INFO | ✅ Oil (WTI): $82.50 (+3.2%)
2025-11-17 22:47:04 | INFO | 🚨 Signal: OIL_PRICE_SPIKE (impact: MEDIUM)
2025-11-17 22:47:05 | INFO | 📊 Affected: XLE (Energy ETF), CVX, XOM
2025-11-17 22:47:06 | INFO | 📰 Fetching government policy news...
2025-11-17 22:47:08 | INFO | ✅ Policy: EV tax credit extension announced

📊 Summary:
  Commodities tracked: 5
  Policy news: 2
  Signals found: 2
    - OIL_PRICE_SPIKE (impact: MEDIUM)
    - EV_POLICY_POSITIVE (impact: HIGH)
```

**시그널 예시**:
- `OIL_PRICE_SPIKE`: 유가 급등 → 에너지 섹터 강세
- `COPPER_SHORTAGE`: 구리 부족 → FCX, SCCO 수혜
- `SEMICONDUCTOR_POLICY`: 반도체 지원법 → NVDA, AMD 수혜

---

### 5️⃣ Corporate Events Collector

```bash
python scripts/news_collectors/corporate_events_collector.py
```

**필요 조건**:
- ✅ `FMP_API_KEY` 설정됨

**기대 결과**:
```
=== Corporate Events Collector Started ===
2025-11-17 22:48:01 | INFO | 📋 Fetching SEC filings (8-K, 10-Q)...
2025-11-17 22:48:03 | INFO | ✅ AAPL: 8-K filed (Share buyback program $90B)
2025-11-17 22:48:04 | INFO | 🚨 Signal: AAPL_BUYBACK_BULLISH (impact: MEDIUM)
2025-11-17 22:48:05 | INFO | 📊 Fetching insider trading...
2025-11-17 22:48:07 | INFO | ✅ NVDA CEO sold $50M worth of shares
2025-11-17 22:48:08 | INFO | ⚠️  Signal: NVDA_INSIDER_SELL (impact: LOW)

📊 Summary:
  SEC filings: 15
  Insider trades: 8
  Signals found: 3
    - AAPL_BUYBACK_BULLISH (impact: MEDIUM)
    - MSFT_ACQUISITION_ANNOUNCED (impact: HIGH)
    - NVDA_INSIDER_SELL (impact: LOW)
```

**시그널 예시**:
- `AAPL_BUYBACK_BULLISH`: 자사주 매입 프로그램
- `MSFT_ACQUISITION_ANNOUNCED`: M&A 발표
- `TSLA_CEO_CHANGE`: CEO 교체

---

### 6️⃣ Geopolitical Collector

```bash
python scripts/news_collectors/geopolitical_collector.py
```

**필요 조건**:
- ✅ `yfinance` 설치됨

**기대 결과**:
```
=== Geopolitical News Collector Started ===
2025-11-17 22:49:01 | INFO | 🌏 Fetching China economic data...
2025-11-17 22:49:03 | INFO | ✅ Shanghai Composite: +2.1%
2025-11-17 22:49:04 | INFO | ✅ China GDP: 5.2% (beat expectations)
2025-11-17 22:49:05 | INFO | 🚨 Signal: CHINA_RECOVERY (impact: HIGH)
2025-11-17 22:49:06 | INFO | 📊 Affected: AAPL, NVDA, TSLA (China exposure)
2025-11-17 22:49:07 | INFO | 💱 USD/CNY: 7.25 (-0.5%)

📊 Summary:
  China indicators: 3
  Currency movements: 2
  Signals found: 2
    - CHINA_RECOVERY (impact: HIGH)
    - USD_STRENGTH (impact: MEDIUM)
```

**시그널 예시**:
- `CHINA_RECOVERY`: 중국 경기 회복 → 애플, 테슬라 수혜
- `USD_STRENGTH`: 달러 강세 → 수출주 약세
- `OIL_GEOPOLITICAL`: 중동 갈등 → 유가 급등

---

## 🔄 전체 수집기 일괄 실행

### 방법 1: 순차 실행 스크립트

```bash
# 새 스크립트 생성
cat > scripts/run_all_collectors.sh << 'EOF'
#!/bin/bash
cd /Users/jinxin/dev/aivesto

echo "=== Starting All News Collectors ==="
echo ""

echo "1/6 Tech Trends..."
python scripts/news_collectors/tech_trends_collector.py

echo "2/6 Macro Economic..."
python scripts/news_collectors/macro_collector.py

echo "3/6 Earnings..."
python scripts/news_collectors/earnings_collector.py

echo "4/6 Sector..."
python scripts/news_collectors/sector_collector.py

echo "5/6 Corporate Events..."
python scripts/news_collectors/corporate_events_collector.py

echo "6/6 Geopolitical..."
python scripts/news_collectors/geopolitical_collector.py

echo ""
echo "=== All Collectors Completed ==="
EOF

chmod +x scripts/run_all_collectors.sh
./scripts/run_all_collectors.sh
```

---

### 방법 2: 병렬 실행 (빠름)

```bash
# 6개 수집기를 동시에 백그라운드 실행
python scripts/news_collectors/tech_trends_collector.py &
python scripts/news_collectors/macro_collector.py &
python scripts/news_collectors/earnings_collector.py &
python scripts/news_collectors/sector_collector.py &
python scripts/news_collectors/corporate_events_collector.py &
python scripts/news_collectors/geopolitical_collector.py &

# 모든 작업이 끝날 때까지 대기
wait

echo "All collectors completed!"
```

---

## 📊 수집 결과 확인

### Supabase 대시보드에서 확인

1. https://supabase.com/dashboard 접속
2. **Table Editor** 메뉴 클릭
3. 각 테이블 확인:
   - `tech_trends`
   - `macro_news`
   - `earnings_news`
   - `sector_news`
   - `corporate_events`
   - `geopolitical_news`

---

### SQL로 확인

```sql
-- 오늘 수집된 모든 시그널
SELECT * FROM all_trading_signals
WHERE created_at >= CURRENT_DATE
ORDER BY created_at DESC;

-- 카테고리별 수집 건수
SELECT
  (SELECT COUNT(*) FROM tech_trends WHERE created_at >= CURRENT_DATE) AS tech,
  (SELECT COUNT(*) FROM macro_news WHERE created_at >= CURRENT_DATE) AS macro,
  (SELECT COUNT(*) FROM earnings_news WHERE created_at >= CURRENT_DATE) AS earnings,
  (SELECT COUNT(*) FROM sector_news WHERE created_at >= CURRENT_DATE) AS sector,
  (SELECT COUNT(*) FROM corporate_events WHERE created_at >= CURRENT_DATE) AS events,
  (SELECT COUNT(*) FROM geopolitical_news WHERE created_at >= CURRENT_DATE) AS geo;

-- HIGH/CRITICAL 시그널만 조회
SELECT signal_category, signal, impact_level, created_at
FROM all_trading_signals
WHERE impact_level IN ('HIGH', 'CRITICAL')
AND created_at >= CURRENT_DATE
ORDER BY created_at DESC;
```

---

### Python으로 확인

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# 오늘의 모든 시그널 조회
result = supabase.table('all_trading_signals') \
    .select('*') \
    .gte('created_at', 'today') \
    .order('created_at', desc=True) \
    .execute()

print(f"Total signals found: {len(result.data)}")
for signal in result.data:
    print(f"  {signal['signal_category']}: {signal['signal']} (impact: {signal['impact_level']})")
```

---

## 🔧 문제 해결

### 문제 1: ModuleNotFoundError

**증상**: `ModuleNotFoundError: No module named 'yfinance'`

**해결**:
```bash
pip install yfinance feedparser requests beautifulsoup4 loguru python-dotenv supabase
```

---

### 문제 2: API Key Not Found

**증상**: `FRED_API_KEY not found in environment`

**해결**:
1. `.env` 파일 확인:
   ```bash
   cat .env | grep API_KEY
   ```
2. API 키 설정 가이드 참조: `/docs/API_KEYS_SETUP_GUIDE.md`

---

### 문제 3: Rate Limit Exceeded

**증상**: `429 Too Many Requests` 또는 `Rate limit exceeded`

**해결**:
- **Alpha Vantage**: 무료 플랜은 25 req/day, 5 req/min
  - 해결: 수집 빈도를 줄이거나 유료 플랜 ($49.99/월)
- **FMP**: 무료 플랜은 250 req/day
  - 해결: 요청 횟수 모니터링, 필요시 유료 플랜 ($29/월)

---

### 문제 4: Database Connection Error

**증상**: `Could not find the table 'tech_trends' in the schema cache`

**해결**:
1. 데이터베이스 스키마가 배포되었는지 확인:
   ```sql
   SELECT tablename FROM pg_tables WHERE tablename LIKE '%news%';
   ```
2. 배포 안 되었으면: `/docs/DATABASE_SCHEMA_DEPLOYMENT.md` 참조

---

### 문제 5: No Signals Found

**증상**: `📊 Summary: Signals found: 0`

**이것은 정상입니다!**
- 시그널은 특정 조건을 만족할 때만 생성됩니다
- 예: CPI가 전망치보다 0.2%p 이상 높을 때만 `INFLATION_RISING` 시그널 발생
- 뉴스가 수집되어도 시그널이 없을 수 있습니다

**확인 방법**:
```bash
# 데이터는 수집되었는지 확인
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
result = supabase.table('tech_trends').select('count', count='exact').execute()
print(f'Tech trends collected: {result.count}')
"
```

---

## 📅 자동화 스케줄 설정

### cron job으로 매일 자동 실행

```bash
crontab -e
```

다음 내용 추가:

```bash
# 매일 오전 9시: Tech Trends (가장 중요)
0 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/tech_trends_collector.py >> logs/tech_trends.log 2>&1

# 매일 오전 9시 5분: Macro
5 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/macro_collector.py >> logs/macro.log 2>&1

# 매일 오전 9시 10분: Earnings
10 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/earnings_collector.py >> logs/earnings.log 2>&1

# 매일 오전 9시 15분: Sector
15 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/sector_collector.py >> logs/sector.log 2>&1

# 매일 오전 10시: Corporate Events
0 10 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/corporate_events_collector.py >> logs/corporate.log 2>&1

# 매일 오전 9시 20분: Geopolitical
20 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/geopolitical_collector.py >> logs/geopolitical.log 2>&1

# 매일 오후 2시: Tech Trends 추가 수집
0 14 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/tech_trends_collector.py >> logs/tech_trends_afternoon.log 2>&1

# 매일 오후 5시: Earnings 추가 수집 (장 마감 후)
0 17 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/earnings_collector.py >> logs/earnings_evening.log 2>&1
```

**로그 디렉토리 생성**:
```bash
mkdir -p logs
```

**cron 작동 확인**:
```bash
# 오늘의 로그 확인
tail -f logs/tech_trends.log

# 모든 로그 한눈에 보기
tail -f logs/*.log
```

---

## 📈 성능 모니터링

### 수집 성공률 확인

```python
# scripts/check_collection_health.py
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

tables = ['tech_trends', 'macro_news', 'earnings_news', 'sector_news', 'corporate_events', 'geopolitical_news']

print("=== News Collection Health Check ===")
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

for table in tables:
    # 오늘 수집 건수
    today = datetime.now().date().isoformat()
    result = supabase.table(table).select('*', count='exact').gte('created_at', today).execute()

    # 시그널 건수
    signal_col = 'signal' if table != 'earnings_news' else 'signal_strength'
    signals = supabase.table(table).select('*', count='exact').gte('created_at', today).not_.is_(signal_col, 'null').execute()

    print(f"{table:20} | Collected: {result.count:3} | Signals: {signals.count:2}")

print()
print("=== End of Health Check ===")
```

실행:
```bash
python scripts/check_collection_health.py
```

---

## 🎯 다음 단계

뉴스 수집이 완료되면:

1. **시그널 확인**
   ```sql
   SELECT * FROM all_trading_signals
   WHERE created_at >= CURRENT_DATE
   ORDER BY created_at DESC;
   ```

2. **블로그 생성**
   ```bash
   python scripts/generate_blog_from_signals.py
   ```

3. **웹사이트 배포**
   - `public/blog.html` 자동 업데이트됨
   - 로컬 서버로 확인: `cd public && python -m http.server 8000`

---

## 📚 추가 문서

- [API 키 설정 가이드](./API_KEYS_SETUP_GUIDE.md)
- [데이터베이스 스키마 배포](./DATABASE_SCHEMA_DEPLOYMENT.md)
- [빠른 시작 체크리스트](./QUICK_START_CHECKLIST.md)
- [전체 작업 요약](./WORK_SUMMARY_20251117.md)

---

**다음 가이드**: [블로그 자동 생성 가이드](./BLOG_GENERATION_GUIDE.md)
