-- Add additional user profile columns to profiles table
-- Run this in your Supabase SQL editor

-- Add first_name column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'first_name') THEN
        ALTER TABLE profiles ADD COLUMN first_name TEXT;
        COMMENT ON COLUMN profiles.first_name IS 'User first name';
    END IF;
END $$;

-- Add last_name column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'last_name') THEN
        ALTER TABLE profiles ADD COLUMN last_name TEXT;
        COMMENT ON COLUMN profiles.last_name IS 'User last name';
    END IF;
END $$;

-- Add phone column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'phone') THEN
        ALTER TABLE profiles ADD COLUMN phone TEXT;
        COMMENT ON COLUMN profiles.phone IS 'User phone number';
    END IF;
END $$;

-- Add sparky_username column
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'sparky_username') THEN
        ALTER TABLE profiles ADD COLUMN sparky_username TEXT;
        COMMENT ON COLUMN profiles.sparky_username IS 'Sparky AI username';
    END IF;
END $$;

-- Check if role column exists (it should from previous setup)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'role') THEN
        ALTER TABLE profiles ADD COLUMN role TEXT DEFAULT 'user';
        COMMENT ON COLUMN profiles.role IS 'User role (user, manager, supervisor, admin)';
    END IF;
END $$;

-- Add manager_id column (if not exists from previous setup)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'manager_id') THEN
        ALTER TABLE profiles ADD COLUMN manager_id UUID REFERENCES profiles(id);
        COMMENT ON COLUMN profiles.manager_id IS 'User assigned to this manager (for regular users)';
    END IF;
END $$;

-- Add supervisor_id column (if not exists from previous setup)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'supervisor_id') THEN
        ALTER TABLE profiles ADD COLUMN supervisor_id UUID REFERENCES profiles(id);
        COMMENT ON COLUMN profiles.supervisor_id IS 'Manager assigned to this supervisor (for managers)';
    END IF;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_manager_id ON profiles(manager_id);
CREATE INDEX IF NOT EXISTS idx_profiles_supervisor_id ON profiles(supervisor_id);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

-- Update existing users with sample data (optional - uncomment if needed)
-- UPDATE profiles SET 
--     first_name = split_part(display_name, ' ', 1),
--     last_name = split_part(display_name, ' ', 2)
-- WHERE display_name IS NOT NULL AND display_name != '';

-- View complete user hierarchy (useful for testing)
-- SELECT 
--     p.id,
--     p.first_name,
--     p.last_name,
--     p.email,
--     p.phone,
--     p.sparky_username,
--     p.role,
--     CONCAT(m.first_name, ' ', m.last_name) as manager_name,
--     CONCAT(s.first_name, ' ', s.last_name) as supervisor_name
-- FROM profiles p
-- LEFT JOIN profiles m ON p.manager_id = m.id
-- LEFT JOIN profiles s ON p.supervisor_id = s.id
-- ORDER BY 
--     CASE p.role 
--         WHEN 'admin' THEN 1 
--         WHEN 'supervisor' THEN 2 
--         WHEN 'manager' THEN 3 
--         ELSE 4 
--     END,
--     p.last_name, p.first_name;
