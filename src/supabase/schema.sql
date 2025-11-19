-- Supabase database schema for text documents and summaries

-- Create text_documents table
CREATE TABLE IF NOT EXISTS text_documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    filename TEXT NOT NULL,
    file_size BIGINT,
    storage_path TEXT NOT NULL,
    storage_url TEXT,
    original_language TEXT DEFAULT 'Korean',
    genre TEXT DEFAULT 'non_fiction',
    
    -- Summary fields
    summary_text TEXT,
    summary_language TEXT,
    summary_model TEXT,
    summary_created_at TIMESTAMPTZ,
    summary_tokens_used INTEGER,
    
    -- Chain of Thought summaries
    cod_iterations INTEGER DEFAULT 0,
    cod_summaries JSONB,
    missing_entities JSONB,
    
    -- YouTube script fields
    youtube_script TEXT,
    youtube_script_model TEXT,
    youtube_script_created_at TIMESTAMPTZ,
    youtube_script_tokens_used INTEGER,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for better query performance
CREATE INDEX idx_text_documents_title ON text_documents(title);
CREATE INDEX idx_text_documents_author ON text_documents(author);
CREATE INDEX idx_text_documents_genre ON text_documents(genre);
CREATE INDEX idx_text_documents_created_at ON text_documents(created_at DESC);

-- Create update trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_text_documents_updated_at BEFORE UPDATE
    ON text_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create summary_iterations table for tracking Chain of Density iterations
CREATE TABLE IF NOT EXISTS summary_iterations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES text_documents(id) ON DELETE CASCADE,
    iteration_number INTEGER NOT NULL,
    chunk_number INTEGER,
    summary_text TEXT NOT NULL,
    missing_entities TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(document_id, iteration_number, chunk_number)
);

-- Create processing_logs table for tracking processing status
CREATE TABLE IF NOT EXISTS processing_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES text_documents(id) ON DELETE CASCADE,
    process_type TEXT NOT NULL, -- 'upload', 'summary', 'youtube_script'
    status TEXT NOT NULL, -- 'started', 'completed', 'failed'
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    metadata JSONB
);

-- RLS (Row Level Security) policies
ALTER TABLE text_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE summary_iterations ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_logs ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust as needed)
CREATE POLICY "Enable all for authenticated users" ON text_documents
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON summary_iterations
    FOR ALL USING (true);

CREATE POLICY "Enable all for authenticated users" ON processing_logs
    FOR ALL USING (true);