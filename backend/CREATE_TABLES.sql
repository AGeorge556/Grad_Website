-- SQL Commands to Create Missing Tables
-- Run these commands in your Supabase SQL Editor
-- Go to: https://app.supabase.com/project/YOUR_PROJECT_ID/sql

-- 1. Create topics table
CREATE TABLE IF NOT EXISTS topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  image_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create user_topics table for tracking user progress
CREATE TABLE IF NOT EXISTS user_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  is_favorite BOOLEAN DEFAULT FALSE,
  progress INTEGER DEFAULT 0,
  last_accessed TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, topic_id)
);

-- 3. Create space_topics table for organizing topics within spaces
CREATE TABLE IF NOT EXISTS space_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  space_id UUID REFERENCES spaces(id) ON DELETE CASCADE,
  topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
  position INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(space_id, topic_id)
);

-- 4. Insert some sample topics
INSERT INTO topics (title, description, image_url) 
SELECT 'Machine Learning', 'Learn about AI and machine learning fundamentals', 'https://source.unsplash.com/random/800x600?machine+learning'
WHERE NOT EXISTS (SELECT 1 FROM topics WHERE title = 'Machine Learning');

INSERT INTO topics (title, description, image_url) 
SELECT 'Web Development', 'Master modern web development technologies', 'https://source.unsplash.com/random/800x600?coding'
WHERE NOT EXISTS (SELECT 1 FROM topics WHERE title = 'Web Development');

INSERT INTO topics (title, description, image_url) 
SELECT 'Data Science', 'Explore data analysis and visualization', 'https://source.unsplash.com/random/800x600?data'
WHERE NOT EXISTS (SELECT 1 FROM topics WHERE title = 'Data Science');

INSERT INTO topics (title, description, image_url) 
SELECT 'Cybersecurity', 'Learn about network security and ethical hacking', 'https://source.unsplash.com/random/800x600?security'
WHERE NOT EXISTS (SELECT 1 FROM topics WHERE title = 'Cybersecurity');

-- 5. Create trigger function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$ language 'plpgsql';

-- 6. Add triggers to update timestamps automatically
CREATE TRIGGER update_topics_updated_at
  BEFORE UPDATE ON topics
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_topics_updated_at
  BEFORE UPDATE ON user_topics
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- 7. Enable Row Level Security (RLS) for the tables
ALTER TABLE topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE space_topics ENABLE ROW LEVEL SECURITY;

-- 8. Create RLS policies for topics (public read access)
CREATE POLICY "Topics are publicly readable" ON topics
  FOR SELECT USING (true);

CREATE POLICY "Topics are publicly writable" ON topics
  FOR ALL USING (true);

-- 9. Create RLS policies for user_topics (user can only access their own data)
CREATE POLICY "Users can view their own topics" ON user_topics
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own topics" ON user_topics
  FOR ALL USING (auth.uid() = user_id);

-- 10. Create RLS policies for space_topics (user can only access topics in their spaces)
CREATE POLICY "Users can view topics in their spaces" ON space_topics
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM spaces 
      WHERE spaces.id = space_topics.space_id 
      AND spaces.user_id = auth.uid()
    )
  );

CREATE POLICY "Users can manage topics in their spaces" ON space_topics
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM spaces 
      WHERE spaces.id = space_topics.space_id 
      AND spaces.user_id = auth.uid()
    )
  ); 