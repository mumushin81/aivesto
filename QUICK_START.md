# ⚡ 빠른 시작 가이드

10분 안에 시스템을 실행하는 단계별 가이드입니다.

---

## 📋 체크리스트

시작하기 전에 다음을 준비하세요:

- [ ] Python 3.9 이상 설치
- [ ] pip 설치
- [ ] 신용카드 (Anthropic Claude API용, $5 최소 충전)
- [ ] 이메일 계정 (API 가입용)

---

## 🚀 5단계로 시작하기

### 1단계: API 키 발급 (5분)

#### A. Finnhub (무료, 1분)
```
1. https://finnhub.io/register 접속
2. 이메일 가입
3. Dashboard에서 API Key 복사
4. 메모장에 저장
```

#### B. Alpha Vantage (무료, 1분)
```
1. https://www.alphavantage.co/support/#api-key 접속
2. 이메일 입력 후 "GET FREE API KEY" 클릭
3. 화면에 표시된 키 복사
4. 메모장에 저장
```

#### C. Anthropic Claude (유료, 2분)
```
1. https://console.anthropic.com 접속
2. 계정 생성 (Google 로그인 가능)
3. Settings > Billing > Add Credits ($20 충전 권장)
4. API Keys > Create Key
5. ⚠️ 생성된 키 즉시 복사 (한 번만 표시!)
6. 메모장에 저장
```

#### D. Supabase (무료, 1분)
```
1. https://supabase.com 접속
2. GitHub로 로그인
3. New Project 클릭
4. 프로젝트 이름: stock-news-db
5. 비밀번호 설정 (저장 필수!)
6. Region: Northeast Asia (Seoul)
7. 2-3분 대기 후 Settings > API에서 URL과 anon key 복사
8. 메모장에 저장
```

---

### 2단계: 프로젝트 설정 (2분)

```bash
# 프로젝트 디렉토리로 이동
cd /Users/jinxin/dev/stock-news-automation

# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (메모장에서 복사한 키 입력)
nano .env
```

**.env 파일 작성:**
```env
SUPABASE_URL=https://여기에_복사한_URL.supabase.co
SUPABASE_KEY=여기에_복사한_anon_key

FINNHUB_API_KEY=여기에_복사한_finnhub_key
ALPHA_VANTAGE_API_KEY=여기에_복사한_alphavantage_key

ANTHROPIC_API_KEY=sk-ant-api03-여기에_복사한_claude_key

NEWS_COLLECTION_INTERVAL=900
ANALYSIS_INTERVAL=1800
ARTICLE_GENERATION_INTERVAL=3600
MIN_RELEVANCE_SCORE=70
```

---

### 3단계: 의존성 설치 (1분)

```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 로그 디렉토리 생성
mkdir logs
```

---

### 4단계: 데이터베이스 설정 (1분)

```bash
# 1. Supabase 대시보드 열기
# https://supabase.com/dashboard/project/YOUR_PROJECT_ID

# 2. SQL Editor 메뉴 클릭

# 3. New query 클릭

# 4. schema.sql 내용 복사
cat database/schema.sql

# 5. SQL Editor에 붙여넣기

# 6. RUN 버튼 클릭 (Cmd/Ctrl + Enter)

# 7. "Success" 메시지 확인

# 8. Table Editor에서 테이블 3개 확인:
#    - news_raw
#    - analyzed_news
#    - published_articles
```

---

### 5단계: 테스트 실행 (1분)

```bash
# 전체 파이프라인 1회 실행
python main.py --mode once
```

**예상 출력:**
```
2025-11-12 22:00:00 | INFO | Starting Stock News Automation System
2025-11-12 22:00:01 | INFO | === Starting news collection job ===
2025-11-12 22:00:05 | INFO | FinnhubCollector collected 15 new news items
2025-11-12 22:00:10 | INFO | AlphaVantageCollector collected 8 new news items
2025-11-12 22:00:15 | INFO | RSSCollector collected 23 new news items
2025-11-12 22:00:20 | INFO | === News collection completed: 46 items ===

2025-11-12 22:00:25 | INFO | === Starting news analysis job ===
2025-11-12 22:00:30 | INFO | Found 46 unanalyzed news items
2025-11-12 22:01:00 | INFO | News analyzed (score: 85): Apple announces...
2025-11-12 22:02:00 | INFO | === Analysis completed: 12 items ===

2025-11-12 22:02:05 | INFO | === Starting article generation job ===
2025-11-12 22:02:10 | INFO | Generating articles for top 5 symbols...
2025-11-12 22:03:00 | INFO | Article generated: AAPL 관련 최신 뉴스 분석
2025-11-12 22:05:00 | INFO | === Article generation completed: 5 articles ===
```

---

## ✅ 성공 확인

### Supabase에서 데이터 확인

1. Supabase 대시보드 > Table Editor
2. `news_raw` 테이블 확인 → 뉴스 데이터 있어야 함
3. `analyzed_news` 테이블 확인 → 분석 데이터 있어야 함
4. `published_articles` 테이블 확인 → 생성된 글 있어야 함

### 생성된 블로그 글 확인

```sql
-- Supabase SQL Editor에서 실행
SELECT title, created_at
FROM published_articles
ORDER BY created_at DESC
LIMIT 5;
```

---

## 🎯 24/7 자동 실행

모든 테스트가 성공했다면:

```bash
# 포그라운드 실행 (로그 확인하며)
python main.py --mode run

# 백그라운드 실행 (Mac/Linux)
nohup python main.py --mode run > logs/system.log 2>&1 &

# 실행 중인 프로세스 확인
ps aux | grep main.py

# 중지하기
pkill -f main.py
```

---

## 📊 모니터링

### 실시간 로그 확인
```bash
tail -f logs/stock_news_$(date +%Y-%m-%d).log
```

### 통계 확인
```sql
-- Supabase SQL Editor에서 실행

-- 오늘 수집된 뉴스
SELECT COUNT(*) FROM news_raw
WHERE created_at > CURRENT_DATE;

-- 높은 관련성 뉴스
SELECT title, relevance_score, affected_symbols
FROM analyzed_news
WHERE relevance_score >= 80
ORDER BY created_at DESC
LIMIT 10;

-- 인기 종목
SELECT * FROM popular_symbols;

-- 오늘 생성된 글
SELECT title, created_at
FROM published_articles
WHERE created_at > CURRENT_DATE
ORDER BY created_at DESC;
```

---

## 🔧 실행 모드

```bash
# 전체 시스템 (24/7 자동)
python main.py --mode run

# 모든 작업 1회 실행 (테스트용)
python main.py --mode once

# 뉴스 수집만
python main.py --mode collect

# 뉴스 분석만
python main.py --mode analyze

# 블로그 글 생성만
python main.py --mode generate
```

---

## ⚠️ 문제 해결

### "Invalid API key" 오류
```bash
# .env 파일 확인
cat .env | grep API_KEY

# 공백이나 특수문자 확인
# 키를 다시 복사해서 입력
```

### "Failed to connect to Supabase" 오류
```bash
# URL과 KEY 확인
cat .env | grep SUPABASE

# Supabase 프로젝트가 실행 중인지 확인
# 브라우저에서 Supabase 대시보드 접속
```

### "Rate limit exceeded" 오류
```bash
# Alpha Vantage 제한 (25 req/일)
# .env 파일 수정
NEWS_COLLECTION_INTERVAL=3600  # 1시간으로 변경

# 또는 Alpha Vantage 비활성화
# scheduler/jobs.py에서 주석 처리
```

### 뉴스가 수집되지 않음
```bash
# 개별 수집기 테스트
python main.py --mode collect

# 로그 확인
tail -f logs/stock_news_$(date +%Y-%m-%d).log | grep ERROR
```

### Claude API 비용 걱정
```bash
# .env 파일 수정으로 비용 절감
MIN_RELEVANCE_SCORE=80  # 더 엄격한 필터링
ANALYSIS_INTERVAL=3600  # 분석 간격 늘리기
ARTICLE_GENERATION_INTERVAL=7200  # 글 생성 간격 늘리기

# 예상 비용: $100/월 → $30/월
```

---

## 💰 예상 비용

### 최소 구성 (무료 + AI 최소)
- Finnhub: 무료
- Alpha Vantage: 무료 (또는 비활성화)
- Supabase: 무료
- Claude API: $20-30/월
- **총: $20-30/월**

### 권장 구성
- Finnhub: 무료
- Alpha Vantage: 무료
- Supabase: 무료
- Claude API: $30-50/월 (하루 50개 뉴스)
- **총: $30-50/월**

### 프리미엄 구성
- Finnhub: $449/월 (선택)
- Alpha Vantage: $49.99/월 (선택)
- Supabase: $25/월 (선택)
- Claude API: $100/월 (대량 처리)
- **총: $624/월**

---

## 📚 다음 단계

1. **블로그 플랫폼 설정**
   - Ghost CMS 또는 WordPress 설치
   - 도메인 연결
   - Google Analytics 설정

2. **SEO 최적화**
   - Sitemap 생성
   - Google Search Console 등록
   - 메타 태그 최적화

3. **수익화**
   - Google AdSense 신청
   - Affiliate 링크 추가
   - 프리미엄 컨텐츠 제공

4. **자동화 강화**
   - WordPress 자동 발행
   - 소셜 미디어 자동 공유
   - 이메일 뉴스레터 발송

---

## 🆘 도움이 필요하신가요?

- 📖 **상세 가이드:** `API_KEYS_GUIDE.md`
- 📘 **전체 문서:** `README.md`
- 🔧 **설치 가이드:** `SETUP_GUIDE.md`

---

**축하합니다! 🎉**

AI 기반 주식 뉴스 블로그 시스템이 성공적으로 실행되었습니다!
