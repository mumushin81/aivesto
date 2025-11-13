# Vercel 배포 단계별 가이드

## 📋 사전준비

### 1. Vercel 계정 생성
- https://vercel.com에 접속
- GitHub 또는 이메일로 회원가입
- 이메일 인증 완료

### 2. Vercel CLI 설치
```powershell
npm install -g vercel
```

### 3. Vercel 로그인
```powershell
vercel login
```
→ 브라우저에서 계정으로 로그인 후 승인

---

## 🚀 배포 방법 (3가지)

### 방법 1: 자동 배포 스크립트 (권장)

#### Windows (PowerShell)
```powershell
# PowerShell을 관리자 권한으로 실행
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy-vercel.ps1
```

#### Linux/Mac
```bash
bash deploy-vercel.sh
```

---

### 방법 2: 수동 배포 (단계별)

#### Step 1: 현재 디렉토리 확인
```powershell
cd C:\dev\aivesto
ls vercel.json
ls public\index.html
```

#### Step 2: 프리뷰 배포
```powershell
vercel
```

프롬프트:
```
? Set up and deploy "~/aivesto"? [Y/n] Y
? Which scope do you want to deploy to? (your-name)
? Linked to your-org/aivesto (created .vercel/project.json)
? Inspect: https://vercel.com/dashboard
? Production - https://aivesto.vercel.app [v] done (2s)
```

📝 **생성된 URL 기록**: `https://aivesto.vercel.app`

#### Step 3: 프로덕션 배포
```powershell
vercel --prod
```

---

### 방법 3: GitHub 연결 배포 (자동)

#### Step 1: GitHub 저장소에 Push
```powershell
git push origin main
```

#### Step 2: Vercel 대시보드
1. https://vercel.com/dashboard 방문
2. "Import Project" 클릭
3. GitHub 저장소 선택
4. 자동으로 배포됨

---

## ⚙️ 환경변수 설정

### Vercel 대시보드에서 설정

1. 프로젝트 선택 → Settings
2. Environment Variables 선택
3. 다음 변수 추가:

```
Name:  TELEGRAM_BOT_TOKEN
Value: 8499274416:AAHvMbNBAxTKHLqVCIMKLQtGnYj9aKp3-9w

Name:  TELEGRAM_CHAT_IDS
Value: 6645624184
```

4. Save 버튼 클릭

---

## 🔗 API 서버 설정

### 로컬 개발 (localhost)
```javascript
// public/index.html 수정 (자동으로 감지됨)
const API_BASE = 'http://localhost:5000/api';
```

### 클라우드 배포 (권장)

#### 1. Railway 배포 (권장)

**Step 1: Railway 계정 생성**
- https://railway.app 접속
- GitHub으로 로그인

**Step 2: 새 프로젝트 생성**
```
Create → Import from GitHub
```

**Step 3: 저장소 선택**
```
aivesto 저장소 선택
```

**Step 4: 자동 배포**
```
배포 완료 후 URL 기록
예: https://aivesto-api.railway.app
```

**Step 5: Vercel에서 API URL 설정**

public/index.html 수정:
```javascript
const API_BASE = 'https://aivesto-api.railway.app/api';
```

변경사항 커밋 및 배포:
```powershell
git add public/index.html
git commit -m "Update API URL for production"
git push
```

---

#### 2. Render 배포

**Step 1: Render 계정 생성**
- https://render.com 접속
- GitHub으로 로그인

**Step 2: 새 웹 서비스 생성**
```
New → Web Service
```

**Step 3: GitHub 저장소 연결**
```
aivesto 저장소 선택
```

**Step 4: 설정**
```
Name:            aivesto-api
Environment:     Python
Build Command:   pip install -r requirements.txt
Start Command:   python dashboard/server.py
```

**Step 5: 배포**
```
Deploy 버튼 클릭
배포 완료 후 URL 기록
```

---

## 🧪 배포 확인

### 1. 대시보드 접속
```
https://aivesto.vercel.app
```

### 2. 기능 테스트
- [ ] 페이지 로드 확인
- [ ] 기사 카드 표시 확인
- [ ] 통계 로드 확인
- [ ] 새로고침 버튼 작동 확인

### 3. API 연결 테스트
```powershell
# API 테스트
curl https://aivesto-api.railway.app/api/health
```

예상 응답:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-13T15:00:00.000000",
  "service": "Investment Signal Dashboard"
}
```

---

## 🔧 트러블슈팅

### 문제 1: CORS 에러
```
Access to XMLHttpRequest... blocked by CORS policy
```

**해결책:**
1. API 서버 Flask 앱에 CORS 헤더 추가 확인
2. API_BASE URL이 올바른지 확인
3. 방화벽 규칙 확인

### 문제 2: 기사가 로드되지 않음
```
GET /api/articles 404 Not Found
```

**해결책:**
1. API 서버가 실행 중인지 확인
2. articles/ 디렉토리 확인
3. signal_api.py의 articles_dir 경로 확인

### 문제 3: 배포가 실패함
```
Error: Build failed
```

**해결책:**
1. requirements.txt 확인
2. vercel.json 문법 확인
3. 파일 인코딩 확인 (UTF-8)
4. 로그 확인:
   ```powershell
   vercel logs
   ```

---

## 📊 배포 후 최적화

### 1. 캐싱 설정
```json
// vercel.json
"headers": [
  {
    "source": "/public/(.*)",
    "headers": [
      {"key": "Cache-Control", "value": "public, max-age=86400"}
    ]
  }
]
```

### 2. 모니터링
- Vercel 대시보드에서 실시간 모니터링
- Analytics 탭에서 트래픽 확인

### 3. 자동 배포
```
Settings → Git → Production Branch
main 브랜치 선택
```

---

## 📈 성능 최적화 팁

1. **정적 파일 압축**
   ```
   gzip, brotli 자동 적용
   ```

2. **CDN 캐싱**
   ```
   Vercel Edge Network 자동 사용
   ```

3. **API 응답 최적화**
   ```
   Python 서버에서 JSON 응답 압축
   ```

---

## 📚 참고자료

- [Vercel 문서](https://vercel.com/docs)
- [Railway 배포](https://docs.railway.app)
- [Render 배포](https://render.com/docs)
- [Flask CORS](https://flask-cors.readthedocs.io)

---

**마지막 업데이트**: 2025-11-13
**배포 버전**: 1.0.0
**상태**: Ready for Production ✅
