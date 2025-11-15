# 자동화 스케줄러 가이드

뉴스 파이프라인을 자동으로 실행하는 스케줄러 설정 방법

---

## 방법 1: APScheduler (권장)

Python 스크립트 내에서 스케줄링

### 설치

```bash
pip install apscheduler
```

### 실행

```bash
# 포그라운드 실행 (테스트용)
python run_scheduler.py

# 백그라운드 실행 (운영용)
nohup python run_scheduler.py > logs/scheduler.log 2>&1 &

# 프로세스 확인
ps aux | grep run_scheduler

# 종료
pkill -f run_scheduler.py
```

### 스케줄 설정

`run_scheduler.py`에서 수정:

```python
# 매 시간 실행
CronTrigger(hour='*/1')

# 매 30분 실행
CronTrigger(minute='*/30')

# 매일 오전 9시
CronTrigger(hour=9, minute=0)

# 평일 오전 9시, 오후 3시
CronTrigger(day_of_week='mon-fri', hour='9,15', minute=0)
```

---

## 방법 2: Cron (Unix/Linux/Mac)

시스템 Cron을 사용한 스케줄링

### 설정

```bash
# Cron 편집기 열기
crontab -e

# 아래 라인 추가 (매 시간 실행)
0 * * * * cd /Users/jinxin/dev/aivesto && /usr/bin/python3 test_e2e_pipeline.py >> logs/cron.log 2>&1

# 저장 후 확인
crontab -l
```

### Cron 표현식 예시

```bash
# 매 시간 정각
0 * * * * command

# 매 30분
*/30 * * * * command

# 매일 오전 9시
0 9 * * * command

# 평일 오전 9시, 오후 3시
0 9,15 * * 1-5 command

# 매주 월요일 오전 10시
0 10 * * 1 command
```

---

## 방법 3: systemd (Linux)

서비스로 등록하여 부팅 시 자동 시작

### 서비스 파일 생성

```bash
sudo nano /etc/systemd/system/aivesto-scheduler.service
```

```ini
[Unit]
Description=Aivesto News Pipeline Scheduler
After=network.target

[Service]
Type=simple
User=jinxin
WorkingDirectory=/Users/jinxin/dev/aivesto
ExecStart=/usr/bin/python3 /Users/jinxin/dev/aivesto/run_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 서비스 관리

```bash
# 서비스 활성화
sudo systemctl enable aivesto-scheduler

# 서비스 시작
sudo systemctl start aivesto-scheduler

# 상태 확인
sudo systemctl status aivesto-scheduler

# 로그 확인
sudo journalctl -u aivesto-scheduler -f

# 서비스 중지
sudo systemctl stop aivesto-scheduler
```

---

## 로그 관리

### 로그 위치

```bash
# APScheduler 로그
logs/scheduler_YYYY-MM-DD.log

# Cron 로그
logs/cron.log

# 시스템 로그 (systemd)
sudo journalctl -u aivesto-scheduler
```

### 로그 확인

```bash
# 실시간 모니터링
tail -f logs/scheduler_$(date +%Y-%m-%d).log

# 최근 50줄
tail -50 logs/scheduler_$(date +%Y-%m-%d).log

# 에러만 확인
grep "ERROR" logs/scheduler_*.log

# 성공한 실행만
grep "Pipeline completed successfully" logs/scheduler_*.log
```

### 로그 로테이션 (자동)

APScheduler는 자동으로 일별 로그 파일 생성 및 30일 보관

---

## 모니터링

### 파이프라인 성공 확인

```bash
# 최근 실행 결과
tail -100 logs/scheduler_$(date +%Y-%m-%d).log | grep "Pipeline Stats"

# High-priority 시그널
tail -100 logs/scheduler_$(date +%Y-%m-%d).log | grep "high-priority signals detected"
```

### Telegram 알림 (선택)

`run_scheduler.py`에 추가:

```python
# High-priority 알림
if stats['high_priority_count'] > 5:
    send_telegram_alert(f"🔔 {stats['high_priority_count']} high-priority signals!")
```

---

## 권장 스케줄

### 개발 환경

```bash
# 테스트: 매 30분
*/30 * * * * command
```

### 운영 환경

```bash
# 매 시간 정각
0 * * * * command

# 또는 평일 거래 시간만 (미국 동부 오전 9시 ~ 오후 4시)
0 9-16 * * 1-5 command
```

### 리소스 고려

- **매 시간**: 적당한 빈도 (권장)
- **매 30분**: 빠른 시그널 포착
- **매 2시간**: 서버 리소스 절약

---

## 문제 해결

### Q: 스케줄러가 실행되지 않습니다

```bash
# 1. 프로세스 확인
ps aux | grep run_scheduler

# 2. 로그 확인
tail -50 logs/scheduler_*.log

# 3. 수동 실행 테스트
python run_scheduler.py
```

### Q: Cron이 작동하지 않습니다

```bash
# 1. Cron 서비스 상태 확인 (Linux)
sudo systemctl status cron

# 2. Cron 로그 확인 (Mac)
tail -f /var/log/system.log | grep cron

# 3. 절대 경로 사용
0 * * * * cd /Users/jinxin/dev/aivesto && /usr/bin/python3 test_e2e_pipeline.py
```

### Q: 메모리 부족

```bash
# 1. FinBERT 비활성화 (메모리 절약)
pipeline = NewsPipeline(db_client=db, use_finbert=False)

# 2. 프로세스 재시작 주기 설정
# systemd: Restart=always, RestartSec=3600
```

---

## 성능 최적화

### 병렬 처리 (선택)

여러 스케줄러를 병렬로 실행:

```bash
# 스케줄러 1: Layer 1 수집 (매 시간)
# 스케줄러 2: Layer 2 수집 (매 2시간)
# 스케줄러 3: 분석 (매 3시간)
```

### 캐싱

```python
# RSS 피드 캐싱 (15분)
fetcher = RSSFetcher(cache_ttl=900)
```

---

**권장 설정**: APScheduler (매 시간 실행) + 로그 모니터링
