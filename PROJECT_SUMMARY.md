# 🚀 미국 주식 뉴스 자동 분석 블로그 시스템

## 📌 프로젝트 개요

AI(Claude)를 활용하여 미국 주식 뉴스를 자동으로 수집, 분석하고 한국어 블로그 글을 생성하는 완전 자동화 시스템

---

## ✨ 핵심 기능

### 1. 자동 뉴스 수집 (3개 소스)
- **Finnhub API**: 실시간 주식 뉴스 (무료, 60 req/분)
- **Alpha Vantage API**: 감성 분석 포함 금융 뉴스 (무료, 25 req/일)
- **RSS Feeds**: Yahoo Finance, Reuters, MarketWatch 등
- **수집 주기**: 15분~2시간 (설정 가능)
- **중복 제거**: URL 기반 자동 필터링

### 2. AI 기반 뉴스 분석 (Claude 3.5 Sonnet)
- **관련성 점수**: 0-100점 자동 계산
- **주식 심볼 추출**: 뉴스에서 관련 종목 자동 파악
- **주가 영향 예측**: 상승/하락/중립
- **중요도 분류**: HIGH/MEDIUM/LOW
- **필터링**: 관련성 70점 이상만 통과

### 3. 블로그 글 자동 생성 (Claude 3.5 Sonnet)
- **구조화된 포맷**:
  - 📊 무엇이 일어났는가
  - 🔄 어떻게 작동하는가
  - 💡 왜 주가에 영향을 주는가
  - 📈 투자 시사점
- **SEO 최적화**: 1,500-2,000자, 키워드 자연 배치
- **객관적 분석**: 투자 조언 아닌 정보 제공
- **한국어 작성**: 투자자 친화적 문체

### 4. 데이터 관리 (Supabase)
- **3개 테이블 구조**:
  - `news_raw`: 원본 뉴스 (24시간 TTL)
  - `analyzed_news`: 분석 결과
  - `published_articles`: 발행된 글
- **자동 정리**: 24시간 이상 된 원본 뉴스 삭제
- **통계 뷰**: 인기 종목, 뉴스 통계

### 5. 완전 자동화 (Scheduler)
- **뉴스 수집**: 15분~2시간마다
- **뉴스 분석**: 30분~2시간마다
- **글 생성**: 1시간~4시간마다
- **데이터 정리**: 매일 새벽 3시
- **24/7 무인 운영**

---

## 📁 프로젝트 구조

```
stock-news-automation/
├── collectors/              # 뉴스 수집기 (3개)
│   ├── finnhub_collector.py
│   ├── alpha_vantage_collector.py
│   └── rss_collector.py
├── analyzers/              # AI 분석 시스템
│   ├── relevance_analyzer.py    # Claude 분석
│   └── analysis_pipeline.py
├── writers/                # 블로그 글 생성
│   └── article_generator.py
├── database/               # Supabase 연동
│   ├── models.py
│   ├── supabase_client.py
│   └── schema.sql
├── scheduler/              # 자동화
│   └── jobs.py
├── config/                 # 설정
│   └── settings.py
├── main.py                 # 메인 실행 파일
└── docs/                   # 문서 (9개)
    ├── README.md
    ├── QUICK_START.md
    ├── API_KEYS_GUIDE.md
    ├── SETUP_GUIDE.md
    └── COST_OPTIMIZATION.md
```

**총 24개 파일 생성 완료**

---

## 💰 비용 구조

### 필수 비용
| 항목 | 무료 플랜 | 유료 (필요시) |
|------|-----------|---------------|
| Finnhub | ✅ 무료 (60 req/분) | $449/월 |
| Alpha Vantage | ✅ 무료 (25 req/일) | $49.99/월 |
| Supabase | ✅ 무료 (500MB) | $25/월 |
| Claude API | ❌ 유료 필수 | $20-100/월 |

### 시나리오별 예상 비용

#### 미니멀 ($15-20/월)
- 뉴스 분석: 30개/일
- 블로그 글: 9개/일
- 간격: 2-8시간

#### 밸런스 ($25-35/월) ⭐ 추천
- 뉴스 분석: 60개/일
- 블로그 글: 18개/일
- 간격: 1-4시간

#### 적극형 ($50-70/월)
- 뉴스 분석: 120개/일
- 블로그 글: 36개/일
- 간격: 30분-2시간

#### 프리미엄 ($100+/월)
- 뉴스 분석: 240개/일
- 블로그 글: 72개/일
- 간격: 15분-1시간

---

## 🎯 예상 ROI

### 수익 모델 (Google AdSense)
```
월간 방문자: 30,000명 (1,000/일)
페이지뷰: 75,000 (2.5 페이지/방문)
RPM: $10
월간 수익: $750

비용: $39 (밸런스)
순익: $711
ROI: 1,825%
```

### 손익분기점
- **필요 방문자**: 하루 52명
- **필요 페이지뷰**: 하루 130회
- **도달 예상**: 1-3개월 (SEO 최적화 시)

---

## 🚀 시작하기 (10분)

### 1단계: API 키 발급 (5분)
```bash
# 4개 서비스 가입
✅ Finnhub (무료)
✅ Alpha Vantage (무료)
✅ Anthropic Claude ($5 충전)
✅ Supabase (무료)
```

### 2단계: 환경 설정 (2분)
```bash
cd /Users/jinxin/dev/stock-news-automation
cp .env.budget .env  # 또는 .env.example
nano .env  # API 키 입력
```

### 3단계: 설치 (1분)
```bash
pip install -r requirements.txt
mkdir logs
```

### 4단계: DB 설정 (1분)
```bash
# Supabase SQL Editor에서 실행
cat database/schema.sql
# → 복사 → SQL Editor → RUN
```

### 5단계: 실행 (1분)
```bash
# 테스트
python main.py --mode once

# 24/7 실행
python main.py --mode run
```

---

## 📚 문서 가이드

### 초보자
1. **QUICK_START.md** - 10분 빠른 시작
2. **API_KEYS_GUIDE.md** - API 키 발급 상세 가이드
3. **SETUP_GUIDE.md** - 설치 및 문제 해결

### 고급 사용자
4. **COST_OPTIMIZATION.md** - 비용 절감 전략
5. **README.md** - 전체 시스템 문서

### 설정 파일
6. **.env.example** - 기본 설정
7. **.env.budget** - 저비용 설정 ($25/월)
8. **.env.aggressive** - 고성능 설정 ($100/월)

---

## 🔧 실행 모드

```bash
# 전체 시스템 (24/7)
python main.py --mode run

# 1회 실행 (테스트)
python main.py --mode once

# 뉴스 수집만
python main.py --mode collect

# 분석만
python main.py --mode analyze

# 글 생성만
python main.py --mode generate
```

---

## 📊 시스템 플로우

```
15분마다
    ↓
[뉴스 수집] → Finnhub, Alpha Vantage, RSS
    ↓
[Supabase 저장] → news_raw (24시간 TTL)
    ↓ 30분마다
[Claude 분석] → 관련성 점수, 심볼 추출, 영향 예측
    ↓ 점수 70+ 필터링
[Supabase 저장] → analyzed_news
    ↓ 1시간마다
[Claude 글 작성] → 종합 분석, SEO 최적화
    ↓
[Supabase 저장] → published_articles
    ↓
[WordPress/Ghost] → 블로그 발행 (선택)
```

---

## ✅ 주요 특징

### 장점
- ✅ **완전 자동화**: 설정 후 방치 가능
- ✅ **AI 기반**: Claude 3.5 Sonnet 사용
- ✅ **저비용 시작**: 월 $25부터 가능
- ✅ **확장 가능**: 설정으로 성능 조절
- ✅ **SEO 최적화**: 구조화된 블로그 포맷
- ✅ **실시간 모니터링**: 로그 & Supabase 대시보드
- ✅ **오픈소스**: 완전 커스터마이징 가능

### 제약사항
- ⚠️ Claude API 유료 (필수)
- ⚠️ Alpha Vantage 무료 제한 (25 req/일)
- ⚠️ 초기 트래픽 확보 필요 (SEO 시간 소요)
- ⚠️ WordPress 연동은 수동 설정 필요

---

## 🎯 다음 단계

### Phase 1: 시스템 안정화 (1주)
- [ ] 24시간 테스트 실행
- [ ] 로그 모니터링
- [ ] 비용 확인
- [ ] 글 품질 검토

### Phase 2: 블로그 구축 (1-2주)
- [ ] Ghost/WordPress 설치
- [ ] 도메인 연결
- [ ] 디자인 커스터마이징
- [ ] Google Analytics 설정

### Phase 3: SEO 최적화 (2-4주)
- [ ] Sitemap 생성
- [ ] Google Search Console 등록
- [ ] 메타 태그 최적화
- [ ] 내부 링크 구조

### Phase 4: 수익화 (1-3개월)
- [ ] Google AdSense 신청 (방문자 1,000+/일)
- [ ] Affiliate 링크 추가
- [ ] 프리미엄 컨텐츠 제공
- [ ] 이메일 뉴스레터

---

## 🛠 개발 계획 업데이트 (2025-11)

### 목표
- 기사 발행 시점을 기준으로 **포트폴리오 관점의 사후 추적** 기능을 추가
- 24시간 이후에도 종목 가격 움직임과 후속 이벤트를 시각적으로 관찰할 수 있는 **관찰 대시보드** 구현
- 기사 페이지와 포트폴리오 뷰가 자연스럽게 연결되도록 설계

### 작업 패키지

**1. 데이터 수집 및 저장**
- [ ] `price_observations` 테이블 설계 (symbol, observed_at, price, volume 등)
- [ ] 뉴스 발행 시각(`published_at`) 이후 가격 데이터 수집 스크립트 작성
- [ ] 스케줄러 연동: 뉴스 발행 후 최초 24시간은 1시간 간격, 이후 일 단위 업데이트
- [ ] 후속 이벤트 로그 테이블/필드 정의 (추가 기사, 실적, 애널리스트 리포트)

**2. 분석 및 요약 로직**
- [ ] 구간별 수익률/변동성 계산 유틸 추가 (`0~24h`, `1~3일`, `3~7일`, `1~4주`)
- [ ] 거래량, VWAP 등 관찰 지표 산출
- [ ] 관찰 메모/자동 요약 템플릿 정의 (Claude Code 활용)

**3. UI/UX 설계**
- [ ] 기사 상세 페이지에 `📈 뉴스 이후 가격 추적` 섹션 추가
- [ ] 타임라인/차트 컴포넌트 설계 (Plotly/Chart.js 등)
- [ ] 구간별 성과 카드, 관찰 로그, 관찰 토글 UI 구현
- [ ] 포트폴리오 모드(여러 기사 묶음 관찰) 정보구조 정의

**4. 자동화 & 통합**
- [ ] `scripts/get_price_history.py` 등 CLI 유틸 제작
- [ ] 분석 결과를 Markdown 섹션에 자동 삽입하는 파이프라인(템플릿 기반)
- [ ] Supabase/플라스크 앱에서 API 엔드포인트 추가 혹은 기존 뷰 확장
- [ ] 관찰 알림(이메일/슬랙 등) 필요 시 연동 옵션 검토

**5. 검증 및 릴리스**
- [ ] AAPL/TSLA 사례로 기능 E2E 검증
- [ ] 차트/지표의 정확도 확인(수동 샘플 체크)
- [ ] UX 검토 후 스타일 가이드 업데이트
- [ ] 문서 반영: README, CLAUDE_CODE_WORKFLOW, QUICK_START 업데이트

### 예상 일정
- 주차 1: 데이터 모델링 + 수집 스크립트
- 주차 2: 분석 유틸 + 관찰 템플릿
- 주차 3: UI 구현 + 백엔드 연동
- 주차 4: QA, 문서화, 파일럿 적용 (핵심 종목 3개)

### 리스크 & 대응
- **실시간 시세 API 제한** → 캐시/저장 방식 도입, 저빈도 업데이트
- **차트 성능 문제** → 초기엔 스파크라인/간단한 SVG로 시작, 점진적 개선
- **데이터 정확도** → 수동 검증 절차/로그 도입, 오류 시 재수집 루틴 마련

### 산출물
- 업데이트된 기사 상세 디자인/스타일
- 가격/관찰 데이터 저장 스키마 및 스크립트
- 관찰 대시보드 UI 구현 코드
- 포트폴리오 추적 활용 가이드 (MD 문서)

---

## 🆘 지원

### 문서
- 📖 **상세 가이드**: `API_KEYS_GUIDE.md`
- 📘 **전체 문서**: `README.md`
- 🔧 **설치 가이드**: `SETUP_GUIDE.md`
- 💰 **비용 최적화**: `COST_OPTIMIZATION.md`

### 문제 해결
- 로그 확인: `tail -f logs/stock_news_*.log`
- Supabase: 대시보드에서 데이터 확인
- API 키: `.env` 파일 재확인

---

## 📈 성공 사례 시나리오

### 3개월 후
- 일일 방문자: 1,000명
- 발행 글: 1,620개 (18개/일 × 90일)
- 월 수익: $750 (AdSense)
- 월 비용: $39
- 순익: $711/월

### 6개월 후
- 일일 방문자: 3,000명
- 발행 글: 3,240개
- 월 수익: $2,250
- 월 비용: $39-70 (트래픽 증가 시 확장)
- 순익: $2,180/월

### 12개월 후
- 일일 방문자: 10,000명
- 발행 글: 6,480개
- 월 수익: $7,500
- 월 비용: $100 (프리미엄)
- 순익: $7,400/월

**핵심은 꾸준한 컨텐츠 생성과 SEO 최적화!**

---

## 🎉 축하합니다!

미국 주식 뉴스 자동 분석 블로그 시스템 개발이 완료되었습니다.

**지금 바로 시작하세요:**
```bash
python main.py --mode run
```

**행운을 빕니다! 🚀📈💰**
