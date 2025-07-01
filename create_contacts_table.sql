-- Create contacts table for storing contact information
-- This table supports all columns defined in the list.html interface

CREATE TABLE IF NOT EXISTS contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Sponsor information
    sponsor TEXT,
    sponsor_first TEXT,
    sponsor_last TEXT,
    
    -- User and contact details
    user_id TEXT,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    email_valid BOOLEAN DEFAULT NULL,
    phone TEXT,
    
    -- Address information
    address TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    
    -- Status and rating
    status TEXT,
    rating TEXT,
    
    -- Technical details
    ip_address TEXT,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    timezone TEXT,
    
    -- Phone type information
    cell BOOLEAN DEFAULT NULL,
    carrier TEXT,
    landline BOOLEAN DEFAULT NULL,
    voip BOOLEAN DEFAULT NULL,
    other_phone BOOLEAN DEFAULT NULL,
    foreign_number BOOLEAN DEFAULT NULL,
    country TEXT DEFAULT 'US',
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes for common queries
    CONSTRAINT contacts_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' OR email IS NULL)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contacts_sponsor ON contacts(sponsor);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id);
CREATE INDEX IF NOT EXISTS idx_contacts_created_at ON contacts(created_at);
CREATE INDEX IF NOT EXISTS idx_contacts_country ON contacts(country);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_contacts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_contacts_updated_at();

-- Insert sample data for testing
INSERT INTO contacts (
    sponsor, sponsor_first, sponsor_last, user_id, first_name, last_name, 
    email, email_valid, phone, address, city, state, zip, status, rating,
    ip_address, timezone, cell, carrier, country
) VALUES 
    ('John Doe', 'John', 'Doe', 'user001', 'Alice', 'Smith', 'alice@example.com', true, '555-0101', '123 Main St', 'Anytown', 'CA', '90210', 'Active', 'A', '192.168.1.1', 'PST', true, 'Verizon', 'US'),
    ('Jane Wilson', 'Jane', 'Wilson', 'user002', 'Bob', 'Johnson', 'bob@example.com', true, '555-0102', '456 Oak Ave', 'Another City', 'TX', '75001', 'Active', 'B', '192.168.1.2', 'CST', true, 'AT&T', 'US'),
    ('Mike Davis', 'Mike', 'Davis', 'user003', 'Carol', 'Brown', 'carol@example.com', true, '555-0103', '789 Pine Rd', 'Third City', 'NY', '10001', 'Pending', 'A', '192.168.1.3', 'EST', false, 'T-Mobile', 'US');

-- Comment explaining the table structure
COMMENT ON TABLE contacts IS 'Main contacts table storing all contact information with support for sponsor tracking, phone type classification, and geographic data';
COMMENT ON COLUMN contacts.email_valid IS 'Boolean indicating if the email address has been validated';
COMMENT ON COLUMN contacts.cell IS 'Boolean indicating if the phone number is a cellular/mobile number';
COMMENT ON COLUMN contacts.landline IS 'Boolean indicating if the phone number is a landline';
COMMENT ON COLUMN contacts.voip IS 'Boolean indicating if the phone number is a VoIP number';
COMMENT ON COLUMN contacts.foreign_number IS 'Boolean indicating if the phone number is from outside the default country';
