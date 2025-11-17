-- Extended schema for contextual Midjourney blog images
-- Apply with: supabase db push --file database/article_images_schema.sql

-- Storage bucket (idempotent)
-- Note: If bucket already exists, this will return an error but won't affect table creation
insert into storage.buckets (id, name, public, file_size_limit)
values ('blog-images', 'blog-images', true, 10485760)
on conflict (id) do nothing;

-- Images metadata
create table if not exists public.images (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  topic text not null,
  prompt text not null,
  image_url text not null,
  section_title text,
  context_keywords text[],
  image_type text, -- hero, diagram, chart, comparison, closeup, business, concept
  caption text,
  created_at timestamptz not null default now()
);

-- Article sections with linkage to chosen image
create table if not exists public.article_sections (
  id uuid primary key default gen_random_uuid(),
  article_id text not null,
  section_index integer not null,
  section_title text not null,
  content_excerpt text,
  keywords text[],
  image_id uuid references public.images(id) on delete set null,
  created_at timestamptz not null default now()
);

-- Placements (allows multiple images per article)
create table if not exists public.blog_images (
  article_id text not null,
  image_id uuid not null references public.images(id) on delete cascade,
  position integer not null default 0,
  section_index integer,
  created_at timestamptz not null default now(),
  constraint blog_images_pk primary key (article_id, image_id)
);

create index if not exists idx_images_symbol_created on public.images(symbol, created_at desc);
create index if not exists idx_blog_images_article on public.blog_images(article_id, position);
create index if not exists idx_article_sections_article on public.article_sections(article_id, section_index);
