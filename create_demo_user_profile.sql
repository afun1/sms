-- Check if user already has a profile
SELECT id, email, first_name, last_name, role, column_preferences 
FROM profiles 
WHERE id = '29d0eb05-fb7f-425d-b734-25ab8d7d1d11';

-- If no profile exists, create one
INSERT INTO profiles (
    id, 
    email, 
    first_name, 
    last_name, 
    role,
    column_preferences
) VALUES (
    '29d0eb05-fb7f-425d-b734-25ab8d7d1d11',
    'john+4@tpnlife.com',
    'Test',
    'Manager',
    'manager',
    '{}'
) ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    first_name = EXCLUDED.first_name,
    last_name = EXCLUDED.last_name,
    role = EXCLUDED.role;

-- Verify the record
SELECT id, email, first_name, last_name, role, column_preferences 
FROM profiles 
WHERE id = '29d0eb05-fb7f-425d-b734-25ab8d7d1d11';
