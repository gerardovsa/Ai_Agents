-- =====================================================
-- Business Rules Table - Editable via Prompt Library UI
-- Created: January 8, 2026
-- =====================================================
-- 
-- PURPOSE:
-- Store flexible, text-based business rules that AI agents
-- automatically check during quote generation, customer interactions,
-- and other operations.
--
-- INTEGRATION:
-- - Accessed via new "Business Rules" tab in Prompt Library UI
-- - Auto-loaded by AI agents during quote workflow
-- - Validates calculator outputs, applies discounts, enforces margins
--
-- USAGE:
-- Users edit rules in plain English through UI, system enforces them
-- =====================================================

-- Main business rules table
CREATE TABLE IF NOT EXISTS ai_infrastructure.business_rules (
    rule_id SERIAL PRIMARY KEY,
    
    -- Categorization
    category VARCHAR(50) NOT NULL, -- 'calculator_validation', 'customer_discounts', 'profit_margins', 'product_rules', 'seasonal', 'custom'
    subcategory VARCHAR(100), -- e.g., 'corflute_signs', 'business_cards', 'trade_customers'
    
    -- Rule identification
    rule_name VARCHAR(200) NOT NULL,
    rule_description TEXT NOT NULL, -- Plain English explanation
    
    -- Rule content (flexible text format)
    rule_content JSONB NOT NULL, -- Stores rule logic in flexible JSON structure
    rule_text TEXT NOT NULL, -- Human-readable rule statement
    
    -- Scope and application
    applies_to VARCHAR(100)[], -- ['all_customers', 'trade_customers', 'specific_customer:CustomerID']
    product_types VARCHAR(100)[], -- ['corflute_signs', 'business_cards', 'all']
    calculator_names VARCHAR(100)[], -- ['calculate_corflute_signs_shopify', 'all']
    
    -- Priority and enforcement
    priority INTEGER DEFAULT 100, -- Lower = higher priority, executed first
    enforcement_level VARCHAR(20) DEFAULT 'mandatory', -- 'mandatory', 'warning', 'advisory'
    auto_apply BOOLEAN DEFAULT TRUE, -- If true, AI automatically applies rule
    
    -- Status and versioning
    is_active BOOLEAN DEFAULT TRUE,
    version INTEGER DEFAULT 1,
    effective_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE, -- NULL = no expiry
    
    -- Audit trail
    created_by INTEGER REFERENCES ai_infrastructure.users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER REFERENCES ai_infrastructure.users(user_id),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_applied_at TIMESTAMP, -- Track when rule was last used
    application_count INTEGER DEFAULT 0, -- How many times rule has been applied
    
    -- Metadata
    tags VARCHAR(100)[], -- For searching/filtering
    notes TEXT, -- Internal notes for rule maintainers
    
    CONSTRAINT unique_rule_name UNIQUE (category, rule_name)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_business_rules_category ON ai_infrastructure.business_rules(category) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_business_rules_applies_to ON ai_infrastructure.business_rules USING GIN(applies_to) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_business_rules_products ON ai_infrastructure.business_rules USING GIN(product_types) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_business_rules_calculators ON ai_infrastructure.business_rules USING GIN(calculator_names) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_business_rules_priority ON ai_infrastructure.business_rules(priority, category) WHERE is_active = TRUE;

-- Rule execution log (audit trail)
CREATE TABLE IF NOT EXISTS ai_infrastructure.business_rules_execution_log (
    log_id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES ai_infrastructure.business_rules(rule_id),
    
    -- Execution context
    user_id INTEGER REFERENCES ai_infrastructure.users(user_id),
    session_id VARCHAR(100),
    conversation_thread_id BIGINT,
    
    -- What was checked
    context_type VARCHAR(50), -- 'quote_calculation', 'customer_discount', 'invoice_validation'
    context_data JSONB, -- Full context (calculator inputs, customer data, etc.)
    
    -- Result
    rule_triggered BOOLEAN, -- Did rule apply to this case?
    action_taken VARCHAR(50), -- 'applied', 'warning_issued', 'blocked', 'skipped'
    before_value JSONB, -- State before rule application
    after_value JSONB, -- State after rule application
    
    -- Outcome
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- Timing
    executed_at TIMESTAMP DEFAULT NOW(),
    execution_time_ms INTEGER -- Performance tracking
);

CREATE INDEX IF NOT EXISTS idx_rules_log_rule_id ON ai_infrastructure.business_rules_execution_log(rule_id);
CREATE INDEX IF NOT EXISTS idx_rules_log_user ON ai_infrastructure.business_rules_execution_log(user_id, executed_at);
CREATE INDEX IF NOT EXISTS idx_rules_log_context ON ai_infrastructure.business_rules_execution_log(context_type, executed_at);

-- Rule conflicts table (track when rules contradict each other)
CREATE TABLE IF NOT EXISTS ai_infrastructure.business_rules_conflicts (
    conflict_id SERIAL PRIMARY KEY,
    rule_id_1 INTEGER REFERENCES ai_infrastructure.business_rules(rule_id),
    rule_id_2 INTEGER REFERENCES ai_infrastructure.business_rules(rule_id),
    
    conflict_type VARCHAR(50), -- 'contradictory', 'overlapping', 'priority_issue'
    conflict_description TEXT,
    
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES ai_infrastructure.users(user_id)
);

-- =====================================================
-- SAMPLE DATA - Business Rules for Quote Calculator
-- =====================================================

-- Rule 1: Calculator Validation - Corflute Double-Sided Check
INSERT INTO ai_infrastructure.business_rules (
    category, subcategory, rule_name, rule_description,
    rule_content, rule_text,
    applies_to, product_types, calculator_names,
    priority, enforcement_level, created_by
) VALUES (
    'calculator_validation',
    'corflute_signs',
    'corflute_double_sided_validation',
    'Validate that double-sided cost is $0 when double_sided parameter is false',
    '{
        "validation_type": "breakdown_check",
        "parameter": "double_sided",
        "condition": "equals",
        "value": false,
        "expected_breakdown_field": "double_sided_cost",
        "expected_value": 0,
        "error_message": "Double-sided cost should be $0 for single-sided orders"
    }'::jsonb,
    'IF calculator input double_sided = false, THEN breakdown.double_sided_cost MUST = $0',
    ARRAY['all_customers'],
    ARRAY['corflute_signs'],
    ARRAY['calculate_corflute_signs_shopify'],
    1, -- Highest priority
    'mandatory',
    1 -- admin user
);

-- Rule 2: Customer Discount - Simply Signs Trade Discount
INSERT INTO ai_infrastructure.business_rules (
    category, subcategory, rule_name, rule_description,
    rule_content, rule_text,
    applies_to, product_types, calculator_names,
    priority, enforcement_level, created_by
) VALUES (
    'customer_discounts',
    'trade_customers',
    'simply_signs_corflute_discount',
    'Simply Signs receives 15% trade discount on all corflute sign orders',
    '{
        "customer_identifier": "simply signs",
        "discount_type": "percentage",
        "discount_value": 15,
        "applies_to_products": ["corflute_signs"],
        "minimum_order_value": 0,
        "discount_description": "Trade customer discount"
    }'::jsonb,
    'Simply Signs gets 15% discount on corflute signs (no minimum order)',
    ARRAY['specific_customer:simply signs'],
    ARRAY['corflute_signs'],
    ARRAY['calculate_corflute_signs_shopify', 'calculate_corflute_signs_bulk_god'],
    50,
    'mandatory',
    1
);

-- Rule 3: Profit Margin Enforcement - Business Cards Minimum
INSERT INTO ai_infrastructure.business_rules (
    category, subcategory, rule_name, rule_description,
    rule_content, rule_text,
    applies_to, product_types, calculator_names,
    priority, enforcement_level, created_by
) VALUES (
    'profit_margins',
    'business_cards',
    'business_cards_minimum_margin',
    'Business cards must maintain minimum 30% profit margin',
    '{
        "margin_type": "percentage",
        "minimum_margin": 30,
        "target_margin": 40,
        "action_if_below_minimum": "flag_for_approval",
        "exceptions": ["bulk_orders_1000_plus"]
    }'::jsonb,
    'Business cards minimum margin: 30%. Target: 40%. Flag if below 30%.',
    ARRAY['all_customers'],
    ARRAY['business_cards'],
    ARRAY['calculate_business_cards', 'calculate_premium_business_cards_shopify', 'calculate_economical_business_cards_shopify'],
    10,
    'warning',
    1
);

-- Rule 4: Product-Specific - Corflute Thickness Pricing
INSERT INTO ai_infrastructure.business_rules (
    category, subcategory, rule_name, rule_description,
    rule_content, rule_text,
    applies_to, product_types, calculator_names,
    priority, enforcement_level, created_by
) VALUES (
    'product_rules',
    'corflute_signs',
    'corflute_thickness_pricing',
    '5mm corflute should be 20% more expensive than 3mm for same size',
    '{
        "pricing_rule": "thickness_multiplier",
        "base_thickness": "3mm",
        "premium_thickness": "5mm",
        "price_increase_percentage": 20,
        "validation": "check_price_difference"
    }'::jsonb,
    '5mm corflute = 3mm price × 1.20 (material cost difference)',
    ARRAY['all_customers'],
    ARRAY['corflute_signs'],
    ARRAY['calculate_corflute_signs_shopify'],
    30,
    'advisory',
    1
);

-- Rule 5: Calculator Validation - Eyelet Cost Check
INSERT INTO ai_infrastructure.business_rules (
    category, subcategory, rule_name, rule_description,
    rule_content, rule_text,
    applies_to, product_types, calculator_names,
    priority, enforcement_level, created_by
) VALUES (
    'calculator_validation',
    'corflute_signs',
    'corflute_eyelet_validation',
    'Validate that eyelet cost is $0 when eyelet_option is none',
    '{
        "validation_type": "breakdown_check",
        "parameter": "eyelet_option",
        "condition": "equals",
        "value": "none",
        "expected_breakdown_field": "eyelet_cost",
        "expected_value": 0,
        "error_message": "Eyelet cost should be $0 when no eyelets specified"
    }'::jsonb,
    'IF eyelet_option = "none", THEN breakdown.eyelet_cost MUST = $0',
    ARRAY['all_customers'],
    ARRAY['corflute_signs'],
    ARRAY['calculate_corflute_signs_shopify'],
    1,
    'mandatory',
    1
);

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to get active rules for a context
CREATE OR REPLACE FUNCTION ai_infrastructure.get_business_rules_for_context(
    p_category VARCHAR,
    p_calculator_name VARCHAR DEFAULT NULL,
    p_product_type VARCHAR DEFAULT NULL,
    p_customer VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    rule_id INTEGER,
    rule_name VARCHAR,
    rule_content JSONB,
    rule_text TEXT,
    priority INTEGER,
    enforcement_level VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        br.rule_id,
        br.rule_name,
        br.rule_content,
        br.rule_text,
        br.priority,
        br.enforcement_level
    FROM ai_infrastructure.business_rules br
    WHERE br.is_active = TRUE
      AND br.category = p_category
      AND (p_calculator_name IS NULL OR p_calculator_name = ANY(br.calculator_names) OR 'all' = ANY(br.calculator_names))
      AND (p_product_type IS NULL OR p_product_type = ANY(br.product_types) OR 'all' = ANY(br.product_types))
      AND (p_customer IS NULL OR p_customer = ANY(br.applies_to) OR 'all_customers' = ANY(br.applies_to))
      AND (br.effective_date IS NULL OR br.effective_date <= CURRENT_DATE)
      AND (br.expiry_date IS NULL OR br.expiry_date > CURRENT_DATE)
    ORDER BY br.priority ASC, br.rule_id ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to log rule execution
CREATE OR REPLACE FUNCTION ai_infrastructure.log_business_rule_execution(
    p_rule_id INTEGER,
    p_user_id INTEGER,
    p_context_type VARCHAR,
    p_context_data JSONB,
    p_rule_triggered BOOLEAN,
    p_action_taken VARCHAR,
    p_before_value JSONB DEFAULT NULL,
    p_after_value JSONB DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_log_id INTEGER;
BEGIN
    INSERT INTO ai_infrastructure.business_rules_execution_log (
        rule_id, user_id, context_type, context_data,
        rule_triggered, action_taken, before_value, after_value
    ) VALUES (
        p_rule_id, p_user_id, p_context_type, p_context_data,
        p_rule_triggered, p_action_taken, p_before_value, p_after_value
    ) RETURNING log_id INTO v_log_id;
    
    -- Update rule application count
    UPDATE ai_infrastructure.business_rules
    SET application_count = application_count + 1,
        last_applied_at = NOW()
    WHERE rule_id = p_rule_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- GRANTS
-- =====================================================

GRANT SELECT, INSERT, UPDATE ON ai_infrastructure.business_rules TO authenticated;
GRANT SELECT, INSERT ON ai_infrastructure.business_rules_execution_log TO authenticated;
GRANT SELECT ON ai_infrastructure.business_rules_conflicts TO authenticated;
GRANT USAGE ON SEQUENCE ai_infrastructure.business_rules_rule_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE ai_infrastructure.business_rules_execution_log_log_id_seq TO authenticated;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE ai_infrastructure.business_rules IS 'Flexible, text-based business rules for quote validation, customer discounts, and profit margins';
COMMENT ON COLUMN ai_infrastructure.business_rules.rule_content IS 'JSONB field stores rule logic in flexible structure that can be interpreted by AI or code';
COMMENT ON COLUMN ai_infrastructure.business_rules.enforcement_level IS 'mandatory = block operation, warning = flag for review, advisory = informational only';
COMMENT ON COLUMN ai_infrastructure.business_rules.applies_to IS 'Array of customer identifiers or "all_customers" for universal rules';

COMMENT ON TABLE ai_infrastructure.business_rules_execution_log IS 'Audit trail of every time a business rule is checked or applied';
COMMENT ON FUNCTION ai_infrastructure.get_business_rules_for_context IS 'Retrieve active rules matching specific context (calculator, product, customer)';
COMMENT ON FUNCTION ai_infrastructure.log_business_rule_execution IS 'Log rule execution with before/after state for audit purposes';
