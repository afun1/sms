-- SQL to add Sparky Phone and Support columns to the settings table
-- Run this in your Supabase SQL Editor

-- Add the new Sparky Phone, Support, and Sparky Username columns
ALTER TABLE settings 
ADD COLUMN IF NOT EXISTS sparky_phone VARCHAR(16),
ADD COLUMN IF NOT EXISTS support VARCHAR(255),
ADD COLUMN IF NOT EXISTS sparky_username VARCHAR(50);

-- Add comments to document the new columns
COMMENT ON COLUMN settings.sparky_phone IS 'Sparky callback phone number - up to 16 characters';
COMMENT ON COLUMN settings.support IS 'Live support link or contact information - up to 255 characters';
COMMENT ON COLUMN settings.sparky_username IS 'Sparky username - up to 50 characters';

-- Verify the table structure (optional check)
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' 
AND column_name IN ('sparky_phone', 'support', 'sparky_username')
ORDER BY ordinal_position;
