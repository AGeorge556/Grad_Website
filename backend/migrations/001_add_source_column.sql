-- Add source column to videos table
ALTER TABLE videos
ADD COLUMN source TEXT NOT NULL DEFAULT 'file';
 
-- Add a check constraint to ensure source is either 'file' or 'youtube'
ALTER TABLE videos
ADD CONSTRAINT check_source_type
CHECK (source IN ('file', 'youtube')); 