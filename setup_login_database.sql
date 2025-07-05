-- Complete setup script for login system database
-- Run this in your Supabase SQL editor

-- 1. Create profiles table if it doesn't exist
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT DEFAULT '',
    last_name TEXT DEFAULT '',
    display_name TEXT DEFAULT '',
    phone TEXT DEFAULT '',
    sparky_username TEXT DEFAULT '',
    role TEXT DEFAULT 'user',
    secondary_role TEXT DEFAULT NULL,
    organization_id UUID DEFAULT NULL,
    manager_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    supervisor_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    avatar_url TEXT DEFAULT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 3. Create trigger for updated_at
DROP TRIGGER IF EXISTS update_profiles_updated_at ON profiles;
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Enable RLS (Row Level Security)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- 5. Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can update all profiles" ON profiles;
DROP POLICY IF EXISTS "Admins can insert profiles" ON profiles;
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON profiles;

-- 6. Create RLS policies
-- Allow users to view their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

-- Allow users to update their own profile  
CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);

-- Allow users to insert their own profile
CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Allow admin users to view all profiles
CREATE POLICY "Admins can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'supervisor', 'manager')
        )
    );

-- Allow admin users to update all profiles
CREATE POLICY "Admins can update all profiles" ON profiles
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'supervisor')
        )
    );

-- Allow admin users to insert profiles
CREATE POLICY "Admins can insert profiles" ON profiles
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'supervisor')
        )
    );

-- 7. Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);
CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role);
CREATE INDEX IF NOT EXISTS idx_profiles_manager_id ON profiles(manager_id);
CREATE INDEX IF NOT EXISTS idx_profiles_supervisor_id ON profiles(supervisor_id);
CREATE INDEX IF NOT EXISTS idx_profiles_organization_id ON profiles(organization_id);
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles(created_at);

-- 8. Create function to handle user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, first_name, last_name, display_name, phone, sparky_username)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'first_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email),
        COALESCE(NEW.raw_user_meta_data->>'phone', ''),
        COALESCE(NEW.raw_user_meta_data->>'sparky_username', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Create trigger for new user creation
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 10. Insert default admin user (uncomment and modify as needed)
-- INSERT INTO auth.users (id, email, encrypted_password, email_confirmed_at, created_at, updated_at, raw_user_meta_data, aud, role)
-- VALUES (
--     gen_random_uuid(),
--     'admin@example.com',
--     crypt('admin123', gen_salt('bf')),
--     NOW(),
--     NOW(),
--     NOW(),
--     '{"first_name": "Admin", "last_name": "User", "display_name": "Admin User"}',
--     'authenticated',
--     'authenticated'
-- );

-- 11. Create some sample users for testing (uncomment as needed)
-- DO $$
-- DECLARE
--     admin_id UUID := gen_random_uuid();
--     manager_id UUID := gen_random_uuid();
--     user_id UUID := gen_random_uuid();
-- BEGIN
--     -- Insert directly into profiles table for testing
--     INSERT INTO profiles (id, email, first_name, last_name, display_name, role) VALUES
--         (admin_id, 'admin@test.com', 'Admin', 'User', 'Admin User', 'admin'),
--         (manager_id, 'manager@test.com', 'Manager', 'User', 'Manager User', 'manager'),
--         (user_id, 'user@test.com', 'Regular', 'User', 'Regular User', 'user');
-- END $$;

-- 12. Grant necessary permissions
GRANT ALL ON profiles TO authenticated;
GRANT ALL ON profiles TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO anon;

-- 13. Create view for user management (optional)
CREATE OR REPLACE VIEW user_management AS
SELECT 
    p.id,
    p.email,
    p.first_name,
    p.last_name,
    p.display_name,
    p.phone,
    p.sparky_username,
    p.role,
    p.secondary_role,
    p.is_active,
    p.created_at,
    p.updated_at,
    COALESCE(m.display_name, m.email) as manager_name,
    COALESCE(s.display_name, s.email) as supervisor_name
FROM profiles p
LEFT JOIN profiles m ON p.manager_id = m.id
LEFT JOIN profiles s ON p.supervisor_id = s.id
ORDER BY p.role, p.created_at DESC;

-- 14. Create function to get user hierarchy
CREATE OR REPLACE FUNCTION get_user_hierarchy(user_id UUID)
RETURNS TABLE(
    level INTEGER,
    id UUID,
    email TEXT,
    display_name TEXT,
    role TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE hierarchy AS (
        -- Base case: start with the given user
        SELECT 1 as level, p.id, p.email, p.display_name, p.role
        FROM profiles p
        WHERE p.id = user_id
        
        UNION ALL
        
        -- Recursive case: get subordinates
        SELECT h.level + 1, p.id, p.email, p.display_name, p.role
        FROM profiles p
        JOIN hierarchy h ON (p.manager_id = h.id OR p.supervisor_id = h.id)
        WHERE h.level < 10  -- Prevent infinite recursion
    )
    SELECT * FROM hierarchy ORDER BY level, display_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 15. Final verification query
SELECT 
    'Profiles table created' as status,
    COUNT(*) as profile_count,
    COUNT(CASE WHEN role = 'admin' THEN 1 END) as admin_count,
    COUNT(CASE WHEN role = 'manager' THEN 1 END) as manager_count,
    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_count
FROM profiles;

-- Success message
SELECT 'Database setup complete! You can now use the login system.' as message;
