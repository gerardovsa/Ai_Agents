/*
Customer Reactivation Module - Database Schema
Created: January 18, 2026
Purpose: Email campaigns for at-risk customers (Xero integration)

Tables:
- reactivation_campaigns: Campaign definitions and metrics
- reactivation_recipients: Campaign recipient list with tracking
- reactivation_templates: Email template library
- reactivation_tracking: Event tracking (opens, clicks, reorders)
- reactivation_prospects: Synced at-risk customers from Xero
*/

-- ============================================================================
-- 1. CAMPAIGNS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.reactivation_campaigns (
    campaign_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    campaign_name VARCHAR(255) NOT NULL,
    campaign_type VARCHAR(50) DEFAULT 'reactivation', -- reactivation, feedback, follow_up, cross_sell
    xero_business_id INT DEFAULT 1, -- 1=Print, 2=Publishing, 3=Signs
    target_segment VARCHAR(50), -- 'at_risk', 'lost', 'inactive', 'high_value'
    churn_threshold INT DEFAULT 60, -- Min churn risk score (0-100)
    template_id INT, -- References reactivation_templates
    subject_line VARCHAR(500),
    from_name VARCHAR(255) DEFAULT 'InHouse Print',
    from_email VARCHAR(255) DEFAULT 'sales@inhouseprint.com.au',
    discount_code VARCHAR(50),
    discount_amount DECIMAL(10,2),
    discount_type VARCHAR(20) DEFAULT 'percentage', -- percentage, fixed
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, sending, completed, paused
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    total_recipients INT DEFAULT 0,
    emails_sent INT DEFAULT 0,
    opens INT DEFAULT 0,
    clicks INT DEFAULT 0,
    reorders INT DEFAULT 0,
    bounces INT DEFAULT 0,
    unsubscribes INT DEFAULT 0,
    revenue_recovered DECIMAL(12,2) DEFAULT 0,
    campaign_cost DECIMAL(10,2) DEFAULT 0,
    roi_percentage DECIMAL(8,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INT,
    notes TEXT
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_reactivation_campaigns_user_id ON ai_infrastructure.reactivation_campaigns(user_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_campaigns_status ON ai_infrastructure.reactivation_campaigns(status);
CREATE INDEX IF NOT EXISTS idx_reactivation_campaigns_xero_business ON ai_infrastructure.reactivation_campaigns(xero_business_id);

-- ============================================================================
-- 2. RECIPIENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.reactivation_recipients (
    id SERIAL PRIMARY KEY,
    campaign_id INT NOT NULL REFERENCES ai_infrastructure.reactivation_campaigns(campaign_id) ON DELETE CASCADE,
    xero_contact_id VARCHAR(100), -- Xero GUID
    xero_business_id INT DEFAULT 1,
    email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(50),
    last_order_date DATE,
    total_revenue DECIMAL(12,2),
    average_order_value DECIMAL(10,2),
    order_frequency DECIMAL(6,2), -- Orders per month
    churn_risk_score INT, -- 0-100 from Xero ML
    months_since_last_order INT,
    last_product_ordered TEXT, -- From Xero invoice line items
    custom_fields JSONB, -- Additional personalization data
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, opened, clicked, bounced, unsubscribed, reordered
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    bounced_at TIMESTAMP,
    unsubscribed_at TIMESTAMP,
    reordered_at TIMESTAMP,
    reorder_amount DECIMAL(10,2),
    reorder_invoice_id VARCHAR(100), -- Xero invoice ID
    tracking_id UUID DEFAULT gen_random_uuid(), -- For tracking pixel/links
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(campaign_id, email)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reactivation_recipients_campaign ON ai_infrastructure.reactivation_recipients(campaign_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_recipients_xero_contact ON ai_infrastructure.reactivation_recipients(xero_contact_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_recipients_status ON ai_infrastructure.reactivation_recipients(status);
CREATE INDEX IF NOT EXISTS idx_reactivation_recipients_tracking_id ON ai_infrastructure.reactivation_recipients(tracking_id);

-- ============================================================================
-- 3. TEMPLATES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.reactivation_templates (
    template_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    template_name VARCHAR(255) NOT NULL,
    template_type VARCHAR(50) DEFAULT 'reactivation', -- reactivation, feedback, follow_up, thank_you, reminder
    subject VARCHAR(500),
    html_body TEXT NOT NULL,
    text_body TEXT,
    thumbnail_url VARCHAR(500),
    merge_fields JSONB, -- ["{{first_name}}", "{{last_order_date}}", "{{discount_code}}"]
    category VARCHAR(100), -- win_back, vip, seasonal, anniversary
    is_public BOOLEAN DEFAULT FALSE,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by INT
);

-- Index
CREATE INDEX IF NOT EXISTS idx_reactivation_templates_user_id ON ai_infrastructure.reactivation_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_templates_type ON ai_infrastructure.reactivation_templates(template_type);

-- ============================================================================
-- 4. TRACKING TABLE (Events)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.reactivation_tracking (
    tracking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id INT REFERENCES ai_infrastructure.reactivation_campaigns(campaign_id) ON DELETE CASCADE,
    recipient_id INT REFERENCES ai_infrastructure.reactivation_recipients(id) ON DELETE CASCADE,
    recipient_email VARCHAR(255),
    xero_contact_id VARCHAR(100),
    event_type VARCHAR(50) NOT NULL, -- sent, open, click, bounce, unsubscribe, reorder
    event_data JSONB, -- {link_url, user_agent, ip_address, error_code}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reactivation_tracking_campaign ON ai_infrastructure.reactivation_tracking(campaign_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_tracking_recipient ON ai_infrastructure.reactivation_tracking(recipient_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_tracking_event_type ON ai_infrastructure.reactivation_tracking(event_type);
CREATE INDEX IF NOT EXISTS idx_reactivation_tracking_created_at ON ai_infrastructure.reactivation_tracking(created_at);

-- ============================================================================
-- 5. PROSPECTS TABLE (Synced from Xero)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.reactivation_prospects (
    id SERIAL PRIMARY KEY,
    xero_business_id INT NOT NULL,
    xero_contact_id VARCHAR(100) NOT NULL,
    contact_name VARCHAR(255),
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(50),
    churn_risk_score INT, -- From Xero ML
    segment VARCHAR(50), -- Champions, Loyal, At Risk, Lost
    months_since_last_order INT,
    total_revenue DECIMAL(12,2),
    average_order_value DECIMAL(10,2),
    order_frequency DECIMAL(6,2),
    last_invoice_date DATE,
    first_invoice_date DATE,
    total_invoices INT,
    last_product_ordered TEXT,
    synced_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(xero_contact_id, xero_business_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reactivation_prospects_xero_business ON ai_infrastructure.reactivation_prospects(xero_business_id);
CREATE INDEX IF NOT EXISTS idx_reactivation_prospects_churn_risk ON ai_infrastructure.reactivation_prospects(churn_risk_score);
CREATE INDEX IF NOT EXISTS idx_reactivation_prospects_segment ON ai_infrastructure.reactivation_prospects(segment);
CREATE INDEX IF NOT EXISTS idx_reactivation_prospects_email ON ai_infrastructure.reactivation_prospects(email);

-- ============================================================================
-- 6. SEED DEFAULT TEMPLATES
-- ============================================================================

INSERT INTO ai_infrastructure.reactivation_templates (user_id, template_name, template_type, subject, html_body, text_body, merge_fields, category, is_public)
VALUES 
(1, 'Win-Back - We Miss You', 'reactivation', 'We Miss You, {{first_name}}! Come Back for 25% Off', 
'<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #13B5EA; color: white; padding: 30px; text-align: center; }
        .content { background: #f9f9f9; padding: 30px; }
        .cta { background: #238636; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>We Miss You, {{first_name}}!</h1>
        </div>
        <div class="content">
            <p>Hi {{first_name}},</p>
            <p>We noticed it''s been <strong>{{months_inactive}} months</strong> since your last order with InHouse Print.</p>
            <p>You''ve been a valued customer since {{first_order_year}}, with {{total_orders}} orders totaling <strong>${{total_spent}}</strong>.</p>
            <p>We''d love to have you back! Here''s an exclusive offer just for you:</p>
            <div style="text-align: center; margin: 30px 0; padding: 20px; background: white; border: 2px dashed #238636;">
                <h2 style="color: #238636; margin: 0;">25% OFF</h2>
                <p style="margin: 10px 0;">Your Next Order</p>
                <p style="font-size: 20px; font-weight: bold; color: #13B5EA;">{{discount_code}}</p>
            </div>
            <p>Whether you need more <strong>{{last_product_category}}</strong> or something new, we''re here to help.</p>
            <p style="text-align: center;">
                <a href="https://inhouseprint.com.au/quote?code={{discount_code}}" class="cta">Get Your Quote Now</a>
            </p>
            <p>Questions? Just reply to this email or call us at <strong>(02) 9638 2944</strong>.</p>
            <p>Thanks,<br>The InHouse Print Team</p>
        </div>
        <div class="footer">
            <p>InHouse Print | 5 Foundry Rd, Seven Hills NSW 2147</p>
            <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>',
'Hi {{first_name}},

We noticed it''s been {{months_inactive}} months since your last order with InHouse Print.

You''ve been a valued customer since {{first_order_year}}, with {{total_orders}} orders totaling ${{total_spent}}.

Come back and get 25% OFF your next order with code: {{discount_code}}

Visit: https://inhouseprint.com.au/quote?code={{discount_code}}

Questions? Call (02) 9638 2944 or reply to this email.

Thanks,
The InHouse Print Team

---
Unsubscribe: {{unsubscribe_url}}',
'["{{first_name}}", "{{months_inactive}}", "{{first_order_year}}", "{{total_orders}}", "{{total_spent}}", "{{last_product_category}}", "{{discount_code}}", "{{unsubscribe_url}}"]'::jsonb,
'win_back', TRUE),

(1, 'VIP High-Value Retention', 'reactivation', '{{first_name}}, You''re Important to Us - Exclusive VIP Offer Inside', 
'<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; text-align: center; }
        .vip-badge { background: gold; color: #333; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 12px; }
        .content { background: #f9f9f9; padding: 30px; }
        .cta { background: gold; color: #333; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; font-weight: bold; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="vip-badge">⭐ VIP CUSTOMER</span>
            <h1 style="margin-top: 15px;">You''re Valued, {{first_name}}</h1>
        </div>
        <div class="content">
            <p>Hi {{first_name}},</p>
            <p>As one of our top customers with <strong>${{total_spent}}</strong> in lifetime orders, we wanted to personally reach out.</p>
            <p>We noticed it''s been {{months_inactive}} months since your last order. Is everything okay? Can we help with anything?</p>
            <p><strong>Your dedicated Account Manager:</strong></p>
            <div style="background: white; padding: 15px; margin: 20px 0; border-left: 4px solid gold;">
                <p style="margin: 5px 0;"><strong>{{manager_name}}</strong></p>
                <p style="margin: 5px 0;">📞 {{manager_phone}}</p>
                <p style="margin: 5px 0;">✉️ {{manager_email}}</p>
            </div>
            <p>Plus, here''s an exclusive <strong>30% discount</strong> just for you:</p>
            <div style="text-align: center; margin: 30px 0; padding: 20px; background: white; border: 2px solid gold;">
                <h2 style="color: #667eea; margin: 0;">VIP EXCLUSIVE</h2>
                <p style="margin: 10px 0;">30% OFF Your Next Order</p>
                <p style="font-size: 24px; font-weight: bold; color: #333;">{{discount_code}}</p>
            </div>
            <p style="text-align: center;">
                <a href="https://inhouseprint.com.au/quote?code={{discount_code}}&vip=true" class="cta">Claim Your VIP Discount</a>
            </p>
            <p>We truly value your business and look forward to serving you again.</p>
            <p>Best regards,<br>The InHouse Print Team</p>
        </div>
        <div class="footer">
            <p>InHouse Print | 5 Foundry Rd, Seven Hills NSW 2147</p>
            <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>',
'Hi {{first_name}},

As one of our top VIP customers (${{total_spent}} lifetime), we wanted to personally reach out.

We noticed it''s been {{months_inactive}} months since your last order. Is everything okay?

Your Account Manager {{manager_name}} is here to help:
📞 {{manager_phone}}
✉️ {{manager_email}}

Plus, here''s an exclusive 30% VIP discount: {{discount_code}}

Visit: https://inhouseprint.com.au/quote?code={{discount_code}}&vip=true

We value your business!

Best regards,
The InHouse Print Team',
'["{{first_name}}", "{{total_spent}}", "{{months_inactive}}", "{{manager_name}}", "{{manager_phone}}", "{{manager_email}}", "{{discount_code}}", "{{unsubscribe_url}}"]'::jsonb,
'vip', TRUE),

(1, 'Post-Order Feedback Request', 'feedback', 'How Was Your Recent Order? Quick 2-Minute Survey', 
'<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #1f6feb; color: white; padding: 30px; text-align: center; }
        .content { background: #f9f9f9; padding: 30px; }
        .cta { background: #238636; color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Feedback Matters!</h1>
        </div>
        <div class="content">
            <p>Hi {{first_name}},</p>
            <p>Thanks for your recent order <strong>#{{invoice_number}}</strong> of {{product_summary}}.</p>
            <p>We''d love to hear about your experience! It''ll only take 2 minutes.</p>
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 18px; margin: 10px 0;">How would you rate your experience?</p>
                <div style="font-size: 40px; letter-spacing: 10px;">
                    <a href="{{survey_url}}?rating=5">😀</a>
                    <a href="{{survey_url}}?rating=4">🙂</a>
                    <a href="{{survey_url}}?rating=3">😐</a>
                    <a href="{{survey_url}}?rating=2">😕</a>
                    <a href="{{survey_url}}?rating=1">😞</a>
                </div>
            </div>
            <p style="text-align: center;">
                <a href="{{survey_url}}" class="cta">Take Quick Survey</a>
            </p>
            <p>Your feedback helps us serve you better.</p>
            <p>Thanks,<br>The InHouse Print Team</p>
        </div>
        <div class="footer">
            <p>InHouse Print | 5 Foundry Rd, Seven Hills NSW 2147</p>
            <p><a href="{{unsubscribe_url}}">Unsubscribe</a></p>
        </div>
    </div>
</body>
</html>',
'Hi {{first_name}},

Thanks for your recent order #{{invoice_number}} of {{product_summary}}.

We''d love to hear about your experience! Quick 2-minute survey:
{{survey_url}}

How was:
- Print quality?
- Delivery time?
- Customer service?

Your feedback helps us improve!

Thanks,
The InHouse Print Team',
'["{{first_name}}", "{{invoice_number}}", "{{product_summary}}", "{{survey_url}}", "{{unsubscribe_url}}"]'::jsonb,
'feedback', TRUE)

ON CONFLICT DO NOTHING;

-- ============================================================================
-- 7. UPDATE TRIGGER FOR updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_reactivation_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_reactivation_campaigns_updated_at
    BEFORE UPDATE ON ai_infrastructure.reactivation_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_reactivation_updated_at();

CREATE TRIGGER update_reactivation_recipients_updated_at
    BEFORE UPDATE ON ai_infrastructure.reactivation_recipients
    FOR EACH ROW
    EXECUTE FUNCTION update_reactivation_updated_at();

CREATE TRIGGER update_reactivation_templates_updated_at
    BEFORE UPDATE ON ai_infrastructure.reactivation_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_reactivation_updated_at();

CREATE TRIGGER update_reactivation_prospects_updated_at
    BEFORE UPDATE ON ai_infrastructure.reactivation_prospects
    FOR EACH ROW
    EXECUTE FUNCTION update_reactivation_updated_at();

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON TABLE ai_infrastructure.reactivation_campaigns IS 'Email campaigns for customer reactivation, feedback, and follow-up';
COMMENT ON TABLE ai_infrastructure.reactivation_recipients IS 'Campaign recipient list with tracking and Xero integration';
COMMENT ON TABLE ai_infrastructure.reactivation_templates IS 'Email template library with merge fields';
COMMENT ON TABLE ai_infrastructure.reactivation_tracking IS 'Event tracking for email opens, clicks, and reorders';
COMMENT ON TABLE ai_infrastructure.reactivation_prospects IS 'At-risk customers synced from Xero churn-risk-ml API';
