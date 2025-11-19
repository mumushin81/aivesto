# Midjourney MCP 설정 가이드

**작성일**: 2025-11-15
**목적**: Claude Desktop에서 Midjourney 이미지 생성을 직접 실행
**난이도**: 중급 (Midjourney Discord 계정 필요)

---

## 📋 목차

1. [개요](#개요)
2. [필수 준비사항](#필수-준비사항)
3. [옵션 1: uvx 방식 (권장)](#옵션-1-uvx-방식-권장)
4. [옵션 2: GPTNB API 방식](#옵션-2-gptnb-api-방식)
5. [Midjourney 토큰 획득](#midjourney-토큰-획득)
6. [문제 해결](#문제-해결)
7. [FAQ](#faq)

---

## 개요

### 🎯 **목표**

Claude Desktop에서 자연어로 Midjourney 이미지를 직접 생성할 수 있도록 MCP 서버를 설정합니다.

### ✨ **가능한 작업**

Claude Desktop에서 다음과 같이 요청 가능:

```
"NVIDIA Blackwell GPU 서버실 이미지를 16:9 비율로 생성해줘"
→ Midjourney가 자동으로 이미지 생성
```

### ⚠️ **제한사항**

- Midjourney 유료 구독 필요 (Basic $10/월, Standard $30/월)
- Discord 계정 필요
- 기술적 설정 필요 (토큰 추출)

---

## 필수 준비사항

### 1️⃣ **Midjourney 구독**

- [Midjourney 웹사이트](https://www.midjourney.com/account) 방문
- Discord 계정 연동
- 구독 플랜 선택:
  - **Basic Plan**: $10/월 (200장)
  - **Standard Plan**: $30/월 (무제한, 추천)
  - **Pro Plan**: $60/월 (상업용)

### 2️⃣ **Python 환경**

```bash
python3 --version  # Python 3.10+ 필요
```

### 3️⃣ **uvx 설치 (권장 방식)**

```bash
# uv 설치 (Python 패키지 관리자)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 또는 Homebrew
brew install uv
```

---

## 옵션 1: uvx 방식 (권장)

### 장점
- ✅ 설치 간단 (1줄)
- ✅ 자동 업데이트
- ✅ Python 환경 관리 불필요

### 단점
- ⚠️ Midjourney Discord 토큰 필요 (TOKEN_R, TOKEN_I)

---

### Step 1: Midjourney 토큰 획득

#### 방법 A: Chrome DevTools (권장)

1. **Chrome에서 Discord 웹 열기**
   - https://discord.com/channels/@me

2. **DevTools 열기**
   - `Command + Option + I` (Mac)
   - `F12` (Windows)

3. **Application 탭 → Cookies**
   - `https://discord.com` 선택

4. **토큰 복사**
   - `__Secure-user_token_r` → TOKEN_R
   - `__Secure-user_token_i` → TOKEN_I

#### 방법 B: 브라우저 확장 프로그램

1. [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie) 설치
2. Discord 접속
3. 쿠키 아이콘 클릭
4. `__Secure-user_token_r`, `__Secure-user_token_i` 복사

---

### Step 2: Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 편집:

```json
{
  "mcpServers": {
    "midjourney": {
      "command": "uvx",
      "args": ["midjourney-mcp"],
      "env": {
        "TOKEN_R": "여기에_TOKEN_R_붙여넣기",
        "TOKEN_I": "여기에_TOKEN_I_붙여넣기",
        "API_BASE": "midjourney.com",
        "SUFFIX": "--v 6.1"
      }
    }
  }
}
```

**⚠️ 주의**: 기존 `mcpServers` 항목(zen, supabase 등)을 **삭제하지 말고** `"midjourney"` 항목만 **추가**하세요!

---

### Step 3: Claude Desktop 재시작

1. Claude Desktop 완전 종료
2. Activity Monitor에서 "Claude" 프로세스 확인 및 종료
3. Claude Desktop 재시작
4. 새 대화 시작

---

### Step 4: 테스트

Claude Desktop에서 입력:

```
Midjourney로 "a futuristic NVIDIA datacenter with green glowing servers"를 16:9 비율로 생성해줘
```

**예상 결과**:
- MCP가 Midjourney API 호출
- 이미지 생성 작업 시작
- 약 60초 후 이미지 URL 반환

---

## 옵션 2: GPTNB API 방식

### 장점
- ✅ Discord 토큰 불필요
- ✅ API 기반으로 안정적

### 단점
- ⚠️ 별도 API 키 필요 (유료 서비스)
- ⚠️ Python 환경 직접 관리

---

### Step 1: 리포지토리 클론

```bash
cd ~/dev
git clone https://github.com/z23cc/midjourney-mcp.git
cd midjourney-mcp
```

---

### Step 2: Python 가상환경 및 의존성 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Step 3: GPTNB API 키 발급

1. [GPTNB 웹사이트](https://aiclound.vip) 방문 (예시)
2. 계정 생성
3. API 키 발급
4. 결제 (사용량 기반)

---

### Step 4: 환경 변수 설정

`.env` 파일 생성:

```bash
cd ~/dev/midjourney-mcp
nano .env
```

내용:

```env
GPTNB_API_KEY=your_api_key_here
GPTNB_BASE_URL=https://aiclound.vip
```

---

### Step 5: Claude Desktop 설정

`~/Library/Application Support/Claude/claude_desktop_config.json` 편집:

```json
{
  "mcpServers": {
    "midjourney": {
      "command": "/Users/jinxin/dev/midjourney-mcp/venv/bin/python",
      "args": ["/Users/jinxin/dev/midjourney-mcp/src/server.py"],
      "env": {
        "GPTNB_API_KEY": "your_api_key_here",
        "GPTNB_BASE_URL": "https://aiclound.vip"
      }
    }
  }
}
```

---

### Step 6: 테스트

```bash
# 서버 단독 실행 (디버깅용)
cd ~/dev/midjourney-mcp
source venv/bin/activate
python src/server.py
```

Claude Desktop에서 테스트:

```
Midjourney로 Tesla Robotaxi 이미지 생성해줘
```

---

## Midjourney 토큰 획득 (상세)

### 🔐 **보안 주의사항**

- **TOKEN_R, TOKEN_I는 비밀번호와 동일**
- GitHub에 절대 커밋하지 마세요
- `.gitignore`에 `claude_desktop_config.json` 추가
- 토큰 유출 시 Discord 비밀번호 즉시 변경

---

### 📸 **Chrome DevTools 스크린샷 가이드**

#### Step 1: Discord 웹 접속
![Discord Web](https://discord.com/channels/@me)

#### Step 2: DevTools 열기
- Mac: `Command + Option + I`
- Windows: `F12`

#### Step 3: Application 탭
```
Application
  └─ Storage
      └─ Cookies
          └─ https://discord.com
```

#### Step 4: 쿠키 찾기
```
Name                          | Value
__Secure-user_token_r         | MTIzNDU2Nzg5MDEyMzQ1Njc4OTA...
__Secure-user_token_i         | dXNlcl9pZF8xMjM0NTY3ODkw...
```

#### Step 5: 복사
- 우클릭 → "Copy Value"
- 또는 더블클릭 후 `Command + C`

---

## 문제 해결

### ❌ **문제 1: "MCP server failed to start"**

**원인**: 잘못된 Python 경로 또는 의존성 누락

**해결**:
```bash
# Python 경로 확인
which python3

# 의존성 재설치
cd ~/dev/midjourney-mcp
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

### ❌ **문제 2: "Invalid TOKEN_R or TOKEN_I"**

**원인**: 만료되거나 잘못된 토큰

**해결**:
1. Discord 로그아웃 후 재로그인
2. Chrome DevTools에서 토큰 재확인
3. Claude Desktop 설정 업데이트
4. Claude 완전 재시작

---

### ❌ **문제 3: "Rate limit exceeded"**

**원인**: Midjourney API 호출 제한 초과

**해결**:
- Basic Plan: 시간당 제한 확인
- Standard Plan으로 업그레이드 ($30/월)
- 잠시 대기 (5-10분)

---

### ❌ **문제 4: "Image generation timeout"**

**원인**: Midjourney 서버 과부하

**해결**:
- 재시도 (1-2회)
- 프롬프트 단순화
- 비혼잡 시간대 사용

---

## FAQ

### ❓ **Q1: uvx 방식과 GPTNB 방식 중 어떤 게 좋나요?**

**A**: 상황에 따라 다릅니다.

| 항목 | uvx 방식 | GPTNB 방식 |
|------|----------|------------|
| **설치 난이도** | 쉬움 | 중간 |
| **비용** | Midjourney 구독만 | Midjourney + API 비용 |
| **토큰 관리** | Discord 토큰 필요 | API 키만 필요 |
| **안정성** | 중간 (토큰 만료 가능) | 높음 |
| **권장 대상** | 개인 사용자 | 팀/상업용 |

**추천**: 개인 사용자라면 **uvx 방식** (간단)

---

### ❓ **Q2: 토큰이 만료되면 어떻게 하나요?**

**A**: Discord 재로그인 후 토큰 재발급

1. Discord 로그아웃
2. 재로그인
3. Chrome DevTools에서 새 토큰 복사
4. `claude_desktop_config.json` 업데이트
5. Claude 재시작

---

### ❓ **Q3: Midjourney 구독 없이 테스트할 수 있나요?**

**A**: 불가능합니다. 다음 대안 고려:

- **DALL-E 3**: ChatGPT Plus ($20/월)
- **Stable Diffusion**: 무료 (로컬) 또는 Leonardo.ai (무료 티어)
- **Midjourney 무료 체험**: 현재 종료 (2023년 3월까지만 제공)

---

### ❓ **Q4: 생성된 이미지는 어디에 저장되나요?**

**A**: Claude Desktop 대화 내 또는 URL로 제공

- Claude가 이미지 URL 반환
- 우클릭 → "다른 이름으로 이미지 저장"
- 자동 저장 원하면 스크립트 작성 필요

---

### ❓ **Q5: 상업적으로 사용 가능한가요?**

**A**: Midjourney 구독 플랜에 따라 다릅니다.

| 플랜 | 상업적 사용 |
|------|-------------|
| Basic ($10/월) | ❌ 불가 |
| Standard ($30/월) | ⚠️ 연 매출 $1M 이하 기업만 |
| Pro ($60/월) | ✅ 가능 |

블로그 기사용은 **Standard** 이상 권장

---

## 📚 **추가 리소스**

### 공식 문서
- [Midjourney 공식 문서](https://docs.midjourney.com)
- [Model Context Protocol](https://modelcontextprotocol.io)

### GitHub 리포지토리
- [z23cc/midjourney-mcp](https://github.com/z23cc/midjourney-mcp) - GPTNB 방식
- [Lala-0x3f/mj-mcp](https://github.com/Lala-0x3f/mj-mcp) - uvx 방식

### 커뮤니티
- [Midjourney Discord](https://discord.gg/midjourney)
- [r/midjourney](https://reddit.com/r/midjourney)

---

## 🎉 **완료 체크리스트**

설정이 완료되면 다음을 확인하세요:

- [ ] Midjourney 구독 활성화
- [ ] TOKEN_R, TOKEN_I 또는 GPTNB API 키 발급
- [ ] Claude Desktop 설정 파일 업데이트
- [ ] Claude 완전 재시작
- [ ] 테스트 이미지 생성 성공
- [ ] 토큰/키 보안 확인 (GitHub에 미포함)

---

## 🚀 **다음 단계**

1. **Aivesto 블로그 워크플로우 통합**
   ```
   "NVDA Blackwell GPU 이미지를
   scripts/ai_image_prompts.json의
   midjourney_prompt로 생성해줘"
   ```

2. **자동화 스크립트 제작**
   - 기사 작성 시 자동 이미지 생성
   - `public/images/` 폴더에 자동 저장

3. **품질 관리**
   - 생성된 이미지 1200x630 크기 확인
   - 브랜드 색상 일치 여부 검증

---

**작성일**: 2025-11-15
**버전**: 1.0
**작성자**: Claude Code
**테스트 환경**: macOS, Python 3.10+, Claude Desktop
