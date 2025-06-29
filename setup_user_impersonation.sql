-- User Impersonation System Database Setup
-- Run this in your Supabase SQL editor to ensure proper database support

-- 1. Ensure profiles table has required columns for impersonation
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS first_name TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS last_name TEXT;
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user';
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS secondary_role TEXT;

-- 2. Create index for better performance on user searches
CREATE INDEX IF NOT EXISTS idx_profiles_search ON profiles (first_name, last_name, email, role);

-- 3. Create function to update display_name automatically
CREATE OR REPLACE FUNCTION update_display_name()
RETURNS TRIGGER AS $$
BEGIN
    -- Auto-generate display_name if not provided
    IF NEW.display_name IS NULL OR NEW.display_name = '' THEN
        NEW.display_name := COALESCE(
            NULLIF(TRIM(CONCAT(NEW.first_name, ' ', NEW.last_name)), ''),
            NEW.email
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Create trigger to automatically update display_name
DROP TRIGGER IF EXISTS trigger_update_display_name ON profiles;
CREATE TRIGGER trigger_update_display_name
    BEFORE INSERT OR UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_display_name();

-- 5. Create impersonation log table for audit trail
CREATE TABLE IF NOT EXISTS impersonation_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    admin_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    impersonated_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    admin_email TEXT NOT NULL,
    impersonated_email TEXT NOT NULL,
    session_start TIMESTAMPTZ DEFAULT NOW(),
    session_end TIMESTAMPTZ,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Enable RLS on impersonation logs
ALTER TABLE impersonation_logs ENABLE ROW LEVEL SECURITY;

-- 7. Create RLS policy for impersonation logs (admins only)
DROP POLICY IF EXISTS "Admins can view impersonation logs" ON impersonation_logs;
CREATE POLICY "Admins can view impersonation logs" ON impersonation_logs
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND (role = 'admin' OR secondary_role = 'admin')
        )
    );

-- 8. Create function to log impersonation start
CREATE OR REPLACE FUNCTION log_impersonation_start(
    p_impersonated_user_id UUID,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_admin_user_id UUID;
    v_admin_email TEXT;
    v_impersonated_email TEXT;
    v_log_id UUID;
BEGIN
    -- Get current admin user info
    v_admin_user_id := auth.uid();
    
    SELECT email INTO v_admin_email 
    FROM auth.users 
    WHERE id = v_admin_user_id;
    
    SELECT email INTO v_impersonated_email 
    FROM auth.users 
    WHERE id = p_impersonated_user_id;
    
    -- Insert log record
    INSERT INTO impersonation_logs (
        admin_user_id,
        impersonated_user_id,
        admin_email,
        impersonated_email,
        ip_address,
        user_agent
    ) VALUES (
        v_admin_user_id,
        p_impersonated_user_id,
        v_admin_email,
        v_impersonated_email,
        p_ip_address::INET,
        p_user_agent
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Create function to log impersonation end
CREATE OR REPLACE FUNCTION log_impersonation_end(p_log_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE impersonation_logs 
    SET session_end = NOW()
    WHERE id = p_log_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. Create view for easy impersonation reporting
CREATE OR REPLACE VIEW impersonation_report AS
SELECT 
    il.id,
    il.admin_email,
    il.impersonated_email,
    ap.first_name || ' ' || ap.last_name AS admin_name,
    ip.first_name || ' ' || ip.last_name AS impersonated_name,
    ap.role AS admin_role,
    ip.role AS impersonated_role,
    il.session_start,
    il.session_end,
    CASE 
        WHEN il.session_end IS NULL THEN 'Active'
        ELSE 'Completed'
    END AS session_status,
    CASE 
        WHEN il.session_end IS NOT NULL THEN 
            EXTRACT(EPOCH FROM (il.session_end - il.session_start)) / 60
        ELSE 
            EXTRACT(EPOCH FROM (NOW() - il.session_start)) / 60
    END AS duration_minutes,
    il.ip_address,
    il.created_at
FROM impersonation_logs il
LEFT JOIN profiles ap ON ap.id = il.admin_user_id
LEFT JOIN profiles ip ON ip.id = il.impersonated_user_id
ORDER BY il.created_at DESC;

-- 11. Grant permissions
GRANT SELECT ON impersonation_report TO authenticated;
GRANT EXECUTE ON FUNCTION log_impersonation_start(UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION log_impersonation_end(UUID) TO authenticated;

-- 12. Update existing users to have display names
UPDATE profiles 
SET display_name = COALESCE(
    NULLIF(TRIM(CONCAT(first_name, ' ', last_name)), ''),
    email
)
WHERE display_name IS NULL OR display_name = '';

-- 13. Create sample admin user (modify as needed)
-- This creates an admin user - replace with your actual admin email
INSERT INTO profiles (
    id,
    email,
    first_name,
    last_name,
    role,
    display_name,
    created_at,
    updated_at
)
SELECT 
    u.id,
    u.email,
    'Admin',
    'User',
    'admin',
    'Admin User',
    NOW(),
    NOW()
FROM auth.users u
WHERE u.email = 'admin@yourcompany.com'  -- Replace with your admin email
ON CONFLICT (id) DO UPDATE SET
    role = EXCLUDED.role,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    display_name = EXCLUDED.display_name,
    updated_at = EXCLUDED.updated_at;

-- 14. Verify setup
DO $$
DECLARE
    profile_count INTEGER;
    admin_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO profile_count FROM profiles;
    SELECT COUNT(*) INTO admin_count FROM profiles WHERE role = 'admin' OR secondary_role = 'admin';
    
    RAISE NOTICE 'Setup completed successfully!';
    RAISE NOTICE 'Total profiles: %', profile_count;
    RAISE NOTICE 'Admin users: %', admin_count;
    RAISE NOTICE 'Impersonation system is ready to use.';
END $$;

-- Example queries for testing:

-- View all users available for impersonation
-- SELECT id, display_name, email, role, secondary_role FROM profiles ORDER BY display_name;

-- View impersonation history
-- SELECT * FROM impersonation_report LIMIT 10;

-- Check current admin users
-- SELECT * FROM profiles WHERE role = 'admin' OR secondary_role = 'admin';

-- Manual impersonation log entry (for testing)
-- SELECT log_impersonation_start('target-user-id-here'::UUID);
