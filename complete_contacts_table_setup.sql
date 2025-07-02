-- Complete contacts table setup with all required columns
-- Execute this SQL in your Supabase SQL editor to ensure all columns exist

-- First, create the table if it doesn't exist (with integer ID for simplicity)
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    
    -- DND flags (SMS, Call, Email columns expected by HTML)
    sms VARCHAR(10) DEFAULT '',
    call VARCHAR(10) DEFAULT '', 
    email_flag VARCHAR(10) DEFAULT '',
    
    -- Assignment column
    assignee VARCHAR(255) DEFAULT '',
    
    -- Sponsor information
    sponsor TEXT DEFAULT '',
    sponsor_first TEXT DEFAULT '',
    sponsor_last TEXT DEFAULT '',
    
    -- User and contact details
    user_id TEXT DEFAULT '',
    first_name TEXT DEFAULT '',
    last_name TEXT DEFAULT '',
    email TEXT DEFAULT '',
    valid TEXT DEFAULT '', -- This maps to email_valid but HTML expects 'valid'
    phone TEXT DEFAULT '',
    
    -- Address information
    address TEXT DEFAULT '',
    city TEXT DEFAULT '',
    state TEXT DEFAULT '',
    zip TEXT DEFAULT '',
    
    -- Technical details
    ip_address TEXT DEFAULT '',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timezone TEXT DEFAULT '',
    
    -- Phone type information
    cell BOOLEAN DEFAULT NULL,
    carrier TEXT DEFAULT '',
    landline BOOLEAN DEFAULT NULL,
    voip BOOLEAN DEFAULT NULL,
    other_phone BOOLEAN DEFAULT NULL,
    foreign_number BOOLEAN DEFAULT NULL,
    country TEXT DEFAULT 'US',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add missing columns if they don't exist (for existing tables)
DO $$
BEGIN
    -- Add SMS column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='sms') THEN
        ALTER TABLE contacts ADD COLUMN sms VARCHAR(10) DEFAULT '';
    END IF;
    
    -- Add Call column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='call') THEN
        ALTER TABLE contacts ADD COLUMN call VARCHAR(10) DEFAULT '';
    END IF;
    
    -- Add Email flag column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='email_flag') THEN
        ALTER TABLE contacts ADD COLUMN email_flag VARCHAR(10) DEFAULT '';
    END IF;
    
    -- Add Assignee column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='assignee') THEN
        ALTER TABLE contacts ADD COLUMN assignee VARCHAR(255) DEFAULT '';
    END IF;
    
    -- Add valid column if missing (HTML expects 'valid', not 'email_valid')
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='valid') THEN
        ALTER TABLE contacts ADD COLUMN valid TEXT DEFAULT '';
    END IF;
    
    -- Ensure all other expected columns exist with default values
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='sponsor') THEN
        ALTER TABLE contacts ADD COLUMN sponsor TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='sponsor_first') THEN
        ALTER TABLE contacts ADD COLUMN sponsor_first TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='sponsor_last') THEN
        ALTER TABLE contacts ADD COLUMN sponsor_last TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='user_id') THEN
        ALTER TABLE contacts ADD COLUMN user_id TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='first_name') THEN
        ALTER TABLE contacts ADD COLUMN first_name TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='last_name') THEN
        ALTER TABLE contacts ADD COLUMN last_name TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='email') THEN
        ALTER TABLE contacts ADD COLUMN email TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='phone') THEN
        ALTER TABLE contacts ADD COLUMN phone TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='address') THEN
        ALTER TABLE contacts ADD COLUMN address TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='city') THEN
        ALTER TABLE contacts ADD COLUMN city TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='state') THEN
        ALTER TABLE contacts ADD COLUMN state TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='zip') THEN
        ALTER TABLE contacts ADD COLUMN zip TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='ip_address') THEN
        ALTER TABLE contacts ADD COLUMN ip_address TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='timezone') THEN
        ALTER TABLE contacts ADD COLUMN timezone TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='carrier') THEN
        ALTER TABLE contacts ADD COLUMN carrier TEXT DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='contacts' AND column_name='country') THEN
        ALTER TABLE contacts ADD COLUMN country TEXT DEFAULT 'US';
    END IF;
    
END$$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contacts_sms ON contacts(sms);
CREATE INDEX IF NOT EXISTS idx_contacts_call ON contacts(call);
CREATE INDEX IF NOT EXISTS idx_contacts_email_flag ON contacts(email_flag);
CREATE INDEX IF NOT EXISTS idx_contacts_assignee ON contacts(assignee);
CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);

-- Insert sample data if table is empty
INSERT INTO contacts (
    sms, call, email_flag, assignee, sponsor, sponsor_first, sponsor_last, 
    user_id, first_name, last_name, email, valid, phone, 
    address, city, state, zip, ip_address, timezone, 
    cell, carrier, landline, voip, other_phone, foreign_number, country
) 
SELECT '', '', '', '', 'John Doe', 'John', 'Doe', 'user001', 'Alice', 'Smith', 
       'alice@example.com', 'Yes', '555-0101', '123 Main St', 'Anytown', 'CA', '90210', 
       '192.168.1.1', 'PST', true, 'Verizon', false, false, false, false, 'US'
WHERE NOT EXISTS (SELECT 1 FROM contacts LIMIT 1);

INSERT INTO contacts (
    sms, call, email_flag, assignee, sponsor, sponsor_first, sponsor_last, 
    user_id, first_name, last_name, email, valid, phone, 
    address, city, state, zip, ip_address, timezone, 
    cell, carrier, landline, voip, other_phone, foreign_number, country
) 
SELECT '', '', '', '', 'Jane Wilson', 'Jane', 'Wilson', 'user002', 'Bob', 'Johnson', 
       'bob@example.com', 'Yes', '555-0102', '456 Oak Ave', 'Another City', 'TX', '75001', 
       '192.168.1.2', 'CST', true, 'AT&T', false, false, false, false, 'US'
WHERE (SELECT COUNT(*) FROM contacts) < 2;

INSERT INTO contacts (
    sms, call, email_flag, assignee, sponsor, sponsor_first, sponsor_last, 
    user_id, first_name, last_name, email, valid, phone, 
    address, city, state, zip, ip_address, timezone, 
    cell, carrier, landline, voip, other_phone, foreign_number, country
) 
SELECT '', '', '', '', 'Mike Davis', 'Mike', 'Davis', 'user003', 'Carol', 'Brown', 
       'carol@example.com', 'Yes', '555-0103', '789 Pine Rd', 'Third City', 'NY', '10001', 
       '192.168.1.3', 'EST', false, 'T-Mobile', true, false, false, false, 'US'
WHERE (SELECT COUNT(*) FROM contacts) < 3;

-- Show the final table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'contacts' 
ORDER BY ordinal_position;

-- Show sample data
SELECT id, first_name, last_name, email, phone, city, state, assignee, sms, call, email_flag
FROM contacts 
LIMIT 3;
