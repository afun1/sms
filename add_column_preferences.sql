-- Add column_preferences column to profiles table
-- This will store user's column order and visibility preferences as JSON

-- Add the column_preferences column to the profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS column_preferences JSONB DEFAULT '{}';

-- Add a comment to document the column
COMMENT ON COLUMN profiles.column_preferences IS 'Stores user column preferences including order and visibility settings';

-- Create an index for better performance when querying column preferences
CREATE INDEX IF NOT EXISTS idx_profiles_column_preferences 
ON profiles USING GIN (column_preferences);

-- Example of what the column_preferences JSON structure looks like:
-- {
--   "column_order": ["contact_id", "assignee", "first_name", "last_name", "email", "phone", "city", "state"],
--   "column_visibility": {
--     "contact_id": true,
--     "assignee": true,
--     "first_name": true,
--     "last_name": true,
--     "email": true,
--     "phone": true,
--     "city": false,
--     "state": true
--   },
--   "updated_at": "2025-07-11T10:30:00.000Z"
-- }

-- Verify the column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'profiles' AND column_name = 'column_preferences';

-- Optional: Check current profiles table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'profiles'
ORDER BY ordinal_position;
