-- Supabase RLS Policy for Hierarchical User Access
-- This allows admins and managers to impersonate users below them in hierarchy

-- Enable RLS on profiles table
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
FOR SELECT USING (auth.uid() = id);

-- Policy: Users can update their own profile  
CREATE POLICY "Users can update own profile" ON profiles
FOR UPDATE USING (auth.uid() = id);

-- Policy: Admins can view all profiles
CREATE POLICY "Admins can view all profiles" ON profiles
FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() 
    AND role IN ('admin', 'super_admin')
  )
);

-- Policy: Managers can view users in their organization
CREATE POLICY "Managers can view org users" ON profiles
FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM profiles manager
    WHERE manager.id = auth.uid() 
    AND manager.role = 'manager'
    AND manager.organization_id = profiles.organization_id
  )
);

-- Policy: Super admins can impersonate (act as) any user
CREATE POLICY "Super admins can impersonate users" ON profiles
FOR ALL USING (
  EXISTS (
    SELECT 1 FROM profiles 
    WHERE id = auth.uid() 
    AND role = 'super_admin'
  )
);

-- Function to switch user context (for impersonation)
CREATE OR REPLACE FUNCTION switch_user_context(target_user_id UUID)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  current_user_role TEXT;
  target_user_data JSON;
BEGIN
  -- Check if current user has permission to impersonate
  SELECT role INTO current_user_role 
  FROM profiles 
  WHERE id = auth.uid();
  
  IF current_user_role NOT IN ('admin', 'super_admin', 'manager') THEN
    RAISE EXCEPTION 'Insufficient permissions to impersonate users';
  END IF;
  
  -- Get target user data
  SELECT row_to_json(profiles.*) INTO target_user_data
  FROM profiles 
  WHERE id = target_user_id;
  
  IF target_user_data IS NULL THEN
    RAISE EXCEPTION 'Target user not found';
  END IF;
  
  -- Return user data for frontend impersonation
  RETURN target_user_data;
END;
$$;
