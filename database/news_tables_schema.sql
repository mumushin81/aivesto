-- 6대 뉴스 카테고리 Supabase 데이터베이스 스키마

-- ============================================================
-- 1. 거시경제(Macro) 뉴스 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS macro_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,  -- 'CPI', 'NFP', 'FOMC', 'GDP', 'PPI' 등
    actual NUMERIC,
    consensus NUMERIC,
    previous NUMERIC,
    impact TEXT CHECK (impact IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    affected_sectors JSONB,  -- ['TECH', 'GROWTH_STOCKS']
    signal TEXT,  -- 'TECH_GROWTH_SHORT_TERM_DOWN'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_macro_news_event_type ON macro_news(event_type);
CREATE INDEX idx_macro_news_created_at ON macro_news(created_at DESC);


-- ============================================================
-- 2. 실적(Earnings) 뉴스 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS earnings_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    quarter TEXT,  -- '2025 Q1'
    fiscal_year INTEGER,
    eps_actual NUMERIC,
    eps_consensus NUMERIC,
    revenue_actual NUMERIC,
    revenue_consensus NUMERIC,
    guidance TEXT CHECK (guidance IN ('UP', 'DOWN', 'MAINTAIN')),
    signal_strength TEXT CHECK (signal_strength IN ('WEAK', 'NEUTRAL', 'STRONG', 'VERY_STRONG')),
    signal TEXT,  -- 'STRONG_BUY', 'STRONG_SELL'
    expected_move TEXT,  -- '+3% avg'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_earnings_news_symbol ON earnings_news(symbol);
CREATE INDEX idx_earnings_news_created_at ON earnings_news(created_at DESC);


-- ============================================================
-- 3. 산업군(섹터) 뉴스 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS sector_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector TEXT NOT NULL,  -- 'SEMICONDUCTOR', 'AI', 'ENERGY', 'AUTOMOTIVE'
    event_type TEXT,  -- 'POLICY', 'COMMODITY_MOVE', 'SUPPLY_CHAIN'
    event_description TEXT,
    impact_level TEXT CHECK (impact_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    affected_stocks JSONB,  -- ['NVDA', 'AMD', 'INTC']
    signal TEXT,  -- 'SEMICONDUCTOR_RALLY'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sector_news_sector ON sector_news(sector);
CREATE INDEX idx_sector_news_created_at ON sector_news(created_at DESC);


-- ============================================================
-- 4. 기업 이슈(Corporate Events) 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS corporate_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- 'M&A', 'CEO_CHANGE', 'RECALL', 'LAWSUIT', 'INSIDER_TRADING'
    event_description TEXT,
    signal TEXT,  -- 'IMMEDIATE_SELL', 'SHORT_TERM_DOWN', 'MA_ANNOUNCEMENT'
    severity TEXT CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_corporate_events_symbol ON corporate_events(symbol);
CREATE INDEX idx_corporate_events_event_type ON corporate_events(event_type);
CREATE INDEX idx_corporate_events_created_at ON corporate_events(created_at DESC);


-- ============================================================
-- 5. AI/테크 트렌드 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS tech_trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trend_type TEXT NOT NULL,  -- 'AI_CHIP', 'GPU_DEMAND', 'PARTNERSHIP', 'NEW_MODEL'
    title TEXT,
    source TEXT,  -- 'TechCrunch', 'NVIDIA Blog', 'The Verge'
    companies JSONB,  -- ['NVDA', 'MSFT', 'GOOGL']
    signal TEXT,  -- 'NVDA_STRONG_BUY', 'US_AI_CHIP_RALLY'
    impact_score NUMERIC CHECK (impact_score BETWEEN 0 AND 100),
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_tech_trends_trend_type ON tech_trends(trend_type);
CREATE INDEX idx_tech_trends_impact_score ON tech_trends(impact_score DESC);
CREATE INDEX idx_tech_trends_created_at ON tech_trends(created_at DESC);


-- ============================================================
-- 6. 지정학적(Geopolitical) 뉴스 테이블
-- ============================================================
CREATE TABLE IF NOT EXISTS geopolitical_news (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region TEXT NOT NULL,  -- 'CHINA', 'MIDDLE_EAST', 'RUSSIA', 'EUROPE', 'GLOBAL'
    event_type TEXT NOT NULL,  -- 'WAR', 'SANCTIONS', 'ECONOMIC_DATA', 'CURRENCY', 'COMMODITY'
    event_description TEXT,
    affected_sectors JSONB,  -- ['TECH', 'ENERGY', 'DEFENSE']
    affected_stocks JSONB,  -- ['AAPL', 'TSLA', 'XOM']
    signal TEXT,  -- 'CHINA_MARKET_DOWN', 'OIL_SURGE_ENERGY_UP'
    impact_level TEXT CHECK (impact_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_geopolitical_news_region ON geopolitical_news(region);
CREATE INDEX idx_geopolitical_news_event_type ON geopolitical_news(event_type);
CREATE INDEX idx_geopolitical_news_created_at ON geopolitical_news(created_at DESC);


-- ============================================================
-- 통합 시그널 뷰 (All Signals Combined)
-- ============================================================
CREATE OR REPLACE VIEW all_trading_signals AS
SELECT
    'MACRO' AS signal_category,
    event_type AS event_name,
    signal,
    impact AS impact_level,
    affected_sectors AS affected_entities,
    created_at
FROM macro_news
WHERE signal IS NOT NULL

UNION ALL

SELECT
    'EARNINGS' AS signal_category,
    symbol AS event_name,
    signal,
    signal_strength AS impact_level,
    jsonb_build_array(symbol) AS affected_entities,
    created_at
FROM earnings_news
WHERE signal IS NOT NULL

UNION ALL

SELECT
    'SECTOR' AS signal_category,
    sector AS event_name,
    signal,
    impact_level,
    affected_stocks AS affected_entities,
    created_at
FROM sector_news
WHERE signal IS NOT NULL

UNION ALL

SELECT
    'CORPORATE' AS signal_category,
    symbol AS event_name,
    signal,
    severity AS impact_level,
    jsonb_build_array(symbol) AS affected_entities,
    created_at
FROM corporate_events
WHERE signal IS NOT NULL

UNION ALL

SELECT
    'TECH' AS signal_category,
    trend_type AS event_name,
    signal,
    CASE
        WHEN impact_score >= 80 THEN 'CRITICAL'
        WHEN impact_score >= 60 THEN 'HIGH'
        WHEN impact_score >= 40 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS impact_level,
    companies AS affected_entities,
    created_at
FROM tech_trends
WHERE signal IS NOT NULL

UNION ALL

SELECT
    'GEOPOLITICAL' AS signal_category,
    region AS event_name,
    signal,
    impact_level,
    affected_stocks AS affected_entities,
    created_at
FROM geopolitical_news
WHERE signal IS NOT NULL

ORDER BY created_at DESC;


-- ============================================================
-- Row Level Security (RLS) 정책
-- ============================================================

-- Macro News
ALTER TABLE macro_news ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON macro_news FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON macro_news FOR INSERT WITH CHECK (true);

-- Earnings News
ALTER TABLE earnings_news ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON earnings_news FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON earnings_news FOR INSERT WITH CHECK (true);

-- Sector News
ALTER TABLE sector_news ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON sector_news FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON sector_news FOR INSERT WITH CHECK (true);

-- Corporate Events
ALTER TABLE corporate_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON corporate_events FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON corporate_events FOR INSERT WITH CHECK (true);

-- Tech Trends
ALTER TABLE tech_trends ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON tech_trends FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON tech_trends FOR INSERT WITH CHECK (true);

-- Geopolitical News
ALTER TABLE geopolitical_news ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Enable read access for all users" ON geopolitical_news FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users" ON geopolitical_news FOR INSERT WITH CHECK (true);


-- ============================================================
-- 샘플 쿼리
-- ============================================================

-- 최근 24시간 HIGH/CRITICAL 시그널
-- SELECT * FROM all_trading_signals
-- WHERE impact_level IN ('HIGH', 'CRITICAL')
-- AND created_at >= NOW() - INTERVAL '24 hours'
-- ORDER BY created_at DESC;

-- 특정 종목에 영향을 주는 모든 시그널
-- SELECT * FROM all_trading_signals
-- WHERE affected_entities ? 'NVDA'
-- ORDER BY created_at DESC
-- LIMIT 20;

-- 섹터별 최근 시그널
-- SELECT signal_category, COUNT(*) as signal_count
-- FROM all_trading_signals
-- WHERE created_at >= NOW() - INTERVAL '7 days'
-- GROUP BY signal_category
-- ORDER BY signal_count DESC;
