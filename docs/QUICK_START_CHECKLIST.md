# 🚀 빠른 시작 체크리스트

뉴스 수집 → 블로그 생성 자동화 시스템을 바로 시작하세요!

---

## ✅ 체크리스트

### 1. 환경 설정 (10분)

#### 1.1 Python 패키지 설치
```bash
cd /Users/jinxin/dev/aivesto
pip install yfinance feedparser requests beautifulsoup4 loguru python-dotenv supabase
```

**확인**:
```bash
python -c "import yfinance; print('✅ yfinance 설치 완료')"
```

---

#### 1.2 API 키 발급

##### 🔴 필수 (무료)

**A. FRED API** (5분)
- [ ] https://fred.stlouisfed.org/ 접속
- [ ] 계정 생성 → 로그인
- [ ] My Account → API Keys
- [ ] Request API Key 클릭
- [ ] 발급된 키 복사

**B. FMP API** (3분)
- [ ] https://site.financialmodelingprep.com/ 접속
- [ ] Get Your Free API Key 클릭
- [ ] 이메일/비밀번호 입력
- [ ] 대시보드에서 API Key 복사

**C. yfinance** (이미 설치됨)
- [ ] API 키 불필요 ✅

##### 🟡 선택 (나중에)

**D. Alpha Vantage API**
- [ ] https://www.alphavantage.co/support/#api-key
- [ ] 이메일 입력 → GET FREE API KEY
- [ ] 이메일에서 API 키 확인

---

#### 1.3 .env 파일 설정

```bash
# .env 파일 열기
nano /Users/jinxin/dev/aivesto/.env
```

**추가할 내용**:
```bash
# News Collection API Keys
FRED_API_KEY=여기에_FRED_키_붙여넣기
FMP_API_KEY=여기에_FMP_키_붙여넣기
ALPHA_VANTAGE_API_KEY=여기에_Alpha_Vantage_키_붙여넣기
```

**저장**: `Ctrl + O` → `Enter` → `Ctrl + X`

---

#### 1.4 API 키 검증

```bash
python scripts/test_api_keys.py
```

**기대 결과**:
```
✅ FRED API 정상 작동
✅ FMP API 정상 작동
⚠️  Alpha Vantage API 미설정 (선택사항)
✅ yfinance 정상 작동

총 3/4개 API 정상 작동
```

---

### 2. 데이터베이스 설정 (5분)

#### 2.1 Supabase 대시보드 접속
- [ ] https://supabase.com/dashboard 로그인
- [ ] 프로젝트 선택
- [ ] SQL Editor 메뉴 클릭

#### 2.2 스키마 실행
- [ ] New query 버튼 클릭
- [ ] `/database/news_tables_schema.sql` 파일 내용 복사
- [ ] 붙여넣기
- [ ] Run 버튼 클릭

**확인**:
```sql
SELECT tablename FROM pg_tables
WHERE schemaname = 'public'
AND tablename LIKE '%news%';
```

**기대 결과**:
```
macro_news
earnings_news
sector_news
corporate_events
tech_trends
geopolitical_news
```

---

### 3. 뉴스 수집 테스트 (2분)

#### 3.1 개별 수집기 테스트

```bash
# 테크 트렌드 (가장 안정적)
python scripts/news_collectors/tech_trends_collector.py
```

**기대 결과**:
```
✅ TechCrunch: AI/테크 뉴스 12개 수집
✅ TheVerge: AI/테크 뉴스 6개 수집
✅ NVIDIA 블로그: 10개 수집
✅ 시그널 발견: 2개
```

#### 3.2 전체 수집기 실행

```bash
# 거시경제
python scripts/news_collectors/macro_collector.py

# 실적
python scripts/news_collectors/earnings_collector.py

# 섹터
python scripts/news_collectors/sector_collector.py

# 기업 이슈
python scripts/news_collectors/corporate_events_collector.py

# 지정학
python scripts/news_collectors/geopolitical_collector.py
```

---

### 4. 블로그 생성 테스트 (1분)

```bash
python scripts/generate_blog_from_signals.py
```

**기대 결과**:
```
✅ 총 2개 블로그 글 생성 완료
  📄 MSFT: Microsoft, AI 오피스 통합으로 생산성 혁명 주도
  📄 GOOGL: Google, AI 검색 혁신으로 광고 수익 방어
```

**생성된 파일 확인**:
```bash
ls -lh public/article_*.html
```

---

### 5. 웹사이트 확인 (1분)

#### 로컬 서버 실행
```bash
cd /Users/jinxin/dev/aivesto/public
python -m http.server 8000
```

#### 브라우저에서 확인
- [ ] http://localhost:8000/blog.html
- [ ] 새 글 2개 표시되는지 확인
- [ ] 클릭하여 상세 페이지 확인

---

## 🎯 최종 확인

모든 항목이 체크되었나요?

- [ ] Python 패키지 설치 완료
- [ ] API 키 3개 이상 발급 및 설정
- [ ] API 키 검증 통과 (3/4 이상)
- [ ] 데이터베이스 스키마 배포 완료
- [ ] 뉴스 수집기 정상 작동
- [ ] 블로그 글 자동 생성 성공
- [ ] 웹사이트에서 확인 완료

---

## 🔄 자동화 설정 (선택)

### cron job 설정

매일 오전 9시에 자동으로 뉴스 수집 및 블로그 생성:

```bash
crontab -e
```

**추가할 내용**:
```bash
# 매일 오전 9시: 테크 트렌드 수집
0 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/news_collectors/tech_trends_collector.py

# 매일 오전 9시 10분: 블로그 생성
10 9 * * * cd /Users/jinxin/dev/aivesto && python scripts/generate_blog_from_signals.py
```

---

## 🆘 문제 해결

### 문제 1: API 키 오류
**증상**: `API key not found` 또는 `401 Unauthorized`
**해결**:
```bash
# .env 파일 확인
cat .env | grep API_KEY

# 키가 올바른지 확인
python scripts/test_api_keys.py
```

### 문제 2: 모듈 없음 오류
**증상**: `ModuleNotFoundError: No module named 'yfinance'`
**해결**:
```bash
pip install yfinance feedparser requests beautifulsoup4 loguru
```

### 문제 3: 데이터베이스 테이블 없음
**증상**: `Could not find the table 'tech_trends'`
**해결**:
- Supabase SQL Editor에서 `/database/news_tables_schema.sql` 실행

### 문제 4: 뉴스 수집 안됨
**증상**: `✅ 시그널 발견: 0개`
**해결**:
- 정상입니다! 시그널이 항상 발견되는 것은 아닙니다
- 시그널이 없어도 블로그 생성은 샘플 데이터로 진행됩니다

---

## 📚 추가 문서

- [API 키 설정 상세 가이드](./API_KEYS_SETUP_GUIDE.md)
- [데이터베이스 스키마 설명](../database/news_tables_schema.sql)
- [파이프라인 실행 결과](./NEWS_TO_BLOG_PIPELINE_20251117.md)
- [전체 작업 요약](./WORK_SUMMARY_20251117.md)

---

## 🎉 완료!

모든 체크리스트를 완료하셨다면, 이제 자동화된 AI 투자 뉴스 분석 시스템이 준비되었습니다!

**다음 실행**:
```bash
# 언제든지 실행 가능
python scripts/news_collectors/tech_trends_collector.py
python scripts/generate_blog_from_signals.py
```

**질문이나 문제가 있으시면**:
- 문서 확인: `/docs/` 폴더
- GitHub Issues: 문제 보고
