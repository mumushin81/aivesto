-- magic_book 호환용 midjourney_images 테이블 생성 (완전한 스키마)
-- aivesto Supabase에 적용

CREATE TABLE IF NOT EXISTS public.midjourney_images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    image_id TEXT UNIQUE NOT NULL,  -- 고유 이미지 ID (해시 기반)

    -- 프롬프트 정보
    prompt TEXT NOT NULL,

    -- 저장 정보
    original_url TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,

    -- 이미지 속성
    width INTEGER,
    height INTEGER,
    file_size BIGINT,
    format TEXT DEFAULT 'png',

    -- 크롭된 이미지 정보 (JSON 배열)
    cropped_images JSONB DEFAULT '[]',

    -- 생성 정보
    generation_model TEXT DEFAULT 'midjourney',
    generated_at TIMESTAMPTZ DEFAULT NOW(),

    -- 추가 메타데이터
    metadata JSONB DEFAULT '{}',

    -- 크롭 관련 컬럼
    parent_image_id TEXT,
    image_type TEXT DEFAULT 'original', -- 'original' or 'cropped'
    crop_position TEXT, -- 'top_left', 'top_right', 'bottom_left', 'bottom_right'
    crop_number INTEGER, -- 1, 2, 3, 4

    -- 타임스탬프
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_midjourney_images_image_id ON public.midjourney_images(image_id);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_prompt ON public.midjourney_images(prompt);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_created_at ON public.midjourney_images(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_generated_at ON public.midjourney_images(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_parent_id ON public.midjourney_images(parent_image_id);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_type ON public.midjourney_images(image_type);
CREATE INDEX IF NOT EXISTS idx_midjourney_images_crop_position ON public.midjourney_images(crop_position);

-- 외래 키 제약조건 추가 (CASCADE 삭제 지원)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'fk_midjourney_images_parent'
    ) THEN
        ALTER TABLE public.midjourney_images
        ADD CONSTRAINT fk_midjourney_images_parent
        FOREIGN KEY (parent_image_id)
        REFERENCES public.midjourney_images(image_id)
        ON DELETE CASCADE;
    END IF;
END $$;

-- RLS 활성화
ALTER TABLE public.midjourney_images ENABLE ROW LEVEL SECURITY;

-- Public 접근 정책
CREATE POLICY "Public read access for midjourney_images"
ON public.midjourney_images
FOR SELECT
TO public
USING (true);

CREATE POLICY "Public insert access for midjourney_images"
ON public.midjourney_images
FOR INSERT
TO public
WITH CHECK (true);

CREATE POLICY "Public update access for midjourney_images"
ON public.midjourney_images
FOR UPDATE
TO public
USING (true)
WITH CHECK (true);

-- 원본 이미지와 크롭된 이미지들을 함께 조회하기 위한 뷰 생성
CREATE OR REPLACE VIEW public.midjourney_image_groups AS
SELECT
    o.id as original_id,
    o.image_id as original_image_id,
    o.prompt,
    o.original_url,
    o.public_url as original_public_url,
    o.width as original_width,
    o.height as original_height,
    o.file_size as original_file_size,
    o.generated_at,
    o.metadata,
    json_agg(
        json_build_object(
            'id', c.id,
            'image_id', c.image_id,
            'crop_position', c.crop_position,
            'crop_number', c.crop_number,
            'public_url', c.public_url,
            'storage_path', c.storage_path,
            'width', c.width,
            'height', c.height,
            'file_size', c.file_size
        ) ORDER BY c.crop_number
    ) FILTER (WHERE c.id IS NOT NULL) as cropped_images
FROM public.midjourney_images o
LEFT JOIN public.midjourney_images c ON c.parent_image_id = o.image_id AND c.image_type = 'cropped'
WHERE o.image_type = 'original'
GROUP BY o.id, o.image_id, o.prompt, o.original_url, o.public_url,
         o.width, o.height, o.file_size, o.generated_at, o.metadata;

-- 테이블 및 컬럼 설명
COMMENT ON TABLE public.midjourney_images IS 'Midjourney 생성 이미지 및 메타데이터 저장';
COMMENT ON COLUMN public.midjourney_images.image_id IS '고유 이미지 ID (타임스탬프 + 파일명 해시)';
COMMENT ON COLUMN public.midjourney_images.cropped_images IS '크롭된 이미지 정보 배열: [{position, url, storage_path}, ...]';
COMMENT ON COLUMN public.midjourney_images.parent_image_id IS '원본 이미지 ID (크롭된 이미지인 경우)';
COMMENT ON COLUMN public.midjourney_images.image_type IS '이미지 타입: original 또는 cropped';
COMMENT ON COLUMN public.midjourney_images.crop_position IS '크롭 위치: top_left, top_right, bottom_left, bottom_right';
COMMENT ON COLUMN public.midjourney_images.crop_number IS '크롭 번호: 1, 2, 3, 4';
