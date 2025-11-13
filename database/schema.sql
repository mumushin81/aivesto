-- Supabase 데이터베이스 스키마
-- 이 파일을 Supabase SQL Editor에서 실행하세요

-- 1. 원본 뉴스 테이블 (24시간 TTL)
CREATE TABLE IF NOT EXISTS news_raw (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  content TEXT,
  published_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  symbols TEXT[],
  metadata JSONB
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_news_raw_created_at ON news_raw(created_at);
CREATE INDEX IF NOT EXISTS idx_news_raw_symbols ON news_raw USING GIN(symbols);
CREATE INDEX IF NOT EXISTS idx_news_raw_url ON news_raw(url);

-- 24시간 자동 삭제 함수
CREATE OR REPLACE FUNCTION delete_old_news()
RETURNS void AS $$
BEGIN
  DELETE FROM news_raw
  WHERE created_at < NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql;

-- 매시간 자동 실행 (pg_cron 필요)
-- SELECT cron.schedule('cleanup-old-news', '0 * * * *', 'SELECT delete_old_news()');

-- 2. 분석된 뉴스 테이블
CREATE TABLE IF NOT EXISTS analyzed_news (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  raw_news_id UUID REFERENCES news_raw(id) ON DELETE CASCADE,
  relevance_score INTEGER CHECK (relevance_score BETWEEN 0 AND 100),
  affected_symbols TEXT[] NOT NULL,
  price_impact TEXT CHECK (price_impact IN ('up', 'down', 'neutral')),
  importance TEXT CHECK (importance IN ('high', 'medium', 'low')),
  analysis JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_analyzed_news_score ON analyzed_news(relevance_score);
CREATE INDEX IF NOT EXISTS idx_analyzed_news_symbols ON analyzed_news USING GIN(affected_symbols);
CREATE INDEX IF NOT EXISTS idx_analyzed_news_importance ON analyzed_news(importance);
CREATE INDEX IF NOT EXISTS idx_analyzed_news_created ON analyzed_news(created_at);

-- 3. 발행된 블로그 글 테이블
CREATE TABLE IF NOT EXISTS published_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  analyzed_news_ids UUID[],
  wordpress_id INTEGER,
  published_at TIMESTAMPTZ,
  views INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  metadata JSONB
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_published_articles_created ON published_articles(created_at);
CREATE INDEX IF NOT EXISTS idx_published_articles_published ON published_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_published_articles_wordpress ON published_articles(wordpress_id);

-- 4. 통계 뷰 (선택적)
CREATE OR REPLACE VIEW news_statistics AS
SELECT
  DATE(created_at) as date,
  source,
  COUNT(*) as news_count,
  COUNT(DISTINCT url) as unique_news
FROM news_raw
GROUP BY DATE(created_at), source
ORDER BY date DESC, news_count DESC;

-- 5. 인기 종목 통계 뷰
CREATE OR REPLACE VIEW popular_symbols AS
SELECT
  UNNEST(affected_symbols) as symbol,
  COUNT(*) as mention_count,
  AVG(relevance_score) as avg_score,
  COUNT(CASE WHEN price_impact = 'up' THEN 1 END) as bullish_count,
  COUNT(CASE WHEN price_impact = 'down' THEN 1 END) as bearish_count
FROM analyzed_news
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY symbol
ORDER BY mention_count DESC
LIMIT 50;

-- Row Level Security (RLS) 설정 (선택적)
ALTER TABLE news_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE analyzed_news ENABLE ROW LEVEL SECURITY;
ALTER TABLE published_articles ENABLE ROW LEVEL SECURITY;

-- 익명 사용자 읽기 권한 (API 키로 제어)
CREATE POLICY "Enable read access for all users" ON news_raw FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON analyzed_news FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON published_articles FOR SELECT USING (true);

-- 서비스 역할 전체 권한
CREATE POLICY "Enable all for service role" ON news_raw FOR ALL USING (true);
CREATE POLICY "Enable all for service role" ON analyzed_news FOR ALL USING (true);
CREATE POLICY "Enable all for service role" ON published_articles FOR ALL USING (true);

-- 완료 메시지
DO $$
BEGIN
  RAISE NOTICE 'Database schema created successfully!';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. Enable pg_cron extension for automated cleanup';
  RAISE NOTICE '2. Configure your .env file with Supabase credentials';
  RAISE NOTICE '3. Run the Python collectors to start gathering news';
END $$;
