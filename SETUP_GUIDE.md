# 설치 및 실행 가이드

## 1단계: API 키 발급

### Finnhub (무료)

1. https://finnhub.io/register 접속
2. 이메일로 가입
3. Dashboard > API Key 복사

### Alpha Vantage (무료)

1. https://www.alphavantage.co/support/#api-key 접속
2. 이메일 입력
3. API Key 이메일로 받기

### Anthropic Claude

1. https://console.anthropic.com/ 접속
2. 계정 생성
3. API Keys 메뉴에서 새 키 생성
4. 크레딧 충전 ($5 minimum)

### Supabase (무료)

1. https://supabase.com/ 접속
2. GitHub로 로그인
3. New Project 클릭
4. 프로젝트 이름, 비밀번호 설정
5. 리전 선택 (Seoul 추천)
6. Settings > API에서 URL과 anon key 복사

## 2단계: 환경 설정

### .env 파일 생성

```bash
cp .env.example .env
nano .env  # 또는 선호하는 에디터
```

### .env 파일 작성

```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# News APIs
FINNHUB_API_KEY=xxxxxxxxxxxxxxxxxx
ALPHA_VANTAGE_API_KEY=XXXXXXXXXXXX

# AI API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx

# 설정 (선택사항)
NEWS_COLLECTION_INTERVAL=900
ANALYSIS_INTERVAL=1800
ARTICLE_GENERATION_INTERVAL=3600
MIN_RELEVANCE_SCORE=70
```

## 3단계: Supabase 데이터베이스 설정

1. Supabase 대시보드 열기
2. SQL Editor 메뉴 클릭
3. New Query 클릭
4. `database/schema.sql` 파일 내용 복사
5. 붙여넣기 후 RUN 클릭
6. 성공 메시지 확인

## 4단계: Python 환경 설정

### 가상환경 생성 (권장)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 의존성 설치

```bash
pip install -r requirements.txt
```

### 로그 디렉토리 생성

```bash
mkdir logs
```

## 5단계: 테스트 실행

### 뉴스 수집 테스트

```bash
python main.py --mode collect
```

출력 예시:
```
2025-11-12 10:00:00 | INFO     | Starting news collection job
2025-11-12 10:00:05 | INFO     | FinnhubCollector collected 15 new news items
2025-11-12 10:00:10 | INFO     | AlphaVantageCollector collected 8 new news items
2025-11-12 10:00:15 | INFO     | RSSCollector collected 23 new news items
2025-11-12 10:00:20 | INFO     | News collection completed: 46 items
```

### 뉴스 분석 테스트

```bash
python main.py --mode analyze
```

출력 예시:
```
2025-11-12 10:05:00 | INFO     | Starting news analysis job
2025-11-12 10:05:05 | INFO     | Found 46 unanalyzed news items
2025-11-12 10:05:30 | INFO     | News analyzed (score: 85): Apple announces new...
2025-11-12 10:06:00 | INFO     | Analysis completed: 12 items
```

### 블로그 글 생성 테스트

```bash
python main.py --mode generate
```

출력 예시:
```
2025-11-12 10:10:00 | INFO     | Starting article generation job
2025-11-12 10:10:05 | INFO     | Generating articles for top 5 symbols: ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
2025-11-12 10:10:30 | INFO     | Article generated: AAPL 관련 최신 뉴스 분석...
2025-11-12 10:11:00 | INFO     | Article generation completed: 5 articles
```

### 전체 파이프라인 1회 실행

```bash
python main.py --mode once
```

## 6단계: 24/7 자동 실행

### 포그라운드 실행

```bash
python main.py --mode run
```

### 백그라운드 실행 (Linux/Mac)

```bash
nohup python main.py --mode run > logs/system.log 2>&1 &
```

### systemd 서비스 등록 (Linux)

`/etc/systemd/system/stock-news.service` 생성:

```ini
[Unit]
Description=Stock News Automation System
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/stock-news-automation
ExecStart=/path/to/venv/bin/python main.py --mode run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

서비스 시작:

```bash
sudo systemctl enable stock-news
sudo systemctl start stock-news
sudo systemctl status stock-news
```

### Docker 실행 (선택사항)

`Dockerfile` 생성:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py", "--mode", "run"]
```

실행:

```bash
docker build -t stock-news-automation .
docker run -d --env-file .env --name stock-news stock-news-automation
```

## 7단계: 모니터링

### 실시간 로그 확인

```bash
tail -f logs/stock_news_$(date +%Y-%m-%d).log
```

### Supabase 대시보드 확인

1. Supabase 대시보드 열기
2. Table Editor 메뉴
3. `news_raw`, `analyzed_news`, `published_articles` 테이블 확인

### 통계 쿼리

```sql
-- 오늘 수집된 뉴스 수
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

## 문제 해결

### API 키 오류

```
Error: Invalid API key
```

해결: `.env` 파일의 API 키 재확인

### Supabase 연결 오류

```
Error: Failed to connect to Supabase
```

해결:
1. `SUPABASE_URL`과 `SUPABASE_KEY` 확인
2. Supabase 프로젝트가 활성화되어 있는지 확인

### Claude API Rate Limit

```
Error: Rate limit exceeded
```

해결:
1. 잠시 대기 후 재시도
2. `ANALYSIS_INTERVAL`과 `ARTICLE_GENERATION_INTERVAL` 증가

### 메모리 부족

대량의 뉴스 처리 시 메모리 부족 가능

해결:
```python
# collectors/base.py에서 배치 사이즈 조정
def collect_and_save(self, batch_size: int = 10)
```

## 다음 단계

1. WordPress/Ghost 블로그 설정
2. Google AdSense 등록
3. SEO 최적화 (sitemap, meta tags)
4. 소셜 미디어 자동 공유 설정
5. 이메일 뉴스레터 연동

## 지원

문제가 발생하면 GitHub Issues에 등록해주세요.
