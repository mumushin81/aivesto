# AI 이미지 생성 시스템 - Quick Start

> Codex AI와 함께 제작한 블로그 기사용 전문 이미지 프롬프트 라이브러리

---

## 🚀 빠른 시작 (30초)

### 1️⃣ 프롬프트 확인
```bash
python3 scripts/generate_ai_image_prompts.py --list
```

### 2️⃣ 원하는 프롬프트 조회
```bash
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip --model midjourney
```

### 3️⃣ 클립보드에 복사
```bash
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip --model midjourney --copy
```

### 4️⃣ AI 플랫폼에서 생성
- **Midjourney**: Discord에서 `/imagine` + 붙여넣기
- **DALL-E**: ChatGPT Plus에서 붙여넣기
- **Stable Diffusion**: Leonardo.ai 또는 로컬에서 생성

---

## 📊 현황

| 항목 | 상태 |
|------|------|
| **총 프롬프트** | 20개 ✅ |
| **지원 종목** | NVDA, TSLA, AAPL, META, GOOGL, MSFT, AMZN, ADBE, NFLX, UBER |
| **AI 모델** | DALL-E, Midjourney, Stable Diffusion |
| **이미지 크기** | 1200x630px (SEO 최적화) |

---

## 🎨 프롬프트 예시

### NVIDIA Blackwell GPU (Midjourney)
```
NVDA Blackwell GPU launch, cinematic 16:9 wide shot,
futuristic server hall, sleek matte-black GPU core with
radiant emerald energy, volumetric light rays, fine metallic
textures, investment blog cover, professional photographic
realism --ar 1200:630 --v 6
```

**스타일**: NVIDIA Green (#76B900) + 차콜 블랙, 미래지향적, 기술적

---

### Tesla Robotaxi (DALL-E)
```
Tesla robotaxi concept gliding through a smart city at dusk,
Tesla red and metallic silver palette, autonomous HUD
projections on windshield, skyscrapers showing subtle
financial tickers, cinematic diagonal composition optimized
for 1200x630, confident professional tone.
```

**스타일**: Tesla Red (#E31937) + 실버, 역동적, 혁신적

---

## 📂 파일 구조

```
aivesto/
├── scripts/
│   ├── ai_image_prompts.json               # 📦 프롬프트 데이터베이스
│   └── generate_ai_image_prompts.py        # 🛠️ 조회 도구
└── docs/
    ├── AI_IMAGE_PROMPTS.md                 # 📋 전체 프롬프트 문서
    ├── ai_image_prompts.csv                # 📊 CSV 형식
    ├── IMAGE_GENERATION_GUIDE.md           # 📚 상세 가이드
    └── AI_IMAGE_README.md                  # 👈 이 문서
```

---

## 💡 사용 시나리오

### 시나리오 1: 새 블로그 기사 작성
1. 종목 선택 (예: NVDA)
2. 관련 주제 확인 (blackwell_chip, ai_datacenter)
3. Midjourney로 고품질 이미지 생성
4. 기사 썸네일로 사용

### 시나리오 2: 기존 기사 이미지 업그레이드
1. 현재 단조로운 PIL 이미지 확인
2. 해당 종목/주제 프롬프트 조회
3. DALL-E로 빠르게 생성 (ChatGPT Plus)
4. 이미지 교체

### 시나리오 3: 소셜 미디어 공유
1. 트렌딩 종목 확인
2. Stable Diffusion으로 무료 생성
3. 1200x630 크기로 Twitter/LinkedIn 공유

---

## 🎯 지원 플랫폼 비교

| 플랫폼 | 장점 | 가격 | 추천 용도 |
|--------|------|------|-----------|
| **DALL-E 3** | ChatGPT Plus로 즉시 사용 | $20/월 | 빠른 테스트 |
| **Midjourney** | 최고 품질, 사진급 리얼리즘 | $30/월 | 상업용 고품질 |
| **Stable Diffusion** | 오픈소스, 로컬 실행 | 무료 | 비용 절감 |

---

## 🔥 인기 프롬프트 Top 5

1. **NVDA_blackwell_chip** - AI 칩 시장 선도
2. **TSLA_robotaxi** - 자율주행 혁명
3. **META_business_ai** - 비즈니스 AI 툴
4. **AAPL_premium_iphone** - 프리미엄 전략
5. **MSFT_copilot** - 생산성 AI

---

## 📖 상세 문서

- **[IMAGE_GENERATION_GUIDE.md](./IMAGE_GENERATION_GUIDE.md)** - 종합 사용 가이드
- **[AI_IMAGE_PROMPTS.md](./AI_IMAGE_PROMPTS.md)** - 전체 프롬프트 목록

---

## 🤝 기여

새로운 종목/주제 프롬프트를 추가하려면:

1. `scripts/ai_image_prompts.json` 편집
2. 형식 준수:
   ```json
   {
     "SYMBOL_topic": {
       "dalle_prompt": "...",
       "midjourney_prompt": "...",
       "stable_diffusion_prompt": "...",
       "style_notes": "..."
     }
   }
   ```
3. Export: `python3 scripts/generate_ai_image_prompts.py --export all`

---

## 💬 피드백

질문이나 제안사항은 GitHub Issues로 제보해주세요!

---

**제작**: Codex AI + Claude Code
**업데이트**: 2025-11-15
**버전**: 1.0
