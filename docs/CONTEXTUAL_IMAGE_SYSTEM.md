# 🎨 문맥 기반 블로그 이미지 자동 생성 시스템

**최종 업데이트**: 2025-11-16
**프로젝트**: Aivesto - AI Blog Image Automation

---

## 📋 시스템 개요

블로그 글의 내용을 AI가 분석하여 각 섹션에 맞는 Midjourney 프롬프트를 자동 생성하고, **최소 5장 이상**의 이미지를 생성하여 문맥에 맞게 배치하는 완전 자동화 시스템

---

## 🔄 전체 플로우

```
1. 블로그 글 분석
   📄 Markdown → 섹션 추출 → 키워드 분석 → 이미지 삽입 위치 식별

2. 프롬프트 생성
   🤖 AI (GPT-4/Claude) → 문맥 기반 Midjourney 프롬프트 생성 (5+개)

3. 이미지 생성
   🎨 Discord Bot → Midjourney → 이미지 생성 (5+장)

4. 저장 및 관리
   💾 Supabase Storage + PostgreSQL (메타데이터)

5. 자동 배치
   ✏️  Markdown에 이미지 태그 자동 삽입

6. 완료!
   🎉 문맥에 맞는 이미지가 포함된 완성된 블로그 글
```

---

## 📁 생성된 파일 구조

```
/Users/jinxin/dev/aivesto/
├── scripts/
│   ├── blog_content_analyzer.py           # 1️⃣ 글 분석 (4.7KB)
│   ├── contextual_prompt_generator.py     # 2️⃣ 프롬프트 생성 (5.1KB)
│   ├── multi_image_generator.py           # 3️⃣ 이미지 생성 (3.1KB)
│   ├── smart_image_injector.py            # 4️⃣ 이미지 배치 (2.1KB)
│   ├── run_blog_image_pipeline.py         # 🚀 파이프라인 실행
│   └── batch_process_all_articles.py      # 📦 배치 처리
├── database/
│   └── article_images_schema.sql          # 확장된 스키마
└── articles/
    ├── article_NVDA_blackwell_gpu_20251113.md  # 원본
    ├── article_TSLA_robotaxi_fleet_20251113.md
    └── ... (11개 기사)
```

---

## 🚀 사용 방법

### 방법 1: 단일 기사 처리

```bash
python scripts/run_blog_image_pipeline.py \
  articles/article_NVDA_blackwell_gpu_20251113.md \
  --article-id nvda_blackwell_20251113 \
  --workdir tmp/pipeline
```

### 방법 2: 모든 기사 배치 처리 ⭐ 추천

```bash
# 모든 기사 처리 (11개)
python scripts/batch_process_all_articles.py

# 테스트 모드 (실제 이미지 생성 안 함)
python scripts/batch_process_all_articles.py --dry-run

# 특정 기사만 처리
python scripts/batch_process_all_articles.py --articles "NVDA,TSLA,AAPL"

# 동시 처리 수 조절 (기본 2개)
python scripts/batch_process_all_articles.py --max-concurrent 3
```

### 방법 3: 단계별 수동 실행

```bash
# 1단계: 글 분석
python scripts/blog_content_analyzer.py \
  articles/article_NVDA_blackwell_gpu_20251113.md \
  --out tmp/analysis.json

# 2단계: 프롬프트 생성
python scripts/contextual_prompt_generator.py \
  tmp/analysis.json \
  --out tmp/prompts.json

# 3단계: 이미지 생성
python scripts/multi_image_generator.py \
  tmp/prompts.json \
  --article-id nvda_blackwell_20251113 \
  --out tmp/images.json

# 4단계: 이미지 삽입
python scripts/smart_image_injector.py \
  articles/article_NVDA_blackwell_gpu_20251113.md \
  tmp/images.json \
  --out articles_with_images/article_NVDA_blackwell_gpu_20251113.md
```

---

## 📊 데이터베이스 스키마

### 확장된 images 테이블

```sql
CREATE TABLE public.images (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol text NOT NULL,                   -- NVDA, TSLA, etc.
  topic text NOT NULL,                    -- blackwell_chip, robotaxi, etc.
  prompt text NOT NULL,                   -- Midjourney 프롬프트
  image_url text NOT NULL,                -- Supabase Storage URL
  section_title text,                     -- 섹션 제목 (NEW!)
  context_keywords text[],                -- 문맥 키워드 (NEW!)
  image_type text,                        -- hero, diagram, chart, etc. (NEW!)
  caption text,                           -- 이미지 캡션 (NEW!)
  created_at timestamptz DEFAULT now()
);
```

### article_sections 테이블 (NEW!)

```sql
CREATE TABLE public.article_sections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id text NOT NULL,
  section_index integer NOT NULL,
  section_title text NOT NULL,
  content_excerpt text,
  keywords text[],
  image_id uuid REFERENCES images(id),
  created_at timestamptz DEFAULT now()
);
```

### 스키마 적용 방법

```bash
# Supabase Dashboard → SQL Editor
# 또는 CLI 사용
supabase db push --file database/article_images_schema.sql
```

---

## 🎯 기능 상세

### 1. blog_content_analyzer.py

**기능:**
- Markdown 파싱 및 섹션 추출
- 각 섹션의 주제 및 키워드 자동 분석
- 이미지 삽입 최적 위치 식별 (최소 5개)

**출력 예시:**
```json
{
  "sections": [
    {
      "index": 0,
      "title": "NVIDIA Blackwell GPU 출시",
      "keywords": ["GPU", "AI", "Blackwell", "아키텍처"],
      "image_slot_after_line": 5,
      "type": "hero"
    },
    ...
  ]
}
```

### 2. contextual_prompt_generator.py

**기능:**
- GPT-4/Claude API로 문맥 이해
- 각 섹션에 최적화된 Midjourney 프롬프트 생성
- 브랜드 컬러 및 스타일 일관성 유지

**생성 프롬프트 예시:**
```
1. Hero: "Ultra-detailed 1200x630 hero image of NVIDIA Blackwell GPU..."
2. Architecture: "Technical diagram showing Blackwell architecture..."
3. Market: "Professional business chart, AI chip market share..."
4. Competition: "Comparative infographic AMD vs NVIDIA vs Intel..."
5. Technical: "Close-up 3D render of Blackwell chip circuitry..."
```

### 3. multi_image_generator.py

**기능:**
- 5개 이상의 이미지 동시 생성
- Discord Bot을 통한 Midjourney 자동화
- Supabase Storage 업로드 및 메타데이터 저장

**특징:**
- 비동기 처리로 빠른 생성
- 섹션별 메타데이터 자동 태깅
- 에러 처리 및 재시도 로직

### 4. smart_image_injector.py

**기능:**
- Markdown에 반응형 이미지 태그 자동 삽입
- 각 섹션에 문맥에 맞는 이미지 배치
- 자동 캡션 생성

**삽입 예시:**
```markdown
## Blackwell 아키텍처 혁신

<picture>
  <img src="https://supabase.../nvda_arch_diagram.jpg"
       alt="Blackwell Architecture Diagram"
       loading="lazy">
</picture>
*Blackwell 아키텍처의 핵심 구성요소*

NVIDIA의 차세대 GPU는...
```

---

## 📦 배치 처리 (11개 기사 전체)

### 실행 명령

```bash
cd /Users/jinxin/dev/aivesto

# 전체 기사 처리
python scripts/batch_process_all_articles.py
```

### 처리 대상 기사 (11개)

1. ✅ NVDA - Blackwell GPU
2. ✅ NVDA - Foxconn AI Server
3. ✅ TSLA - Robotaxi Fleet
4. ✅ AAPL - iPhone Sales
5. ✅ MSFT - Copilot Integration
6. ✅ META - Enterprise AI
7. ✅ GOOGL - Search AI
8. ✅ AMZN - AWS AI Services
9. ✅ ADBE - Creative AI
10. ✅ NFLX - Subscriber Growth
11. ✅ UBER - Profitability

### 예상 결과

```
📊 배치 프로세싱 완료!
  총 11개 기사
  → 55+ 이미지 생성 (기사당 5장 이상)
  → articles_with_images/ 에 저장
```

---

## ⚙️ 환경 설정

### 필수 환경 변수 (.env)

```bash
# Discord Bot
DISCORD_BOT_TOKEN=your_token
MIDJOURNEY_CHANNEL_ID=your_channel_id
MIDJOURNEY_BOT_ID=936929561302675456

# Supabase
SUPABASE_URL=https://czubqsnahmtdsmnyawlk.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key  # 업로드용

# OpenAI (선택사항 - 프롬프트 생성 고도화)
OPENAI_API_KEY=your_openai_key  # 없으면 휴리스틱 방식 사용
```

### Python 패키지

```bash
pip install discord.py supabase aiohttp beautifulsoup4 loguru python-dotenv markdown
```

---

## 🐛 문제 해결

### Midjourney 이미지가 생성되지 않음

```bash
# 1. Discord 봇 확인
# MESSAGE CONTENT INTENT 활성화 확인

# 2. Midjourney 구독 확인
# /info 명령어로 구독 상태 확인

# 3. 채널 권한 확인
# 봇이 해당 채널에서 메시지 읽기/쓰기 권한 있는지 확인
```

### Supabase 업로드 실패

```bash
# Service Role Key 확인
# .env 파일의 SUPABASE_SERVICE_ROLE_KEY 설정 확인

# 스키마 적용 확인
supabase db push --file database/article_images_schema.sql
```

### 프롬프트 품질이 낮음

```bash
# OPENAI_API_KEY 설정
# GPT-4를 사용하면 더 정교한 프롬프트 생성
```

---

## ⚠️ 중요 주의사항

### TOS 위험

- Discord/Midjourney 자동화는 약관 위반 가능
- **개인 서버**에서만 사용
- **상업적 사용 금지**
- Rate limiting 준수 (분당 2-3회 이하)

### 비용

- Midjourney 구독 필요 ($10~60/월)
- OpenAI API (선택, ~$0.01/기사)
- Supabase (무료 tier 가능)

### 성능

- 기사당 처리 시간: ~5-10분 (이미지 생성 시간)
- 11개 기사 전체: ~1-2시간 (배치 처리)

---

## 📈 다음 단계

### 1단계: 스키마 적용

```bash
# Supabase Dashboard → SQL Editor
https://supabase.com/dashboard/project/czubqsnahmtdsmnyawlk/sql/new

# database/article_images_schema.sql 실행
```

### 2단계: 테스트 실행

```bash
# 단일 기사 테스트 (NVDA)
python scripts/run_blog_image_pipeline.py \
  articles/article_NVDA_blackwell_gpu_20251113.md \
  --article-id nvda_test
```

### 3단계: 배치 실행

```bash
# 전체 11개 기사 처리
python scripts/batch_process_all_articles.py
```

### 4단계: 결과 확인

```bash
# 생성된 기사 확인
ls -lh articles_with_images/

# 이미지 확인
# Supabase Dashboard → Storage → blog-images
```

---

## 🎉 완성!

시스템이 완전히 준비되었습니다!

```bash
# 지금 바로 실행하세요
python scripts/batch_process_all_articles.py
```

---

## 📞 지원

문제 발생 시:
1. `docs/SYSTEM_READY.md` 확인
2. `logs/` 디렉토리 에러 로그 확인
3. Supabase Dashboard에서 데이터 확인

**Happy Blogging with AI Images!** 🎨✨
