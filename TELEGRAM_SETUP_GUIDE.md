# 📱 Telegram 알림 시스템 설정 가이드

**설정 시간**: 5분
**필요한 것**: Telegram 계정, BotFather 봇

---

## 🚀 빠른 시작 (3단계)

### Step 1️⃣: Telegram 봇 생성 (BotFather)

1. Telegram 검색에서 **`@BotFather`** 검색 및 실행
2. `/start` 명령어 입력
3. `/newbot` 입력

```
BotFather: Alright, a new bot. How are we going to call it?
(봇 이름 입력, 예: Investment Signal Bot)

BotFather: Good. Now let's choose a username for your bot...
(봇 사용자명 입력, 예: aivesto_signal_bot)

Here is your bot token:
123456789:ABCDefGHIjklMNOpqrSTUvwxyz
```

**✅ Bot Token 복사** → `.env` 파일에 저장

---

### Step 2️⃣: Chat ID 확인

#### 방법 1️⃣: Python 스크립트 (권장)

```bash
# 최소한 1회 봇과 상호작용 필요
# 1. Telegram에서 @aivesto_signal_bot (위에서 만든 봇) 찾기
# 2. /start 또는 아무 메시지 보내기
# 3. 아래 스크립트 실행

python scripts/get_telegram_chat_id.py \
  --token "123456789:ABCDefGHIjklMNOpqrSTUvwxyz"

# 출력 예:
# Chat ID: 987654321
# Bot: @aivesto_signal_bot
```

#### 방법 2️⃣: 웹 방식

1. 브라우저에서 다음 URL 방문:
```
https://api.telegram.org/bot123456789:ABCDefGHIjklMNOpqrSTUvwxyz/getUpdates
```

2. JSON 응답에서 `"id"` 값 찾기:
```json
{
  "ok": true,
  "result": [
    {
      "message": {
        "chat": {
          "id": 987654321,
          "first_name": "YourName"
        }
      }
    }
  ]
}
```

**✅ Chat ID 복사** → `.env` 파일에 저장

---

### Step 3️⃣: .env 파일 설정

`.env` 파일에 다음 환경 변수 추가:

```bash
# Telegram 알림 설정
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjklMNOpqrSTUvwxyz
TELEGRAM_CHAT_IDS=987654321,987654322

# 여러 명에게 보낼 경우 쉼표로 구분
# TELEGRAM_CHAT_IDS=ID1,ID2,ID3
```

---

## ✅ 설정 검증

```bash
# 테스트 메시지 전송
python scripts/test_telegram_alerts.py

# 또는 Python에서:
from alerts.telegram_alerts import TelegramAlertService

service = TelegramAlertService()
service.send_test_message("987654321")
```

**✅ 확인사항:**
- Telegram 채팅에 테스트 메시지 수신
- 메시지 포맷 확인 (이모지, 링크 등)

---

## 📧 이메일 vs 📱 텔레그램

| 항목 | 이메일 | 텔레그램 |
|------|--------|---------|
| **설정 난이도** | 중간 | 낮음 (5분) |
| **실시간 알림** | 느림 (지연) | 빠름 (즉시) |
| **모바일 경험** | 보통 | 최적 |
| **용량 제한** | 없음 | 4096자/메시지 |
| **비용** | 무료 | 무료 |
| **구독 해제** | 번거로움 | 쉬움 (/stop) |

---

## 🎯 알림 종류

### 1️⃣ 긴급 신호 (Urgent Alert) 🔴

**언제**: Level 1 신호 감지 시 즉시
**형식**: 신호 제목, 관련 종목, 점수, 분석 요약

```
🔴 긴급 신호 알림!

제목:
Apple Q4 earnings beat expectations

영향 종목:
AAPL, MSFT

관련성 점수:
92/100

분석 요약:
Apple이 Q4 실적에서 기대치 15% 초과 달성...
```

---

### 2️⃣ 일일 요약 (Daily Digest) 📊

**언제**: 매일 오전 9시 (설정 가능)
**형식**: 신호 통계, 트렌딩 종목 top 5

```
📊 일일 투자 신호 요약

2025-11-13

신호 통계:
🔴 긴급 (Level 1): 5
🟠 높음 (Level 2): 12
🟡 중간 (Level 3): 18
🟢 낮음 (Level 4): 8

📈 트렌딩 종목 (상위 5):
1. MSFT - 8개 신호, 평균 점수: 85.2
2. AAPL - 6개 신호, 평균 점수: 82.1
...
```

---

### 3️⃣ 높은 우선순위 알림 (High Priority) 🟠

**언제**: 매시간 (Level 1-2만 수집)
**형식**: 신호 리스트 (상위 10개)

```
🟠 높은 우선순위 신호 - 7개 알림

Level 1 (긴급) 및 Level 2 (높음) 신호

1. 🔴 Microsoft announces $10B AI investment
   종목: MSFT
   점수: 92/100

2. 🟠 NVIDIA earnings surge expectations
   종목: NVDA
   점수: 88/100
...
```

---

### 4️⃣ 종목별 알림 (Symbol Alert) 📈

**언제**: 특정 종목 신호 발생 시
**형식**: 종목 관련 신호만 표시

```
📈 MSFT 신호 알림 - 3개 업데이트

1. Microsoft announces new Azure features
   점수: 85/100 | Level 2

2. Microsoft partners with OpenAI
   점수: 78/100 | Level 3
```

---

## 🔧 고급 설정

### 여러 채팅방에 전송

```env
TELEGRAM_CHAT_IDS=123456789,987654321,555666777
```

### 특정 신호 레벨만 받기

`alerts/telegram_alerts.py` 수정:

```python
def send_urgent_alert(self, signal_data: dict, chat_ids: List[str] = None) -> bool:
    # Level 1만 받으려면
    if signal_data.get('signal_level', 4) > 1:
        return False
    # ...
```

### 메시지 커스터마이징

`_format_urgent_message()` 메서드 수정:

```python
def _format_urgent_message(self, signal_data: dict) -> str:
    # 자신의 포맷 적용
    message = f"""
    🔴 {signal_data['title']}
    ...
    """
    return message
```

---

## 🐛 문제 해결

### Q: "Bot token invalid" 오류

**A**: Bot Token 확인
```bash
# BotFather에서 다시 확인
# Token: 123456789:ABCDefGHIjklMNOpqrSTUvwxyz
# 끝 부분 특수문자 포함 여부 확인
```

---

### Q: "Chat ID not configured"

**A**: Chat ID 설정 확인
```bash
# 1. Telegram 봇에 /start 메시지 보냄
# 2. Chat ID 조회 스크립트 실행
python scripts/get_telegram_chat_id.py --token YOUR_TOKEN

# 3. .env에 추가
TELEGRAM_CHAT_IDS=YOUR_CHAT_ID
```

---

### Q: 메시지가 도착하지 않음

**A**: 디버그 단계

```bash
# 1. 테스트 메시지 전송
python scripts/test_telegram_alerts.py

# 2. 로그 확인
tail -f logs/stock_news_*.log | grep Telegram

# 3. 봇 상태 확인
curl https://api.telegram.org/botTOKEN/getMe
```

---

### Q: "Message too long"

**A**: Telegram 메시지 크기 제한 (4096자)
- 시스템이 자동으로 처리함
- 필요시 분할 전송 기능 추가 가능

---

## 📊 모니터링

### Telegram 알림 로그

```bash
# 텔레그램 관련 로그만 확인
grep -i telegram logs/stock_news_*.log

# 출력 예:
# 2025-11-13 09:00:00 | INFO | Telegram alerts enabled for 1 chat(s)
# 2025-11-13 09:00:15 | INFO | Telegram message sent to 987654321
```

### 알림 통계

```bash
# 일일 알림 수 확인
grep "Telegram message sent" logs/stock_news_*.log | wc -l

# 알림 실패 확인
grep "Error sending message" logs/stock_news_*.log
```

---

## 🎯 최적 실행 전략

### 추천 설정

```env
# 긴급 신호만 빠르게
TELEGRAM_CHAT_IDS=YOUR_CHAT_ID
# (일일 다이제스트는 아침 9시에 자동 발송)
```

### 종일 모니터링

```bash
# 대시보드 열기
http://localhost:5000

# 동시에 Telegram 알림 받기
# (백그라운드에서 자동 실행)
python main.py --mode run
```

### 팀 공유

```env
# 팀원들의 Chat ID 추가
TELEGRAM_CHAT_IDS=ID1,ID2,ID3,ID4

# 모두 같은 알림 수신
# (개인별 설정 가능: /subscribe level:1 등)
```

---

## 📱 텔레그램 봇 명령어 (향후)

```
/start - 봇 시작
/stop - 알림 중지
/status - 상태 확인
/score_90 - 90점 이상만 받기
/symbol_msft - MSFT만 받기
/daily_off - 일일 요약 제외
```

*(현재는 수동 설정만 지원, 향후 추가 예정)*

---

## 🔗 관련 문서

- [LOCAL_WORKFLOW.md](./LOCAL_WORKFLOW.md) - 일일 워크플로우
- [API_REFERENCE.md](./API_REFERENCE.md) - API 엔드포인트
- [README_LOCAL_SETUP.md](./README_LOCAL_SETUP.md) - 전체 설정

---

## ✨ 특징

| 항목 | 상태 |
|------|------|
| 긴급 신호 알림 | ✅ 실시간 |
| 일일 요약 | ✅ 자동 |
| 높은 우선순위 | ✅ 매시간 |
| 종목별 알림 | ✅ 트리거 기반 |
| HTML 포맷 | ✅ 마크다운 |
| 다중 채팅방 | ✅ 지원 |
| 링크 미리보기 | ✅ 비활성화 |

---

## 🎉 설정 완료!

**다음 단계:**

```bash
# 1. 환경 변수 설정 확인
cat .env | grep TELEGRAM

# 2. 시스템 시작
python main.py --mode run

# 3. 대시보드 확인
# http://localhost:5000

# 4. Telegram 알림 수신 대기
```

**첫 알림은 다음 스케줄에 도착합니다:**
- 🔴 긴급 신호: 즉시
- 📊 일일 요약: 매일 09:00 UTC
- 🟠 높은 우선순위: 매시간
- 📈 종목별: 감지 시

---

**문제 발생시**: 로그 확인 및 위 문제해결 섹션 참고

**최종 수정**: 2025-11-13
**상태**: ✅ 프로덕션 준비 완료
