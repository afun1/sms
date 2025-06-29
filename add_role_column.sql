-- Add role column to profiles table for role-based access control
-- Run this in your Supabase SQL editor

-- Add role column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'profiles' 
                   AND column_name = 'role') THEN
        ALTER TABLE profiles ADD COLUMN role TEXT DEFAULT 'user';
    END IF;
END $$;

-- Update existing user to admin for testing (replace with your actual user ID)
-- You can find your user ID in the auth.users table or from the browser console
UPDATE profiles 
SET role = 'admin' 
WHERE email = 'john@tpnlife.com';

-- Create some example roles for reference:
-- 'user' - Default role for regular users
-- 'manager' - Can access admin features
-- 'supervisor' - Can access admin features  
-- 'admin' - Full admin access

-- You can also set roles by user ID:
-- UPDATE profiles SET role = 'admin' WHERE id = 'your-user-id-here';

-- Check current roles:
-- SELECT id, email, display_name, role FROM profiles;
