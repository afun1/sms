-- SQL to set up assets bucket with proper user-based access control
-- Run this in your Supabase SQL Editor

-- Step 1: Create the assets bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'assets',
    'assets',
    false, -- Not public - requires authentication
    52428800, -- 50MB limit
    ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml', 'application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'video/mp4', 'video/quicktime', 'audio/mpeg', 'audio/wav']
)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    public = EXCLUDED.public,
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Step 2: Enable RLS on storage.objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Step 3: Create user roles table for hierarchical access
CREATE TABLE IF NOT EXISTS public.user_roles (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'manager', 'supervisor', 'admin')),
    manager_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    supervisor_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Step 4: Enable RLS on user_roles table
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;

-- Step 5: Create RLS policies for user_roles
DROP POLICY IF EXISTS "Users can view relevant roles" ON user_roles;
DROP POLICY IF EXISTS "Admins can manage all roles" ON user_roles;
DROP POLICY IF EXISTS "Managers can view their team roles" ON user_roles;

CREATE POLICY "Users can view relevant roles" ON user_roles
    FOR SELECT USING (
        auth.uid() = user_id OR 
        auth.uid() = manager_id OR 
        auth.uid() = supervisor_id OR
        EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "Admins can manage all roles" ON user_roles
    FOR ALL USING (
        EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "Managers can view their team roles" ON user_roles
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM user_roles WHERE user_id = auth.uid() AND role IN ('manager', 'supervisor') AND manager_id = auth.uid())
    );

-- Step 6: Create function to check if user can access another user's assets
CREATE OR REPLACE FUNCTION public.can_access_user_assets(target_user_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    current_user_id UUID;
    current_user_role VARCHAR(20);
    target_manager_id UUID;
    target_supervisor_id UUID;
BEGIN
    current_user_id := auth.uid();
    
    -- If it's the same user, allow access
    IF current_user_id = target_user_id THEN
        RETURN TRUE;
    END IF;
    
    -- Get current user's role
    SELECT role INTO current_user_role 
    FROM user_roles 
    WHERE user_id = current_user_id;
    
    -- Admins can access everything
    IF current_user_role = 'admin' THEN
        RETURN TRUE;
    END IF;
    
    -- Get target user's manager and supervisor
    SELECT manager_id, supervisor_id INTO target_manager_id, target_supervisor_id
    FROM user_roles 
    WHERE user_id = target_user_id;
    
    -- Check if current user is the manager or supervisor of target user
    IF current_user_id = target_manager_id OR current_user_id = target_supervisor_id THEN
        RETURN TRUE;
    END IF;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 7: Drop existing storage policies and create new ones
DROP POLICY IF EXISTS "Users can view own assets" ON storage.objects;
DROP POLICY IF EXISTS "Users can insert own assets" ON storage.objects;
DROP POLICY IF EXISTS "Users can update own assets" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete own assets" ON storage.objects;

-- Step 8: Create storage policies for assets bucket
CREATE POLICY "Users can view authorized assets" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'assets' AND
        (
            -- Extract user_id from the path (assuming format: user_id/filename)
            auth.uid()::text = split_part(name, '/', 1) OR
            public.can_access_user_assets(split_part(name, '/', 1)::UUID)
        )
    );

CREATE POLICY "Users can insert own assets" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'assets' AND
        auth.uid()::text = split_part(name, '/', 1)
    );

CREATE POLICY "Users can update own assets" ON storage.objects
    FOR UPDATE USING (
        bucket_id = 'assets' AND
        auth.uid()::text = split_part(name, '/', 1)
    );

CREATE POLICY "Users can delete authorized assets" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'assets' AND
        (
            auth.uid()::text = split_part(name, '/', 1) OR
            public.can_access_user_assets(split_part(name, '/', 1)::UUID)
        )
    );

-- Step 9: Create function to automatically assign user role when they first sign up
CREATE OR REPLACE FUNCTION public.handle_new_user_role() 
RETURNS TRIGGER AS $$
BEGIN
    -- Insert default user role for new users
    INSERT INTO public.user_roles (user_id, role, created_at, updated_at)
    VALUES (NEW.id, 'user', NOW(), NOW())
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 10: Create trigger for auto-role assignment
DROP TRIGGER IF EXISTS on_auth_user_role_created ON auth.users;
CREATE TRIGGER on_auth_user_role_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user_role();

-- Step 11: Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.user_roles TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_access_user_assets(UUID) TO authenticated;

-- Step 12: Insert sample roles (modify as needed for your organization)
-- This creates an admin user - replace with actual user email/ID
INSERT INTO public.user_roles (user_id, role, created_at, updated_at)
SELECT 
    id, 
    'admin', 
    NOW(), 
    NOW()
FROM auth.users 
WHERE email = 'admin@yourcompany.com' -- Replace with actual admin email
ON CONFLICT (user_id) DO UPDATE SET
    role = EXCLUDED.role,
    updated_at = EXCLUDED.updated_at;

-- Step 13: Create view for easy role management
CREATE OR REPLACE VIEW public.user_roles_with_details AS
SELECT 
    ur.id,
    ur.user_id,
    u.email as user_email,
    ur.role,
    ur.manager_id,
    m.email as manager_email,
    ur.supervisor_id,
    s.email as supervisor_email,
    ur.created_at,
    ur.updated_at
FROM public.user_roles ur
LEFT JOIN auth.users u ON ur.user_id = u.id
LEFT JOIN auth.users m ON ur.manager_id = m.id
LEFT JOIN auth.users s ON ur.supervisor_id = s.id;

-- Grant access to the view
GRANT SELECT ON public.user_roles_with_details TO authenticated;

-- Step 14: Verification queries
SELECT 'Assets bucket configuration:' as info;
SELECT id, name, public, file_size_limit FROM storage.buckets WHERE id = 'assets';

SELECT 'Storage policies for assets:' as info;
SELECT policyname, permissive, roles, cmd 
FROM pg_policies 
WHERE schemaname = 'storage' AND tablename = 'objects' AND policyname LIKE '%asset%';

SELECT 'User roles table structure:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'user_roles' 
ORDER BY ordinal_position;
