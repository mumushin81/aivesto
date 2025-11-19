# Discord 토큰 찾기 - 완전 가이드

**작성일**: 2025-11-16
**목적**: Midjourney MCP 설정을 위한 Discord 토큰 획득
**난이도**: 초급 (스크린샷 포함)

---

## 📋 목차

1. [필수 준비사항](#필수-준비사항)
2. [방법 1: Chrome DevTools (권장)](#방법-1-chrome-devtools-권장)
3. [방법 2: 네트워크 탭 사용](#방법-2-네트워크-탭-사용)
4. [방법 3: 브라우저 확장 프로그램](#방법-3-브라우저-확장-프로그램)
5. [토큰이 안 보이는 경우](#토큰이-안-보이는-경우)
6. [문제 해결](#문제-해결)

---

## 필수 준비사항

### ✅ 체크리스트
- [ ] Midjourney 구독 활성화 (Basic/Standard/Pro)
- [ ] Discord 계정 로그인 완료
- [ ] Midjourney Discord 서버 참여
- [ ] Chrome 브라우저 (또는 Chromium 기반)

---

## 방법 1: Chrome DevTools (권장)

### 🎯 **Step 1: Discord 웹 접속**

1. **Chrome 브라우저 열기**
   - 시크릿 모드는 사용하지 마세요!

2. **Discord 웹 접속**
   ```
   https://discord.com/app
   ```
   또는
   ```
   https://discord.com/channels/@me
   ```

3. **로그인 확인**
   - 왼쪽에 서버 목록이 보여야 함
   - Midjourney 서버 아이콘 확인

---

### 🎯 **Step 2: DevTools 열기**

#### macOS
```
Command (⌘) + Option (⌥) + I
```

#### Windows/Linux
```
F12
```
또는
```
Ctrl + Shift + I
```

**또는 메뉴에서:**
1. 화면 오른쪽 상단 ⋮ (세 점) 클릭
2. "도구 더보기" → "개발자 도구" 선택

---

### 🎯 **Step 3: Application 탭으로 이동**

1. **DevTools 상단 탭에서 "Application" 클릭**
   - 안 보이면 `>>` 버튼 클릭 후 찾기

2. **왼쪽 사이드바 구조**
   ```
   Application
   ├─ Application
   ├─ Storage
   │  ├─ Local Storage
   │  ├─ Session Storage
   │  ├─ IndexedDB
   │  ├─ Web SQL
   │  ├─ Cookies  👈 여기!
   │  ├─ Cache Storage
   │  └─ ...
   ```

---

### 🎯 **Step 4: Cookies 찾기**

1. **Storage 섹션 확장**
   - 왼쪽 사이드바에서 "Storage" 클릭

2. **Cookies 확장**
   - "Cookies" 옆 ▶ 클릭

3. **discord.com 선택**
   ```
   Cookies
   ├─ https://discord.com  👈 이것 클릭!
   ```

---

### 🎯 **Step 5: 토큰 찾기 (가장 중요!)**

#### 오른쪽 패널에서 찾을 쿠키들:

| Name (쿠키 이름) | 찾는 방법 | 복사할 값 |
|------------------|-----------|-----------|
| `__Secure-user_token_r` | 스크롤해서 찾기 | Value 열 전체 |
| `__Secure-user_token_i` | 바로 아래 있음 | Value 열 전체 |

#### 🔍 **찾는 팁:**

1. **Name 열 클릭** → 알파벳 순 정렬
2. `__Secure-` 로 시작하는 것 찾기
3. `user_token_r`, `user_token_i` 확인

---

### 🎯 **Step 6: 토큰 복사**

#### 방법 A: 더블클릭
1. `__Secure-user_token_r` 행의 **Value** 셀 더블클릭
2. 전체 선택 (Command+A 또는 Ctrl+A)
3. 복사 (Command+C 또는 Ctrl+C)

#### 방법 B: 우클릭
1. `__Secure-user_token_r` 행 우클릭
2. "Copy" → "Copy Value" 선택

#### 토큰 형식 예시:
```
TOKEN_R (예시):
YOUR_USER_TOKEN_R_HERE.XXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYY

TOKEN_I (예시):
YOUR_USER_TOKEN_I_HERE_BASE64_ENCODED
```

---

## 방법 2: 네트워크 탭 사용

### 토큰이 Cookies에 안 보일 때 사용

### 🎯 **Step 1: DevTools Network 탭**

1. **Chrome DevTools 열기**
   - Command+Option+I (Mac)
   - F12 (Windows)

2. **Network 탭 클릭**

3. **필터 설정**
   - 상단 필터에 `api` 입력

---

### 🎯 **Step 2: Discord 페이지 새로고침**

1. **페이지 새로고침**
   - Command+R (Mac)
   - F5 (Windows)

2. **네트워크 요청 관찰**
   - `gateway` 또는 `users/@me` 요청 찾기

---

### 🎯 **Step 3: 요청 헤더 확인**

1. **요청 클릭**
   - 예: `users/@me`

2. **Headers 탭 선택**

3. **Request Headers 섹션 확장**

4. **Authorization 헤더 찾기**
   ```
   Authorization: YOUR_USER_TOKEN_R_HERE.XXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYY
   ```

5. **값 복사**
   - 이것이 TOKEN_R입니다!

---

## 방법 3: 브라우저 확장 프로그램

### 🔧 **EditThisCookie (권장)**

1. **설치**
   - [Chrome 웹 스토어](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg) 접속
   - "Chrome에 추가" 클릭

2. **사용 방법**
   - Discord 웹 접속
   - 브라우저 상단 쿠키 아이콘 🍪 클릭
   - `__Secure-user_token_r` 찾기
   - Value 옆 📋 (복사 아이콘) 클릭

3. **장점**
   - 시각적으로 쉬움
   - 한 번 클릭으로 복사

---

## 토큰이 안 보이는 경우

### 🔍 **원인 1: 로그인 상태가 아님**

#### 해결 방법:
1. Discord 로그아웃
2. 완전히 재로그인
3. DevTools 다시 열기
4. Cookies 재확인

---

### 🔍 **원인 2: 시크릿 모드 사용**

#### 해결 방법:
- **일반 브라우저 창**에서 Discord 접속
- 시크릿/프라이빗 모드는 쿠키 저장 안 됨

---

### 🔍 **원인 3: 쿠키 이름 변경**

Discord가 쿠키 이름을 변경했을 수 있음

#### 확인 방법:
1. Cookies에서 `token` 검색
2. 다음 이름들 확인:
   - `token`
   - `__dcfduid`
   - `__sdcfduid`
   - `__cfruid`

---

### 🔍 **원인 4: 쿠키 필터링**

#### 해결 방법:
1. **DevTools → Application → Cookies**
2. 상단 검색창에 `secure` 입력
3. `__Secure-` 로 시작하는 모든 쿠키 확인

---

### 🔍 **원인 5: 잘못된 도메인**

#### 확인 사항:
```
올바른 도메인:
✅ https://discord.com
✅ https://discord.com/app
✅ https://discord.com/channels/@me

잘못된 도메인:
❌ https://discordapp.com (구버전)
❌ https://ptb.discord.com (Public Test Build)
❌ https://canary.discord.com (Canary 버전)
```

---

## 🎥 **단계별 스크린샷 가이드**

### 1️⃣ Discord 웹 접속
```
주소창: https://discord.com/app
↓
로그인 확인 (왼쪽에 서버 목록 표시)
```

### 2️⃣ DevTools 열기
```
Mac: Command + Option + I
Windows: F12
↓
DevTools 패널이 화면 하단 또는 오른쪽에 나타남
```

### 3️⃣ Application 탭
```
DevTools 상단:
[Elements] [Console] [Sources] [Network] [Application] 👈
                                            ↑ 여기 클릭
```

### 4️⃣ Cookies 확장
```
왼쪽 사이드바:
Application
  Storage
    Cookies ▶ 👈 클릭
      https://discord.com 👈 클릭
```

### 5️⃣ 토큰 찾기
```
오른쪽 패널 (Name 열 기준):
...
__Secure-next-on-complete-callback-url
__Secure-recent_mfa
__Secure-user_token_i         👈 이것!
__Secure-user_token_r         👈 이것!
__stripe_mid
...
```

### 6️⃣ 값 복사
```
Value 열에서:
__Secure-user_token_r | MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.GaBcDe.Fg... 👈 전체 복사
```

---

## 💡 **실전 예시**

### TOKEN_R 값 예시:
```
YOUR_USER_TOKEN_R_HERE.XXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYY
```
- 길이: 약 70-90자
- 형식: `XXXXX.XXXXX.XXXXX` (점 2개로 구분)

### TOKEN_I 값 예시:
```
YOUR_USER_TOKEN_I_HERE_BASE64_ENCODED
```
- 길이: 약 40-60자
- 형식: Base64 인코딩 + URL 인코딩 (`%3D` = `=`)

---

## 🔐 **보안 주의사항**

### ⚠️ 절대 하지 말아야 할 것:

1. **토큰을 GitHub에 커밋**
   ```bash
   # .gitignore에 추가 필수!
   claude_desktop_config.json
   .env
   ```

2. **토큰을 다른 사람과 공유**
   - 토큰 = Discord 비밀번호
   - 누군가 토큰을 얻으면 계정 접근 가능

3. **스크린샷 공유 시 토큰 노출**
   - 토큰 부분 가리기
   - 또는 재생성 후 공유

### ✅ 토큰 유출 시 대응:

1. **즉시 Discord 비밀번호 변경**
2. **로그아웃 후 재로그인**
3. **새 토큰 발급됨**
4. **Claude Desktop 설정 업데이트**

---

## 🧪 **토큰 검증**

### 토큰이 올바른지 확인:

```bash
# curl로 테스트 (TOKEN_R 사용)
curl -H "Authorization: YOUR_TOKEN_R_HERE" \
     https://discord.com/api/v10/users/@me
```

**성공 응답 예시:**
```json
{
  "id": "123456789012345678",
  "username": "YourUsername",
  "discriminator": "0",
  "avatar": "abcdef123456",
  ...
}
```

**실패 응답:**
```json
{
  "message": "401: Unauthorized",
  "code": 0
}
```

---

## 📝 **Claude Desktop 설정 예시**

토큰을 찾았다면 다음 설정 파일에 붙여넣기:

**파일 위치**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "midjourney": {
      "command": "uvx",
      "args": ["midjourney-mcp"],
      "env": {
        "TOKEN_R": "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA.GaBcDe.FgHiJkLmNo...",
        "TOKEN_I": "dXNlcl9pZF8xMjM0NTY3ODkwMTIzNDU2Nzg5MA%3D%3D",
        "API_BASE": "midjourney.com",
        "SUFFIX": "--v 6.1"
      }
    }
  }
}
```

---

## 🆘 **여전히 안 될 때**

### 최후의 방법: Console에서 직접 추출

1. **DevTools → Console 탭**

2. **다음 코드 입력:**
   ```javascript
   // TOKEN_R 찾기
   document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_r')).split('=')[1]
   ```

3. **결과 복사**
   - 따옴표 제외하고 복사

4. **TOKEN_I 찾기:**
   ```javascript
   document.cookie.split('; ').find(row => row.startsWith('__Secure-user_token_i')).split('=')[1]
   ```

---

## 📞 **추가 도움**

### 문제가 계속되면:

1. **Discord 앱 (데스크톱) 사용**
   - 웹 대신 앱에서 토큰 추출 (고급)

2. **Midjourney Discord 서버 질문**
   - #support 채널에서 도움 요청

3. **대안: GPTNB API 방식**
   - Discord 토큰 대신 API 키 사용
   - [MIDJOURNEY_MCP_SETUP.md](./MIDJOURNEY_MCP_SETUP.md) 참조

---

## ✅ **성공 확인**

토큰을 정확히 찾았다면:

- [ ] TOKEN_R이 약 70-90자 길이
- [ ] 점(`.`)이 2개 있음
- [ ] TOKEN_I가 약 40-60자 길이
- [ ] `%3D` 문자가 포함됨
- [ ] 복사 시 앞뒤 공백 없음

---

## 🎉 **다음 단계**

토큰을 찾았다면:

1. **[MIDJOURNEY_MCP_SETUP.md](./MIDJOURNEY_MCP_SETUP.md)** - MCP 설정 계속
2. **자동 설정 스크립트 실행**
   ```bash
   ./scripts/setup_midjourney_mcp.sh
   ```

---

**작성일**: 2025-11-16
**버전**: 1.0
**업데이트**: Discord 쿠키 정책 변경 시 재확인 필요
