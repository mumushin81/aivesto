# Aivesto - AI-Powered Stock News Signal Detection

미국 주식 뉴스에서 투자 시그널을 자동으로 발굴하고 SEO 최적화 기사를 작성하는 시스템

**배포 URL**: https://aivesto-dashboard-f30hi3pct-mumushin81-gmailcoms-projects.vercel.app

---

## 🚀 핵심 기능

### 1. 다층적 뉴스 수집 (Multi-Layer Collection)

```
Layer 1 (Core Signal)        → Bloomberg, Reuters, WSJ
Layer 2 (Sentiment Momentum) → Fox News, CNN, Yahoo Finance
Layer 3 (Broad Impact)       → Reddit, Local News (예정)
```

### 2. 자동화된 분석 파이프라인

- **NER (Named Entity Recognition)**: 종목 심볼 자동 추출
- **Sentiment Analysis**: VADER + FinBERT 하이브리드
- **Policy Detection**: 정부 정책/규제 변화 감지 (최우선!)
- **Amplification Detection**: Layer 1→2 여론 증폭 효과 탐지

### 3. 우선순위 스코어링 (0-100점)

- **90-100점**: 정책 시그널 → 즉시 기사 작성
- **80-89점**: High-priority → 당일 작성
- **70-79점**: Medium → 주간 리포트
- **70점 미만**: Low → 무시

---

## 📊 실시간 성능

```bash
$ python test_e2e_pipeline.py

============================================================
🚀 Starting News Pipeline
============================================================

📈 Collection:
  Total Articles: 417
  Layer 1 (Core Signal): 60
  Layer 2 (Sentiment & Momentum): 357

🔬 Analysis:
  Analyzed Articles: 417
  High Priority (80+): 174 (42%)
  Policy Signals Detected: 4

🔊 Amplification:
  Amplification Detected: True
  Amplification Ratio: 5.9x (L2/L1)
  Amplification Level: high

⏱️  Performance:
  Total Duration: 19.2s
  Processing Speed: ~1,300 articles/minute
```

---

## 🔧 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/mumushin81/aivesto.git
cd aivesto

# 의존성 설치
pip install -r requirements.txt
```

### 2. 필수 패키지 (Phase 1-4)

```bash
pip install vaderSentiment feedparser httpx beautifulsoup4
```

### 3. 환경 변수 설정

```bash
cp .env.example .env
nano .env
```

```env
# Supabase (선택)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your_anon_key

# News APIs (선택)
FINNHUB_API_KEY=your_key
```

### 4. E2E 파이프라인 실행

```bash
# 전체 파이프라인 (정리 → 수집 → 분석 → 증폭 감지)
python test_e2e_pipeline.py

# 결과:
# - 24시간 지난 뉴스 자동 삭제
# - 417개 기사 자동 수집 및 분석 (19초)
```

**자동 정리 기능**:
- 뉴스 수집 시작 전 24시간 이상 된 뉴스 자동 삭제
- 매일 새벽 3시 정기 정리 작업 실행
- 데이터베이스 최적화 및 스토리지 관리

---

## 📂 프로젝트 구조

```
aivesto/
├── collectors/              # 뉴스 수집기
│   ├── wsj_collector.py        # WSJ RSS ✅
│   ├── fox_collector.py        # Fox News
│   ├── cnn_collector.py        # CNN
│   └── yahoo_collector.py      # Yahoo Finance
│
├── analyzers/               # 분석 엔진
│   ├── ner_extractor.py        # 종목 심볼 추출
│   ├── sentiment_analyzer.py   # 감성 분석 (VADER/FinBERT)
│   ├── policy_detector.py      # 정책 변화 감지
│   └── amplification_detector.py  # 증폭 감지
│
├── pipeline/                # E2E 오케스트레이터
│   └── news_pipeline.py        # 통합 파이프라인
│
├── articles/                # 발행된 기사
│   ├── article_NVDA_blackwell_gpu_20251113.md
│   └── ...
│
├── web/                     # Flask 웹서버
│   └── app.py
│
├── test_*.py                # 테스트 스크립트
└── DEV_GUIDE.md             # 개발 가이드 (상세)
```

---

## 🎯 사용 예시

### 1. NER (종목 심볼 추출)

```python
from analyzers.ner_extractor import NERExtractor

ner = NERExtractor(use_spacy=False)
symbols = ner.extract_symbols("Apple (AAPL) and Microsoft (MSFT) announced partnership")
print(symbols)  # → ['AAPL', 'MSFT']
```

### 2. Sentiment Analysis (감성 분석)

```python
from analyzers.sentiment_analyzer import SentimentAnalyzer

sentiment = SentimentAnalyzer(use_finbert=False)
result = sentiment.analyze("Tesla stock plummeted after CEO resignation")
print(result)
# → {'sentiment': 'negative', 'score': -0.7, 'confidence': 0.7}
```

### 3. Policy Detection (정책 감지)

```python
from analyzers.policy_detector import PolicyDetector

policy = PolicyDetector()
result = policy.detect("SEC introduces new cryptocurrency trading regulation")
print(result)
# → {
#   'has_policy_change': True,
#   'change_type': 'new_policy',
#   'affected_sectors': ['Finance'],
#   'confidence': 1.0
# }
```

### 4. E2E Pipeline (전체 파이프라인)

```python
from pipeline.news_pipeline import NewsPipeline
from database.supabase_client import SupabaseClient

# DB 연결 (선택)
db = SupabaseClient()

# 파이프라인 실행
pipeline = NewsPipeline(db_client=db, use_finbert=False)
results = pipeline.run(save_to_db=True)

# 결과 확인
print(f"수집: {results['stats']['total_articles']}개")
print(f"High-Priority: {results['stats']['high_priority_count']}개")
print(f"정책 시그널: {results['stats']['policy_signals']}개")
```

---

## 🧪 테스트

```bash
# Phase 1: Layer 1 수집 테스트
python test_layer1_collectors.py
# → WSJ 60개 기사

# Phase 2: 분석 엔진 테스트
python test_phase2_analyzers.py
# → NER, Sentiment, Policy 검증

# Phase 3: Layer 2 + 증폭 테스트
python test_layer2_collectors.py
python test_phase3_amplification.py
# → Fox/CNN/Yahoo 354개, 증폭 비율 확인

# Phase 4: 전체 E2E 테스트
python test_e2e_pipeline.py
# → 417개 기사 수집 → 분석 (19초)
```

---

## 📈 성과

| 지표 | 결과 |
|------|------|
| **수집 속도** | ~400개/분 |
| **분석 속도** | ~1,300개/분 |
| **전체 파이프라인** | 19초 (417개 기사) |
| **High-Priority 비율** | 42% (174/417) |
| **정책 시그널 감지** | 4개 |
| **증폭 비율** | 5.9x (Layer 2/Layer 1) |

---

## 🛠️ 기술 스택

- **Backend**: Python 3.12+, Flask
- **Database**: Supabase (PostgreSQL)
- **News Collection**: RSS (feedparser, httpx)
- **NLP**: VADER, spaCy, FinBERT (ONNX)
- **Image Generation**: Midjourney (Discord 봇 자동화)
- **Storage**: Supabase Storage
- **Deployment**: Vercel
- **Alerts**: Telegram Bot

---

## 📚 문서

- **[DEV_GUIDE.md](DEV_GUIDE.md)**: 전체 개발 가이드 (상세)
  - Phase 1-4 구현 상세
  - 시그널 분석 8가지 기준
  - 기사 작성 11단계 구조
  - 일일 워크플로우

---

## 🔜 로드맵

- [x] Phase 1: Layer 1 수집기 (WSJ)
- [x] Phase 2: 분석 엔진 (NER, Sentiment, Policy)
- [x] Phase 3: Layer 2 수집기 + 증폭 감지
- [x] Phase 4: E2E 파이프라인
- [x] Phase 5: 스케줄러 (APScheduler)
- [x] Phase 6: 대시보드 실시간 연동
- [x] 블로그 이미지 자동 생성 시스템
  - Discord 봇을 통한 Midjourney 연동 (공식 API 없음)
  - Supabase Storage 자동 업로드
  - 문맥 기반 이미지 배치 (기사당 5장+)
- [ ] 백테스팅 시스템 (시그널 정확도 검증)
- [ ] 알림 시스템 (Telegram/Email)
- [ ] 모바일 앱

---

## 📝 라이선스

MIT License

---

## 🤝 기여

이슈 제보 및 Pull Request 환영합니다!

---

## 📸 최근 개발: 블로그 이미지 자동화

### 시스템 구성

```
블로그 글 분석 → AI 프롬프트 생성 → Midjourney 이미지 생성 → Supabase 저장 → 자동 배치
```

### 주요 기능

1. **문맥 기반 이미지 생성**
   - 블로그 내용 분석하여 섹션별 최적 이미지 프롬프트 자동 생성
   - 기사당 최소 5장 이상의 이미지 생성

2. **Discord 봇 자동화**
   - Midjourney Discord 봇을 통한 이미지 생성 (공식 API 미제공)
   - 비동기 처리로 다중 이미지 동시 생성

3. **Supabase 통합**
   - 생성된 이미지 자동 업로드
   - 메타데이터(섹션, 키워드, 캡션) 자동 저장

4. **스마트 배치**
   - Markdown에 문맥에 맞는 위치에 이미지 자동 삽입
   - 반응형 이미지 태그 및 캡션 생성

### 사용 방법

```bash
# 단일 기사 처리
python scripts/run_blog_image_pipeline.py articles/article_NVDA_*.md

# 전체 기사 배치 처리 (11개)
python scripts/batch_process_all_articles.py
```

### ⚠️ 중요 주의사항

**Midjourney 공식 API는 존재하지 않습니다**
- Discord 봇을 통한 자동화만 가능
- 약관 위반 위험: 개인 서버에서만 사용, 상업적 사용 금지
- Rate limiting 필수 (분당 2-3회 이하)
- 테스트/학습 목적으로만 권장

자세한 내용은 `docs/CONTEXTUAL_IMAGE_SYSTEM.md` 참조

---

**작성자**: Jinxin
**최종 업데이트**: 2025-11-16
