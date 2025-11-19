# 📸 수동 이미지 제작 + 자동 배치 워크플로우

**최종 업데이트**: 2025-11-16  
**프로젝트**: Aivesto Blog - Manual Image Workflow

---

## 🎯 개요

Midjourney에서 직접 이미지를 제작한 후, 스크립트로 Supabase 업로드 및 블로그 자동 배치

---

## 📋 전체 워크플로우

```
1. Midjourney에서 이미지 제작 (수동)
   ↓
2. 이미지 다운로드
   ↓
3. Supabase 업로드 (스크립트)
   ↓
4. 블로그 자동 배치 (스크립트)
   ↓
5. 완성! 🎉
```

---

## 🔧 1단계: 프롬프트 확인

먼저 어떤 이미지가 필요한지 확인합니다:

```bash
# 기사 분석하여 필요한 이미지 확인
python scripts/blog_content_analyzer.py \
  articles/article_NVDA_blackwell_gpu_20251113.md \
  --out tmp/analysis.json

# 프롬프트 생성 (참고용)
python scripts/contextual_prompt_generator.py \
  tmp/analysis.json \
  --out tmp/prompts.json

# 생성된 프롬프트 확인
cat tmp/prompts.json | jq
```

**출력 예시:**
```json
{
  "0": {
    "section_index": 0,
    "section_title": "NVIDIA Blackwell GPU 출시",
    "image_type": "hero",
    "prompt": "Futuristic NVIDIA GPU chip with glowing green circuits...",
    "position": 0
  },
  ...
}
```

---

## 🎨 2단계: Midjourney에서 이미지 제작

1. **Midjourney Discord** 또는 **Midjourney.com** 접속
2. 생성된 프롬프트를 사용하여 이미지 제작
3. 고해상도 이미지 다운로드
4. 파일명을 의미있게 변경 (예: `nvda_hero_gpu.jpg`)

---

## 📤 3단계: Supabase 업로드

이미지를 Supabase에 업로드하고 메타데이터 저장:

```bash
python scripts/manual_image_uploader.py \
  path/to/image.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 0 \
  --section-title "NVIDIA Blackwell GPU 출시" \
  --image-type hero \
  --keywords "nvidia,blackwell,gpu,ai" \
  --caption "NVIDIA Blackwell GPU가 AI 성능을 5배 향상시켰습니다"
```

**파라미터 설명:**
- `image.jpg`: 업로드할 이미지 파일 경로
- `--article-id`: 기사 ID (파일명에서 추출, 예: `nvda_blackwell_20251113`)
- `--section-index`: 섹션 인덱스 (0부터 시작)
- `--section-title`: 섹션 제목
- `--image-type`: `hero` | `diagram` | `chart` | `concept` | `comparison` | `closeup` | `business`
- `--keywords`: 쉼표로 구분된 키워드
- `--caption`: 이미지 캡션 (선택사항)

**예시 - NVDA 기사 5개 이미지 업로드:**

```bash
# Hero 이미지
python scripts/manual_image_uploader.py \
  images/nvda_hero.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 0 \
  --section-title "NVIDIA Blackwell GPU 출시" \
  --image-type hero \
  --keywords "nvidia,blackwell,gpu"

# 다이어그램
python scripts/manual_image_uploader.py \
  images/nvda_architecture.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 1 \
  --section-title "아키텍처 혁신" \
  --image-type diagram \
  --keywords "architecture,chip,design"

# 차트
python scripts/manual_image_uploader.py \
  images/nvda_market_chart.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 2 \
  --section-title "시장 점유율" \
  --image-type chart \
  --keywords "market,share,growth"

# 비교
python scripts/manual_image_uploader.py \
  images/nvda_comparison.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 3 \
  --section-title "경쟁사 비교" \
  --image-type comparison \
  --keywords "amd,intel,comparison"

# 클로즈업
python scripts/manual_image_uploader.py \
  images/nvda_closeup.jpg \
  --article-id nvda_blackwell_20251113 \
  --section-index 4 \
  --section-title "칩 상세" \
  --image-type closeup \
  --keywords "chip,silicon,closeup"
```

---

## 📝 4단계: 블로그 자동 배치

업로드된 이미지를 자동으로 블로그 기사에 삽입:

```bash
python scripts/auto_inject_images_from_db.py \
  --article-id nvda_blackwell_20251113 \
  --input articles/article_NVDA_blackwell_gpu_20251113.md \
  --output articles_with_images/article_NVDA_blackwell_gpu_20251113.md
```

**결과:**
- `articles_with_images/article_NVDA_blackwell_gpu_20251113.md` 생성
- 이미지가 자동으로 삽입된 완성된 기사

---

## 📦 전체 11개 기사 처리 예시

```bash
# 1. NVDA - Blackwell
# (위 예시 참조)

# 2. NVDA - Foxconn
python scripts/manual_image_uploader.py images/nvda_foxconn_1.jpg \
  --article-id nvda_foxconn_ai_server_20251115 \
  --section-index 0 --section-title "Title" --image-type hero

# 3. TSLA - Robotaxi
python scripts/manual_image_uploader.py images/tsla_robotaxi_1.jpg \
  --article-id tsla_robotaxi_fleet_20251113 \
  --section-index 0 --section-title "Title" --image-type hero

# ... (나머지 8개 기사도 동일한 패턴)
```

---

## 🗄️ Supabase 데이터 확인

Supabase Dashboard에서 확인:

1. **Images 테이블**: https://supabase.com/dashboard/project/czubqsnahmtdsmnyawlk/editor
2. **Blog Images 테이블**: 기사별 이미지 매핑
3. **Storage**: https://supabase.com/dashboard/project/czubqsnahmtdsmnyawlk/storage/buckets/blog-images

---

## 🔍 문제 해결

### 이미지 업로드 실패

```bash
# Supabase 연결 확인
python3 << 'EOF'
from supabase import create_client
import os
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print(supabase.table('images').select("*").limit(1).execute())
EOF
```

### DB에 이미지가 없음

```bash
# 특정 article_id의 이미지 확인
python3 << 'EOF'
from supabase import create_client
import os
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
result = supabase.table('blog_images').select('*').eq('article_id', 'nvda_blackwell_20251113').execute()
print(result.data)
EOF
```

---

## 📊 진행 상황 추적

```bash
# 11개 기사별 체크리스트
- [ ] NVDA - Blackwell (5개 이미지)
- [ ] NVDA - Foxconn (5개 이미지)
- [ ] TSLA - Robotaxi (5개 이미지)
- [ ] AAPL - iPhone (5개 이미지)
- [ ] MSFT - Copilot (5개 이미지)
- [ ] META - Enterprise AI (5개 이미지)
- [ ] GOOGL - Search AI (5개 이미지)
- [ ] AMZN - AWS AI (5개 이미지)
- [ ] ADBE - Creative AI (5개 이미지)
- [ ] NFLX - Subscriber (5개 이미지)
- [ ] UBER - Profitability (5개 이미지)

총: 55개 이미지
```

---

## 🎉 완료!

모든 이미지가 업로드되고 블로그에 배치되었습니다!

**다음 단계:**
1. `articles_with_images/` 폴더의 완성된 기사 확인
2. 블로그 사이트에 배포
3. Supabase Storage에서 이미지 URL 확인

---

## 📞 참고 문서

- [Supabase 스키마 설정](./SUPABASE_SCHEMA_SETUP.md)
- [문맥 기반 이미지 시스템](./CONTEXTUAL_IMAGE_SYSTEM.md)
- [시스템 준비 완료](./SYSTEM_READY.md)
