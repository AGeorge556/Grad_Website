-- Create recordings table
CREATE TABLE IF NOT EXISTS recordings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    title TEXT NOT NULL,
    duration INTEGER, -- Duration in seconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create index on user_id for faster queries
CREATE INDEX IF NOT EXISTS recordings_user_id_idx ON recordings(user_id);

-- Enable Row Level Security
ALTER TABLE recordings ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to view their own recordings
CREATE POLICY "Users can view their own recordings"
    ON recordings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own recordings
CREATE POLICY "Users can insert their own recordings"
    ON recordings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to update their own recordings
CREATE POLICY "Users can update their own recordings"
    ON recordings
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Create policy to allow users to delete their own recordings
CREATE POLICY "Users can delete their own recordings"
    ON recordings
    FOR DELETE
    USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_recordings_updated_at
    BEFORE UPDATE ON recordings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 