# Discord Bot 설정 완전 가이드

## 📌 목차
1. [Discord Bot 생성](#1-discord-bot-생성)
2. [Bot Token 발급](#2-bot-token-발급)
3. [봇 권한 설정](#3-봇-권한-설정)
4. [서버에 봇 초대](#4-서버에-봇-초대)
5. [Channel ID 확인](#5-channel-id-확인)
6. [환경 변수 설정](#6-환경-변수-설정)

---

## 1. Discord Bot 생성

### 1-1. Discord Developer Portal 접속
```
https://discord.com/developers/applications
```

### 1-2. 새 애플리케이션 생성
1. **"New Application"** 클릭
2. 이름 입력: `Aivesto Midjourney Bot`
3. **"Create"** 클릭

---

## 2. Bot Token 발급

### 2-1. Bot 페이지 이동
- 좌측 메뉴 → **"Bot"** 클릭

### 2-2. Bot 추가
- **"Add Bot"** → **"Yes, do it!"** 확인

### 2-3. Token 복사
1. **"Reset Token"** 클릭
2. 표시된 토큰 복사
3. ⚠️ **절대 공유하지 마세요!**

```
토큰 형식 예시:
YOUR_BOT_TOKEN_HERE.XXXXXX.YYYYYYYYYYYYYYYYYYYYYYYYYY
```

---

## 3. 봇 권한 설정

### 3-1. Privileged Gateway Intents
Bot 페이지에서 스크롤 다운:

- ✅ **MESSAGE CONTENT INTENT** (필수!)
- ✅ **SERVER MEMBERS INTENT**
- ✅ **PRESENCE INTENT**

⚠️ **MESSAGE CONTENT INTENT를 활성화하지 않으면 봇이 메시지를 읽을 수 없습니다!**

---

## 4. 서버에 봇 초대

### 4-1. OAuth2 URL 생성
좌측 메뉴 → **"OAuth2"** → **"URL Generator"**

### 4-2. SCOPES 선택
- ✅ `bot`
- ✅ `applications.commands`

### 4-3. BOT PERMISSIONS 선택
- ✅ **Read Messages/View Channels**
- ✅ **Send Messages**
- ✅ **Read Message History**
- ✅ **Attach Files**
- ✅ **Use Slash Commands**

### 4-4. URL로 초대
1. 하단 **GENERATED URL** 복사
2. 브라우저에 붙여넣기
3. 서버 선택
4. **"Authorize"** 클릭

---

## 5. Channel ID 확인

### 5-1. Discord 개발자 모드 활성화
1. Discord 앱 설정 열기
2. **고급** → **개발자 모드** 활성화

### 5-2. Channel ID 복사
1. Midjourney를 사용할 채널에서 우클릭
2. **"Copy ID"** 클릭
3. 복사된 ID 저장 (18자리 숫자)

```
예시: 1234567890123456789
```

---

## 6. 환경 변수 설정

### 6-1. .env 파일 편집
`/Users/jinxin/dev/aivesto/.env` 파일을 열어 다음 값을 입력:

```bash
# Discord Bot Configuration
DISCORD_BOT_TOKEN=여기에_복사한_봇_토큰_붙여넣기
MIDJOURNEY_CHANNEL_ID=여기에_채널_ID_붙여넣기
MIDJOURNEY_BOT_ID=936929561302675456

# Supabase (이미 설정됨)
SUPABASE_URL=https://czubqsnahmtdsmnyawlk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 6-2. 설정 확인
```bash
# .env 파일이 올바르게 설정되었는지 확인
cat .env | grep DISCORD
```

---

## ✅ 체크리스트

완료 여부를 확인하세요:

- [ ] Discord Developer Portal에서 애플리케이션 생성
- [ ] Bot 추가 및 Token 복사
- [ ] MESSAGE CONTENT INTENT 활성화
- [ ] 필요한 권한 설정
- [ ] 서버에 봇 초대 완료
- [ ] Channel ID 복사
- [ ] .env 파일에 Token 및 Channel ID 설정

---

## 🚨 문제 해결

### Bot이 메시지를 읽지 못함
→ **MESSAGE CONTENT INTENT**가 활성화되었는지 확인

### Bot이 서버에 보이지 않음
→ OAuth2 URL로 다시 초대 시도

### Channel ID를 찾을 수 없음
→ Discord 개발자 모드 활성화 확인

### Token이 작동하지 않음
→ "Reset Token"으로 새 토큰 발급

---

## 📚 다음 단계

1. ✅ Discord Bot Token 발급 완료
2. ⏭️ Midjourney 서버 설정
3. ⏭️ Supabase 스키마 적용
4. ⏭️ 테스트 실행

---

## 🔗 참고 링크

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Midjourney Documentation](https://docs.midjourney.com/)
