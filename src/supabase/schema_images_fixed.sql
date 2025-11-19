-- Fixed schema for book images functionality (avoiding duplicate columns)

-- Create book_images table
CREATE TABLE IF NOT EXISTS book_images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES text_documents(id) ON DELETE CASCADE,
    
    -- Storage information
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    
    -- Image properties
    width INTEGER,
    height INTEGER,
    file_size BIGINT,
    content_type TEXT DEFAULT 'image/png',
    
    -- Classification
    image_type TEXT DEFAULT 'book_cover',
    variation_number INTEGER DEFAULT 1,
    is_primary BOOLEAN DEFAULT false,
    
    -- Generation information
    generation_model TEXT DEFAULT 'qwen/qwen-image',
    generation_time FLOAT,
    prompt_text TEXT,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    
    -- Constraints
    UNIQUE(document_id, image_type, variation_number)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_book_images_document_id ON book_images(document_id);
CREATE INDEX IF NOT EXISTS idx_book_images_type ON book_images(image_type);
CREATE INDEX IF NOT EXISTS idx_book_images_primary ON book_images(is_primary) WHERE is_primary = true;
CREATE INDEX IF NOT EXISTS idx_book_images_created_at ON book_images(created_at DESC);

-- Check if columns exist before adding them (safe approach)
DO $$ 
BEGIN
    -- Add image_ids column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'text_documents' AND column_name = 'image_ids') THEN
        ALTER TABLE text_documents ADD COLUMN image_ids UUID[];
    END IF;
    
    -- Add primary_image_id column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'text_documents' AND column_name = 'primary_image_id') THEN
        ALTER TABLE text_documents ADD COLUMN primary_image_id UUID;
    END IF;
    
    -- Add has_images column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'text_documents' AND column_name = 'has_images') THEN
        ALTER TABLE text_documents ADD COLUMN has_images BOOLEAN DEFAULT false;
    END IF;
END $$;

-- Add foreign key constraint for primary_image_id (if not already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'text_documents' 
        AND constraint_name = 'text_documents_primary_image_id_fkey'
    ) THEN
        ALTER TABLE text_documents 
        ADD CONSTRAINT text_documents_primary_image_id_fkey 
        FOREIGN KEY (primary_image_id) REFERENCES book_images(id);
    END IF;
END $$;

-- Create indexes for image lookups
CREATE INDEX IF NOT EXISTS idx_text_documents_primary_image ON text_documents(primary_image_id);
CREATE INDEX IF NOT EXISTS idx_text_documents_has_images ON text_documents(has_images) WHERE has_images = true;

-- RLS (Row Level Security) policies for book_images
ALTER TABLE book_images ENABLE ROW LEVEL SECURITY;

-- Drop existing policy if it exists, then create new one
DROP POLICY IF EXISTS "Allow all operations on book_images" ON book_images;
CREATE POLICY "Allow all operations on book_images" ON book_images
    FOR ALL USING (true);

-- Function to automatically set is_primary for first image
CREATE OR REPLACE FUNCTION set_primary_image_trigger()
RETURNS TRIGGER AS $$
BEGIN
    -- If this is the first image for a document, mark it as primary
    IF NOT EXISTS (
        SELECT 1 FROM book_images 
        WHERE document_id = NEW.document_id 
        AND id != NEW.id
    ) THEN
        NEW.is_primary = true;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for auto-setting primary image
DROP TRIGGER IF EXISTS trigger_set_primary_image ON book_images;
CREATE TRIGGER trigger_set_primary_image
    BEFORE INSERT ON book_images
    FOR EACH ROW
    EXECUTE FUNCTION set_primary_image_trigger();

-- Function to update document when images are added/removed
CREATE OR REPLACE FUNCTION update_document_images()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the text_documents table with current image information
    IF TG_OP = 'INSERT' THEN
        -- Add image to document's image_ids array
        UPDATE text_documents 
        SET 
            image_ids = COALESCE(image_ids, ARRAY[]::UUID[]) || NEW.id,
            has_images = true,
            primary_image_id = CASE 
                WHEN primary_image_id IS NULL AND NEW.is_primary 
                THEN NEW.id 
                ELSE primary_image_id 
            END
        WHERE id = NEW.document_id;
        
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        -- Remove image from document's image_ids array
        UPDATE text_documents 
        SET 
            image_ids = array_remove(COALESCE(image_ids, ARRAY[]::UUID[]), OLD.id),
            has_images = CASE 
                WHEN array_remove(COALESCE(image_ids, ARRAY[]::UUID[]), OLD.id) = ARRAY[]::UUID[]
                THEN false 
                ELSE true 
            END,
            primary_image_id = CASE 
                WHEN primary_image_id = OLD.id 
                THEN (SELECT id FROM book_images WHERE document_id = OLD.document_id AND id != OLD.id LIMIT 1)
                ELSE primary_image_id 
            END
        WHERE id = OLD.document_id;
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for maintaining document image references
DROP TRIGGER IF EXISTS trigger_update_document_images_insert ON book_images;
CREATE TRIGGER trigger_update_document_images_insert
    AFTER INSERT ON book_images
    FOR EACH ROW
    EXECUTE FUNCTION update_document_images();

DROP TRIGGER IF EXISTS trigger_update_document_images_delete ON book_images;
CREATE TRIGGER trigger_update_document_images_delete
    AFTER DELETE ON book_images
    FOR EACH ROW
    EXECUTE FUNCTION update_document_images();

-- View for easy access to documents with their primary images
CREATE OR REPLACE VIEW documents_with_images AS
SELECT 
    d.*,
    i.id as primary_image_db_id,
    i.public_url as primary_image_url,
    i.width as primary_image_width,
    i.height as primary_image_height,
    i.storage_path as primary_image_path,
    (SELECT COUNT(*) FROM book_images WHERE document_id = d.id) as total_images
FROM text_documents d
LEFT JOIN book_images i ON d.primary_image_id = i.id;

-- Create storage bucket for images (if using SQL)
-- Note: This might not work in all Supabase setups, bucket creation is usually done via dashboard
-- INSERT INTO storage.buckets (id, name, public) VALUES ('book-images', 'book-images', true) ON CONFLICT DO NOTHING;