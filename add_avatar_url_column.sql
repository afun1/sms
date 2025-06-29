-- SQL to add avatar_url column to the settings table
-- Run this in your Supabase SQL Editor

-- Add the avatar_url column to the settings table
ALTER TABLE settings 
ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Add comment to document the column
COMMENT ON COLUMN settings.avatar_url IS 'User profile picture URL from Supabase Storage';

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' AND column_name = 'avatar_url';

-- Optional: View the updated table structure
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' 
ORDER BY ordinal_position;
