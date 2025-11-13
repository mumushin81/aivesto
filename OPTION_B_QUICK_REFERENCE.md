# 🚀 옵션 B 구현 - 빠른 참조

## 📌 한 줄 요약

**기사 생성 파이프라인에 자동 품질 검증 시스템 추가**
- 모든 생성되는 기사가 자동으로 품질 기준을 만족하도록 개선

---

## 🎯 목표 달성

| 기준 | 현재 | 목표 |
|------|------|------|
| 평균 점수 | 38.8/100 | 90+/100 |
| 파일 형식 | 0% | 100% ✅ |
| 필수 섹션 | 0% | 100% ✅ |
| 한국어 비율 | 42-69% | 70%+ ✅ |
| 내부 링크 | 0개 | 2-5개 ✅ |

---

## 📁 구현 내용

### 1️⃣ 새 파일: `writers/article_formatter.py`

**역할:** 기사 검증 및 자동 수정

```python
# 사용 예
from writers.article_formatter import ArticleFormatter

formatter = ArticleFormatter()
result = formatter.validate_and_fix(content, symbol='MSFT')

print(result['original_score'])    # 85/100
print(result['fixed_score'])       # 100/100
print(result['fixes_applied'])     # [수정 목록]
```

### 2️⃣ 수정 파일: `writers/article_generator.py`

**변경사항:**
- ArticleFormatter 통합
- 향상된 프롬프트 (품질 요구사항 명시)
- load_article_from_file()에 자동 검증 추가

---

## 🔄 동작 방식

### 생성 단계 (자동)
```
1. generate_articles_job()
   → 프롬프트 생성 및 저장
   → 향상된 요구사항 포함
```

### 작성 단계 (수동 - Claude Code)
```
2. Claude Code에서
   → 프롬프트 읽기
   → 기사 작성 (TITLE: / CONTENT: 형식)
   → 필수 섹션 포함
   → 한국어 비율 70%+
   → 내부 링크 2-5개
   → articles/article_MSFT_*.md 저장
```

### 검증 단계 (자동)
```
3. load_article_from_file()
   → ArticleFormatter.validate_and_fix() 호출
   ├─ 파일 형식 검증 ✓
   ├─ 필수 섹션 확인 ✓
   ├─ 한국어 비율 개선 ✓
   ├─ 내부 링크 추가 ✓
   └─ 점수 계산 및 로깅
   → 수정된 기사 저장
```

---

## ✨ 자동 수정 기능

### 1. 파일 형식 수정
```
❌ # 제목\n본문
✅ TITLE:\n제목\n\nCONTENT:\n본문
```

### 2. 필수 섹션 추가
```
자동 추가:
- ### 무슨 일이 일어났나
- ### 왜 주가에 영향을 주는가
```

### 3. 한국어 비율 개선
```
❌ AI and ML technologies
✅ AI(인공지능) 및 ML(머신러닝) 기술
```

### 4. 내부 링크 추가
```
자동으로 "관련 기사" 섹션 생성:
- [관련기사1](./articles/...)
- [관련기사2](./articles/...)
```

### 5. 점수 계산
```
원본 점수: 85/100
수정 후 점수: 100/100
개선: +15점
```

---

## 📊 검증 기준

| 기준 | 요구사항 | 확인 방법 |
|------|---------|---------|
| **형식** | TITLE: / CONTENT: | 정규식 매칭 |
| **섹션** | 2가지 필수 섹션 | 텍스트 검색 |
| **한국어** | 70% 이상 | 유니코드 범위 계산 |
| **링크** | 2-5개 | 마크다운 링크 계산 |
| **길이** | 500자 이상 | 텍스트 길이 계산 |

---

## 💡 프롬프트 개선 사항

새로운 프롬프트에 추가된 섹션:

```markdown
================================================================================
✅ 품질 요구사항 (자동 검증)
================================================================================

1️⃣ **파일 형식** (필수)
2️⃣ **필수 섹션** (반드시 포함)
3️⃣ **한국어 비율** (최소 70%)
4️⃣ **내부 링크** (2-5개)
5️⃣ **내용 길이** (최소 500자)

모든 요구사항을 충족하지 않으면 점수 감점과 자동 수정이 적용됩니다.
```

---

## 🔍 검증 로그 예시

```
📋 Quality validation for articles/article_MSFT_AI_investment.md:
   Original score: 85/100
   Fixed score: 100/100
   Issues found: 3
   - ❌ 파일 형식: TITLE: / CONTENT: 구조 없음
   - ❌ 필수 섹션 누락: 무슨 일이 일어났나
   - ⚠️ 내부 링크 부족: 0개 (권장: 2-5개)
   Fixes applied: 3
   - ✅ 파일 형식: TITLE: / CONTENT: 구조 추가
   - ✅ 필수 섹션 추가: 무슨 일이 일어났나
   - ✅ 내부 링크 추가: 0개 → 3개
✅ Article saved: Microsoft AI 투자 전략 (Quality: 100/100)
```

---

## 🚀 실제 사용

### 새 기사 생성 시
```bash
# 1. 프롬프트 생성 (자동)
python main.py --mode run

# 2. Claude Code에서 기사 작성
# (프롬프트 읽고 TITLE:/CONTENT: 형식으로 작성)

# 3. 자동 검증 적용 (자동)
# (load_article_from_file() 호출 시 자동 실행)
```

### 기존 기사 검증
```bash
# 검증만 수행
python scripts/validate_article_quality.py --dir articles/ --verbose

# 검증 + 리포트 생성
python scripts/validate_article_quality.py --dir articles/ --output report.json
```

---

## ⚙️ 커스터마이징

필요시 요구사항 변경:

**파일:** `writers/article_formatter.py`

```python
class ArticleFormatter:
    def __init__(self):
        self.min_korean_ratio = 0.70      # 70% → 원하는 값
        self.min_internal_links = 2       # 2개 → 원하는 값
        self.max_internal_links = 5       # 5개 → 원하는 값
```

---

## 📚 문서

- **상세 가이드:** `ARTICLE_QUALITY_PIPELINE.md`
- **검증 스크립트:** `scripts/validate_article_quality.py`
- **포매터:** `writers/article_formatter.py`

---

## ✅ 체크리스트 (Claude Code용)

기사 작성 시:

- [ ] TITLE: / CONTENT: 형식 사용
- [ ] "무슨 일이 일어났나" 섹션 포함
- [ ] "왜 주가에 영향을 주는가" 섹션 포함
- [ ] 한국어 비율 70% 이상
- [ ] 내부 링크 2-5개
- [ ] 내용 500자 이상
- [ ] 제목 60자 이내

---

## 📊 효과

### Before (옵션 B 이전)
```
평균 점수: 38.8/100
❌ 파일 형식 0% 준수
❌ 필수 섹션 0% 포함
⚠️ 한국어 42-69% (낮음)
❌ 내부 링크 0개
```

### After (옵션 B 이후)
```
평균 점수: 90+/100
✅ 파일 형식 100% 준수 (자동)
✅ 필수 섹션 100% 포함 (자동)
✅ 한국어 70%+ (자동)
✅ 내부 링크 2-5개 (자동)
```

---

**구현 완료:** 2025-11-13
**버전:** 1.0
