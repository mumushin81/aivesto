# Python 업그레이드 로그

**업그레이드 날짜**: 2025-11-16
**작업자**: Claude Code

---

## 📊 업그레이드 요약

| 항목 | Before | After | 상태 |
|------|--------|-------|------|
| **Python 버전** | 3.9.6 | 3.12.12 | ✅ |
| **pyenv** | 2.6.11 | 2.6.12 | ✅ |
| **pip** | - | 25.3 | ✅ |
| **가상환경** | 없음 | venv (3.12.12) | ✅ |

---

## 🔧 수행한 작업

### 1️⃣ pyenv 업데이트
```bash
brew upgrade pyenv
# 2.6.11 → 2.6.12
```

### 2️⃣ Python 3.12.12 설치
```bash
pyenv install 3.12.12
# 설치 경로: /Users/jinxin/.pyenv/versions/3.12.12
```

### 3️⃣ 글로벌 버전 변경
```bash
pyenv global 3.12.12
python3 --version
# Python 3.12.12 ✅
```

### 4️⃣ 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```

### 5️⃣ 패키지 설치
```bash
pip install --upgrade pip  # 25.3
pip install -r requirements.txt
```

---

## 📦 설치된 패키지 (주요)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| **Flask** | 2.3.3 | 웹 서버 |
| **flask-cors** | 4.0.0 | CORS 처리 |
| **supabase** | 2.3.4 | 데이터베이스 |
| **loguru** | 0.7.2 | 로깅 |
| **python-dotenv** | 1.0.0 | 환경변수 |
| **pydantic** | 2.12.4 | 데이터 검증 |
| **httpx** | 0.25.2 | HTTP 클라이언트 |

**총 설치 패키지**: 36개

---

## ✅ 확인 사항

### Python 버전
```bash
$ python3 --version
Python 3.12.12 ✅

$ source venv/bin/activate
$ python --version
Python 3.12.12 ✅
```

### pip 버전
```bash
$ pip --version
pip 25.3 ✅
```

### 설치 위치
```bash
$ which python3
/Users/jinxin/.pyenv/shims/python3 ✅

$ pyenv versions
  system
  3.12.0
* 3.12.12 (set by /Users/jinxin/.pyenv/version)
```

---

## 🚀 Python 3.12의 주요 개선사항

### 성능
- **최대 5% 빠른 실행 속도**
- 메모리 사용량 최적화
- asyncio 성능 향상

### 새로운 기능
- **PEP 701**: f-string 문법 개선
- **PEP 698**: `@override` 데코레이터
- **PEP 692**: TypedDict `**kwargs` 지원
- **PEP 688**: Buffer Protocol 개선

### 보안
- 최신 보안 패치 적용
- SSL/TLS 라이브러리 업데이트

---

## 📝 사용 방법

### 가상환경 활성화
```bash
cd /Users/jinxin/dev/aivesto
source venv/bin/activate
```

### Flask 서버 실행
```bash
python3 -m web.app
# → http://localhost:5001
```

### 스크립트 실행
```bash
# 이미지 프롬프트 조회
python3 scripts/generate_ai_image_prompts.py --list

# E2E 파이프라인
python3 test_e2e_pipeline.py
```

---

## ⚠️ 주의사항

### 가상환경 사용 필수
```bash
# ❌ 잘못된 방법
python3 main.py

# ✅ 올바른 방법
source venv/bin/activate
python main.py
```

### 패키지 추가 시
```bash
source venv/bin/activate
pip install new_package
pip freeze > requirements.txt  # requirements 업데이트
```

### 가상환경 비활성화
```bash
deactivate
```

---

## 🔄 롤백 방법 (필요 시)

### Python 3.9.6으로 복원
```bash
pyenv global 3.9.6
python3 --version  # 확인
```

### 가상환경 재생성
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📂 백업 파일

- **패키지 목록**: `requirements_backup_20251116.txt`
- **위치**: `/Users/jinxin/dev/aivesto/`

복원 방법:
```bash
pip install -r requirements_backup_20251116.txt
```

---

## 🎯 다음 단계

1. **테스트 실행**
   ```bash
   source venv/bin/activate
   python3 test_e2e_pipeline.py
   ```

2. **웹 서버 확인**
   ```bash
   python3 -m web.app
   # → http://localhost:5001
   ```

3. **Midjourney MCP 테스트** (설정 완료 시)
   ```bash
   # Claude Desktop에서 테스트
   ```

---

## 🐛 문제 해결

### "No module named 'xxx'" 에러
```bash
source venv/bin/activate  # 가상환경 활성화 확인
pip install xxx
```

### "command not found: python3"
```bash
# pyenv 셸 설정 확인
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

### pip 업그레이드 오류
```bash
source venv/bin/activate
python -m pip install --upgrade pip
```

---

## 📚 참고 문서

- [Python 3.12 릴리즈 노트](https://docs.python.org/3.12/whatsnew/3.12.html)
- [pyenv 공식 문서](https://github.com/pyenv/pyenv)
- [Python venv 가이드](https://docs.python.org/3/library/venv.html)

---

**작성일**: 2025-11-16
**버전**: Python 3.12.12
**환경**: macOS (ARM64), pyenv 2.6.12
