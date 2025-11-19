-- Supabase schema for Midjourney→Blog image pipeline
-- Run with: supabase db push --file database/midjourney_blog_schema.sql

-- Storage bucket
select storage.create_bucket('blog-images', public := true, file_size_limit := 5242880); -- 5MB limit per object

-- Images table
create table if not exists public.images (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  topic text not null,
  prompt text not null,
  image_url text not null,
  created_at timestamptz not null default now()
);

-- Blog placements (FK optional to external article id)
create table if not exists public.blog_images (
  article_id text not null,
  image_id uuid not null references public.images(id) on delete cascade,
  position integer not null default 0,
  created_at timestamptz not null default now(),
  constraint blog_images_pk primary key (article_id, image_id)
);

-- Helpful index for symbol/topic queries
create index if not exists idx_images_symbol_created on public.images(symbol, created_at desc);
create index if not exists idx_blog_images_article on public.blog_images(article_id, position);
