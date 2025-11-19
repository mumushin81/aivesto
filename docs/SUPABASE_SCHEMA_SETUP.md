# Supabase 스키마 설정 가이드

## 🎯 목표
Midjourney 이미지를 저장할 Supabase 데이터베이스 스키마 생성

---

## 방법 1: Supabase Dashboard에서 직접 실행 (추천)

### 1단계: Supabase Dashboard 접속
```
https://supabase.com/dashboard/project/czubqsnahmtdsmnyawlk
```

### 2단계: SQL Editor 열기
1. 좌측 메뉴에서 **"SQL Editor"** 클릭
2. **"New query"** 클릭

### 3단계: SQL 복사 및 실행

다음 SQL을 복사하여 붙여넣고 **"Run"** 클릭:

```sql
-- Supabase schema for Midjourney→Blog image pipeline

-- Storage bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit)
VALUES ('blog-images', 'blog-images', true, 5242880)
ON CONFLICT (id) DO NOTHING;

-- Images table
CREATE TABLE IF NOT EXISTS public.images (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  symbol text NOT NULL,
  topic text NOT NULL,
  prompt text NOT NULL,
  image_url text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- Blog placements (FK optional to external article id)
CREATE TABLE IF NOT EXISTS public.blog_images (
  article_id text NOT NULL,
  image_id uuid NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
  position integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT blog_images_pk PRIMARY KEY (article_id, image_id)
);

-- Helpful indexes for symbol/topic queries
CREATE INDEX IF NOT EXISTS idx_images_symbol_created ON public.images(symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_blog_images_article ON public.blog_images(article_id, position);

-- Enable Row Level Security (RLS)
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.blog_images ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access
CREATE POLICY "Enable read access for all users" ON public.images
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.images
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON public.blog_images
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.blog_images
  FOR INSERT WITH CHECK (true);
```

### 4단계: 실행 결과 확인

성공 메시지가 표시되면:
```
✓ Success. No rows returned
```

---

## 방법 2: Python 스크립트로 실행

```bash
python3 /Users/jinxin/dev/aivesto/scripts/setup_supabase_schema.py
```

---

## 📊 생성되는 구조

### Storage Bucket
- **이름**: `blog-images`
- **Public**: ✅ (Public URL 생성 가능)
- **파일 크기 제한**: 5MB

### Tables

#### 1. `images` 테이블
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary Key (자동 생성) |
| symbol | text | 주식 심볼 (NVDA, TSLA, etc.) |
| topic | text | 주제 (blackwell_chip, robotaxi, etc.) |
| prompt | text | Midjourney 프롬프트 |
| image_url | text | Supabase Storage Public URL |
| created_at | timestamptz | 생성 시간 |

#### 2. `blog_images` 테이블
| Column | Type | Description |
|--------|------|-------------|
| article_id | text | 기사 ID (PK) |
| image_id | uuid | images 테이블 FK (PK) |
| position | integer | 이미지 위치 |
| created_at | timestamptz | 생성 시간 |

---

## ✅ 확인 방법

### Supabase Dashboard에서 확인
1. **Table Editor** 클릭
2. `images`와 `blog_images` 테이블 확인
3. **Storage** → `blog-images` 버킷 확인

### Python으로 확인
```python
from supabase import create_client

url = "https://czubqsnahmtdsmnyawlk.supabase.co"
key = "your_anon_key"

supabase = create_client(url, key)

# 테이블 확인
result = supabase.table('images').select("*").limit(1).execute()
print("✅ images 테이블 작동 중")

result = supabase.table('blog_images').select("*").limit(1).execute()
print("✅ blog_images 테이블 작동 중")
```

---

## 🔧 문제 해결

### "permission denied" 오류
→ Supabase Service Role Key 필요 (Settings → API)

### "relation does not exist" 오류
→ SQL Editor에서 스키마를 다시 실행

### Storage 버킷 생성 실패
→ Dashboard → Storage → "New bucket" 수동 생성

---

## 📍 다음 단계

1. ✅ Supabase 스키마 생성 완료
2. ⏭️ Discord 봇 테스트 실행
3. ⏭️ Midjourney 이미지 생성 테스트
4. ⏭️ 블로그 자동 업데이트 확인
