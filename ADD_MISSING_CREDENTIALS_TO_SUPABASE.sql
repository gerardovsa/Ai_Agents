-- Add Missing Credentials to Supabase user_platform_credentials
-- Run this in your Supabase SQL Editor

-- 1. Xero Publishing
INSERT INTO ai_infrastructure.user_platform_credentials (
    user_id,
    platform,
    credential_type,
    credential_key,
    credential_value,
    is_active,
    metadata,
    credentials
) VALUES (
    1,
    'xero_publishing',
    'oauth',
    'client_credentials',
    '926A463987B749FB9F21950B3B4212E9',
    true,
    '{"business": "Publishing", "base_url": "https://api.xero.com", "description": "Xero API - InHouse Publishing"}',
    '{"business": "Publishing", "base_url": "https://api.xero.com", "client_id": "926A463987B749FB9F21950B3B4212E9", "client_secret": "aBWKAnfBl17roRt3jgD_hGba7JM0di3YGj5WLHv0T89kyTyq"}'
)
ON CONFLICT (user_id, platform) DO UPDATE SET
    credential_value = EXCLUDED.credential_value,
    credentials = EXCLUDED.credentials,
    metadata = EXCLUDED.metadata,
    updated_at = CURRENT_TIMESTAMP;

-- 2. Xero Signs
INSERT INTO ai_infrastructure.user_platform_credentials (
    user_id,
    platform,
    credential_type,
    credential_key,
    credential_value,
    is_active,
    metadata,
    credentials
) VALUES (
    1,
    'xero_signs',
    'oauth',
    'client_credentials',
    '7D5CE8F957944A95878F5B1F1CEE6F3D',
    true,
    '{"business": "Signs", "base_url": "https://api.xero.com", "description": "Xero API - InHouse Signs"}',
    '{"business": "Signs", "base_url": "https://api.xero.com", "client_id": "7D5CE8F957944A95878F5B1F1CEE6F3D", "client_secret": "xykFPAGUy5mHfMvOqwtfmg7y5uqNjaxES4OPet6L9tVoDhS3"}'
)
ON CONFLICT (user_id, platform) DO UPDATE SET
    credential_value = EXCLUDED.credential_value,
    credentials = EXCLUDED.credentials,
    metadata = EXCLUDED.metadata,
    updated_at = CURRENT_TIMESTAMP;

-- 3. Email Settings (SMTP)
INSERT INTO ai_infrastructure.user_platform_credentials (
    user_id,
    platform,
    credential_type,
    credential_key,
    credential_value,
    is_active,
    metadata,
    credentials
) VALUES (
    1,
    'email_smtp',
    'smtp',
    'office365',
    'printing@inhouseprint.com.au',
    true,
    '{"smtp_server": "smtp.office365.com", "port": 587, "description": "Office 365 SMTP for automated emails"}',
    '{"smtp_server": "smtp.office365.com", "port": 587, "username": "printing@inhouseprint.com.au", "password": "J@ck20!!", "recipients": {"completed_orders": "guy@inhouseprint.com.au"}}'
)
ON CONFLICT (user_id, platform) DO UPDATE SET
    credential_value = EXCLUDED.credential_value,
    credentials = EXCLUDED.credentials,
    metadata = EXCLUDED.metadata,
    updated_at = CURRENT_TIMESTAMP;

-- 4. Business Divisions (Configuration)
INSERT INTO ai_infrastructure.user_platform_credentials (
    user_id,
    platform,
    credential_type,
    credential_key,
    credential_value,
    is_active,
    metadata,
    credentials
) VALUES (
    1,
    'business_config',
    'configuration',
    'divisions',
    '{"1": "InHouse Print", "2": "InHouse Publishing", "3": "InHouse Signs"}',
    true,
    '{"description": "Business division mappings for InHouse Print companies"}',
    '{"divisions": {"1": "InHouse Print", "2": "InHouse Publishing", "3": "InHouse Signs"}}'
)
ON CONFLICT (user_id, platform) DO UPDATE SET
    credential_value = EXCLUDED.credential_value,
    credentials = EXCLUDED.credentials,
    metadata = EXCLUDED.metadata,
    updated_at = CURRENT_TIMESTAMP;

-- Verify insertions
SELECT 
    platform,
    credential_type,
    is_active,
    created_at,
    updated_at
FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 1
ORDER BY platform;
