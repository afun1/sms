-- Add hierarchical management columns to profiles table
-- Run this in your Supabase SQL editor

-- Add manager_id column (users assigned to managers)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'manager_id') THEN
        ALTER TABLE profiles ADD COLUMN manager_id UUID REFERENCES profiles(id);
        COMMENT ON COLUMN profiles.manager_id IS 'User assigned to this manager (for regular users)';
    END IF;
END $$;

-- Add supervisor_id column (managers assigned to supervisors)
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

-- Example hierarchy setup (uncomment and modify as needed):
-- 
-- -- Create some test users with different roles
-- INSERT INTO profiles (id, email, display_name, role) VALUES 
-- ('00000000-0000-0000-0000-000000000001', 'admin@company.com', 'Admin User', 'admin'),
-- ('00000000-0000-0000-0000-000000000002', 'supervisor@company.com', 'John Supervisor', 'supervisor'),
-- ('00000000-0000-0000-0000-000000000003', 'manager1@company.com', 'Jane Manager', 'manager'),
-- ('00000000-0000-0000-0000-000000000004', 'manager2@company.com', 'Bob Manager', 'manager'),
-- ('00000000-0000-0000-0000-000000000005', 'user1@company.com', 'Alice User', 'user'),
-- ('00000000-0000-0000-0000-000000000006', 'user2@company.com', 'Charlie User', 'user');
--
-- -- Assign managers to supervisor
-- UPDATE profiles SET supervisor_id = '00000000-0000-0000-0000-000000000002' 
-- WHERE id IN ('00000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000004');
--
-- -- Assign users to managers
-- UPDATE profiles SET manager_id = '00000000-0000-0000-0000-000000000003' 
-- WHERE id = '00000000-0000-0000-0000-000000000005';
-- UPDATE profiles SET manager_id = '00000000-0000-0000-0000-000000000004' 
-- WHERE id = '00000000-0000-0000-0000-000000000006';

-- View hierarchy query (useful for testing):
-- SELECT 
--     p.id,
--     p.email,
--     p.display_name,
--     p.role,
--     m.display_name as manager_name,
--     s.display_name as supervisor_name
-- FROM profiles p
-- LEFT JOIN profiles m ON p.manager_id = m.id
-- LEFT JOIN profiles s ON p.supervisor_id = s.id
-- ORDER BY p.role DESC, p.display_name;
