# 데이터베이스 스키마 배포 가이드

뉴스 수집 시스템을 위한 Supabase 데이터베이스 테이블을 배포하는 방법입니다.

---

## 📋 배포할 테이블 목록

| 테이블명 | 용도 | 예상 레코드 수/월 |
|---------|------|-------------------|
| `macro_news` | 거시경제 데이터 (CPI, 실업률, FOMC) | ~50 |
| `earnings_news` | 기업 실적 및 애널리스트 레포트 | ~300 |
| `sector_news` | 섹터별 뉴스 (원자재, 정책, ETF) | ~200 |
| `corporate_events` | 기업 이벤트 (M&A, SEC, 내부자 매매) | ~150 |
| `tech_trends` | AI/테크 트렌드 | ~500 |
| `geopolitical_news` | 지정학 리스크 | ~100 |

**총 6개 테이블 + 1개 통합 뷰**

---

## 🚀 배포 절차 (5분 소요)

### Step 1: Supabase 대시보드 접속

1. 브라우저에서 https://supabase.com/dashboard 접속
2. 로그인 (GitHub 또는 이메일)
3. 프로젝트 선택: **aivesto** 프로젝트 클릭

---

### Step 2: SQL Editor 열기

1. 좌측 메뉴에서 **"SQL Editor"** 클릭
2. 상단의 **"New query"** 버튼 클릭
3. 빈 SQL 편집기 창이 열림

---

### Step 3: 스키마 파일 복사

1. 터미널에서 스키마 파일 내용 확인:
   ```bash
   cat /Users/jinxin/dev/aivesto/database/news_tables_schema.sql
   ```

2. 또는 파일을 에디터로 열기:
   ```bash
   open /Users/jinxin/dev/aivesto/database/news_tables_schema.sql
   ```

3. 전체 내용 복사 (Cmd+A → Cmd+C)

---

### Step 4: SQL 실행

1. Supabase SQL Editor에 붙여넣기 (Cmd+V)
2. 우측 하단의 **"Run"** 버튼 클릭
3. 실행 완료 대기 (약 10초)

**기대 결과**:
```
Success. No rows returned
```

---

### Step 5: 배포 확인

#### 5.1 테이블 확인

SQL Editor에서 다음 쿼리 실행:

```sql
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE '%news%'
ORDER BY tablename;
```

**기대 결과**:
```
corporate_events
earnings_news
geopolitical_news
macro_news
sector_news
tech_trends
```

#### 5.2 통합 뷰 확인

```sql
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
AND table_name = 'all_trading_signals';
```

**기대 결과**:
```
all_trading_signals
```

#### 5.3 RLS 정책 확인

```sql
SELECT tablename, policyname
FROM pg_policies
WHERE schemaname = 'public'
AND tablename LIKE '%news%';
```

**기대 결과**: 각 테이블마다 2개 정책 (총 12개)
```
macro_news         | Enable read access for all users
macro_news         | Enable insert for authenticated users only
earnings_news      | Enable read access for all users
earnings_news      | Enable insert for authenticated users only
...
```

---

## 🧪 테스트 데이터 삽입

### 테스트 1: Macro News

```sql
INSERT INTO macro_news (
    event_type,
    actual,
    consensus,
    previous,
    impact,
    affected_sectors,
    signal
) VALUES (
    'CPI',
    3.7,
    3.6,
    3.5,
    'HIGH',
    '["금리민감주", "부동산", "금융"]'::jsonb,
    'INFLATION_RISING'
);

SELECT * FROM macro_news ORDER BY created_at DESC LIMIT 1;
```

**기대 결과**: 방금 삽입한 레코드 1개 반환

---

### 테스트 2: Tech Trends

```sql
INSERT INTO tech_trends (
    source,
    headline,
    summary,
    url,
    affected_stocks,
    signal,
    impact_score
) VALUES (
    'TechCrunch',
    'NVIDIA announces new Blackwell GPU',
    'NVIDIA unveils next-generation AI chip with 2.5x performance improvement',
    'https://techcrunch.com/nvidia-blackwell',
    '["NVDA", "AMD", "INTC"]'::jsonb,
    'NVDA_STRONG_BUY',
    95
);

SELECT * FROM tech_trends ORDER BY created_at DESC LIMIT 1;
```

**기대 결과**: 방금 삽입한 레코드 1개 반환

---

### 테스트 3: 통합 뷰 확인

```sql
SELECT * FROM all_trading_signals
ORDER BY created_at DESC
LIMIT 5;
```

**기대 결과**: 위에서 삽입한 2개 시그널 포함 (INFLATION_RISING, NVDA_STRONG_BUY)

---

## 🧹 테스트 데이터 삭제

테스트가 끝나면 삽입한 데이터 삭제:

```sql
DELETE FROM macro_news WHERE signal = 'INFLATION_RISING';
DELETE FROM tech_trends WHERE signal = 'NVDA_STRONG_BUY';
```

---

## 🔒 보안 설정 확인

### RLS (Row Level Security) 활성화 확인

```sql
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE '%news%';
```

**기대 결과**: 모든 테이블의 `rowsecurity` 컬럼이 `true`

---

## 📊 스키마 상세 정보

### 1. macro_news 테이블

```sql
\d macro_news
```

**주요 컬럼**:
- `event_type`: CPI, NFP, FOMC, GDP, PPI
- `actual`, `consensus`, `previous`: 실제값, 전망치, 이전값
- `impact`: LOW, MEDIUM, HIGH, CRITICAL
- `signal`: 자동 생성된 거래 시그널

---

### 2. earnings_news 테이블

**주요 컬럼**:
- `symbol`: 종목 코드 (AAPL, MSFT, NVDA 등)
- `eps_actual`, `eps_estimate`: 실제 EPS, 예상 EPS
- `revenue_actual`, `revenue_estimate`: 실제 매출, 예상 매출
- `guidance`: RAISED, LOWERED, MAINTAINED
- `signal_strength`: 0-100

---

### 3. tech_trends 테이블

**주요 컬럼**:
- `source`: TechCrunch, TheVerge, Reuters 등
- `headline`: 뉴스 제목
- `affected_stocks`: 영향받는 종목 배열 (JSONB)
- `impact_score`: 0-100

---

### 4. all_trading_signals 뷰

**목적**: 모든 카테고리의 시그널을 통합 조회

**쿼리 예시**:
```sql
-- 오늘 발생한 HIGH 이상 시그널
SELECT * FROM all_trading_signals
WHERE impact_level IN ('HIGH', 'CRITICAL')
AND created_at >= CURRENT_DATE
ORDER BY created_at DESC;
```

---

## 🚨 문제 해결

### 문제 1: "permission denied for table"

**원인**: RLS 정책이 올바르게 생성되지 않음

**해결**:
```sql
-- RLS 비활성화 (개발 환경에서만)
ALTER TABLE macro_news DISABLE ROW LEVEL SECURITY;
ALTER TABLE earnings_news DISABLE ROW LEVEL SECURITY;
-- ... 나머지 테이블도 동일
```

---

### 문제 2: "relation already exists"

**원인**: 테이블이 이미 존재함

**해결**:
```sql
-- 기존 테이블 삭제 후 재생성
DROP TABLE IF EXISTS macro_news CASCADE;
DROP TABLE IF EXISTS earnings_news CASCADE;
DROP TABLE IF EXISTS sector_news CASCADE;
DROP TABLE IF EXISTS corporate_events CASCADE;
DROP TABLE IF EXISTS tech_trends CASCADE;
DROP TABLE IF EXISTS geopolitical_news CASCADE;

DROP VIEW IF EXISTS all_trading_signals;

-- 그 다음 스키마 파일 재실행
```

---

### 문제 3: "invalid input syntax for type json"

**원인**: JSONB 데이터 형식 오류

**해결**:
```sql
-- 올바른 JSONB 형식
INSERT INTO tech_trends (affected_stocks)
VALUES ('["NVDA", "AMD"]'::jsonb);  -- ✅ 정확

-- 잘못된 형식
INSERT INTO tech_trends (affected_stocks)
VALUES (['NVDA', 'AMD']);  -- ❌ 오류
```

---

## 📈 성능 최적화

### 인덱스 확인

```sql
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename LIKE '%news%'
ORDER BY tablename;
```

**기대 결과**: 각 테이블마다 다음 인덱스 존재
- `{table}_pkey`: Primary key
- `idx_{table}_created_at`: created_at 컬럼 인덱스
- `idx_{table}_signal`: signal 컬럼 인덱스 (tech_trends 등)

---

### 추가 인덱스 생성 (선택)

고급 쿼리 성능 향상을 위한 복합 인덱스:

```sql
-- 시그널 + 날짜 복합 인덱스
CREATE INDEX idx_tech_trends_signal_date
ON tech_trends(signal, created_at DESC)
WHERE signal IS NOT NULL;

-- 종목 + 날짜 복합 인덱스
CREATE INDEX idx_earnings_symbol_date
ON earnings_news(symbol, earnings_date DESC);
```

---

## 🔄 백업 및 복구

### 백업 생성

Supabase 대시보드:
1. **Database** → **Backups** 메뉴
2. **Create backup** 클릭
3. 백업 완료 확인

또는 SQL로 덤프:
```bash
# 로컬 백업 (pg_dump 필요)
pg_dump -h db.xxx.supabase.co -U postgres -d postgres \
  -t macro_news -t earnings_news -t sector_news \
  -t corporate_events -t tech_trends -t geopolitical_news \
  > news_tables_backup_$(date +%Y%m%d).sql
```

---

### 복구

```sql
-- 백업 SQL 파일 실행
\i /path/to/news_tables_backup_20251117.sql
```

---

## ✅ 배포 체크리스트

모든 항목이 완료되었는지 확인하세요:

- [ ] Supabase SQL Editor에서 `news_tables_schema.sql` 실행
- [ ] 6개 테이블 생성 확인 (`SELECT * FROM pg_tables WHERE ...`)
- [ ] `all_trading_signals` 뷰 생성 확인
- [ ] RLS 정책 12개 생성 확인
- [ ] 테스트 데이터 삽입 및 조회 성공
- [ ] 인덱스 생성 확인
- [ ] 백업 생성 (선택)

---

## 🎯 다음 단계

데이터베이스 배포가 완료되면:

1. **뉴스 수집기 실행**
   ```bash
   python scripts/news_collectors/tech_trends_collector.py
   ```

2. **데이터 확인**
   ```sql
   SELECT COUNT(*) FROM tech_trends;
   SELECT * FROM all_trading_signals LIMIT 10;
   ```

3. **블로그 생성**
   ```bash
   python scripts/generate_blog_from_signals.py
   ```

---

## 📞 도움이 필요하신가요?

### Supabase 관련 문제
- 공식 문서: https://supabase.com/docs
- 커뮤니티: https://github.com/supabase/supabase/discussions

### 프로젝트 관련 문제
- 스키마 파일: `/database/news_tables_schema.sql`
- 문서: `/docs/` 폴더 참조

---

**다음 가이드**: [뉴스 수집기 실행 가이드](./NEWS_COLLECTORS_GUIDE.md)
