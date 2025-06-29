-- Minimal script to add secondary_role column
-- Run this in Supabase SQL Editor

-- 1. Add the secondary_role column
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS secondary_role TEXT;

-- 2. Add constraint to ensure valid roles (optional but recommended)
ALTER TABLE profiles 
ADD CONSTRAINT valid_secondary_role 
CHECK (secondary_role IS NULL OR secondary_role IN ('user', 'manager', 'supervisor', 'admin'));

-- 3. Add constraint to prevent same primary and secondary role
ALTER TABLE profiles 
ADD CONSTRAINT different_roles 
CHECK (secondary_role IS NULL OR secondary_role != role);

-- 4. Update RLS policy to support dual roles
CREATE OR REPLACE FUNCTION user_has_role(user_id UUID, check_role TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles 
        WHERE id = user_id 
        AND (role = check_role OR secondary_role = check_role)
    );
END;
$$ LANGUAGE plpgsql;

-- 5. Update the RLS policy
DROP POLICY IF EXISTS "admin_supervisor_access" ON profiles;
DROP POLICY IF EXISTS "dual_role_admin_access" ON profiles;

CREATE POLICY "dual_role_admin_access" ON profiles
FOR ALL
TO authenticated
USING (
    user_has_role(auth.uid(), 'admin')
    OR 
    user_has_role(auth.uid(), 'supervisor')
    OR
    auth.uid() = id
);

-- Done! Now you can assign secondary roles to users
