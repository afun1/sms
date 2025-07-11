-- Fix Profile Creation Trigger for New Users
-- Run this in your Supabase SQL Editor to ensure profiles are created automatically

-- 1. Create or replace the profile creation function
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert a new profile when a user is created
    INSERT INTO public.profiles (
        id, 
        email, 
        first_name, 
        last_name, 
        display_name, 
        phone, 
        sparky_username,
        role,
        created_at,
        updated_at
    )
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'first_name', ''),
        COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
        COALESCE(
            NEW.raw_user_meta_data->>'display_name', 
            CONCAT(
                COALESCE(NEW.raw_user_meta_data->>'first_name', ''), 
                ' ', 
                COALESCE(NEW.raw_user_meta_data->>'last_name', '')
            ),
            NEW.email
        ),
        COALESCE(NEW.raw_user_meta_data->>'phone', ''),
        COALESCE(NEW.raw_user_meta_data->>'sparky_username', ''),
        'user',
        NOW(),
        NOW()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- 3. Create the trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- 4. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON public.profiles TO authenticated;

-- 5. Create a manual profile for the specific user (info@prosperityhighwayglobal.com)
-- Find the user ID first, then create the profile

-- Check if profile exists for this email
DO $$
DECLARE
    user_record RECORD;
    profile_exists BOOLEAN;
BEGIN
    -- Get user from auth.users
    SELECT id, email, raw_user_meta_data, created_at
    INTO user_record
    FROM auth.users 
    WHERE email = 'info@prosperityhighwayglobal.com';
    
    IF user_record.id IS NOT NULL THEN
        -- Check if profile already exists
        SELECT EXISTS(SELECT 1 FROM profiles WHERE id = user_record.id) INTO profile_exists;
        
        IF NOT profile_exists THEN
            -- Create the missing profile
            INSERT INTO public.profiles (
                id, 
                email, 
                first_name, 
                last_name, 
                display_name, 
                phone, 
                sparky_username,
                role,
                created_at,
                updated_at
            )
            VALUES (
                user_record.id,
                user_record.email,
                COALESCE(user_record.raw_user_meta_data->>'first_name', ''),
                COALESCE(user_record.raw_user_meta_data->>'last_name', ''),
                COALESCE(
                    user_record.raw_user_meta_data->>'display_name',
                    CONCAT(
                        COALESCE(user_record.raw_user_meta_data->>'first_name', ''), 
                        ' ', 
                        COALESCE(user_record.raw_user_meta_data->>'last_name', '')
                    ),
                    user_record.email
                ),
                COALESCE(user_record.raw_user_meta_data->>'phone', ''),
                COALESCE(user_record.raw_user_meta_data->>'sparky_username', ''),
                'user',
                user_record.created_at,
                NOW()
            );
            
            RAISE NOTICE 'Profile created for user: %', user_record.email;
        ELSE
            RAISE NOTICE 'Profile already exists for user: %', user_record.email;
        END IF;
    ELSE
        RAISE NOTICE 'User not found: info@prosperityhighwayglobal.com';
    END IF;
END $$;

-- 6. Verify the profile was created
SELECT 
    p.id,
    p.email,
    p.display_name,
    p.role,
    p.created_at
FROM profiles p
WHERE p.email = 'info@prosperityhighwayglobal.com';
