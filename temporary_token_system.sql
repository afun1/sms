-- SQL function to generate temporary login tokens for impersonation
CREATE OR REPLACE FUNCTION generate_impersonation_token(
    admin_user_id UUID,
    target_user_id UUID
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    admin_role TEXT;
    temp_token TEXT;
BEGIN
    -- Verify admin permissions
    SELECT role INTO admin_role 
    FROM profiles 
    WHERE id = admin_user_id;
    
    IF admin_role NOT IN ('admin', 'super_admin', 'manager') THEN
        RAISE EXCEPTION 'Insufficient permissions';
    END IF;
    
    -- Generate temporary token (24 hour expiry)
    temp_token := encode(
        hmac(
            target_user_id::text || extract(epoch from now())::text,
            'your-secret-key',
            'sha256'
        ),
        'hex'
    );
    
    -- Store token with expiry
    INSERT INTO impersonation_tokens (
        token,
        admin_user_id,
        target_user_id,
        expires_at
    ) VALUES (
        temp_token,
        admin_user_id,
        target_user_id,
        now() + interval '24 hours'
    );
    
    RETURN temp_token;
END;
$$;
