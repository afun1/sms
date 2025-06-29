-- Create message_templates table for SMS Editor
-- This table stores user-created SMS message templates

CREATE TABLE IF NOT EXISTS message_templates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    description TEXT,
    tags TEXT[], -- Array of tags for categorization
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_message_templates_user_id ON message_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_message_templates_created_at ON message_templates(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_message_templates_tags ON message_templates USING GIN(tags);

-- Enable Row Level Security (RLS)
ALTER TABLE message_templates ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see their own templates
CREATE POLICY "Users can view their own templates" ON message_templates
    FOR SELECT USING (auth.uid() = user_id);

-- Users can only insert their own templates
CREATE POLICY "Users can create their own templates" ON message_templates
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can only update their own templates
CREATE POLICY "Users can update their own templates" ON message_templates
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can only delete their own templates
CREATE POLICY "Users can delete their own templates" ON message_templates
    FOR DELETE USING (auth.uid() = user_id);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_message_templates_updated_at
    BEFORE UPDATE ON message_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE, DELETE ON message_templates TO authenticated;
GRANT USAGE ON SEQUENCE message_templates_id_seq TO authenticated;
