-- Migration: Create automation_workflows table
-- Description: Stores user-created automation workflows with canvas data and execution stats
-- Date: 2025-12-21

-- Create the main automation_workflows table
CREATE TABLE IF NOT EXISTS public.automation_workflows (
    workflow_id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(250) NOT NULL,
    description TEXT NULL,
    category VARCHAR(50) NULL,
    workflow_json TEXT NOT NULL,
    canvas_data TEXT NULL,
    enabled BOOLEAN NULL DEFAULT true,
    version VARCHAR(20) NULL DEFAULT '1.0',
    created_at TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT CURRENT_TIMESTAMP,
    last_run_at TIMESTAMP WITHOUT TIME ZONE NULL,
    run_count INTEGER NULL DEFAULT 0,
    success_count INTEGER NULL DEFAULT 0,
    error_count INTEGER NULL DEFAULT 0,
    CONSTRAINT automation_workflows_pkey PRIMARY KEY (workflow_id),
    CONSTRAINT automation_workflows_slug_key UNIQUE (slug)
) TABLESPACE pg_default;

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_workflows_user 
    ON public.automation_workflows USING btree (user_id) 
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_workflows_slug 
    ON public.automation_workflows USING btree (slug) 
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_workflows_category 
    ON public.automation_workflows USING btree (category) 
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_workflows_enabled 
    ON public.automation_workflows USING btree (enabled) 
    TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_workflows_updated 
    ON public.automation_workflows USING btree (updated_at DESC) 
    TABLESPACE pg_default;

-- Create trigger function for updated_at timestamp
CREATE OR REPLACE FUNCTION update_automation_workflows_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS automation_workflows_updated_at_trigger ON public.automation_workflows;
CREATE TRIGGER automation_workflows_updated_at_trigger 
    BEFORE UPDATE ON public.automation_workflows 
    FOR EACH ROW 
    EXECUTE FUNCTION update_automation_workflows_updated_at();

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.automation_workflows TO your_app_user;

COMMENT ON TABLE public.automation_workflows IS 'Stores user-created automation workflows with visual canvas data';
COMMENT ON COLUMN public.automation_workflows.workflow_json IS 'JSON definition of workflow nodes and connections';
COMMENT ON COLUMN public.automation_workflows.canvas_data IS 'Canvas positioning and visual layout data';
COMMENT ON COLUMN public.automation_workflows.run_count IS 'Total number of times workflow has been executed';
COMMENT ON COLUMN public.automation_workflows.success_count IS 'Number of successful workflow executions';
COMMENT ON COLUMN public.automation_workflows.error_count IS 'Number of failed workflow executions';
