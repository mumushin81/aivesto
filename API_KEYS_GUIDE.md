# API 키 발급 완전 가이드

이 문서는 각 API 키를 발급받는 상세한 절차를 설명합니다.

---

## 1. Finnhub API (무료) - 주식 뉴스

### 발급 절차

1. **웹사이트 접속**
   - URL: https://finnhub.io/register

2. **회원가입**
   - Email 입력
   - Password 설정 (최소 8자)
   - "Create Account" 클릭

3. **이메일 인증**
   - 받은편지함 확인
   - Finnhub에서 온 인증 이메일 클릭
   - "Verify Email" 버튼 클릭

4. **API 키 복사**
   - 로그인 후 Dashboard로 이동
   - "API Key" 섹션에서 키 확인
   - 형식: `c123abc456def789` (영숫자 16자)
   - 복사 버튼 클릭

5. **.env 파일에 입력**
   ```env
   FINNHUB_API_KEY=c123abc456def789
   ```

### 무료 플랜 제한사항
- ✅ 60 requests/분
- ✅ 실시간 뉴스 접근
- ✅ 회사 뉴스 접근
- ❌ 프리미엄 데이터 제한

### 테스트 방법
```bash
curl "https://finnhub.io/api/v1/news?category=general&token=YOUR_API_KEY"
```

---

## 2. Alpha Vantage API (무료) - 금융 뉴스 & 감성 분석

### 발급 절차

1. **웹사이트 접속**
   - URL: https://www.alphavantage.co/support/#api-key

2. **API 키 신청**
   - "GET YOUR FREE API KEY TODAY" 클릭
   - Email 주소 입력
   - First Name, Last Name 입력 (선택)
   - Organization (선택, 예: "Personal")
   - "GET FREE API KEY" 클릭

3. **즉시 발급**
   - 화면에 API 키 표시됨
   - 형식: `ABCD1234EFGH5678` (영숫자 16자)
   - 이메일로도 전송됨

4. **이메일 확인**
   - Alpha Vantage에서 온 이메일 확인
   - API 키 재확인

5. **.env 파일에 입력**
   ```env
   ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678
   ```

### 무료 플랜 제한사항
- ⚠️ **25 requests/일** (매우 제한적!)
- ✅ 뉴스 감성 분석
- ✅ 주식 데이터 접근
- 💡 **팁:** 뉴스 수집을 하루 1-2회로 제한

### 테스트 방법
```bash
curl "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey=YOUR_API_KEY&limit=10"
```

### 업그레이드 옵션 (선택)
- **Premium**: $49.99/월 - 75 req/분
- **Enterprise**: 커스텀 가격

---

## 3. Anthropic Claude API (유료) - AI 분석 & 글 작성

### 발급 절차

1. **계정 생성**
   - URL: https://console.anthropic.com/
   - "Sign Up" 클릭
   - Google/Email로 가입

2. **이메일 인증**
   - 받은편지함 확인
   - 인증 링크 클릭

3. **결제 정보 등록**
   - Console > Settings > Billing
   - "Add Payment Method" 클릭
   - 신용카드 정보 입력
   - **최소 충전액: $5**

4. **크레딧 충전**
   - "Add Credits" 클릭
   - 금액 선택 (권장: $20-50)
   - 결제 완료

5. **API 키 생성**
   - Console > API Keys 메뉴
   - "Create Key" 클릭
   - 키 이름 입력 (예: "Stock News Automation")
   - 생성된 키 복사
   - 형식: `sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

6. **⚠️ 중요: 키 저장**
   - **한 번만 표시됩니다!**
   - 안전한 곳에 즉시 저장

7. **.env 파일에 입력**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 가격 정보 (Claude 3.5 Sonnet)
- **Input**: $3 / 1M tokens
- **Output**: $15 / 1M tokens

### 예상 사용량
```
하루 50개 뉴스 분석:
- Input: ~500K tokens/일 = $1.50/일
- Output: ~100K tokens/일 = $1.50/일
- 총: ~$3/일 = $90/월

하루 5개 글 생성:
- Input: ~50K tokens/일 = $0.15/일
- Output: ~25K tokens/일 = $0.38/일
- 총: ~$0.53/일 = $16/월

총 예상: $106/월 (최대)
```

### 비용 절감 팁
1. `MIN_RELEVANCE_SCORE` 높이기 (70 → 80)
2. 분석 간격 늘리기 (30분 → 1시간)
3. 글 생성 횟수 줄이기 (5개 → 3개)
4. **절감 후 예상: $30-50/월**

### 사용량 모니터링
- Console > Usage 메뉴
- 실시간 토큰 사용량 확인
- 일일/월간 통계

### 테스트 방법
```bash
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## 4. Supabase (무료) - 데이터베이스

### 발급 절차

1. **계정 생성**
   - URL: https://supabase.com/
   - "Start your project" 클릭
   - GitHub 계정으로 로그인 (권장)

2. **프로젝트 생성**
   - "New Project" 클릭
   - Organization 선택/생성
   - Project name 입력 (예: `stock-news-db`)
   - Database Password 설정
     - **중요: 안전한 곳에 저장!**
     - 최소 12자, 영숫자+특수문자
   - Region 선택: **Northeast Asia (Seoul)** 권장
   - "Create new project" 클릭

3. **프로젝트 초기화 대기**
   - 약 2-3분 소요
   - "Setting up your project..." 표시

4. **API 정보 복사**
   - 프로젝트 대시보드 열림
   - 좌측 메뉴 > Settings > API
   - **Project URL** 복사
     - 형식: `https://abcdefghijklmnop.supabase.co`
   - **anon public** 키 복사
     - 형식: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

5. **.env 파일에 입력**
   ```env
   SUPABASE_URL=https://abcdefghijklmnop.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzOTU4MDU3NywiZXhwIjoxOTU1MTU2NTc3fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

6. **데이터베이스 스키마 설정**
   - 좌측 메뉴 > SQL Editor
   - "New query" 클릭
   - `database/schema.sql` 파일 내용 복사
   - 붙여넣기
   - "RUN" 버튼 클릭 (또는 Ctrl/Cmd + Enter)
   - "Success. No rows returned" 메시지 확인

7. **테이블 확인**
   - 좌측 메뉴 > Table Editor
   - `news_raw`, `analyzed_news`, `published_articles` 테이블 확인

### 무료 플랜 제한사항
- ✅ 500MB 데이터베이스
- ✅ 2GB 전송량/월
- ✅ 50,000 월간 활성 사용자
- ✅ 무제한 API 요청
- ✅ 7일 로그 보관
- **충분합니다!** 수만 개 뉴스 저장 가능

### 업그레이드 (필요시)
- **Pro**: $25/월 - 8GB DB, 250GB 전송
- **Team**: $599/월

### 테스트 방법
```bash
curl 'https://YOUR_PROJECT.supabase.co/rest/v1/news_raw?select=*&limit=10' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

---

## 5. .env 파일 최종 확인

모든 API 키를 발급받았다면 `.env` 파일이 다음과 같이 구성되어야 합니다:

```env
# Supabase Configuration
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzOTU4MDU3NywiZXhwIjoxOTU1MTU2NTc3fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# News APIs
FINNHUB_API_KEY=c123abc456def789
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678

# AI APIs
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# WordPress (Optional - 나중에 설정)
WORDPRESS_URL=
WORDPRESS_USERNAME=
WORDPRESS_PASSWORD=

# Configuration
NEWS_COLLECTION_INTERVAL=900  # 15 minutes
ANALYSIS_INTERVAL=1800  # 30 minutes
ARTICLE_GENERATION_INTERVAL=3600  # 1 hour
MIN_RELEVANCE_SCORE=70
```

---

## 6. 테스트 실행

모든 API 키를 입력했다면:

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 로그 디렉토리 생성
mkdir logs

# 3. 뉴스 수집 테스트
python main.py --mode collect

# 4. 뉴스 분석 테스트
python main.py --mode analyze

# 5. 블로그 글 생성 테스트
python main.py --mode generate

# 6. 전체 파이프라인 1회 실행
python main.py --mode once
```

---

## 7. API 키 보안 주의사항

### ⚠️ 절대 하지 말아야 할 것
- ❌ GitHub에 `.env` 파일 커밋
- ❌ API 키를 코드에 하드코딩
- ❌ 공개 포럼에 키 공유
- ❌ 스크린샷에 키 노출

### ✅ 해야 할 것
- ✅ `.gitignore`에 `.env` 포함 (이미 설정됨)
- ✅ API 키를 비밀번호 관리자에 저장
- ✅ 정기적으로 키 교체
- ✅ 사용량 모니터링

### 키 유출 시 대처법
1. **즉시 해당 API 키 삭제/재발급**
   - Finnhub: Dashboard > API Key > Regenerate
   - Alpha Vantage: 새로 신청
   - Anthropic: Console > API Keys > Revoke
   - Supabase: Settings > API > Reset

2. **사용량 확인**
   - 이상 사용 내역 체크

3. **새 키로 교체**
   - `.env` 파일 업데이트

---

## 8. 비용 최적화 전략

### Alpha Vantage 제한 대처 (25 req/일)

**옵션 1: 수집 빈도 줄이기**
```env
# .env 수정
NEWS_COLLECTION_INTERVAL=3600  # 15분 → 1시간
```

**옵션 2: Alpha Vantage 비활성화**
```python
# scheduler/jobs.py 수정
self.collectors = [
    FinnhubCollector(self.db),
    # AlphaVantageCollector(self.db),  # 주석 처리
    RSSCollector(self.db)
]
```

**옵션 3: 프리미엄 업그레이드**
- $49.99/월 → 75 req/분

### Claude API 비용 절감

```env
# .env 수정
MIN_RELEVANCE_SCORE=80  # 70 → 80 (더 엄격한 필터링)
ANALYSIS_INTERVAL=3600  # 30분 → 1시간
ARTICLE_GENERATION_INTERVAL=7200  # 1시간 → 2시간
```

```python
# writers/article_generator.py 수정
def generate_daily_articles(self, top_n_symbols: int = 3):  # 5 → 3
```

**예상 절감: $106/월 → $30-40/월**

---

## 9. 문제 해결

### "Invalid API key" 오류
- API 키 형식 확인 (앞뒤 공백 제거)
- 키가 활성화되었는지 확인
- 키를 재발급

### "Rate limit exceeded" 오류
- API 호출 간격 늘리기
- 무료 플랜 제한 확인
- 다음 리셋 시간까지 대기

### Supabase 연결 오류
- URL과 KEY 재확인
- 프로젝트가 일시 중지되지 않았는지 확인
- 네트워크 연결 확인

---

## 10. 다음 단계

✅ 모든 API 키 발급 완료
✅ `.env` 파일 설정 완료
✅ Supabase 데이터베이스 설정 완료

**이제 시스템을 실행할 준비가 되었습니다!**

```bash
python main.py --mode run
```

행운을 빕니다! 🚀
