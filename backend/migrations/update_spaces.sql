-- Drop existing table and related objects if they exist
DROP TABLE IF EXISTS spaces CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Create spaces table
CREATE TABLE spaces (
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
CREATE INDEX spaces_user_id_idx ON spaces(user_id);
CREATE INDEX spaces_created_at_idx ON spaces(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
CREATE TRIGGER update_spaces_updated_at
    BEFORE UPDATE ON spaces
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Service role bypass" ON spaces;
DROP POLICY IF EXISTS "Users can view their own spaces" ON spaces;
DROP POLICY IF EXISTS "Users can create their own spaces" ON spaces;
DROP POLICY IF EXISTS "Users can update their own spaces" ON spaces;
DROP POLICY IF EXISTS "Users can delete their own spaces" ON spaces;

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

-- Grant necessary permissions
GRANT ALL ON spaces TO service_role;
GRANT ALL ON spaces TO postgres;
GRANT ALL ON spaces TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;

-- Verify the setup
DO $$
BEGIN
    -- Check if table exists
    IF NOT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'spaces'
    ) THEN
        RAISE EXCEPTION 'Table spaces was not created successfully';
    END IF;

    -- Check if RLS is enabled
    IF NOT EXISTS (
        SELECT FROM pg_class 
        WHERE relname = 'spaces' 
        AND relrowsecurity = true
    ) THEN
        RAISE EXCEPTION 'RLS is not enabled on spaces table';
    END IF;

    -- Check if all policies exist
    IF (
        SELECT COUNT(*) 
        FROM pg_policies 
        WHERE tablename = 'spaces'
    ) != 5 THEN
        RAISE EXCEPTION 'Not all policies were created successfully';
    END IF;

    -- Check if trigger exists
    IF NOT EXISTS (
        SELECT FROM pg_trigger 
        WHERE tgname = 'update_spaces_updated_at'
    ) THEN
        RAISE EXCEPTION 'Trigger was not created successfully';
    END IF;

    RAISE NOTICE 'All checks passed successfully!';
END $$; 