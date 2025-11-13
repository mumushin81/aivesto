# Railway에 API 서버 배포 가이드

## 📋 목차
1. [사전준비](#사전준비)
2. [Railway 배포](#railway-배포)
3. [API URL 확인](#api-url-확인)
4. [Vercel 재배포](#vercel-재배포)
5. [테스트](#테스트)

---

## 🔧 사전준비

### 필요한 것들
- GitHub 계정 ✅ (이미 보유)
- Railway 계정 (새로 생성)
- 이메일 주소

---

## 🚀 Railway 배포

### Step 1: Railway 계정 생성

1. 브라우저에서 **https://railway.app** 방문
2. 우측 상단 **"Start New Project"** 또는 **"Sign up"** 클릭
3. **"Continue with GitHub"** 선택
4. GitHub 로그인 및 권한 허용

### Step 2: 새 프로젝트 생성

1. Railway 대시보드 열기
2. **"Create"** 버튼 클릭
3. **"Deploy from GitHub"** 선택

### Step 3: GitHub 저장소 연결

1. **"Install Railway on GitHub"** 클릭
2. GitHub 계정 선택
3. **"Install & Authorize"** 진행
4. 저장소 선택:
   - `mumushin81/aivesto` 선택
   - **"Deploy"** 클릭

### Step 4: 배포 자동 시작

Railway가 자동으로:
- ✅ Python 환경 감지
- ✅ `requirements.txt` 읽기
- ✅ 의존성 설치
- ✅ `dashboard/server.py` 실행

**대기 시간**: 약 2-3분

---

## 📍 API URL 확인

### Railway 대시보드에서 URL 얻기

1. Railway 프로젝트 대시보드 열기
2. 좌측 메뉴에서 **"Deployments"** 클릭
3. 최신 배포 항목 확인
4. **프로덕션 URL** 찾기

예시:
```
https://aivesto-api.railway.app
```

### URL 테스트

배포된 API가 정상 작동하는지 확인:

```powershell
# 명령어
curl https://aivesto-api.railway.app/api/health

# 예상 응답
{"status": "healthy", "timestamp": "2025-11-13T...", "service": "Investment Signal Dashboard"}
```

### 환경변수 설정 (선택사항)

Railway에서 환경변수 추가:

1. 프로젝트 → **"Variables"** 탭
2. **"New Variable"** 추가:
   ```
   TELEGRAM_BOT_TOKEN = your_token
   TELEGRAM_CHAT_IDS = your_chat_ids
   ```

---

## 🔄 Vercel 재배포

### Step 1: HTML 파일 수정 (이미 완료)

`public/index.html` (Line 377):
```javascript
// 이미 설정됨
const API_BASE = 'https://aivesto-api.railway.app/api';
```

### Step 2: 변경사항 커밋

```powershell
cd C:\dev\aivesto

git add public/index.html dashboard/static/index.html
git commit -m "Update API URL to Railway production endpoint"
git push origin main
```

### Step 3: Vercel 재배포

```powershell
vercel --prod --yes
```

또는 GitHub이 이미 연결되어 있으면 **자동으로 배포됨**

---

## 🧪 테스트

### 1. 대시보드 접속 확인

```
https://aivesto-dashboard-f30hi3pct-mumushin81-gmailcoms-projects.vercel.app
```

### 2. 기능 테스트

- [ ] 페이지 로드 (에러 없음)
- [ ] 기사 카드 표시됨
- [ ] 통계 숫자 보임
- [ ] 새로고침 버튼 작동
- [ ] 콘솔 에러 없음 (F12 > Console)

### 3. 브라우저 개발자 도구 확인

1. **F12** 키 누르기
2. **Console** 탭 확인
3. 에러 메시지 있는지 확인
4. Network 탭에서 API 호출 확인

---

## 🔍 문제 해결

### 문제 1: "502 Bad Gateway"
```
원인: Railway가 Flask 앱을 시작하지 못함
해결: Railway 로그 확인
  - Deployments → 최신 배포 → Logs 클릭
  - 에러 메시지 읽기
```

### 문제 2: "기사가 로드되지 않음"
```
원인: articles/ 디렉토리 경로 오류
해결:
  1. Railway에 articles/ 디렉토리 있는지 확인
  2. signal_api.py의 경로 확인
  3. 필요시 경로 수정
```

### 문제 3: "API 타임아웃"
```
원인: Railway 무료 플랜의 슬립 모드
해결:
  1. 다시 접속하기 (자동 시작)
  2. Railway Pro로 업그레이드
  3. 또는 Render 사용
```

### 문제 4: "CORS 에러"
```
원인: API 서버가 CORS를 설정하지 않음
해결:
  - dashboard/server.py에서 CORS 확인
  - 또는 Render 사용 (자동 CORS 지원)
```

---

## 📊 배포 구조

```
┌──────────────────────────────────┐
│   Vercel (프론트엔드)            │
│ aivesto-dashboard-xxx.vercel.app │
│                                  │
│  public/index.html               │
│  ↓ API 호출 ↓                     │
└──────────────────────────────────┘
           ↓ HTTPS
┌──────────────────────────────────┐
│   Railway (백엔드)               │
│ aivesto-api.railway.app          │
│                                  │
│  dashboard/server.py             │
│  ↓ 파일 읽기 ↓                    │
└──────────────────────────────────┘
           ↓
┌──────────────────────────────────┐
│   데이터 (GitHub 저장소)        │
│  articles/                       │
│  validation_report.json          │
└──────────────────────────────────┘
```

---

## ✅ 배포 체크리스트

### Railway 배포 전
- [ ] GitHub 계정 준비
- [ ] Aivesto 저장소 준비
- [ ] requirements.txt 확인

### Railway 배포 중
- [ ] 프로젝트 생성
- [ ] GitHub 저장소 연결
- [ ] 자동 배포 진행 (2-3분)
- [ ] API URL 복사

### Railway 배포 후
- [ ] 환경변수 설정 (선택)
- [ ] 헬스 체크 성공
- [ ] API 응답 확인

### Vercel 재배포
- [ ] HTML 파일 수정 (이미 완료)
- [ ] 변경사항 커밋
- [ ] `vercel --prod --yes` 실행
- [ ] 배포 완료 확인

### 최종 테스트
- [ ] 대시보드 접속
- [ ] 기사 로드
- [ ] 콘솔 에러 확인
- [ ] 모든 기능 작동

---

## 📞 지원

### Railway 고객 지원
- 공식 문서: https://docs.railway.app
- Discord: https://discord.gg/railway

### 대체 옵션
- **Render**: https://render.com (유사한 배포)
- **Heroku**: https://www.heroku.com (클래식)

---

**배포 상태**: Ready for Production ✅

**예상 완료 시간**: 5-10분

**난이도**: ⭐⭐☆☆☆ (쉬움)
