# 📰 티어 기반 블로그 글 생성 시스템

## 개요

기존의 단순한 "상위 5개 종목" 방식에서 벗어나 **3단계 티어 시스템**으로 전환되었습니다.

각 티어는 뉴스의 중요도와 품질 기준에 따라 자동으로 대상 종목을 선택하며, 효율적인 블로그 운영이 가능합니다.

---

## 🎯 세 가지 티어 설명

### Tier 1: Primary (1주 2-3회)

**목표**: 높은 관심도의 핫이슈 종목

**기준**:
- 높은 중요도(High Importance) 뉴스 **3개 이상**
- 자동 생성 여부: **Yes** (스케줄러가 자동 실행)
- 추천 빈도: **주 2-3회**

**대상 종목 (13개)**:
```
MSFT, NVDA, AAPL, GOOGL, AMZN, TSLA, META,
GOOG, NBIS, BRK.B, AMD, WMT, SPY
```

**예상 효과**:
- 투자자들이 가장 주목하는 종목 커버
- 지속적인 신규 콘텐츠 제공
- SEO 최적화 (자주 검색되는 종목)

---

### Tier 2: Secondary (2주 1회)

**목표**: 심화 분석이 필요한 종목

**기준**:
- 분석된 뉴스 **3개 이상** 보유
- 평균 관련성 점수 **75점 이상**
- 자동 생성 여부: **Yes**
- 추천 빈도: **반주 1회 (주 3-4회)**

**대상 종목 (추가 5개)**:
```
Tier 1(13개) + Tier 2(5개) = 총 18개 종목

Tier 2 추가 종목:
AVGO, TSM, CORW, INTC, RGTI
```

**예상 효과**:
- 중간 규모 기업 분석 콘텐츠
- 틈새시장 투자자 타겟팅
- 전문성 강화

---

### Tier 3: Trend (월 1회)

**목표**: 월간 시장 트렌드 리포트

**기준**:
- 지난 달 상위 **15개** 심볼 추출
- 동적 선택 (매달 변함)
- 자동 생성 여부: **No** (수동 생성)
- 추천 빈도: **월 1회**

**예상 효과**:
- 월간 종합 분석 리포트
- 시장 동향 파악
- 독자 로열티 강화

---

## 🚀 사용 방법

### 기본 사용법

#### Tier 1 실행 (가장 자주 사용)
```bash
python main.py --mode generate --tier tier_1
```

**출력 예시**:
```
🎯 Generating articles for Tier 1 (High Importance >= 3)
   Target symbols (13): MSFT, NVDA, AAPL, GOOGL, AMZN, TSLA, META, GOOG, NBIS, BRK.B, AMD, WMT, SPY

📝 Starting article generation for 13 symbols...
   [1/13] MSFT: Generated
   [2/13] NVDA: Generated
   [3/13] AAPL: Generated
   ...
   [13/13] SPY: Generated

✅ Article generation completed: 13 prompts generated
   Tier: tier_1
   Target symbols: 13
   Generated: 13
```

#### Tier 2 실행 (추가 깊이 있는 분석)
```bash
python main.py --mode generate --tier tier_2
```

**결과**: 18개 종목에 대한 프롬프트 생성 (Tier 1 + 5개 추가 종목)

#### Tier 3 실행 (월간 리포트)
```bash
python main.py --mode generate --tier tier_3
```

**결과**: 상위 15개 종목 동적 추출 후 프롬프트 생성

---

## 📊 데이터 기반 기준

### Tier 1 선정 근거

지난 분석 데이터 (164개 분석 뉴스 기준):

| 순번 | 종목 | 뉴스수 | 평균점수 | 높은중요도 | 선택이유 |
|------|------|--------|----------|-----------|---------|
| 1 | MSFT | 50 | 82.3 | 31 | 가장 많은 뉴스 |
| 2 | NVDA | 49 | 83.7 | 34 | 매우 높은 점수 |
| 3 | AAPL | 39 | 79.9 | 17 | 지속적 관심 |
| 4 | GOOGL | 34 | 82.4 | 20 | 안정적 품질 |
| 5 | AMZN | 24 | 83.0 | 18 | 높은 점수 |

**기준 결정**:
- "높은 중요도 뉴스 3개 이상" = **최고의 균형**
  - 너무 엄격하지 않음 (수집 가능)
  - 너무 관대하지 않음 (품질 보장)
  - 일관된 콘텐츠 공급 가능

---

## 🔄 일일 워크플로우 (개선)

### Option A: 매일 Tier 1 실행

```
월-금 10:00 AM
├─ 뉴스 수집: python main.py --mode collect
├─ 뉴스 분석: python main.py --mode analyze
└─ 글 생성: python main.py --mode generate --tier tier_1
   (13개 종목 프롬프트 생성, 수동 작성)
```

**예상 시간**:
- 자동화: 5분
- 수동 (13개 글): 1.5-2시간

---

### Option B: 분산 운영

```
월/수/금 → Tier 1 (3개 글)
화/목 → Tier 2 중 일부 (2개 글)
토 → Tier 3 임시 리포트
```

**장점**: 일일 작업량 분산, 꾸준한 콘텐츠 공급

---

## 📁 생성된 파일 구조

```
prompts/
├── article_MSFT_20251113_124455.md     ← Tier 1
├── article_NVDA_20251113_124456.md
├── article_AAPL_20251113_124456.md
├── ...
├── article_AVGO_20251113_124500.md     ← Tier 2 (추가)
├── article_TSM_20251113_124501.md
└── ...

articles/
├── article_MSFT_20251113_1300.md       ← 작성된 글
├── article_NVDA_20251113_1310.md
└── ...
```

### 프롬프트 파일 구조

각 프롬프트 파일은 다음을 포함:

```markdown
당신은 미국 주식 시장 전문 블로거입니다...

종목: MSFT

관련 뉴스:
- 뉴스 1: [제목, 출처, 내용, 점수, 분석, 핵심포인트]
- 뉴스 2: ...
- 뉴스 3: ...
- 뉴스 4: ...
- 뉴스 5: ...

다음 구조로 블로그 글을 작성해주세요:
---
제목: [종목명] 관련 최신 뉴스 분석 - [키워드]

## 📊 무엇이 일어났는가
[3-5개 뉴스 종합 요약]

## 🔄 어떻게 작동하는가
[메커니즘 설명]

## 💡 왜 주가에 영향을 주는가
[논리적 연결고리]

## 📈 투자 시사점
- 긍정적 요소
- 리스크 요소
- 투자 전략 제안

## 🔗 참고 자료
[출처 링크]
---

**작성 가이드라인:**
1. 글자 수: 1,500-2,000자
2. 톤: 전문적이지만 이해하기 쉽게
3. 데이터: 구체적인 숫자와 팩트
4. 객관성: 과장 없이 균형잡힌 시각
5. SEO: 종목명과 관련 키워드 자연스럽게
6. 투자 조언 아님: "투자 판단은 본인의 책임" 명시
```

---

## 🤖 Claude Code 워크플로우와 통합

### Step 1: 프롬프트 생성
```bash
python main.py --mode generate --tier tier_1
```
→ `prompts/article_*.md` 생성

### Step 2: Claude Code에서 작성
1. 프롬프트 파일 열기
2. 내용 복사
3. Claude Code에 붙여넣기
4. Claude가 글 작성
5. 결과를 `articles/article_*.md`로 저장

### Step 3: 데이터베이스 저장
```bash
python scripts/publish_articles.py articles/article_*.md
```

**전체 흐름 (자동 + 수동)**:
```
자동화 (5분):    generate → prompts 생성
                  ↓
수동화 (1.5시간): Claude Code → 글 작성
                  ↓
자동화 (1분):    publish → DB 저장
```

---

## 📈 성능 지표

### Tier 1 기대효과

**월간 콘텐츠 생산**:
```
Tier 1: 13개 종목 × 4주 = 52개 글/월
        (주당 2-3회 생성 기준)
```

**필요 시간**:
```
- 자동화: 5분/회
- 수동: 13개 글 × 10분 = 130분 (2시간 10분/회)
- 주 2-3회 → 월 4.3-6.5시간

전체 월간: ~20-25시간 (월 500-600글 기준)
```

**비용**:
```
- 시스템 운영비: $0
- API 비용: $0 (Claude Code 사용)
- Supabase: 무료
- 총 비용: $0/월
```

---

## 🔄 스케줄 추천

### 위클리 플랜

```
월요일 (Morning)
├─ 뉴스 수집
├─ Tier 1 생성 (3개 글 대상)
└─ Claude Code 작성

수요일 (Afternoon)
├─ Tier 2 또는 추가 Tier 1 생성
└─ Claude Code 작성

금요일 (Evening)
├─ 월말 데이터 정리
├─ Tier 3 (월간 리포트) 준비
└─ 다음주 전략 수립
```

### 먼달리 플랜

```
매월 1일 (첫주)
├─ 지난달 트렌드 분석
├─ Tier 3 생성
└─ 월간 리포트 작성

매월 15일 (셋째주)
├─ Tier 1/2 점검
├─ 필요시 기준 조정
└─ 성과 측정
```

---

## 🎯 모니터링

### Tier 별 성과 지표

```bash
# 현재 Tier 1 대상 종목 확인
python scripts/get_trending.py

# 각 종목별 분석된 뉴스 수 확인
python scripts/get_symbol_stats.py

# 이번 달 생성된 글 확인
ls -la articles/ | wc -l

# 평균 블로그 트래픽 추적
```

### 개선 포인트

1. **분기별 평가**:
   - 각 Tier의 글 실적 분석
   - 독자 피드백 수집
   - 필요시 종목 조정

2. **계절성 고려**:
   - 분기 실적 발표 시즌: Tier 2 증가
   - 경제 뉴스 많은 시기: Tier 1 집중

3. **트렌드 적응**:
   - Tier 3의 동적 선택으로 최신 종목 반영
   - 월간 리뷰로 기준 조정

---

## 🚀 향후 확장

### Phase 1 (현재): Tier 1 중심 운영
- 13개 종목, 주 2-3회 생성
- 안정적 콘텐츠 공급

### Phase 2 (1-2개월 후): Tier 2 추가
- 추가 5개 종목 포함
- 주당 4-5회 생성
- 더 광범위한 시장 커버

### Phase 3 (3개월 후): Tier 3 추가
- 월간 종합 리포트 시작
- 트렌드 분석 콘텐츠
- 뉴스레터 형식 도입

### Phase 4 (6개월 후): 자동화 심화
- Claude API 활용 (월 $20-40)
- 완전 자동 생성 가능
- WordPress 자동 발행

---

## 🆘 트러블슈팅

### "No unpublished news found for SYMBOL"
→ **원인**: 해당 종목의 분석된 뉴스 부족
→ **해결**:
- 더 많은 뉴스 수집 필요
- 관련성 기준 일시 완화 가능

### "프롬프트가 너무 깁니다"
→ **원인**: 종목의 분석된 뉴스가 5개 이상
→ **해결**:
```python
# article_generator.py의 max_news 조정
news_items = self.db.get_unpublished_news_by_symbol(symbol, limit=3)  # 5 → 3
```

### "Claude Code 응답이 불완전합니다"
→ **원인**: 프롬프트가 너무 길거나 요청이 복잡
→ **해결**:
- 프롬프트 일부만 먼저 처리
- 뉴스 개수 줄이기
- Claude에게 "단계별로 작성해달라" 요청

---

## 📞 지원

### 설정 파일
- `config/settings.py` - 모든 Tier 설정
  - `ARTICLE_TIER_*_SYMBOLS`
  - `ARTICLE_TIER_*_MIN_*`
  - `ARTICLE_STRATEGY_CONFIG`

### 실행 파일
- `writers/article_generator.py` - 글 생성 로직
- `scheduler/jobs.py` - 스케줄 관리

### 문서
- `CLAUDE_CODE_WORKFLOW.md` - 기본 워크플로우
- `PROJECT_SUMMARY.md` - 전체 시스템 개요
- 이 파일 - Tier 시스템 상세 가이드

---

## ✅ 체크리스트: Tier 시스템 도입

- [x] Tier 1 설정 (13개 종목)
- [x] Tier 2 설정 (5개 추가 종목)
- [x] Tier 3 설정 (15개 동적 선택)
- [x] `main.py --tier` 파라미터 추가
- [x] `scheduler/jobs.py` 업데이트
- [x] Tier 1 테스트 완료 (13개 프롬프트 생성 성공)
- [ ] Tier 2 테스트
- [ ] Tier 3 테스트
- [ ] 월간 운영 프로세스 수립
- [ ] 성과 측정 대시보드 구축

---

## 🎉 결론

**Tier 기반 시스템의 장점**:

✅ **효율성**: 기준명확, 자동 선택
✅ **품질**: 중요도 기반 필터링
✅ **확장성**: 3단계로 단계적 성장
✅ **유연성**: 언제든 기준 조정 가능
✅ **무료**: API 비용 $0

**다음 단계**: Tier 2 → Tier 3으로 점진적 확대
