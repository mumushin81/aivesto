# 🤖 Claude Code 워크플로우 가이드

**완전 무료 버전 - API 비용 $0**

Claude Code를 직접 활용하여 뉴스 분석 및 블로그 글을 작성하는 워크플로우입니다.

---

## 💡 핵심 아이디어

Claude API를 사용하는 대신, **Claude Code를 직접 사용**하여:
1. 뉴스를 자동 수집
2. 분석 프롬프트 자동 생성
3. Claude Code에서 프롬프트 기반으로 분석/작성
4. 결과를 데이터베이스에 저장

**비용**: $0 (완전 무료!)

---

## 🔄 일일 워크플로우

### Morning (아침): 뉴스 수집 및 분석 준비

#### 1. 뉴스 자동 수집 (5분)

```bash
# 뉴스 수집 실행
python main.py --mode collect
```

**결과**:
- Finnhub, Alpha Vantage, RSS에서 최신 뉴스 수집
- Supabase에 자동 저장
- 중복 제거

#### 2. 분석 프롬프트 생성 (1분)

```bash
# 일일 워크플로우 프롬프트 생성
python scripts/generate_daily_workflow.py
```

**생성되는 파일**:
- `prompts/workflow_YYYYMMDD_HHMM.md` - 오늘의 작업 가이드
- `prompts/analysis_YYYYMMDD_HHMM.md` - 뉴스 분석 프롬프트

**예시 출력**:
```
✅ Generated daily workflow

📁 Files created:
  - prompts/workflow_20251112_0900.md
  - prompts/analysis_20251112_0900.md

📊 Today's work:
  - 46 news items to analyze
  - Estimated time: 30-45 minutes

🔄 Next step:
  1. Open prompts/analysis_20251112_0900.md
  2. Analyze news in Claude Code
  3. Save results as prompts/analysis_results_20251112_0900.json
```

---

### Midday (점심): 뉴스 분석 (30-45분)

#### 3. Claude Code로 뉴스 분석

```bash
# 분석 프롬프트 열기
cat prompts/analysis_20251112_0900.md
```

**Claude Code에서 작업**:

1. 프롬프트 내용 복사
2. Claude Code에 붙여넣기
3. Claude가 각 뉴스 분석
4. 결과를 JSON 형식으로 받기

**예시 대화**:
```
User: [분석 프롬프트 전체 붙여넣기]

Claude: 네, 46개 뉴스를 분석하겠습니다.

[각 뉴스 분석 후]

분석 결과를 JSON 배열로 작성했습니다:

```json
[
  {
    "news_id": "abc123...",
    "relevance_score": 85,
    "affected_symbols": ["AAPL", "MSFT"],
    "price_impact": "up",
    "importance": "high",
    "reasoning": "애플이 신제품을 발표...",
    "key_points": [...]
  },
  ...
]
```

User: 이 결과를 prompts/analysis_results_20251112_0900.json에 저장해줘

Claude: [파일 저장 완료]
```

#### 4. 분석 결과 데이터베이스 저장 (1분)

```bash
# 분석 결과 저장
python scripts/save_analysis.py prompts/analysis_results_20251112_0900.json
```

**출력**:
```
✅ Successfully saved 12/46 analysis results to database
(관련성 점수 70+ 만 저장됨)
```

---

### Afternoon (오후): 블로그 글 작성 (30-45분)

#### 5. 트렌딩 종목 확인 (1분)

```bash
# 인기 종목 확인
python scripts/get_trending.py
```

**출력**:
```
📈 Top 10 Trending Symbols

============================================================
 1. AAPL   -  15 mentions
 2. TSLA   -  12 mentions
 3. NVDA   -  10 mentions
 4. MSFT   -   8 mentions
 5. GOOGL  -   7 mentions
...
============================================================

💡 Recommended for article generation: AAPL, TSLA, NVDA

🔄 Next step:
python scripts/generate_article_prompts.py AAPL TSLA NVDA
```

#### 6. 글 작성 프롬프트 생성 (1분)

```bash
# 상위 3개 종목에 대한 글 작성 프롬프트 생성
python scripts/generate_article_prompts.py AAPL TSLA NVDA
```

**출력**:
```
✅ Generated 3 article prompts

======================================================================
📝 AAPL   - 5 news items → prompts/article_AAPL_20251112_1400.md
📝 TSLA   - 4 news items → prompts/article_TSLA_20251112_1400.md
📝 NVDA   - 3 news items → prompts/article_NVDA_20251112_1400.md
======================================================================

🔄 Next steps:
1. Open each prompt file
2. Use Claude Code to write articles
3. Save articles as .md files in 'articles/' directory
4. Run: python scripts/publish_articles.py articles/article_*.md
```

#### 7. Claude Code로 블로그 글 작성 (종목당 10분)

**각 종목별로 반복**:

```bash
# AAPL 프롬프트 열기
cat prompts/article_AAPL_20251112_1400.md
```

**Claude Code에서 작업**:

```
User: [글 작성 프롬프트 전체 붙여넣기]

Claude: 네, AAPL 관련 뉴스 5개를 종합하여 블로그 글을 작성하겠습니다.

# AAPL 관련 최신 뉴스 분석 - 신제품 출시, 실적 호조, AI 투자

## 📊 무엇이 일어났는가

애플(AAPL)은 이번 주 여러 긍정적인 뉴스를 발표했습니다...

[전체 글 작성...]

User: 이 글을 articles/article_AAPL_20251112_1400.md로 저장해줘

Claude: [파일 저장 완료]
```

**TSLA, NVDA도 동일하게 반복**

#### 8. 블로그 글 발행 (1분)

```bash
# 작성한 글들을 데이터베이스에 저장
python scripts/publish_articles.py articles/article_AAPL_20251112_1400.md articles/article_TSLA_20251112_1400.md articles/article_NVDA_20251112_1400.md
```

**출력**:
```
📤 Publishing 3 articles...

✅ articles/article_AAPL_20251112_1400.md
✅ articles/article_TSLA_20251112_1400.md
✅ articles/article_NVDA_20251112_1400.md

============================================================
Published: 3/3 articles
============================================================

🎉 Articles successfully published to database!

View in Supabase:
SELECT title, created_at FROM published_articles ORDER BY created_at DESC LIMIT 10;
```

---

## 📋 요약: 일일 체크리스트

**Morning (10분)**
- [ ] 뉴스 수집: `python main.py --mode collect`
- [ ] 프롬프트 생성: `python scripts/generate_daily_workflow.py`

**Midday (30-45분)**
- [ ] Claude Code로 뉴스 분석
- [ ] 분석 결과 저장: `python scripts/save_analysis.py ...`

**Afternoon (30-45분)**
- [ ] 트렌딩 종목 확인: `python scripts/get_trending.py`
- [ ] 글 작성 프롬프트 생성: `python scripts/generate_article_prompts.py ...`
- [ ] Claude Code로 글 작성 (3-5개)
- [ ] 글 발행: `python scripts/publish_articles.py ...`

**총 소요 시간**: 70-100분/일
**비용**: $0 (완전 무료!)

---

## 🎯 자동화 수준

### 완전 자동 (스크립트)
✅ 뉴스 수집 (Finnhub, Alpha Vantage, RSS)
✅ 프롬프트 생성 (분석, 글 작성)
✅ 트렌딩 종목 추출
✅ 결과 저장 (Supabase)

### 반자동 (Claude Code 활용)
🤖 뉴스 분석 (프롬프트 → Claude Code → JSON)
🤖 블로그 글 작성 (프롬프트 → Claude Code → Markdown)

### 수동 (사용자)
👤 Claude Code와 상호작용
👤 결과물 품질 확인

---

## 💰 비용 비교

| 항목 | API 방식 | Claude Code 방식 |
|------|----------|------------------|
| Claude API | $25-100/월 | **$0** |
| Finnhub | 무료 | 무료 |
| Alpha Vantage | 무료 | 무료 |
| Supabase | 무료 | 무료 |
| **총 비용** | **$25-100/월** | **$0/월** |

**절감액**: 월 $25-100 (연간 $300-1,200)

---

## 🚀 장점

### Claude Code 방식의 이점

1. **완전 무료** - API 비용 $0
2. **품질 관리** - 각 글을 직접 확인
3. **유연성** - 실시간 수정 및 개선 가능
4. **학습** - 주식 뉴스 분석 능력 향상
5. **커스터마이징** - 원하는 스타일로 작성

### 추가 이점

- Claude Code Pro 구독만으로 무제한 사용
- API 제한 없음
- 토큰 사용량 걱정 없음
- 더 나은 품질 컨트롤

---

## ⚡ 팁 & 트릭

### 효율성 높이기

**1. 배치 처리**
```bash
# 아침에 한 번에 처리
python main.py --mode collect && \
python scripts/generate_daily_workflow.py
```

**2. 단축 명령어 (alias)**
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
alias sn-collect='python main.py --mode collect'
alias sn-workflow='python scripts/generate_daily_workflow.py'
alias sn-trending='python scripts/get_trending.py'
```

**3. Claude Code 대화 저장**
- 분석 대화를 템플릿으로 저장
- 다음 번에 빠르게 재사용

**4. 글 작성 시간 단축**
- 자주 사용하는 문구 템플릿화
- 종목별 배경 정보 미리 준비

---

## 🔧 고급 활용

### 주간 배치 처리

주말에 한 주간 뉴스 한 번에 처리:

```bash
# 월-금 뉴스 한 번에 수집 (크론으로 자동화)
0 9 * * 1-5 python main.py --mode collect

# 금요일 오후에 일괄 분석
0 15 * * 5 python scripts/generate_daily_workflow.py
```

### 품질 향상

Claude Code에 추가 지시:

```
분석 시 추가 고려사항:
- 과거 유사 사건과의 비교
- 경쟁사 영향 분석
- 거시경제 환경 고려
```

---

## 🆘 문제 해결

### "프롬프트가 너무 깁니다"
→ 뉴스 개수 제한:
```bash
# main.py 수정
unanalyzed_news = self.db.get_unanalyzed_news(limit=20)  # 50 → 20
```

### "Claude Code 응답이 중단됩니다"
→ 배치 크기 줄이기:
```bash
python scripts/generate_article_prompts.py AAPL  # 한 번에 1개씩
```

### "JSON 형식이 잘못되었습니다"
→ Claude에게 재요청:
```
User: JSON 형식이 잘못되었어. 다시 작성해줘.
      반드시 유효한 JSON 배열로만 출력해줘.
```

---

## 📈 확장 가능성

### WordPress 자동 발행

작성한 글을 WordPress에 자동 업로드:

```bash
python scripts/publish_to_wordpress.py articles/article_AAPL_*.md
```

### 소셜 미디어 공유

트위터/페이스북 자동 게시:

```bash
python scripts/share_to_social.py articles/article_AAPL_*.md
```

### 이메일 뉴스레터

구독자에게 자동 발송:

```bash
python scripts/send_newsletter.py --articles articles/article_*.md
```

---

## 🎉 결론

Claude Code 워크플로우는:
- ✅ **완전 무료** ($0/월)
- ✅ **높은 품질** (직접 확인)
- ✅ **유연한 운영** (원하는 시간에)
- ✅ **확장 가능** (자동화 추가)

**하루 1-2시간 투자로 양질의 주식 뉴스 블로그 운영!**
