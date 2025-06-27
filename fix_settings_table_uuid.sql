-- SQL to fix the settings table ID column type mismatch
-- Run this in your Supabase SQL Editor BEFORE adding the new columns

-- IMPORTANT: This fixes the ID type mismatch between profiles (UUID) and settings (int8)
-- Profiles table uses UUID, but settings table was created with int8

-- Step 1: Check current table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' 
ORDER BY ordinal_position;

-- Step 2: Drop the settings table if it exists (since we need to recreate with proper UUID)
-- WARNING: This will delete all existing settings data!
DROP TABLE IF EXISTS settings;

-- Step 3: Create the settings table with proper UUID for user_id to match profiles
CREATE TABLE settings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    prefix VARCHAR(4),
    middle_initial VARCHAR(1),
    suffix VARCHAR(4),
    city VARCHAR(100),
    state VARCHAR(2),
    country VARCHAR(100),
    website VARCHAR(255),
    hot_link VARCHAR(255),
    bio TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 4: Add comments to document the columns
COMMENT ON TABLE settings IS 'User profile settings and template variables';
COMMENT ON COLUMN settings.id IS 'Primary key - UUID';
COMMENT ON COLUMN settings.user_id IS 'Foreign key to auth.users - UUID';
COMMENT ON COLUMN settings.first_name IS 'User first name';
COMMENT ON COLUMN settings.last_name IS 'User last name';
COMMENT ON COLUMN settings.email IS 'User email address';
COMMENT ON COLUMN settings.phone IS 'User phone number';
COMMENT ON COLUMN settings.prefix IS 'User title prefix (Mr., Dr., etc.) - max 4 characters';
COMMENT ON COLUMN settings.middle_initial IS 'User middle initial - single character';
COMMENT ON COLUMN settings.suffix IS 'User name suffix (Jr., III, etc.) - max 4 characters';
COMMENT ON COLUMN settings.city IS 'User city location';
COMMENT ON COLUMN settings.state IS 'User state/province - 2 character code';
COMMENT ON COLUMN settings.country IS 'User country';
COMMENT ON COLUMN settings.website IS 'User website URL (without https://)';
COMMENT ON COLUMN settings.hot_link IS 'User special/promotional link (without https://)';
COMMENT ON COLUMN settings.bio IS 'User bio/description text - up to 500 characters';

-- Step 5: Create index for faster lookups
CREATE INDEX idx_settings_user_id ON settings(user_id);

-- Step 6: Enable Row Level Security (RLS)
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Step 7: Create RLS policies so users can only access their own settings
CREATE POLICY "Users can view own settings" ON settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON settings
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own settings" ON settings
    FOR DELETE USING (auth.uid() = user_id);

-- Step 8: Verify the final table structure
SELECT column_name, data_type, character_maximum_length, is_nullable
FROM information_schema.columns 
WHERE table_name = 'settings' 
ORDER BY ordinal_position;
