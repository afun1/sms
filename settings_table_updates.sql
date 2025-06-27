-- SQL to add new columns to the settings table
-- Run this in your Supabase SQL Editor

-- Add the new profile fields to the settings table
ALTER TABLE settings 
ADD COLUMN IF NOT EXISTS prefix VARCHAR(4),
ADD COLUMN IF NOT EXISTS middle_initial VARCHAR(1),
ADD COLUMN IF NOT EXISTS suffix VARCHAR(4),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS state VARCHAR(2),
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS website VARCHAR(255),
ADD COLUMN IF NOT EXISTS hot_link VARCHAR(255),
ADD COLUMN IF NOT EXISTS bio TEXT,
ADD COLUMN IF NOT EXISTS sparky_phone VARCHAR(16),
ADD COLUMN IF NOT EXISTS support VARCHAR(255);

-- Add comments to document the columns
COMMENT ON COLUMN settings.prefix IS 'User title prefix (Mr., Dr., etc.) - max 4 characters';
COMMENT ON COLUMN settings.middle_initial IS 'User middle initial - single character';
COMMENT ON COLUMN settings.suffix IS 'User name suffix (Jr., III, etc.) - max 4 characters';
COMMENT ON COLUMN settings.city IS 'User city location';
COMMENT ON COLUMN settings.state IS 'User state/province - 2 character code';
COMMENT ON COLUMN settings.country IS 'User country';
COMMENT ON COLUMN settings.website IS 'User website URL (without https://)';
COMMENT ON COLUMN settings.hot_link IS 'User special/promotional link (without https://)';
COMMENT ON COLUMN settings.bio IS 'User bio/description text - up to 500 characters';
COMMENT ON COLUMN settings.sparky_phone IS 'User Sparky phone number - up to 16 characters';
COMMENT ON COLUMN settings.support IS 'Support contact information or notes - up to 255 characters';

-- Verify the table structure
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' 
ORDER BY ordinal_position;
