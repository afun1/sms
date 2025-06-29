-- Supervisor Password Fix SQL Script

-- 1. First, check the supervisor account status
SELECT 
    id,
    email,
    email_confirmed_at,
    phone_confirmed_at,
    confirmed_at,
    created_at,
    updated_at,
    last_sign_in_at
FROM auth.users 
WHERE email LIKE '%supervisor%' OR email LIKE '%john+4%';

-- 2. Check the supervisor's profile data
SELECT 
    id,
    email,
    first_name,
    last_name,
    role,
    secondary_role,
    created_at
FROM profiles 
WHERE role = 'supervisor' OR email LIKE '%supervisor%' OR email LIKE '%john+4%';

-- 3. Check what relationships depend on this supervisor
SELECT 
    'manager relationships' as relationship_type,
    COUNT(*) as count
FROM profiles 
WHERE supervisor_id IN (
    SELECT id FROM profiles WHERE role = 'supervisor'
)

UNION ALL

SELECT 
    'direct user relationships' as relationship_type,
    COUNT(*) as count
FROM profiles 
WHERE manager_id IN (
    SELECT id FROM profiles WHERE role = 'supervisor'
);

-- 4. If you need to confirm the email (run this if email_confirmed_at is NULL)
-- UPDATE auth.users 
-- SET 
--     email_confirmed_at = NOW(),
--     confirmed_at = NOW()
-- WHERE email = 'your-supervisor-email@domain.com';

-- 5. Check for any auth-related issues
SELECT 
    u.id,
    u.email,
    u.email_confirmed_at,
    p.first_name,
    p.last_name,
    p.role
FROM auth.users u
LEFT JOIN profiles p ON u.id = p.id
WHERE u.email LIKE '%supervisor%' OR u.email LIKE '%john+4%';
