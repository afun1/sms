-- SQL to properly connect settings table with user profiles and auth
-- Run this in your Supabase SQL Editor

-- Step 1: Verify current foreign key relationships
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
    AND tc.table_name = 'settings';

-- Step 2: Add foreign key constraint if it doesn't exist
-- This ensures user_id in settings references auth.users(id)
DO $$
BEGIN
    -- Check if foreign key constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'settings' 
        AND constraint_type = 'FOREIGN KEY'
        AND constraint_name LIKE '%user_id%'
    ) THEN
        ALTER TABLE settings 
        ADD CONSTRAINT fk_settings_user_id 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Step 3: Ensure unique constraint on user_id (one settings record per user)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE table_name = 'settings' 
        AND constraint_type = 'UNIQUE'
        AND constraint_name LIKE '%user_id%'
    ) THEN
        ALTER TABLE settings 
        ADD CONSTRAINT unique_settings_user_id UNIQUE (user_id);
    END IF;
END $$;

-- Step 4: Create index for performance if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'settings' 
        AND indexname = 'idx_settings_user_id'
    ) THEN
        CREATE INDEX idx_settings_user_id ON settings(user_id);
    END IF;
END $$;

-- Step 5: Enable Row Level Security (RLS) if not already enabled
ALTER TABLE settings ENABLE ROW LEVEL SECURITY;

-- Step 6: Drop existing policies if they exist and recreate them
DROP POLICY IF EXISTS "Users can view own settings" ON settings;
DROP POLICY IF EXISTS "Users can insert own settings" ON settings;
DROP POLICY IF EXISTS "Users can update own settings" ON settings;
DROP POLICY IF EXISTS "Users can delete own settings" ON settings;

-- Step 7: Create comprehensive RLS policies
CREATE POLICY "Users can view own settings" ON settings
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON settings
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON settings
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own settings" ON settings
    FOR DELETE USING (auth.uid() = user_id);

-- Step 8: Create a function to automatically create settings record for new users
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.settings (user_id, created_at, updated_at)
    VALUES (new.id, now(), now());
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 9: Create trigger to auto-create settings when user signs up
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Step 10: Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.settings TO authenticated;

-- Step 11: Create a view that joins user auth data with settings (optional)
CREATE OR REPLACE VIEW user_profile_complete AS
SELECT 
    u.id as user_id,
    u.email as auth_email,
    u.created_at as user_created_at,
    s.id as settings_id,
    s.first_name,
    s.last_name,
    s.email as profile_email,
    s.phone,
    s.prefix,
    s.middle_initial,
    s.suffix,
    s.city,
    s.state,
    s.country,
    s.website,
    s.hot_link,
    s.bio,
    s.created_at as settings_created_at,
    s.updated_at as settings_updated_at
FROM auth.users u
LEFT JOIN public.settings s ON u.id = s.user_id;

-- Step 12: Grant access to the view
GRANT SELECT ON user_profile_complete TO authenticated;

-- Step 13: Verify the setup
SELECT 'Settings table constraints:' as info;
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'settings';

SELECT 'Settings table indexes:' as info;
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'settings';

SELECT 'Settings RLS policies:' as info;
SELECT policyname, permissive, roles, cmd 
FROM pg_policies 
WHERE tablename = 'settings';

-- Step 14: Test query to verify connection works
SELECT 'Test: Current user settings (should return empty if no settings yet):' as info;
SELECT * FROM settings WHERE user_id = auth.uid();
