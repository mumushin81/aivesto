# 🔑 .env 파일 설정 가이드 (Claude Code 버전)

.env 파일이 생성되었습니다! 이제 API 키만 입력하면 됩니다.

---

## ✅ .env 파일 위치

```
/Users/jinxin/dev/stock-news-automation/.env
```

---

## 📝 필요한 API 키 (3개만!)

Claude Code 버전은 **Claude API가 필요 없습니다!**

### 필수 API 키 (무료)

1. ✅ **Finnhub API Key** (무료)
2. ✅ **Alpha Vantage API Key** (무료)
3. ✅ **Supabase URL & Key** (무료)

### 선택 API 키 (나중에)

4. ⏭️ **WordPress** (선택사항 - 나중에 설정)

---

## 🚀 빠른 설정 (5분)

### 방법 1: 텍스트 에디터로 편집

```bash
# nano 에디터로 열기
nano .env

# 또는 VS Code로 열기
code .env

# 또는 vim으로 열기
vim .env
```

### 방법 2: 명령어로 직접 입력

```bash
# Supabase 설정
echo 'SUPABASE_URL=https://실제URL.supabase.co' >> .env
echo 'SUPABASE_KEY=실제키' >> .env

# 뉴스 API 설정
echo 'FINNHUB_API_KEY=실제키' >> .env
echo 'ALPHA_VANTAGE_API_KEY=실제키' >> .env
```

---

## 📋 단계별 가이드

### 1단계: Finnhub API 키 발급 (1분)

```bash
# 1. 브라우저에서 열기
open https://finnhub.io/register

# 2. 이메일로 가입
# 3. Dashboard에서 API Key 복사
# 4. .env 파일에 붙여넣기
```

**.env 파일에 입력**:
```env
FINNHUB_API_KEY=여기에_복사한_키_붙여넣기
```

**예시**:
```env
FINNHUB_API_KEY=c123abc456def789
```

---

### 2단계: Alpha Vantage API 키 발급 (1분)

```bash
# 1. 브라우저에서 열기
open https://www.alphavantage.co/support/#api-key

# 2. 이메일 입력 후 "GET FREE API KEY" 클릭
# 3. 화면에 표시된 키 복사
# 4. .env 파일에 붙여넣기
```

**.env 파일에 입력**:
```env
ALPHA_VANTAGE_API_KEY=여기에_복사한_키_붙여넣기
```

**예시**:
```env
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678
```

---

### 3단계: Supabase 프로젝트 생성 (3분)

```bash
# 1. 브라우저에서 열기
open https://supabase.com

# 2. GitHub로 로그인
# 3. "New Project" 클릭
# 4. 프로젝트 정보 입력
```

**프로젝트 설정**:
- Name: `stock-news-db`
- Database Password: 안전한 비밀번호 (저장 필수!)
- Region: `Northeast Asia (Seoul)` 선택
- Create new project 클릭

**2-3분 대기 후...**

```bash
# Settings > API 메뉴로 이동
# 1. Project URL 복사
# 2. anon public key 복사
```

**.env 파일에 입력**:
```env
SUPABASE_URL=https://복사한URL.supabase.co
SUPABASE_KEY=복사한_anon_public_키
```

**예시**:
```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYzOTU4MDU3NywiZXhwIjoxOTU1MTU2NTc3fQ.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## ✅ 최종 .env 파일 예시

```env
# Supabase Configuration
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.실제키...

# News APIs
FINNHUB_API_KEY=c123abc456def789
ALPHA_VANTAGE_API_KEY=ABCD1234EFGH5678

# AI - Claude Code 사용 (API 키 불필요!)
# ANTHROPIC_API_KEY=  # 제거 - Claude Code 직접 사용
# OPENAI_API_KEY=  # 제거 - 사용하지 않음

# WordPress (optional) - 나중에 설정
WORDPRESS_URL=
WORDPRESS_USERNAME=
WORDPRESS_PASSWORD=

# Configuration - 기본값 사용 (수정 불필요)
NEWS_COLLECTION_INTERVAL=900
ANALYSIS_INTERVAL=1800
ARTICLE_GENERATION_INTERVAL=3600
MIN_RELEVANCE_SCORE=70
```

---

## 🔍 설정 확인

### 1. .env 파일 내용 확인

```bash
cat .env
```

**확인 항목**:
- ✅ SUPABASE_URL이 `https://`로 시작하는가?
- ✅ SUPABASE_KEY가 `eyJ`로 시작하는가?
- ✅ FINNHUB_API_KEY가 영숫자로 되어 있는가?
- ✅ ALPHA_VANTAGE_API_KEY가 영숫자로 되어 있는가?
- ✅ `your_*` 같은 플레이스홀더가 남아있지 않은가?

### 2. 연결 테스트

```bash
# Python으로 설정 확인
python -c "
from dotenv import load_dotenv
import os

load_dotenv()

print('✅ Supabase URL:', os.getenv('SUPABASE_URL')[:30] + '...')
print('✅ Supabase Key:', os.getenv('SUPABASE_KEY')[:20] + '...')
print('✅ Finnhub Key:', os.getenv('FINNHUB_API_KEY')[:10] + '...')
print('✅ Alpha Vantage Key:', os.getenv('ALPHA_VANTAGE_API_KEY')[:10] + '...')
"
```

**예상 출력**:
```
✅ Supabase URL: https://abcdefghijklmnop.su...
✅ Supabase Key: eyJhbGciOiJIUzI1NiIs...
✅ Finnhub Key: c123abc456...
✅ Alpha Vantage Key: ABCD123456...
```

---

## 🛡️ 보안 주의사항

### ⚠️ 절대 하지 말 것

- ❌ GitHub에 .env 파일 커밋
- ❌ 공개 포럼에 API 키 공유
- ❌ 스크린샷에 키 노출

### ✅ 해야 할 것

- ✅ .gitignore에 .env 포함 (이미 설정됨)
- ✅ API 키를 비밀번호 관리자에 백업
- ✅ Supabase 비밀번호 안전하게 저장

---

## 🔧 문제 해결

### "Module not found: dotenv"

```bash
pip install python-dotenv
```

### ".env 파일이 읽히지 않습니다"

```bash
# 파일 존재 확인
ls -la .env

# 권한 확인
chmod 600 .env

# 내용 확인
cat .env
```

### "API 키가 유효하지 않습니다"

```bash
# 공백 확인 (앞뒤 공백 제거)
# 따옴표 제거 (키에 따옴표 없어야 함)

# 올바른 형식:
FINNHUB_API_KEY=c123abc456def789

# 잘못된 형식:
FINNHUB_API_KEY="c123abc456def789"  # 따옴표 제거
FINNHUB_API_KEY= c123abc456def789   # 공백 제거
```

---

## 📝 다음 단계

.env 파일 설정이 완료되었다면:

### 1. Supabase 데이터베이스 설정

```bash
# database/schema.sql 파일 내용 확인
cat database/schema.sql

# Supabase 대시보드에서:
# 1. SQL Editor 열기
# 2. 위 내용 복사 & 붙여넣기
# 3. RUN 버튼 클릭
```

### 2. 첫 뉴스 수집 테스트

```bash
# 뉴스 수집
python main.py --mode collect
```

**예상 출력**:
```
2025-11-12 22:00:00 | INFO | Starting news collection job
2025-11-12 22:00:05 | INFO | FinnhubCollector collected 15 new news items
2025-11-12 22:00:10 | INFO | AlphaVantageCollector collected 8 new news items
2025-11-12 22:00:15 | INFO | RSSCollector collected 23 new news items
```

### 3. 워크플로우 시작

```bash
# 일일 워크플로우 프롬프트 생성
python scripts/generate_daily_workflow.py

# 생성된 파일 확인
cat prompts/workflow_*.md
```

---

## 🎉 완료!

.env 파일 설정이 완료되었습니다!

**다음 문서 읽기**:
```bash
cat README_CLAUDE_CODE.md
```

**시작하기**:
```bash
python main.py --mode collect
python scripts/generate_daily_workflow.py
```

**비용**: $0 (완전 무료!)
