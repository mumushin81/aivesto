# 📚 기사 품질 개선 파이프라인 (옵션 B 구현)

## 🎯 목표

모든 생성되는 기사가 다음 품질 기준을 충족하도록 자동화:

| 기준 | 요구사항 | 현황 | 목표 |
|------|---------|------|------|
| **파일 형식** | TITLE: / CONTENT: 구조 | ❌ 0% | ✅ 100% |
| **필수 섹션** | "무슨 일이" + "왜 주가에" | ❌ 0% | ✅ 100% |
| **한국어 비율** | 70% 이상 | ⚠️ 42-69% | ✅ 70%+ |
| **내부 링크** | 2-5개 | ❌ 0개 | ✅ 2-5개 |
| **내용 길이** | 500자 이상 | ⚠️ 부분 미충족 | ✅ 모두 충족 |

---

## 🏗️ 시스템 아키텍처

### Phase 1: 향상된 프롬프트 (자동)
```
generate_articles_job()
    ↓
ArticleGenerator._build_article_prompt()
    • TITLE: / CONTENT: 형식 명시
    • 필수 섹션 요구 (무슨 일이/왜 주가에)
    • 한국어 비율 70% 이상 강조
    • 내부 링크 2-5개 요구
    • 자동 검증 시스템 설명
```

### Phase 2: 기사 작성 (수동 - Claude Code)
```
Claude Code에서 프롬프트를 읽고
위 요구사항을 모두 충족하는 기사 작성
```

### Phase 3: 자동 검증 및 수정 (자동)
```
load_article_from_file()
    ↓
ArticleFormatter.validate_and_fix()
    • 파일 형식 검증 및 수정
    • 필수 섹션 확인 및 추가
    • 한국어 비율 개선
    • 내부 링크 추가
    • 최종 점수 계산
    ↓
수정된 기사 저장 + 점수 로그
```

---

## 📝 새로운 파일과 변경사항

### 1. 새로운 파일: `writers/article_formatter.py`
기사 형식 검증 및 자동 수정 클래스

**주요 기능:**
```python
class ArticleFormatter:
    def validate_and_fix(content, symbol) -> Dict
        # 파일 형식 검증 및 수정
        # 필수 섹션 확인 및 추가
        # 한국어 비율 계산 및 개선
        # 내부 링크 추가
        # 점수 계산

    def _fix_file_format(content) -> str
        # TITLE: / CONTENT: 구조로 변환

    def _add_missing_sections(content, missing) -> tuple
        # 누락된 필수 섹션 자동 추가

    def _improve_korean_ratio(content) -> str
        # 영문 약자에 한국어 설명 추가
        # AI → AI(인공지능)

    def _add_internal_links(content, symbol) -> str
        # 관련 기사 섹션 자동 생성
        # 마크다운 링크 추가
```

### 2. 수정된 파일: `writers/article_generator.py`

**변경사항 1: ArticleFormatter 통합**
```python
def __init__(self, db_client: SupabaseClient):
    ...
    self.formatter = ArticleFormatter()  # 추가
```

**변경사항 2: 향상된 프롬프트**
```python
def _build_article_prompt(symbol, news_items) -> str
    # 추가: "✅ 품질 요구사항 (자동 검증)" 섹션
    # 파일 형식, 필수 섹션, 한국어 비율, 내부 링크 명시
    # 자동 검증 시스템 설명 추가
```

**변경사항 3: 자동 검증 통합**
```python
def load_article_from_file(article_file, news_items) -> Optional[str]
    # 기사 로드
    # ArticleFormatter.validate_and_fix() 호출
    # 검증 결과 로깅 (점수, 문제, 수정사항)
    # 수정된 콘텐츠 저장
```

---

## 🔄 동작 흐름

### 예시: MSFT 기사 생성

```
1️⃣ 프롬프트 생성 (자동)
   scheduler/jobs.py: generate_articles_job()
   → prompts/article_MSFT_20251113_140000.md 생성

2️⃣ Claude Code에서 작성 (수동)
   프롬프트 읽기
   → MSFT AI 투자 기사 작성
   → TITLE: / CONTENT: 형식 준수
   → 필수 섹션 포함
   → 한국어 비율 70% 이상
   → 내부 링크 2-5개
   → articles/article_MSFT_AI_investment_20251113.md 저장

3️⃣ 자동 검증 및 수정
   load_article_from_file() 호출
   ├─ 파일 형식 검증 ✓
   ├─ 필수 섹션 확인 ✓
   ├─ 한국어 비율 검증 (69% 발견)
   │  └─ 자동 개선: AI → AI(인공지능)
   ├─ 내부 링크 확인 (1개 발견)
   │  └─ 자동 추가: 2-5개 목표
   └─ 점수 계산: 85/100 → 95/100

4️⃣ 데이터베이스 저장
   published_articles 테이블에 저장
   log: "✅ Article saved: Microsoft AI 투자 전략 (Quality: 95/100)"
```

---

## 📊 검증 기준 상세

### 1. 파일 형식 (필수)
```markdown
TITLE:
기사 제목

CONTENT:
## 소제목

기사 본문...
```

❌ **잘못된 형식:**
```markdown
# 기사 제목
기사 본문...
```

✅ **자동 수정:**
```python
# ArticleFormatter._fix_file_format()
# "# 제목\n본문" → "TITLE:\n제목\n\nCONTENT:\n본문"
```

---

### 2. 필수 섹션 (2가지)

#### 섹션 1: "무슨 일이 일어났나"
- **목적:** 최근 뉴스/이벤트 설명
- **위치:** 본문 앞부분 (AI 요약 전)
- **내용:** 구체적 사건, 날짜, 배경

#### 섹션 2: "왜 주가에 영향을 주는가"
- **목적:** 시장 영향 분석
- **위치:** 본문 중간
- **내용:** 재무 영향, 시장 심리, 평가 변화

✅ **자동 추가:**
```python
# ArticleFormatter._add_missing_sections()
# 누락된 섹션을 자동으로 추가
```

---

### 3. 한국어 비율 (최소 70%)

**계산 방식:**
```
한국어 문자 / (한글 + 영문 + 숫자) × 100%
```

**개선 예시:**
```
❌ 원본: "AI and ML technologies"
✅ 개선: "AI(인공지능) 및 ML(머신러닝) 기술"

개선율: 40% → 75%
```

**지원 약자:**
- AI → AI(인공지능)
- ML → ML(머신러닝)
- API → API(응용프로그래밍)
- UI/UX → UI(사용자인터페이스)/UX(사용자경험)
- EPS → EPS(주당이익)
- P/E → P/E(주가수익비율)
- Market Cap → 시가총액(Market Cap)
- ROI → ROI(투자수익률)

---

### 4. 내부 링크 (2-5개)

**형식:**
```markdown
[기사 제목](./articles/article_파일명.md)
```

**예시:**
```markdown
### 📚 관련 기사

- [마이크로소프트 AI 투자](./articles/MSFT_AI.md)
- [클라우드 시장 2033년 전망](./articles/cloud_2033.md)
- [기술주 시장 동향](./articles/tech_trends.md)
```

---

### 5. 내용 길이 (최소 500자)

- 마크다운 기호 제외
- 링크 URL 제외
- 순 텍스트만 계산

---

## 🧪 테스트 결과

### 테스트 1: 새 기사 (완전한 형식)
```
입력: 올바른 형식의 기사
출력:
  원본 점수: 90/100
  수정 후 점수: 100/100
  수정: 내부 링크 추가
```

### 테스트 2: 기존 기사 (부분 형식)
```
입력: articles/article_AAPL_AI_strategy_20251112.md
출력:
  원본 점수: 85/100
  수정 후 점수: 100/100
  수정 3가지:
    ✅ 파일 형식 추가
    ✅ 필수 섹션 추가
    ✅ 내부 링크 추가
```

---

## 📈 예상 효과

### 현재 상태 (옵션 B 이전)
| 지표 | 값 |
|------|-----|
| 평균 점수 | 38.8/100 |
| 파일 형식 준수 | 0% |
| 필수 섹션 포함 | 0% |
| 한국어 비율 | 42-69% |
| 내부 링크 | 0개/평균 |

### 예상 상태 (옵션 B 실행 후)
| 지표 | 값 | 개선 |
|------|-----|------|
| 평균 점수 | ~90/100 | +51점 |
| 파일 형식 준수 | 100% | 완전 자동화 |
| 필수 섹션 포함 | 100% | 자동 추가 |
| 한국어 비율 | 70%+ | 자동 개선 |
| 내부 링크 | 2-5개/평균 | 자동 추가 |

---

## 🚀 사용 방법

### 방법 1: 새 기사 생성 (권장)
```bash
# 프롬프트 생성
python -c "
from writers import ArticleGenerator
from database.supabase_client import SupabaseClient

db = SupabaseClient()
gen = ArticleGenerator(db)
gen.generate_article('MSFT')  # prompts/article_MSFT_*.md 생성
"

# Claude Code에서:
# 1. prompts/article_MSFT_*.md 파일 읽기
# 2. 요구사항 확인:
#    - TITLE: / CONTENT: 형식
#    - 필수 섹션 (무슨 일이/왜 주가에)
#    - 한국어 비율 70%+
#    - 내부 링크 2-5개
# 3. articles/article_MSFT_*.md 저장

# 자동 검증 및 수정
python -c "
from writers import ArticleGenerator
from database.supabase_client import SupabaseClient

db = SupabaseClient()
gen = ArticleGenerator(db)
gen.load_article_from_file('articles/article_MSFT_*.md', [])
"
```

### 방법 2: 기존 기사 개선
```bash
python scripts/validate_article_quality.py \
  --dir articles/ \
  --output validation_report.json \
  --verbose
```

---

## 📋 체크리스트 (Claude Code용)

기사를 작성할 때 다음을 확인하세요:

- [ ] TITLE: / CONTENT: 형식 사용
- [ ] "무슨 일이 일어났나" 섹션 포함
- [ ] "왜 주가에 영향을 주는가" 섹션 포함
- [ ] 한국어 비율 70% 이상 (영문은 한국어 설명 병행)
- [ ] 내부 링크 2-5개 추가
- [ ] 내용 길이 500자 이상
- [ ] 제목 60자 이내
- [ ] 모든 마크다운 헤더 사용 (##, ###)
- [ ] 표, 리스트로 정보 시각화
- [ ] 출처와 링크 명시

---

## 🔧 커스터마이징

### 요구사항 변경 시

**파일:** `writers/article_formatter.py`

```python
class ArticleFormatter:
    def __init__(self):
        self.min_korean_ratio = 0.70  # 70% → 원하는 값으로 변경
        self.min_internal_links = 2   # 2개 → 원하는 값으로 변경
        self.max_internal_links = 5   # 5개 → 원하는 값으로 변경
```

---

## 📞 문제 해결

### Q: 자동 수정이 작동하지 않습니다
**A:** 검증 점수가 표시되는지 확인하세요. 로그를 보면 수정 사항이 나옵니다.

### Q: 한국어 비율 계산이 잘못된 것 같습니다
**A:** 공백, 줄바꿈, 마크다운 기호는 계산에 포함되지 않습니다.

### Q: 내부 링크가 추가되지 않습니다
**A:** `articles/` 폴더의 파일 이름을 정확히 참조해야 합니다.

---

## 📊 향후 개선 계획

- [ ] 자동 기사 생성 (Claude Code 없이)
- [ ] 더 정교한 한국어 비율 계산
- [ ] SEO 최적화 자동 검증
- [ ] 기사 길이별 템플릿 제공
- [ ] 대시보드에서 품질 점수 표시

---

**마지막 업데이트:** 2025-11-13
**버전:** 1.0 (옵션 B - 파이프라인 자동화)
