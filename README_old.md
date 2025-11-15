# 미국 주식 뉴스 자동 분석 블로그 시스템

AI 기반 미국 주식 뉴스 자동 수집, 분석 및 블로그 글 생성 시스템

## 🎯 주요 기능

1. **자동 뉴스 수집**
   - Finnhub API: 실시간 주식 뉴스
   - Alpha Vantage API: 감성 분석 포함 금융 뉴스
   - RSS Feeds: Yahoo Finance, Reuters, MarketWatch 등

2. **AI 기반 뉴스 분석**
   - Claude AI를 사용한 관련성 점수 계산 (0-100)
   - 주식 심볼 자동 추출
   - 주가 영향 예측 (상승/하락/중립)
   - 중요도 분류 (HIGH/MEDIUM/LOW)

3. **블로그 글 자동 생성**
   - 관련 뉴스 종합 분석
   - SEO 최적화된 구조
   - 투자 시사점 제공
   - WordPress 자동 발행 지원

4. **자동화 스케줄링**
   - 15분마다 뉴스 수집
   - 30분마다 뉴스 분석
   - 1시간마다 블로그 글 생성
   - 매일 오래된 데이터 정리

## 📋 시스템 요구사항

- Python 3.9+
- Supabase 계정 (무료)
- Anthropic API Key (Claude AI)
- Finnhub API Key (무료)
- Alpha Vantage API Key (무료)

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
cd stock-news-automation
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# News APIs
FINNHUB_API_KEY=your_finnhub_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# AI APIs
ANTHROPIC_API_KEY=your_anthropic_key

# Configuration
MIN_RELEVANCE_SCORE=70
```

### 3. Supabase 데이터베이스 설정

Supabase 대시보드의 SQL Editor에서 `database/schema.sql` 실행:

```bash
# Supabase에 로그인 후 SQL Editor에서 실행
cat database/schema.sql
```

### 4. 로그 디렉토리 생성

```bash
mkdir logs
```

## 💻 사용법

### 전체 시스템 실행 (24/7 자동화)

```bash
python main.py --mode run
```

### 모든 작업 1회 실행 (테스트용)

```bash
python main.py --mode once
```

### 개별 작업 실행

뉴스 수집만:
```bash
python main.py --mode collect
```

뉴스 분석만:
```bash
python main.py --mode analyze
```

블로그 글 생성만:
```bash
python main.py --mode generate
```

## 📊 시스템 아키텍처

```
┌─────────────────────────────────────────────┐
│         뉴스 수집 레이어                     │
│  Finnhub, Alpha Vantage, RSS Feeds          │
└──────────────────┬──────────────────────────┘
                   │ 15분마다
                   ↓
┌─────────────────────────────────────────────┐
│      Supabase 원본 저장소 (24h TTL)         │
└──────────────────┬──────────────────────────┘
                   │ 30분마다
                   ↓
┌─────────────────────────────────────────────┐
│     Claude AI 분석 레이어                    │
│  관련성, 심볼 추출, 영향 예측, 중요도        │
└──────────────────┬──────────────────────────┘
                   │ 점수 70+ 필터링
                   ↓
┌─────────────────────────────────────────────┐
│      Supabase 분석 저장소                    │
└──────────────────┬──────────────────────────┘
                   │ 1시간마다
                   ↓
┌─────────────────────────────────────────────┐
│     Claude 블로그 글 작성                    │
│  종합 분석, SEO 최적화, 투자 시사점          │
└──────────────────┬──────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────┐
│      WordPress/Ghost 블로그                  │
│      (수동 또는 API 자동 발행)               │
└─────────────────────────────────────────────┘
```

## 🗂 프로젝트 구조

```
stock-news-automation/
├── collectors/              # 뉴스 수집기
│   ├── base.py             # 수집기 기본 클래스
│   ├── finnhub_collector.py
│   ├── alpha_vantage_collector.py
│   └── rss_collector.py
│
├── analyzers/              # AI 분석기
│   ├── relevance_analyzer.py  # Claude AI 분석
│   └── analysis_pipeline.py   # 분석 파이프라인
│
├── writers/                # 블로그 글 생성
│   └── article_generator.py   # Claude AI 글 작성
│
├── database/               # 데이터베이스
│   ├── models.py          # 데이터 모델
│   ├── supabase_client.py # Supabase 클라이언트
│   └── schema.sql         # DB 스키마
│
├── scheduler/              # 작업 스케줄러
│   └── jobs.py
│
├── config/                 # 설정
│   └── settings.py
│
├── logs/                   # 로그 파일
├── main.py                 # 메인 실행 파일
├── requirements.txt        # 의존성
└── README.md
```

## 🔑 API 키 발급 방법

### 1. Finnhub (무료)
- https://finnhub.io/register
- 가입 후 Dashboard에서 API Key 복사

### 2. Alpha Vantage (무료)
- https://www.alphavantage.co/support/#api-key
- 이메일 입력 후 API Key 받기
- 무료: 25 requests/day

### 3. Anthropic Claude (유료)
- https://console.anthropic.com/
- 가입 후 API Keys 메뉴에서 생성
- 가격: $3/MTok (input), $15/MTok (output)

### 4. Supabase (무료)
- https://supabase.com/
- 프로젝트 생성 후 Settings > API에서 URL과 Key 복사

## 📈 비용 예상

**무료 티어 사용 시:**
- Finnhub: 무료 (60 req/분)
- Alpha Vantage: 무료 (25 req/일)
- Supabase: 무료 (500MB DB, 2GB 전송)

**AI 비용 (예상):**
- Claude API: 월 $20-50 (분석 + 글 작성)
- 하루 50개 뉴스 분석 + 5개 글 생성 기준

**총 예상 비용: 월 $20-50**

## 🌐 블로그 플랫폼 설정

### Ghost CMS (추천)

```bash
# Ghost 설치
npm install -g ghost-cli

# 블로그 생성
ghost install local
```

### WordPress

1. WordPress 설치 (호스팅 또는 로컬)
2. Application Password 생성
3. `.env`에 WordPress 정보 입력

## 📊 모니터링

### 로그 확인

```bash
# 실시간 로그
tail -f logs/stock_news_$(date +%Y-%m-%d).log

# 에러만 확인
grep "ERROR" logs/stock_news_$(date +%Y-%m-%d).log
```

### Supabase 대시보드

- 수집된 뉴스 수: `SELECT COUNT(*) FROM news_raw`
- 분석된 뉴스 수: `SELECT COUNT(*) FROM analyzed_news`
- 발행된 글 수: `SELECT COUNT(*) FROM published_articles`
- 인기 종목: `SELECT * FROM popular_symbols`

## 🔧 커스터마이징

### 1. 추적 종목 변경

`config/settings.py`의 `TRACKED_SYMBOLS` 수정

### 2. RSS 피드 추가

`config/settings.py`의 `RSS_FEEDS` 배열에 추가

### 3. 분석 임계값 조정

`.env`의 `MIN_RELEVANCE_SCORE` 수정 (0-100)

### 4. 스케줄 간격 변경

`.env`의 `*_INTERVAL` 값 수정 (초 단위)

## 🐛 문제 해결

### API 제한 오류

- Finnhub: 무료는 60 req/분
- Alpha Vantage: 무료는 25 req/일
- 수집 간격 늘리거나 유료 플랜 고려

### 중복 뉴스

- URL 기반 자동 중복 제거
- 24시간 후 자동 삭제

### Claude API 오류

- API 키 확인
- 크레딧 잔액 확인
- Rate limit 확인 (Tier 1: 50 req/분)

## 📝 라이선스

MIT License

## 🤝 기여

이슈 제보 및 PR 환영합니다!

## 📧 문의

프로젝트 관련 문의사항은 이슈로 남겨주세요.
