# Midjourney MCP - 빠른 시작 가이드

> Claude Desktop에서 Midjourney 이미지를 직접 생성하세요!

---

## 🚀 초고속 설정 (5분)

### 필수 준비물
1. **Midjourney 구독** (Standard $30/월 권장)
2. **Discord 계정** (Midjourney 연동됨)
3. **uvx 설치** (Python 패키지 실행 도구)

---

## ⚡ 자동 설정 스크립트

```bash
cd /Users/jinxin/dev/aivesto
./scripts/setup_midjourney_mcp.sh
```

**스크립트가 자동으로:**
1. uvx 설치 확인 (없으면 설치)
2. Discord 토큰 입력 받기
3. Claude Desktop 설정 파일 자동 업데이트
4. 백업 생성

---

## 📋 수동 설정 (3단계)

### Step 1: Discord 토큰 획득

1. Chrome에서 https://discord.com/channels/@me 열기
2. `Command + Option + I` (DevTools)
3. `Application` 탭 → `Cookies` → `discord.com`
4. 다음 값 복사:
   - `__Secure-user_token_r` → **TOKEN_R**
   - `__Secure-user_token_i` → **TOKEN_I**

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

⚠️ **주의**: 기존 서버 설정(zen, supabase)을 삭제하지 마세요!

---

### Step 3: Claude 재시작

1. Claude Desktop 완전 종료
2. Activity Monitor에서 "Claude" 프로세스 확인 및 종료
3. Claude Desktop 재실행

---

## ✅ 테스트

Claude Desktop에서 입력:

```
Midjourney로 "a futuristic NVIDIA datacenter with green glowing servers" 이미지를 16:9 비율로 생성해줘
```

**예상 결과**: 약 60초 후 이미지 URL 반환

---

## 🎨 Aivesto 블로그 통합 예시

### 1. 프롬프트 조회
```bash
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip --model midjourney --copy
```

### 2. Claude Desktop에 요청
```
복사한 Midjourney 프롬프트로 이미지 생성해줘.
아스펙트 비율은 1200:630 (16:9 근사치)
```

### 3. 이미지 다운로드
- Claude가 반환한 이미지 URL 우클릭
- "다른 이름으로 이미지 저장"
- `public/images/NVDA_blackwell_chip.jpg`

---

## 📊 비용

| 플랜 | 가격 | 생성 수 | 상업적 사용 |
|------|------|---------|-------------|
| Basic | $10/월 | 200장 | ❌ |
| **Standard** | **$30/월** | **무제한** | ✅ (연매출 $1M 이하) |
| Pro | $60/월 | 무제한 | ✅ (무제한) |

**권장**: Standard 플랜 (블로그용 충분)

---

## 🔧 문제 해결

### "MCP server failed to start"
```bash
# uvx 재설치
brew install uv

# 설정 파일 백업에서 복원
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup.* ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### "Invalid TOKEN"
- Discord 로그아웃 → 재로그인
- 토큰 재확인 (DevTools)
- Claude 설정 업데이트
- Claude 재시작

### "Rate limit exceeded"
- 잠시 대기 (5-10분)
- Standard 플랜으로 업그레이드

---

## 📂 파일 구조

```
aivesto/
├── scripts/
│   └── setup_midjourney_mcp.sh        # 🛠️ 자동 설정 스크립트
└── docs/
    ├── MIDJOURNEY_MCP_README.md        # 👈 이 문서 (빠른 시작)
    ├── MIDJOURNEY_MCP_SETUP.md         # 📚 상세 가이드
    └── claude_desktop_config_example.json  # 예시 설정 파일
```

---

## 🎯 다음 단계

1. **[IMAGE_GENERATION_GUIDE.md](./IMAGE_GENERATION_GUIDE.md)** - AI 이미지 프롬프트 가이드
2. **[AI_IMAGE_PROMPTS.md](./AI_IMAGE_PROMPTS.md)** - 20개 종목별 프롬프트
3. **블로그 기사 작성** - 생성된 이미지로 썸네일 업그레이드

---

## ⚠️ 보안 주의사항

- **TOKEN_R, TOKEN_I는 비밀번호입니다**
- GitHub에 절대 커밋 금지
- `.gitignore`에 `claude_desktop_config.json` 추가
- 토큰 유출 시 Discord 비밀번호 즉시 변경

---

## 💬 지원

- **상세 가이드**: [MIDJOURNEY_MCP_SETUP.md](./MIDJOURNEY_MCP_SETUP.md)
- **Midjourney Discord**: https://discord.gg/midjourney
- **MCP 문서**: https://modelcontextprotocol.io

---

**작성일**: 2025-11-15
**버전**: 1.0
**테스트 환경**: macOS, Claude Desktop, Python 3.10+
