-- Check if john@tpnlife.com exists in auth users
SELECT id, email FROM auth.users WHERE email = 'john@tpnlife.com';

-- Check if john@tpnlife.com has a profile
SELECT id, email, first_name, last_name, role, column_preferences 
FROM profiles 
WHERE email = 'john@tpnlife.com';
