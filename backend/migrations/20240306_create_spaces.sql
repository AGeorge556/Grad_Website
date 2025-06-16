-- Create spaces table
CREATE TABLE IF NOT EXISTS spaces (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Enable Row Level Security
ALTER TABLE spaces ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX IF NOT EXISTS spaces_user_id_idx ON spaces(user_id);
CREATE INDEX IF NOT EXISTS spaces_created_at_idx ON spaces(created_at);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_spaces_updated_at
    BEFORE UPDATE ON spaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create RLS policies
-- Allow service role to bypass RLS
CREATE POLICY "Service role bypass"
    ON spaces
    FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role')
    WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Allow users to view their own spaces
CREATE POLICY "Users can view their own spaces"
    ON spaces
    FOR SELECT
    USING (auth.uid() = user_id);

-- Allow users to insert their own spaces
CREATE POLICY "Users can create their own spaces"
    ON spaces
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Allow users to update their own spaces
CREATE POLICY "Users can update their own spaces"
    ON spaces
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Allow users to delete their own spaces
CREATE POLICY "Users can delete their own spaces"
    ON spaces
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add comment to table
COMMENT ON TABLE spaces IS 'Stores user learning spaces with RLS policies for data isolation'; 