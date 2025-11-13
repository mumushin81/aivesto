# 🏠 로컬 워크플로우 가이드

**Claude Code 중심의 로컬 분석 및 블로그 글쓰기 시스템**

---

## 📋 개요

### 워크플로우
```
뉴스 수집 (자동)
    ↓
분석 프롬프트 생성 (자동) → Claude Code에 입력
    ↓
분석 결과 저장 (수동 입력)
    ↓
신호 분류 (자동)
    ↓
대시보드 업데이트 (자동)
    ↓
글쓰기 프롬프트 생성 (자동) → Claude Code에 입력
    ↓
글 결과 저장 (수동 입력)
    ↓
완료
```

### 특징
- ✅ Claude API 비용 없음 (로컬 분석)
- ✅ Claude Code가 직접 분석 & 글쓰기
- ✅ 신호 대시보드, 이메일 알림은 자동
- ✅ 완전히 통제 가능한 워크플로우

---

## 🚀 시작하기

### Step 1: 시스템 시작

```bash
# 터미널 1: 뉴스 수집 및 프롬프트 생성 시작
python main.py --mode run
```

출력:
```
=== Running all jobs once ===
=== Starting news collection job ===
=== News collection completed: 23 items ===
=== Starting news analysis job (PROMPT MODE) ===
📝 Generating analysis prompts for 23 news items...
   [1/23] Apple Q4 earnings beat expectations
   [2/23] Microsoft announces AI partnership
   ...
✅ Generated 23 analysis prompts
📂 Location: prompts/analysis/
```

### Step 2: 생성된 프롬프트 확인

```bash
# 분석 프롬프트 디렉토리 확인
ls -la prompts/analysis/

# 또는 프롬프트 내용 보기
cat prompts/analysis/analysis_sample_*.md
```

### Step 3: Claude Code에서 분석

```bash
# 프롬프트 읽기
cat prompts/analysis/analysis_uuid_timestamp.md
```

**그 다음**: 프롬프트 내용을 복사하여 Claude Code 채팅창에 붙여넣기

Claude Code가 JSON 형식의 분석 결과를 제공합니다:
```json
{
  "relevance_score": 92,
  "affected_symbols": ["MSFT", "AAPL"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "...",
  "key_points": ["...", "..."]
}
```

### Step 4: 분석 결과 저장

```bash
# 결과 파일 생성 (Claude Code 응답 복사)
cat > prompts/results/analysis_uuid_timestamp.json << 'EOF'
{
  "news_id": "uuid-from-prompt",
  "relevance_score": 92,
  "affected_symbols": ["MSFT", "AAPL"],
  "price_impact": "up",
  "importance": "high",
  "reasoning": "...",
  "key_points": ["...", "..."]
}
EOF
```

또는 Python 스크립트 사용:
```bash
python load_analysis_results.py
```

### Step 5: 신호 확인

```bash
# 대시보드 서버 시작 (터미널 2)
python dashboard/server.py

# 브라우저에서 http://localhost:5000 접속
```

### Step 6: 글쓰기 프롬프트 생성

```bash
# 글쓰기 프롬프트 생성 (자동)
python main.py --mode generate --tier tier_1

# 출력:
# 📝 Generating articles for Tier 1...
#    [1/13] MSFT: Generated
#    [2/13] AAPL: Generated
# ✅ Article generation completed: 13 articles generated
# 📂 Location: prompts/articles/
```

### Step 7: Claude Code에서 글쓰기

```bash
# 글쓰기 프롬프트 읽기
cat prompts/articles/article_MSFT_timestamp.md
```

**프롬프트를 Claude Code에 붙여넣기**

Claude Code가 다음 형식으로 글을 작성합니다:
```
TITLE:
MSFT 클라우드 전략, 여기가 핵심

CONTENT:
## 📌 핵심 요약 (AI 검색 엔진용)

**상황**: Microsoft가 클라우드 사업에 $10B 투자 발표...
```

### Step 8: 글 결과 저장

```bash
# 글 파일 생성
cat > articles/MSFT_analysis.md << 'EOF'
TITLE:
MSFT 클라우드 전략...

CONTENT:
## 📌 핵심 요약...
EOF

# 또는 Python 스크립트
python save_article.py --file articles/MSFT_analysis.md
```

---

## 📁 디렉토리 구조

```
📦 prompts/
├── 📁 analysis/          ← 분석 프롬프트
│   ├── analysis_uuid_timestamp.md
│   └── analysis_uuid_timestamp.md
├── 📁 results/           ← 분석 결과 (JSON)
│   ├── analysis_uuid_timestamp.json
│   └── analysis_uuid_timestamp.json
├── 📁 articles/          ← 글쓰기 프롬프트
│   ├── article_MSFT_timestamp.md
│   └── article_AAPL_timestamp.md
└── 📁 article_results/   ← 글 결과 (MD)
    ├── MSFT_analysis.md
    └── AAPL_analysis.md
```

---

## 🔄 일일 워크플로우

### 아침 (자동)
```bash
# 터미널에서 시작
python main.py --mode run

# 뉴스 수집 → 분석 프롬프트 생성
# 매 30분마다 반복
```

### 오후 (수동)
```bash
# 1. 분석 프롬프트 확인
ls prompts/analysis/ | head -5

# 2. 프롬프트를 Claude Code에 입력
cat prompts/analysis/analysis_*.md

# 3. 결과를 prompts/results/에 저장
python load_analysis_results.py

# 4. 신호 확인
curl http://localhost:5000/api/signals/urgent
```

### 저녁 (수동)
```bash
# 1. 글쓰기 프롬프트 생성
python main.py --mode generate --tier tier_1

# 2. 프롬프트를 Claude Code에 입력
cat prompts/articles/article_*.md

# 3. 글 결과 저장
python save_article.py --file articles/MSFT_analysis.md
```

---

## 🛠️ 유용한 명령어

### 프롬프트 관리

```bash
# 분석 프롬프트 개수 확인
ls prompts/analysis/ | wc -l

# 최신 분석 프롬프트 보기
cat prompts/analysis/$(ls -t prompts/analysis/ | head -1)

# 결과가 있는 분석만 필터링
ls prompts/results/ | wc -l

# 미처리된 분석 프롬프트
comm -23 <(ls prompts/analysis/ | sort) <(ls prompts/results/ | sort)
```

### 글쓰기 관리

```bash
# 글쓰기 프롬프트 개수
ls prompts/articles/ | wc -l

# 완성된 글 개수
ls articles/ | wc -l

# 미완성 글 목록
comm -23 <(ls prompts/articles/ | sed 's/article_//' | sed 's/_[0-9]*.md//' | sort -u) <(ls articles/ | sed 's/_analysis.md//' | sort -u)
```

### 신호 확인

```bash
# API로 신호 조회
curl http://localhost:5000/api/signals/urgent | jq '.count'

# 트렌딩 종목
curl http://localhost:5000/api/trending-symbols | jq '.symbols[].symbol'

# 대시보드 요약
curl http://localhost:5000/api/dashboard | jq '.urgent_count'
```

---

## 📝 프롬프트 형식

### 분석 프롬프트 (analysis_*.md)

```markdown
당신은 미국 주식 시장 전문 애널리스트입니다...

뉴스 제목: Apple Q4 earnings beat expectations

뉴스 내용:
Apple reported record Q4 earnings...

기존 추출된 심볼: AAPL

다음 항목을 JSON 형식으로 분석해주세요:
[...]

응답 형식 (JSON만 반환):
{
  "relevance_score": 85,
  "affected_symbols": ["AAPL"],
  ...
}
```

### 글쓰기 프롬프트 (article_*.md)

```markdown
당신은 미국 주식 시장 분석 전문가입니다.
다음 기준으로 구글 및 AI 검색 엔진에 노출되기 좋은 글을 한국어로 작성해주세요.

📊 작성 대상: MSFT

분석 대상 뉴스:
[뉴스 1]
제목: Microsoft announces $10B AI investment
...

[작성 가이드 생략]

지금 시작하세요. 글을 작성한 후 위의 형식 (TITLE: / CONTENT:)로 결과를 제시해주세요.
```

---

## 💾 Python 스크립트

### load_analysis_results.py

분석 결과를 자동으로 로드하고 저장:

```python
import json
from pathlib import Path
from database.supabase_client import SupabaseClient
from database.models import AnalyzedNews, PriceImpact, Importance

db = SupabaseClient()

# prompts/results/ 폴더의 모든 JSON 파일 로드
results_dir = Path("prompts/results")

for result_file in results_dir.glob("*.json"):
    with open(result_file) as f:
        data = json.load(f)

    # 데이터베이스에 저장
    analyzed = AnalyzedNews(
        raw_news_id=data["news_id"],
        relevance_score=data["relevance_score"],
        affected_symbols=data["affected_symbols"],
        price_impact=PriceImpact(data["price_impact"]),
        importance=Importance(data["importance"]),
        analysis={
            "reasoning": data.get("reasoning", ""),
            "key_points": data.get("key_points", [])
        }
    )

    db.insert_analyzed_news(analyzed)
    print(f"✅ Saved: {result_file.name}")
```

### save_article.py

글 결과를 자동으로 저장:

```python
import argparse
from pathlib import Path
from database.supabase_client import SupabaseClient
from database.models import PublishedArticle
from writers.article_generator import ArticleGenerator

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, help="Article file path")
args = parser.parse_args()

db = SupabaseClient()
generator = ArticleGenerator(db)

# 파일 읽기
with open(args.file) as f:
    content = f.read()

# 결과 파싱 및 저장
article_data = generator._parse_article_response(content)

published = PublishedArticle(
    title=article_data["title"],
    content=article_data["content"],
    analyzed_news_ids=[]  # 필요시 수동 입력
)

article_id = db.insert_published_article(published)
print(f"✅ Article saved: {article_id}")
```

---

## 🎯 베스트 프랙티스

### 1. 분석 결과 명명
```
prompts/results/analysis_{news_uuid}_{timestamp}.json
```

### 2. 글 파일 명명
```
articles/{SYMBOL}_analysis.md
```

### 3. 배치 처리
한 번에 여러 프롬프트를 Claude Code에 입력:
```bash
# 최대 3개씩 묶기
cat prompts/analysis/analysis_1.md
cat prompts/analysis/analysis_2.md
cat prompts/analysis/analysis_3.md
# → 한 번에 입력 후 결과 3개 저장
```

### 4. 정기적 정리
```bash
# 주 1회 완료된 프롬프트 정리
rm prompts/analysis/analysis_*.md  # 분석된 것만
```

---

## ⚡ 효율성 팁

### 다중 창 설정 (Recommended)
```bash
# 터미널 1: 시스템 실행
python main.py --mode run

# 터미널 2: 대시보드
python dashboard/server.py

# 터미널 3: 파일 작업
cd prompts && ls -la
```

### 자동화 스크립트
```bash
#!/bin/bash
# run_daily.sh

# 1. 프롬프트 생성
python main.py --mode once

# 2. 프롬프트 개수 표시
echo "분석 프롬프트: $(ls prompts/analysis/ | wc -l)개"
echo "글쓰기 프롬프트: $(ls prompts/articles/ | wc -l)개"

# 3. 알림
echo "📝 Claude Code에서 프롬프트를 처리하세요!"
```

---

## 📊 진행 상황 확인

### 대시보드 (웹 UI)
```
http://localhost:5000
```

### API (CLI)
```bash
# 긴급 신호
curl http://localhost:5000/api/signals/urgent

# 고우선순위 신호
curl http://localhost:5000/api/signals/high-priority

# 전체 요약
curl http://localhost:5000/api/dashboard | jq '.'
```

### 파일 시스템
```bash
# 분석 진행률
echo "분석: $(ls prompts/results | wc -l)/$(ls prompts/analysis | wc -l)"

# 글쓰기 진행률
echo "글: $(ls articles | wc -l)/$(ls prompts/articles | wc -l)"
```

---

## 🔧 문제 해결

### Q: 분석 프롬프트가 생성되지 않음
```bash
# 뉴스 수집 확인
python main.py --mode collect

# 로그 확인
tail -f logs/stock_news_*.log
```

### Q: 글쓰기 프롬프트가 생성되지 않음
```bash
# 분석된 뉴스 확인
python -c "from database.supabase_client import SupabaseClient; db = SupabaseClient(); print(len(db.get_high_relevance_news()))"

# 티어 설정 확인
cat config/settings.py | grep ARTICLE_TIER
```

### Q: 대시보드가 로드되지 않음
```bash
# Flask 서버 확인
python dashboard/server.py

# 포트 5000 사용 확인
lsof -i :5000
```

---

## 📚 참고 문서

- **QUICKSTART.md**: 5분 설정 가이드
- **SYSTEM_IMPLEMENTATION.md**: 전체 시스템 설명
- **API_REFERENCE.md**: API 엔드포인트 문서
- **SEO_OPTIMIZED_ARTICLE_GUIDE.md**: 글쓰기 가이드

---

## ✅ 체크리스트

- [ ] 뉴스 수집 확인 (prompts/analysis/ 에 파일이 생성됨)
- [ ] 분석 프롬프트 확인 (cat prompts/analysis/*)
- [ ] Claude Code에서 분석 (프롬프트 입력 후 결과 복사)
- [ ] 결과 저장 (prompts/results/ 에 JSON 저장)
- [ ] 대시보드 확인 (http://localhost:5000)
- [ ] 글쓰기 프롬프트 생성 (python main.py --mode generate)
- [ ] Claude Code에서 글쓰기 (프롬프트 입력 후 결과 복사)
- [ ] 글 저장 (articles/ 에 MD 파일 저장)
- [ ] 완료!

---

**시간 투자**: 하루 30분 ~ 1시간
**자동화 비율**: 70% (수집, 신호 분류, 대시보드)
**수동 작업**: 30% (분석, 글쓰기 - Claude Code)

즐겁게 작업하세요! 🚀
