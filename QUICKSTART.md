# 🚀 빠른 시작 가이드 (Quick Start Guide)

투자 시그널 감지 & 블로거 통합 시스템을 5분 만에 시작하세요!

---

## ✅ 사전 요구사항

### 필수 설정
```bash
# Python 3.9 이상 필요
python --version

# 필수 라이브러리 설치
pip install anthropic supabase loguru schedule flask flask-cors
```

### API 키 준비
1. **Anthropic API Key** - https://console.anthropic.com
2. **Supabase URL & Key** - https://supabase.com
3. **Finnhub API Key** (선택) - https://finnhub.io
4. **Gmail App Password** (이메일 알림용, 선택)

---

## 📝 Step 1: 환경 설정 (2분)

### 파일 생성: `.env`

```bash
# 프로젝트 루트에 .env 파일 생성
cat > .env << 'EOF'
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# APIs
ANTHROPIC_API_KEY=your_anthropic_key
FINNHUB_API_KEY=your_finnhub_key

# Email Alerts (선택사항)
ALERT_RECIPIENTS=your_email@example.com
SENDER_EMAIL=noreply@aivesto.com
SENDER_PASSWORD=your_gmail_app_password

# 수집 간격 (초)
NEWS_COLLECTION_INTERVAL=900
ANALYSIS_INTERVAL=1800
ARTICLE_GENERATION_INTERVAL=3600

# 최소 관련성 점수
MIN_RELEVANCE_SCORE=70
EOF
```

### 환경 변수 확인
```bash
# .env 파일 확인
cat .env

# 또는 직접 내보내기
export ANTHROPIC_API_KEY="your_key_here"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
```

---

## 🔧 Step 2: 데이터베이스 설정 (1분)

### Supabase 테이블 생성

**1단계: Supabase 콘솔에서 SQL 실행**

```sql
-- news_raw 테이블
CREATE TABLE IF NOT EXISTS news_raw (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT,
    title TEXT,
    url TEXT UNIQUE,
    content TEXT,
    published_at TIMESTAMP,
    symbols TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- analyzed_news 테이블 (SIGNAL LEVEL 추가)
CREATE TABLE IF NOT EXISTS analyzed_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_news_id UUID REFERENCES news_raw(id),
    relevance_score INT,
    affected_symbols TEXT[],
    price_impact TEXT,
    importance TEXT,
    signal_level INT DEFAULT 4,
    analysis JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- published_articles 테이블
CREATE TABLE IF NOT EXISTS published_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    content TEXT,
    analyzed_news_ids UUID[],
    wordpress_id INT,
    published_at TIMESTAMP,
    views INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT now()
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX idx_news_raw_created ON news_raw(created_at);
CREATE INDEX idx_analyzed_signal_level ON analyzed_news(signal_level);
CREATE INDEX idx_analyzed_relevance ON analyzed_news(relevance_score);
```

---

## 🎯 Step 3: 첫 실행 (2분)

### 옵션 1: 전체 시스템 한 번 실행 (권장)

```bash
# 모든 작업을 순차적으로 실행
python main.py --mode once

# 예상 출력:
# === Running all jobs once ===
# === Starting news collection job ===
# === News collection completed: 20 items ===
# === Starting news analysis job (AUTO MODE) ===
# 🤖 Starting automated analysis for 20 news items...
# ✅ Automated analysis completed: 15/20 items analyzed
# === Analysis completed: 15 items ===
# === Starting article generation job ===
# === Article generation completed: 2 articles (Tier: tier_1) ===
# === Starting cleanup job ===
# === Cleanup completed ===
```

### 옵션 2: 개별 작업 실행

```bash
# 뉴스 수집만
python main.py --mode collect

# 뉴스 분석만 (자동 모드 - Claude API)
python main.py --mode analyze

# 블로그 글 생성 (Tier 1)
python main.py --mode generate --tier tier_1

# 블로그 글 생성 (Tier 2)
python main.py --mode generate --tier tier_2
```

### 옵션 3: 백그라운드에서 계속 실행

```bash
# 무한 루프 실행 (스케줄러 활성화)
python main.py --mode run

# Ctrl+C로 중단
# 또는 별도의 터미널에서 계속 작업 가능
```

---

## 📊 Step 4: 대시보드 확인 (즉시)

### 대시보드 서버 시작

```bash
# 별도 터미널에서
python dashboard/server.py

# 출력:
# * Running on http://0.0.0.0:5000
```

### 브라우저에서 접속

```
http://localhost:5000
```

**대시보드 화면**:
- ✅ 신호 레벨별 통계 (Level 1-4)
- ✅ 가격 영향 분석 (상승/하락/중립)
- ✅ 트렌딩 종목 (신호 기반)
- ✅ 긴급 신호 리스트
- ✅ 높은 우선순위 신호
- ✅ 실시간 자동 새로고침 (30초)

### API 엔드포인트 테스트

```bash
# 긴급 신호 조회
curl http://localhost:5000/api/signals/urgent

# 트렌딩 종목 조회
curl http://localhost:5000/api/trending-symbols

# 대시보드 요약
curl http://localhost:5000/api/dashboard

# 응답 형식 (JSON):
{
  "level": 1,
  "count": 5,
  "signals": [
    {
      "title": "Apple Q4 earnings beat expectations",
      "affected_symbols": ["AAPL"],
      "relevance_score": 95,
      "signal_level": 1
    }
  ]
}
```

---

## 📧 Step 5: 이메일 알림 설정 (선택사항)

### Gmail 앱 비밀번호 생성

1. Google 계정: https://myaccount.google.com
2. 보안 → 앱 비밀번호
3. "메일" + "Windows 컴퓨터" 선택
4. 생성된 16자리 비밀번호 복사

### 환경 변수 설정

```bash
# .env에 추가
ALERT_RECIPIENTS=investor@example.com
SENDER_EMAIL=your_gmail@gmail.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx
```

### 테스트 이메일 발송

```python
# test_email.py 실행
from alerts import EmailAlertService

service = EmailAlertService()
service.send_daily_digest(['your_email@example.com'], hours=24)
print("✅ 테스트 이메일 발송 완료")
```

---

## 🎓 다음 단계

### 1. 블로거 추천 확인

```python
from blogger import ArticleQueueManager

queue = ArticleQueueManager()

# Tier 1 추천 (긴급 신호)
recommendations = queue.get_recommended_signals(tier='tier_1', limit=20)
for rec in recommendations[:5]:
    print(f"📝 {rec['title'][:60]}")

# 스마트 추천
smart = queue.get_smart_recommendations()
print(f"오늘의 제안: {len(smart['daily_suggestions'])} 종목")
```

### 2. 신호별 블로그 글 작성

1. 대시보드에서 "긴급 신호" 확인
2. `queue_manager.get_urgent_recommendations()` 로 신호 조회
3. 신호 기반으로 블로그 글 작성
4. 발행 후 `mark_signal_published()` 호출

### 3. 대시보드 커스터마이징

**`dashboard/static/index.html`** 수정:
- 색상 변경
- 새로운 섹션 추가
- 차트 추가

### 4. 스케줄러 최적화

**`config/settings.py`** 수정:
```python
# 분석 배치 크기 증가
NEWS_COLLECTION_INTERVAL = 900  # 15분
ANALYSIS_INTERVAL = 1800        # 30분
ARTICLE_GENERATION_INTERVAL = 3600  # 1시간
```

---

## 🐛 문제 해결

### 1. "Anthropic API 오류" 또는 "API 키 잘못됨"

```bash
# API 키 확인
echo $ANTHROPIC_API_KEY

# 없으면 설정
export ANTHROPIC_API_KEY="sk-ant-..."

# 또는 .env 파일 확인
cat .env | grep ANTHROPIC
```

### 2. "Supabase 연결 오류"

```bash
# URL과 키 확인
cat .env | grep SUPABASE

# Supabase 콘솔에서:
# 1. 프로젝트 설정 → API
# 2. URL과 Key (anon public) 복사
# 3. .env 업데이트
```

### 3. "뉴스가 분석되지 않음"

```bash
# 로그 확인
tail -f logs/stock_news_*.log

# 원인:
# - 뉴스가 수집되지 않음: NEWS_COLLECTION_INTERVAL 줄이기
# - API 할당량 초과: 기다리기
# - 네트워크 오류: 인터넷 연결 확인
```

### 4. "대시보드가 표시되지 않음"

```bash
# Flask 서버 확인
ps aux | grep "dashboard/server.py"

# 포트 5000 사용 중:
lsof -i :5000
kill -9 <PID>

# Flask 재시작
python dashboard/server.py
```

---

## 📊 시스템 모니터링

### 로그 확인

```bash
# 실시간 로그
tail -f logs/stock_news_*.log

# 특정 날짜 로그
ls -la logs/stock_news_2025-11-13.log

# 에러만 필터링
grep ERROR logs/stock_news_*.log
```

### 분석 통계

```python
# 현재 분석 상태 확인
from database.supabase_client import SupabaseClient

db = SupabaseClient()

# 레벨별 신호 개수
for level in [1, 2, 3, 4]:
    signals = db.get_signals_by_level(level, hours=24, limit=100)
    print(f"Level {level}: {len(signals)} signals")

# 트렌딩 종목
trending = db.get_trending_symbols(hours=24, limit=10)
for s in trending:
    print(f"{s['symbol']}: {s['count']} signals")
```

---

## 🎯 성공 확인

시스템이 제대로 작동하면:

✅ **1단계**: 뉴스 수집 완료 (20+ items)
✅ **2단계**: 자동 분석 완료 (15+ analyzed)
✅ **3단계**: 신호 분류 완료 (Level 1-4 표시)
✅ **4단계**: 대시보드 로드 (http://localhost:5000)
✅ **5단계**: 긴급 신호 표시 (빨간색 🔴)

---

## 📞 추가 도움

### 로그 읽기

```
2025-11-13 10:30:45 | INFO | Relevance analyzer initialized with Claude API (automatic mode)
🤖 Starting automated analysis for 20 news items...
✅ Automated analysis completed: 18/20 items analyzed
🔴 URGENT | 92 points | MSFT, NVDA
🟠 HIGH | 85 points | AAPL
```

### 자주 묻는 질문

**Q: 분석이 느립니다**
A: 병렬 처리 워커 수 증가
```python
# analyzers/analysis_pipeline.py
max_workers=10  # 5에서 10으로 증가
```

**Q: 비용을 절감하고 싶습니다**
A: 분석 간격 증가
```python
ANALYSIS_INTERVAL = 3600  # 30분에서 1시간으로
```

**Q: 특정 종목만 추적하고 싶습니다**
A: config/settings.py 수정
```python
TRACKED_SYMBOLS = ["MSFT", "AAPL", "NVDA"]  # 원하는 종목만
```

---

## 🎉 축하합니다!

투자 시그널 감지 시스템이 준비되었습니다! 🚀

다음은:
1. 대시보드에서 신호 확인
2. 블로거 추천으로 글쓰기
3. 이메일 알림 수신

행운을 빕니다! 💰
