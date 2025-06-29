-- Add support for dual roles in the profiles table
-- This script adds a secondary_role column and updates the role handling

-- Add secondary_role column to profiles table
ALTER TABLE profiles 
ADD COLUMN secondary_role TEXT;

-- Add a check constraint to ensure valid roles
ALTER TABLE profiles 
ADD CONSTRAINT valid_primary_role 
CHECK (role IN ('user', 'manager', 'supervisor', 'admin'));

ALTER TABLE profiles 
ADD CONSTRAINT valid_secondary_role 
CHECK (secondary_role IS NULL OR secondary_role IN ('user', 'manager', 'supervisor', 'admin'));

-- Add a constraint to ensure secondary role is different from primary role
ALTER TABLE profiles 
ADD CONSTRAINT different_roles 
CHECK (secondary_role IS NULL OR secondary_role != role);

-- Create a function to get all roles for a user (for easier querying)
CREATE OR REPLACE FUNCTION get_user_roles(user_id UUID)
RETURNS TEXT[] AS $$
DECLARE
    user_roles TEXT[] := '{}';
    primary_role TEXT;
    secondary_role TEXT;
BEGIN
    SELECT role, secondary_role INTO primary_role, secondary_role
    FROM profiles 
    WHERE id = user_id;
    
    IF primary_role IS NOT NULL THEN
        user_roles := array_append(user_roles, primary_role);
    END IF;
    
    IF secondary_role IS NOT NULL THEN
        user_roles := array_append(user_roles, secondary_role);
    END IF;
    
    RETURN user_roles;
END;
$$ LANGUAGE plpgsql;

-- Create a function to check if user has a specific role (primary or secondary)
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

-- Update RLS policies to account for dual roles
-- Drop existing policies
DROP POLICY IF EXISTS "admin_supervisor_access" ON profiles;

-- Create new policy for dual role access
CREATE POLICY "dual_role_admin_access" ON profiles
FOR ALL
TO authenticated
USING (
    -- Allow if user is admin (primary or secondary)
    user_has_role(auth.uid(), 'admin')
    OR 
    -- Allow if user is supervisor (primary or secondary)
    user_has_role(auth.uid(), 'supervisor')
    OR
    -- Allow users to see their own profile
    auth.uid() = id
);

-- Example usage and test data
-- Update some existing users to have dual roles
-- UPDATE profiles SET secondary_role = 'admin' WHERE role = 'supervisor' AND email LIKE '%john+1%';
-- UPDATE profiles SET secondary_role = 'supervisor' WHERE role = 'manager' AND email LIKE '%john+2%';

-- Comments for reference:
-- Common dual role combinations:
-- 1. supervisor + admin: Senior supervisors with admin privileges
-- 2. manager + supervisor: Managers who also supervise other managers
-- 3. manager + admin: Department heads with admin access
-- 4. user + manager: Regular users who manage small teams
