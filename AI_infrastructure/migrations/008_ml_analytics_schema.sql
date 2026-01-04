-- ============================================================================
-- ML ANALYTICS SCHEMA - Machine Learning Predictions & Intelligence
-- ============================================================================
-- Creates tables for storing ML models, predictions, customer intelligence cache, 
-- and anomaly detections
-- 
-- Created: January 5, 2026
-- Idempotent: Can be run multiple times safely
-- ============================================================================

-- ML Models Storage
CREATE TABLE IF NOT EXISTS ml_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50),  -- 'xgboost', 'arima', 'neural_network', 'random_forest'
    business_id INTEGER,
    version VARCHAR(20),
    model_binary BYTEA,  -- Pickled model
    metrics JSONB,  -- accuracy, F1, RMSE, etc.
    trained_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ml_models_name ON ml_models(model_name);
CREATE INDEX IF NOT EXISTS idx_ml_models_business ON ml_models(business_id);
CREATE INDEX IF NOT EXISTS idx_ml_models_active ON ml_models(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE ml_models IS 'Stores trained ML models for predictions';
COMMENT ON COLUMN ml_models.metrics IS 'JSON: {"accuracy": 0.85, "f1_score": 0.82, "rmse": 45.2}';

-- ============================================================================
-- ML Predictions Cache
CREATE TABLE IF NOT EXISTS ml_predictions (
    prediction_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- 'customer', 'invoice', 'payment'
    entity_id VARCHAR(100) NOT NULL,
    business_id INTEGER,
    prediction_data JSONB NOT NULL,
    confidence_score FLOAT,
    predicted_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_entity ON ml_predictions(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_business ON ml_predictions(business_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_expires ON ml_predictions(expires_at);

COMMENT ON TABLE ml_predictions IS 'Caches ML predictions with expiration for performance';
COMMENT ON COLUMN ml_predictions.prediction_data IS 'JSON: {"churn_probability": 0.75, "risk_category": "high", "factors": [...]}';

-- ============================================================================
-- Customer Intelligence Cache
CREATE TABLE IF NOT EXISTS customer_intelligence_cache (
    customer_id VARCHAR(100) PRIMARY KEY,
    business_id INTEGER NOT NULL,
    customer_name VARCHAR(200),
    
    -- Churn Prediction
    churn_probability FLOAT,
    churn_risk_category VARCHAR(20),  -- 'low', 'medium', 'high', 'critical'
    churn_factors JSONB,
    
    -- Lifetime Value
    predicted_ltv_12mo FLOAT,
    ltv_confidence FLOAT,
    
    -- Segmentation
    segment VARCHAR(50),  -- 'champion', 'loyal', 'at_risk', 'churned', 'new'
    segment_score FLOAT,
    
    -- Next Purchase
    next_purchase_date DATE,
    next_purchase_confidence FLOAT,
    
    -- Behavior Metrics
    avg_order_value FLOAT,
    order_frequency_days FLOAT,
    days_since_last_order INTEGER,
    total_orders INTEGER,
    total_revenue FLOAT,
    
    -- Timestamps
    updated_at TIMESTAMP DEFAULT NOW(),
    last_order_date DATE
);

CREATE INDEX IF NOT EXISTS idx_customer_intelligence_business ON customer_intelligence_cache(business_id);
CREATE INDEX IF NOT EXISTS idx_customer_intelligence_churn ON customer_intelligence_cache(churn_risk_category) WHERE churn_risk_category IN ('high', 'critical');
CREATE INDEX IF NOT EXISTS idx_customer_intelligence_segment ON customer_intelligence_cache(segment);
CREATE INDEX IF NOT EXISTS idx_customer_intelligence_ltv ON customer_intelligence_cache(predicted_ltv_12mo DESC);

COMMENT ON TABLE customer_intelligence_cache IS 'Cached customer intelligence metrics for dashboard performance';

-- ============================================================================
-- Anomaly Detection Log
CREATE TABLE IF NOT EXISTS anomaly_detections (
    anomaly_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'invoice', 'payment', 'customer'
    entity_id VARCHAR(100) NOT NULL,
    business_id INTEGER,
    anomaly_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- 'low', 'medium', 'high', 'critical'
    details JSONB,
    detected_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    auto_resolved BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_anomaly_entity ON anomaly_detections(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_business ON anomaly_detections(business_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomaly_detections(severity) WHERE resolved_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_anomaly_unresolved ON anomaly_detections(detected_at DESC) WHERE resolved_at IS NULL;

COMMENT ON TABLE anomaly_detections IS 'Log of detected anomalies (fraud, errors, unusual patterns)';
COMMENT ON COLUMN anomaly_detections.details IS 'JSON: {"message": "...", "recommendation": "...", "contributing_factors": [...]}';

-- ============================================================================
-- Xero Contacts Cache (for ML features)
CREATE TABLE IF NOT EXISTS xero_contacts_cache (
    contact_id VARCHAR(100) NOT NULL,
    business_id INTEGER NOT NULL,
    name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    
    -- Metrics
    total_revenue FLOAT DEFAULT 0,
    order_count INTEGER DEFAULT 0,
    avg_order_value FLOAT DEFAULT 0,
    avg_payment_delay_days INTEGER DEFAULT 0,
    days_since_last_order INTEGER,
    last_order_date DATE,
    first_order_date DATE,
    
    -- Timestamps
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (contact_id, business_id)
);

CREATE INDEX IF NOT EXISTS idx_xero_contacts_business ON xero_contacts_cache(business_id);
CREATE INDEX IF NOT EXISTS idx_xero_contacts_revenue ON xero_contacts_cache(total_revenue DESC);
CREATE INDEX IF NOT EXISTS idx_xero_contacts_last_order ON xero_contacts_cache(days_since_last_order);

COMMENT ON TABLE xero_contacts_cache IS 'Cached Xero contact data with calculated metrics for ML features';

-- ============================================================================
-- Xero Invoices Cache (for ML features)
CREATE TABLE IF NOT EXISTS xero_invoices_cache (
    invoice_id VARCHAR(100) NOT NULL,
    business_id INTEGER NOT NULL,
    invoice_number VARCHAR(50),
    contact_id VARCHAR(100),
    contact_name VARCHAR(200),
    
    -- Dates
    date DATE,
    due_date DATE,
    payment_date DATE,
    
    -- Amounts
    total FLOAT DEFAULT 0,
    amount_due FLOAT DEFAULT 0,
    amount_paid FLOAT DEFAULT 0,
    
    -- Status
    status VARCHAR(50),  -- 'DRAFT', 'SUBMITTED', 'AUTHORISED', 'PAID', 'VOIDED'
    days_overdue INTEGER DEFAULT 0,
    
    -- Timestamps
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (invoice_id, business_id)
);

CREATE INDEX IF NOT EXISTS idx_xero_invoices_business ON xero_invoices_cache(business_id);
CREATE INDEX IF NOT EXISTS idx_xero_invoices_contact ON xero_invoices_cache(contact_id);
CREATE INDEX IF NOT EXISTS idx_xero_invoices_status ON xero_invoices_cache(status);
CREATE INDEX IF NOT EXISTS idx_xero_invoices_date ON xero_invoices_cache(date DESC);
CREATE INDEX IF NOT EXISTS idx_xero_invoices_overdue ON xero_invoices_cache(days_overdue) WHERE days_overdue > 0;

COMMENT ON TABLE xero_invoices_cache IS 'Cached Xero invoice data for ML predictions and analytics';

-- ============================================================================
-- Xero Payments Cache (for ML features)
CREATE TABLE IF NOT EXISTS xero_payments_cache (
    payment_id VARCHAR(100) NOT NULL,
    business_id INTEGER NOT NULL,
    invoice_id VARCHAR(100),
    invoice_number VARCHAR(50),
    contact_id VARCHAR(100),
    contact_name VARCHAR(200),
    
    -- Payment details
    date DATE,
    amount FLOAT DEFAULT 0,
    status VARCHAR(50),
    
    -- Timestamps
    updated_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (payment_id, business_id)
);

CREATE INDEX IF NOT EXISTS idx_xero_payments_business ON xero_payments_cache(business_id);
CREATE INDEX IF NOT EXISTS idx_xero_payments_invoice ON xero_payments_cache(invoice_id);
CREATE INDEX IF NOT EXISTS idx_xero_payments_contact ON xero_payments_cache(contact_id);
CREATE INDEX IF NOT EXISTS idx_xero_payments_date ON xero_payments_cache(date DESC);

COMMENT ON TABLE xero_payments_cache IS 'Cached Xero payment data for reconciliation and fraud detection';

-- ============================================================================
-- Success message
DO $$
BEGIN
    RAISE NOTICE '✅ ML Analytics schema migration completed successfully';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - ml_models (model storage)';
    RAISE NOTICE '  - ml_predictions (prediction cache)';
    RAISE NOTICE '  - customer_intelligence_cache (customer metrics)';
    RAISE NOTICE '  - anomaly_detections (fraud/error log)';
    RAISE NOTICE '  - xero_contacts_cache (Xero contact metrics)';
    RAISE NOTICE '  - xero_invoices_cache (Xero invoice data)';
    RAISE NOTICE '  - xero_payments_cache (Xero payment data)';
END $$;
