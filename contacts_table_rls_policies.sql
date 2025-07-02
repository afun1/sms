-- Enable RLS and set up policies for contacts table
-- Run this in Supabase SQL Editor after creating the table

-- Enable Row Level Security
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations for now (you can restrict this later)
CREATE POLICY "Allow all operations on contacts" ON contacts
FOR ALL USING (true) WITH CHECK (true);

-- Alternative: More restrictive policy (uncomment if you want to use this instead)
-- CREATE POLICY "Allow read access to contacts" ON contacts
-- FOR SELECT USING (true);

-- CREATE POLICY "Allow insert access to contacts" ON contacts  
-- FOR INSERT WITH CHECK (true);

-- CREATE POLICY "Allow update access to contacts" ON contacts
-- FOR UPDATE USING (true) WITH CHECK (true);

-- CREATE POLICY "Allow delete access to contacts" ON contacts
-- FOR DELETE USING (true);
