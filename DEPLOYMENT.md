# Aivesto Dashboard - Vercel 배포 가이드

## 📋 목차
1. [로컬 실행](#로컬-실행)
2. [Vercel 배포](#vercel-배포)
3. [API 서버 설정](#api-서버-설정)
4. [환경변수 설정](#환경변수-설정)

---

## 로컬 실행

### 1. 필수 요구사항
```bash
python 3.10+
pip (파이썬 패키지 관리자)
```

### 2. 설치
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 수정 (실제 값 입력)
```

### 3. Flask 서버 실행
```bash
python dashboard/server.py
```

서버가 실행되면:
- **대시보드**: http://localhost:5000
- **API**: http://localhost:5000/api

### 4. API 엔드포인트
```
GET  /api/health                    - 헬스 체크
GET  /api/articles                  - 모든 기사
GET  /api/articles/<symbol>         - 종목별 기사
GET  /api/articles/stats            - 기사 통계
GET  /api/signals/urgent            - 긴급 시그널
GET  /api/trending-symbols          - 트렌딩 종목
GET  /api/dashboard                 - 대시보드 요약
```

---

## Vercel 배포

### 1. Vercel CLI 설치
```bash
npm install -g vercel
```

### 2. Vercel 로그인
```bash
vercel login
```

### 3. 프로젝트 배포
```bash
# 현재 디렉토리에서 배포
vercel

# 또는 production 배포
vercel --prod
```

### 4. 배포 확인
배포 완료 후 제공되는 URL에 접속하여 대시보드 확인:
- **프론트엔드**: https://your-project.vercel.app
- **정적 파일**: public/ 디렉토리의 파일들

---

## API 서버 설정

Vercel은 정적 파일만 호스팅하므로, API 서버는 별도로 호스팅해야 합니다.

### 옵션 1: 로컬 개발 환경
```javascript
// public/index.html의 API_BASE 설정
const API_BASE = 'http://localhost:5000/api';
```

### 옵션 2: 클라우드 호스팅 (권장)

#### Railway 배포
```bash
# 1. Railway 계정 생성 (https://railway.app)
# 2. 프로젝트 생성 및 Python 선택
# 3. GitHub 연결 및 배포

# 배포 후 API_BASE 업데이트
const API_BASE = 'https://your-railway-app.railway.app/api';
```

#### Render 배포
```bash
# 1. Render 계정 생성 (https://render.com)
# 2. Flask 웹 서비스 생성
# 3. GitHub 연결

# 배포 후 API_BASE 업데이트
const API_BASE = 'https://your-render-app.onrender.com/api';
```

#### Heroku 배포 (레거시)
```bash
# Heroku CLI 설치
npm install -g heroku

# Heroku 로그인
heroku login

# 앱 생성 및 배포
heroku create
git push heroku main
```

---

## 환경변수 설정

### Vercel 환경변수 (Vercel 대시보드)
```
Settings > Environment Variables

TELEGRAM_BOT_TOKEN    = your_bot_token
TELEGRAM_CHAT_IDS     = your_chat_ids
```

### API 서버 환경변수 (.env 파일)
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_IDS=your_chat_ids
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

---

## 아키텍처

```
┌─────────────────────────────────────┐
│         Vercel (정적 호스팅)        │
│  ┌──────────────────────────────┐  │
│  │  public/index.html           │  │
│  │  - React/Vanilla JS          │  │
│  │  - 차트 및 데이터 시각화     │  │
│  └──────────────────────────────┘  │
│            ↓ (API 호출)             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│    API 서버 (Railway/Render 등)    │
│  ┌──────────────────────────────┐  │
│  │  Flask + Python              │  │
│  │  - /api/articles             │  │
│  │  - /api/signals              │  │
│  │  - /api/dashboard            │  │
│  └──────────────────────────────┘  │
│            ↓ (데이터 읽기)          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       데이터 소스                    │
│  ┌──────────────────────────────┐  │
│  │  articles/ - 기사 파일       │  │
│  │  validation_report.json      │  │
│  │  Supabase (선택사항)         │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## 트러블슈팅

### CORS 에러
```
Access to XMLHttpRequest at 'https://api.example.com' from origin 'https://vercel-app.com'
has been blocked by CORS policy
```

**해결방법:**
```javascript
// Flask 앱에 CORS 헤더 추가
from flask_cors import CORS
CORS(app, origins=['https://your-vercel-domain.app'])
```

### API 호출 실패
- API 서버가 실행 중인지 확인
- API 서버 URL이 올바른지 확인
- CORS 설정 확인
- 네트워크 보안 규칙 확인

### 기사 로드 안됨
- articles/ 디렉토리 경로 확인
- validation_report.json 파일 확인
- 파일 권한 확인

---

## 빠른 시작

### 로컬 개발
```bash
# 1. 저장소 클론
git clone https://github.com/your-org/aivesto.git
cd aivesto

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일 수정

# 4. Flask 서버 실행
python dashboard/server.py

# 5. 브라우저에서 접속
# http://localhost:5000
```

### Vercel 배포
```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. Vercel 로그인
vercel login

# 3. 프로젝트 배포
vercel --prod

# 4. 대시보드 접속
# https://your-project.vercel.app
```

---

## 참고자료
- [Vercel 문서](https://vercel.com/docs)
- [Flask 문서](https://flask.palletsprojects.com)
- [Railway 배포](https://railway.app/docs)
- [Render 배포](https://render.com/docs)

---

**최종 업데이트**: 2025-11-13
**버전**: 1.0.0
