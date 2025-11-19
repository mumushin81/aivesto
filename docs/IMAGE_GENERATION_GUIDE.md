# AI 이미지 생성 가이드

**작성일**: 2025-11-15
**작성자**: Codex AI + Claude Code
**목적**: Aivesto 블로그 기사용 고품질 이미지 생성

---

## 📋 목차

1. [개요](#개요)
2. [프롬프트 라이브러리](#프롬프트-라이브러리)
3. [사용 방법](#사용-방법)
4. [지원 플랫폼](#지원-플랫폼)
5. [실전 예시](#실전-예시)
6. [품질 가이드](#품질-가이드)
7. [FAQ](#faq)

---

## 개요

### 🎯 **목표**

기존의 단조로운 그라디언트 이미지를 **전문적이고 역동적인 AI 생성 이미지**로 대체하여 블로그 썸네일의 시각적 임팩트를 강화합니다.

### ✨ **특징**

- **20개 종목별 맞춤 프롬프트**: AAPL, NVDA, TSLA, META, GOOGL 등
- **3가지 AI 모델 지원**: DALL-E, Midjourney, Stable Diffusion
- **기업 브랜드 색상 반영**: 각 회사의 공식 컬러 팔레트 사용
- **SEO 최적화 크기**: 1200x630px (소셜 미디어 썸네일 표준)
- **전문적인 비주얼**: 투자/금융/기술 주제에 맞는 신뢰감 있는 디자인

---

## 프롬프트 라이브러리

### 📦 **저장 위치**

```
aivesto/
├── scripts/
│   ├── ai_image_prompts.json          # 프롬프트 데이터베이스
│   └── generate_ai_image_prompts.py   # 프롬프트 조회 도구
└── docs/
    ├── AI_IMAGE_PROMPTS.md            # 전체 프롬프트 문서
    └── ai_image_prompts.csv           # CSV 형식
```

### 📊 **현재 사용 가능한 프롬프트 (20개)**

| 종목 | 주제 | 설명 |
|------|------|------|
| **NVDA** | blackwell_chip | Blackwell GPU 차세대 AI 칩 |
| **NVDA** | ai_datacenter | AI 데이터센터 인프라 |
| **TSLA** | robotaxi | 자율주행 로보택시 |
| **TSLA** | charging_network | 슈퍼차저 충전 네트워크 |
| **AAPL** | premium_iphone | iPhone 프리미엄 전략 |
| **AAPL** | enterprise | 기업용 Apple 제품 |
| **ADBE** | creative_cloud | Creative Cloud 디자인 툴 |
| **ADBE** | firefly_ai | Firefly 생성형 AI |
| **AMZN** | aws_cloud | AWS 클라우드 인프라 |
| **AMZN** | ai_services | Bedrock AI 플랫폼 |
| **GOOGL** | search_ai | AI 기반 검색 혁신 |
| **GOOGL** | advertising | 디지털 광고 플랫폼 |
| **META** | business_ai | Business AI 도구 |
| **META** | llama_opensource | Llama 오픈소스 AI |
| **MSFT** | copilot | Copilot AI 어시스턴트 |
| **MSFT** | azure_cloud | Azure 클라우드 서비스 |
| **NFLX** | streaming | 스트리밍 콘텐츠 |
| **NFLX** | advertising | 광고 기반 구독 |
| **UBER** | rideshare | 라이드셰어 수익성 |
| **UBER** | eats | Uber Eats 배달 |

---

## 사용 방법

### 1️⃣ **프롬프트 목록 확인**

```bash
python3 scripts/generate_ai_image_prompts.py --list
```

**출력 예시**:
```
📸 Available AI Image Prompts

NVDA:
  - ai_datacenter
  - blackwell_chip

TSLA:
  - charging_network
  - robotaxi

✓ Total: 20 prompts available
```

---

### 2️⃣ **특정 프롬프트 조회**

#### 모든 모델 프롬프트 보기
```bash
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip
```

#### 특정 모델만 보기
```bash
# Midjourney만
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip --model midjourney

# DALL-E만
python3 scripts/generate_ai_image_prompts.py --symbol TSLA --topic robotaxi --model dalle

# Stable Diffusion만
python3 scripts/generate_ai_image_prompts.py --symbol AAPL --topic premium_iphone --model stable_diffusion
```

---

### 3️⃣ **클립보드에 복사 (macOS)**

```bash
python3 scripts/generate_ai_image_prompts.py --symbol NVDA --topic blackwell_chip --model midjourney --copy
```

**결과**: 프롬프트가 클립보드에 복사되어 바로 붙여넣기 가능!

---

### 4️⃣ **문서 Export**

#### Markdown 형식
```bash
python3 scripts/generate_ai_image_prompts.py --export markdown
```
→ `docs/AI_IMAGE_PROMPTS.md` 생성

#### CSV 형식
```bash
python3 scripts/generate_ai_image_prompts.py --export csv
```
→ `docs/ai_image_prompts.csv` 생성

#### 모두 Export
```bash
python3 scripts/generate_ai_image_prompts.py --export all
```

---

## 지원 플랫폼

### 🎨 **DALL-E 3 (OpenAI)**

**장점**:
- ChatGPT Plus 구독으로 즉시 사용 가능
- 프롬프트 이해도가 뛰어남
- 텍스트 삽입 가능

**사용법**:
1. [ChatGPT Plus](https://chat.openai.com) 접속
2. DALL-E 3 선택
3. 프롬프트 붙여넣기
4. 생성된 이미지 다운로드

**가격**: $20/월 (무제한)

---

### 🖼️ **Midjourney**

**장점**:
- 가장 고품질 결과물
- 사진 같은 리얼리즘
- 기업용으로 적합

**사용법**:
1. [Midjourney Discord](https://discord.gg/midjourney) 참여
2. `/imagine` 명령어 사용
3. 프롬프트 붙여넣기 (--ar 1200:630 포함)
4. U1~U4로 업스케일 후 다운로드

**가격**:
- Basic: $10/월 (200장)
- Standard: $30/월 (무제한)
- Pro: $60/월 (상업용)

---

### 🌟 **Stable Diffusion**

**장점**:
- 로컬에서 무료 실행 가능
- 오픈소스
- 커스터마이징 자유

**사용법 (로컬)**:
1. [Automatic1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 설치
2. 프롬프트 입력
3. Size: 1200x630 설정
4. Generate

**사용법 (클라우드)**:
- [Leonardo.ai](https://leonardo.ai): 무료 150 크레딧/일
- [DreamStudio](https://beta.dreamstudio.ai): $10 = 1000 크레딧

---

## 실전 예시

### 📸 **예시 1: NVDA Blackwell GPU**

#### Midjourney 프롬프트
```
NVDA Blackwell GPU launch, cinematic 16:9 wide shot, futuristic server hall,
sleek matte-black GPU core with radiant emerald energy, volumetric light rays,
fine metallic textures, investment blog cover, professional photographic realism
--ar 1200:630 --v 6
```

#### 스타일 가이드
- **색상**: NVIDIA Green (#76B900) + 차콜 블랙
- **구도**: 비대칭, 오른쪽에 텍스트 공간 확보
- **분위기**: 미래지향적, 전문적, 기술적

---

### 🚖 **예시 2: TSLA Robotaxi**

#### DALL-E 프롬프트
```
Tesla robotaxi concept gliding through a smart city at dusk, Tesla red and
metallic silver palette, autonomous HUD projections on windshield, skyscrapers
showing subtle financial tickers, cinematic diagonal composition optimized for
1200x630, confident professional tone.
```

#### 스타일 가이드
- **색상**: Tesla Red (#E31937) + 실버 메탈릭
- **구도**: 대각선 역동성, 왼쪽 상단 헤드라인 공간
- **분위기**: 자율주행, 미래 도시, 혁신

---

### 📱 **예시 3: AAPL Premium iPhone**

#### Stable Diffusion 프롬프트
```
Photoreal composition of premium iPhone close-up with stainless steel edges,
soft depth-of-field, transparent financial overlay (revenue growth curve) in
muted gold, modern serif headline space, professional tech-finance aesthetic.
```

#### 스타일 가이드
- **색상**: Apple Silver + Midnight Blue + 골드 액센트
- **구도**: 매크로 샷, 장인정신 강조
- **분위기**: 프리미엄, 럭셔리, 신뢰

---

## 품질 가이드

### ✅ **체크리스트**

이미지 생성 후 다음 항목을 확인하세요:

- [ ] **크기**: 정확히 1200x630px
- [ ] **텍스트 공간**: 헤드라인/부제목 삽입 가능한 여백 확보
- [ ] **브랜드 색상**: 기업 컬러 팔레트 반영
- [ ] **가독성**: 텍스트 오버레이 시 배경 대비 충분
- [ ] **전문성**: 블로그 썸네일로 적합한 품질
- [ ] **일관성**: 다른 기사 이미지와 스타일 조화

---

### 🎨 **색상 팔레트 참고**

| 종목 | Primary | Secondary | 용도 |
|------|---------|-----------|------|
| **NVDA** | #76B900 (Green) | #000000 (Black) | AI 칩, 데이터센터 |
| **TSLA** | #E31937 (Red) | #333333 (Dark Gray) | 자율주행, 전기차 |
| **AAPL** | #000000 (Black) | #999999 (Gray) | 프리미엄 제품 |
| **ADBE** | #ED1C24 (Red) | #FF7F82 (Pink) | 크리에이티브 툴 |
| **AMZN** | #FF9900 (Orange) | #232F3E (Navy) | 클라우드, AI |
| **GOOGL** | #4285F4 (Blue) | #EA4335 (Red) | 검색, 광고 |
| **META** | #0165E1 (Blue) | #00B4FF (Cyan) | 소셜, 비즈니스 AI |
| **MSFT** | #0078D4 (Blue) | #7D7D7D (Gray) | 생산성, 클라우드 |
| **NFLX** | #E50914 (Red) | #000000 (Black) | 스트리밍 |
| **UBER** | #000000 (Black) | #FFFFFF (White) | 라이드셰어 |

---

## FAQ

### ❓ **Q1: 어떤 플랫폼이 가장 좋나요?**

**A**: 목적에 따라 다릅니다.

- **빠른 테스트**: DALL-E (ChatGPT Plus)
- **최고 품질**: Midjourney (상업용)
- **무료/로컬**: Stable Diffusion

---

### ❓ **Q2: 프롬프트를 수정해도 되나요?**

**A**: 네! 프롬프트는 가이드라인입니다. 다음을 자유롭게 조정하세요:

- 색상 톤
- 구도 (세로/가로)
- 특정 요소 추가/제거
- 분위기 (밝게/어둡게)

---

### ❓ **Q3: 새로운 종목 프롬프트를 추가하려면?**

**A**: `scripts/ai_image_prompts.json`에 다음 형식으로 추가:

```json
{
  "SYMBOL_topic_name": {
    "dalle_prompt": "...",
    "midjourney_prompt": "...",
    "stable_diffusion_prompt": "...",
    "style_notes": "..."
  }
}
```

---

### ❓ **Q4: 라이선스는?**

**A**: 플랫폼별로 다릅니다.

- **DALL-E**: 상업적 사용 가능 (ChatGPT Plus 구독 시)
- **Midjourney**: Standard 이상 구독 시 상업적 사용 가능
- **Stable Diffusion**: CreativeML OpenRAIL-M (상업적 사용 가능)

블로그 기사용은 모두 문제없습니다.

---

### ❓ **Q5: 기존 PIL 이미지는 어떻게 하나요?**

**A**: 당분간 병행 사용 권장:

- **AI 이미지**: 주요 기사, 트렌딩 주제
- **PIL 이미지**: 백업, 빠른 테스트

점진적으로 AI 이미지로 전환하세요.

---

## 📚 **추가 리소스**

### 문서
- [AI_IMAGE_PROMPTS.md](./AI_IMAGE_PROMPTS.md) - 전체 프롬프트 목록
- [ai_image_prompts.csv](./ai_image_prompts.csv) - CSV 데이터

### 도구
- [generate_ai_image_prompts.py](../scripts/generate_ai_image_prompts.py) - 프롬프트 조회 스크립트

### 외부 링크
- [ChatGPT Plus](https://chat.openai.com/plus) - DALL-E 3 접근
- [Midjourney](https://www.midjourney.com) - 고품질 이미지 생성
- [Leonardo.ai](https://leonardo.ai) - 무료 Stable Diffusion
- [Prompt Engineering Guide](https://www.promptingguide.ai) - 프롬프트 작성 가이드

---

## 🎉 **마무리**

이제 Aivesto 블로그 기사에 **전문적이고 임팩트 있는 AI 이미지**를 추가할 수 있습니다!

**워크플로우 요약**:
1. 프롬프트 조회: `--symbol NVDA --topic blackwell_chip`
2. 복사: `--copy` 옵션 사용
3. AI 플랫폼에서 생성: Midjourney/DALL-E/SD
4. 다운로드 및 최적화: 1200x630px
5. 블로그에 삽입: `![Alt text](../images/NVDA_blackwell.jpg)`

**질문이나 피드백**은 GitHub Issues로 제보해주세요!

---

**작성일**: 2025-11-15
**버전**: 1.0
**Contributors**: Codex AI, Claude Code
