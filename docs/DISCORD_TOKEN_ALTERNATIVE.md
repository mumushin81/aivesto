# Discord 토큰 찾기 - 대안 방법 (100% 확실)

**Console 경고 메시지 때문에 토큰을 못 찾는 경우**

Discord가 Console에 경고 메시지를 계속 출력해서 토큰 추출이 어려울 수 있습니다.
다음 **3가지 확실한 방법**을 사용하세요!

---

## 🎯 방법 1: Console.clear() 후 토큰 추출 (가장 쉬움!)

### Step 1: Console 정리

1. **Chrome DevTools → Console 탭**

2. **다음 명령어 입력:**
   ```javascript
   console.clear()
   ```

3. **Enter → 화면이 깨끗해짐**

---

### Step 2: 토큰 바로 추출

**한 줄씩 복사해서 실행:**

#### TOKEN_R 찾기:
```javascript
copy(document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_r'))?.split('=')[1] || 'NOT FOUND')
```

**결과:**
- 토큰이 **자동으로 클립보드에 복사됨!**
- Console에 "NOT FOUND" 나오면 → 다음 방법 시도

#### TOKEN_I 찾기:
```javascript
copy(document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_i'))?.split('=')[1] || 'NOT FOUND')
```

**사용법:**
1. 위 코드 복사
2. Console에 붙여넣기
3. Enter
4. 메모장에 붙여넣기 (`Command+V`)
5. 토큰 확인!

---

## 🎯 방법 2: Network 탭에서 Authorization 헤더 확인 (확실함!)

### Step 1: Network 탭 준비

1. **Chrome DevTools → Network 탭**

2. **필터 설정:**
   - 상단 필터에 `api` 입력
   - 또는 `XHR` 버튼 클릭

3. **기존 요청 삭제:**
   - 🚫 (Clear) 버튼 클릭

---

### Step 2: 새 요청 발생시키기

다음 중 **하나만** 실행:

#### 옵션 A: 다른 채널 클릭
- 왼쪽 채널 목록에서 아무거나 클릭

#### 옵션 B: 페이지 새로고침
- `Command+R` (Mac) 또는 `F5` (Windows)

#### 옵션 C: 메시지 입력창 클릭
- 아무 채널의 입력창에 글자 입력 (보내지 말고)

---

### Step 3: API 요청 찾기

Network 탭에서 다음 중 하나 찾기:

```
Name 목록:
├─ users/@me              ← 가장 흔함!
├─ channels
├─ guilds
├─ messages
└─ gateway
```

---

### Step 4: Authorization 헤더 복사

1. **요청 클릭** (예: `users/@me`)

2. **Headers 탭 선택**

3. **스크롤 다운 → Request Headers 섹션**

4. **Authorization 헤더 찾기:**
   ```
   authorization: MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.GaBcDe.FgHiJkLmNoPqRsTuVwXyZ
   ```

5. **값 복사** → 이것이 **TOKEN_R**입니다!

---

### TOKEN_I는?

Network 방법으로는 TOKEN_R만 찾을 수 있습니다.
TOKEN_I는 **방법 3 (EditThisCookie)** 또는 **방법 4 (Application 탭 재시도)** 사용

---

## 🎯 방법 3: EditThisCookie 확장 프로그램 (비개발자 친화적)

### Step 1: 설치

1. **Chrome 웹 스토어 접속:**
   ```
   https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
   ```

2. **"Chrome에 추가" 클릭**

3. **설치 완료 → 브라우저 상단에 🍪 아이콘 표시**

---

### Step 2: 사용

1. **Discord 웹 페이지에서 🍪 아이콘 클릭**

2. **쿠키 목록 표시됨**

3. **검색창에 `token` 입력**

4. **다음 찾기:**
   ```
   __Secure-user_token_r
   __Secure-user_token_i
   ```

5. **Value 옆 📋 (복사) 아이콘 클릭**

**장점:**
- 시각적으로 쉬움
- 개발자 도구 불필요
- 한 번 클릭으로 복사

---

## 🎯 방법 4: Application 탭 재시도 (검색 기능 활용)

### Application 탭에서 토큰이 정말 없는지 확인

1. **DevTools → Application 탭**

2. **Cookies → https://discord.com 선택**

3. **상단 Filter 입력창 사용:**
   ```
   Filter: secure
   ```

4. **나타나는 쿠키 확인:**
   - `__Secure-user_token_r` ✓
   - `__Secure-user_token_i` ✓

**안 보이면:**
- Filter에 `token` 입력
- Filter에 `user` 입력
- 모든 쿠키 스크롤 (100개 이상 있을 수 있음)

---

## 🎯 방법 5: LocalStorage 확인 (드문 경우)

일부 Discord 버전은 토큰을 LocalStorage에 저장

### Step 1: Application 탭

1. **DevTools → Application 탭**

2. **왼쪽 사이드바:**
   ```
   Storage
   ├─ Local Storage  ← 확장
   │  └─ https://discord.com  ← 클릭
   ```

3. **오른쪽 패널에서 검색:**
   - `token`
   - `auth`

---

## 🎯 방법 6: 개발자 도구 없이 - JavaScript 북마클릿

### 설정 (한 번만)

1. **북마크바에서 우클릭 → "페이지 추가"**

2. **이름:** `Discord Token`

3. **URL에 다음 코드 붙여넣기:**
   ```javascript
   javascript:(function(){const r=document.cookie.split('; ').find(row=>row.startsWith('__Secure-user_token_r'))?.split('=')[1];const i=document.cookie.split('; ').find(row=>row.startsWith('__Secure-user_token_i'))?.split('=')[1];alert('TOKEN_R:\n'+r+'\n\nTOKEN_I:\n'+i);})();
   ```

### 사용

1. **Discord 웹 페이지에서**
2. **북마크바의 "Discord Token" 클릭**
3. **팝업에 토큰 표시됨**
4. **복사!**

---

## 🔍 토큰이 정말 없는 경우

### 확인 사항:

1. **로그인 상태 확인**
   ```javascript
   // Console에서 실행
   document.cookie.includes('discord')
   ```
   - `true` 나와야 함
   - `false`면 → 로그아웃 상태

2. **올바른 도메인 확인**
   ```javascript
   // Console에서 실행
   window.location.hostname
   ```
   - `discord.com` 나와야 함
   - 다른 도메인이면 → `discord.com/app` 재접속

3. **쿠키 활성화 확인**
   ```javascript
   // Console에서 실행
   navigator.cookieEnabled
   ```
   - `true` 나와야 함
   - `false`면 → 브라우저 설정 확인

---

## 🎬 실전 데모 (방법 1 - Console)

### 전체 과정:

```javascript
// 1단계: Console 정리
console.clear()

// 2단계: TOKEN_R 복사 (클립보드에 자동 복사됨!)
copy(document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_r'))?.split('=')[1] || 'NOT FOUND')

// 3단계: 메모장에 붙여넣기 (Command+V)
// 토큰이 붙여넣어짐!

// 4단계: TOKEN_I 복사
copy(document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_i'))?.split('=')[1] || 'NOT FOUND')

// 5단계: 메모장에 붙여넣기
// 완료!
```

**예상 결과 (메모장):**
```
YOUR_USER_TOKEN_R_HERE.XXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYY
YOUR_USER_TOKEN_I_HERE_BASE64_ENCODED
```

---

## 🆘 최후의 수단: Discord Desktop 앱 사용

### Chrome에서 정말 안 될 때

#### macOS:

1. **Discord Desktop 앱 설치**
   ```
   https://discord.com/download
   ```

2. **앱 실행 → 로그인**

3. **터미널 열기**

4. **다음 명령어 실행:**
   ```bash
   # Discord 로그 파일에서 토큰 찾기
   grep -r "token" ~/Library/Application\ Support/discord/
   ```

#### 주의:
- Desktop 앱 방법은 고급 사용자용
- 파일 시스템 접근 필요
- 보안 위험 있음

---

## ✅ 성공 확인

토큰을 찾았는지 확인:

```javascript
// Console에서 실행
const token_r = document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_r'))?.split('=')[1];
console.log('TOKEN_R 길이:', token_r?.length);
console.log('점(.) 개수:', (token_r?.match(/\./g) || []).length);
```

**정상 결과:**
```
TOKEN_R 길이: 70-90
점(.) 개수: 2
```

---

## 📝 권장 방법 순서

1. **🥇 방법 1: Console.clear() + copy()** (가장 쉬움)
2. **🥈 방법 2: Network 탭** (TOKEN_R만)
3. **🥉 방법 3: EditThisCookie** (비개발자)
4. **방법 4: Application 탭 재시도** (검색 활용)
5. **방법 5: LocalStorage**
6. **방법 6: 북마클릿**

---

## 🎯 다음 단계

토큰을 찾았다면:

```bash
# 자동 설정 스크립트
cd /Users/jinxin/dev/aivesto
./scripts/setup_midjourney_mcp.sh

# 토큰 입력하면 완료!
```

---

## 🔐 보안 알림

Discord Console 경고 메시지:
```
잠깐만요!
만약 누군가가 이곳에 복사/붙여넣기하라고 시킨 거라면...
110% 확률로 사기예요.
```

**우리는 사기가 아닙니다!**
- 본인이 직접 토큰 추출
- Midjourney MCP 설정 목적
- 토큰은 본인만 사용
- GitHub에 절대 커밋 금지

---

**작성일**: 2025-11-16
**업데이트**: Discord Console 경고 우회 방법
