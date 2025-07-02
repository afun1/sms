-- Add DND (Do Not Disturb) columns and Assignee column to contacts table
-- Execute this SQL in your Supabase SQL editor

-- Add SMS DND column (for SMS do not disturb flag)
ALTER TABLE contacts 
ADD COLUMN sms VARCHAR(10) DEFAULT '';

-- Add Call DND column (for Call do not disturb flag)
ALTER TABLE contacts 
ADD COLUMN call VARCHAR(10) DEFAULT '';

-- Add Email DND column (for Email do not disturb flag)  
ALTER TABLE contacts 
ADD COLUMN email_flag VARCHAR(10) DEFAULT '';

-- Add Assignee column (for user assignment)
ALTER TABLE contacts 
ADD COLUMN assignee VARCHAR(255) DEFAULT '';

-- Add comments to document the new columns
COMMENT ON COLUMN contacts.sms IS 'SMS Do Not Disturb flag - X means do not send SMS';
COMMENT ON COLUMN contacts.call IS 'Call Do Not Disturb flag - X means do not call';
COMMENT ON COLUMN contacts.email_flag IS 'Email Do Not Disturb flag - X means do not send email';
COMMENT ON COLUMN contacts.assignee IS 'Name of the user assigned to this contact';

-- Create indexes for better performance on commonly filtered columns
CREATE INDEX IF NOT EXISTS idx_contacts_sms ON contacts(sms);
CREATE INDEX IF NOT EXISTS idx_contacts_call ON contacts(call);
CREATE INDEX IF NOT EXISTS idx_contacts_email_flag ON contacts(email_flag);
CREATE INDEX IF NOT EXISTS idx_contacts_assignee ON contacts(assignee);

-- Optional: Create a composite index for DND filtering
CREATE INDEX IF NOT EXISTS idx_contacts_dnd_flags ON contacts(sms, call, email_flag);

-- Show the updated table structure
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'contacts' 
ORDER BY ordinal_position;
