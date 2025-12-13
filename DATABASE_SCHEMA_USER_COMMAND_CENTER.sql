-- ============================================================
-- USER COMMAND CENTER - Workspace Persistence Schema
-- ============================================================
-- Purpose: Store per-user UI preferences for agent columns
-- Sync: localStorage (instant) + Database (cross-device)
-- Updated: December 12, 2025
-- ============================================================

-- Create user_command_center table
CREATE TABLE IF NOT EXISTS sessions.user_command_center (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    workspace_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    
    -- Ensure one workspace per user
    CONSTRAINT user_command_center_user_id_unique UNIQUE (user_id)
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_user_command_center_user_id 
    ON sessions.user_command_center USING btree (user_id);

-- Add GIN index for JSONB queries (fast searches within workspace_data)
CREATE INDEX IF NOT EXISTS idx_user_command_center_workspace_data 
    ON sessions.user_command_center USING gin (workspace_data);

-- Add comment explaining the table
COMMENT ON TABLE sessions.user_command_center IS 
    'Stores per-user workspace settings for AI agent columns: view modes, column widths, collapsed states, and column order.';

-- Add column comments
COMMENT ON COLUMN sessions.user_command_center.workspace_data IS 
    'JSONB structure:
    {
        "agents": {
            "1": {
                "viewMode": "ai-collapsed",
                "columnWidth": 613,
                "collapsed": false,
                "order": 0
            },
            "2": {
                "viewMode": "ai-user",
                "columnWidth": 800,
                "collapsed": false,
                "order": 1
            }
        },
        "prime": {
            "viewMode": "all-expanded"
        },
        "columnOrder": [1, 2, 3],
        "lastSyncedAt": "2025-12-12T10:30:00Z"
    }';

-- ============================================================
-- EXAMPLE DATA
-- ============================================================

-- Insert example workspace for user 1
INSERT INTO sessions.user_command_center (user_id, workspace_data)
VALUES (
    1,
    '{
        "agents": {
            "1": {
                "viewMode": "ai-collapsed",
                "columnWidth": 613,
                "collapsed": false,
                "order": 0
            },
            "2": {
                "viewMode": "ai-user",
                "columnWidth": 450,
                "collapsed": false,
                "order": 1
            },
            "3": {
                "viewMode": "all-expanded",
                "columnWidth": 800,
                "collapsed": true,
                "order": 2
            }
        },
        "prime": {
            "viewMode": "ai-expanded"
        },
        "columnOrder": [1, 2, 3],
        "lastSyncedAt": "2025-12-12T10:30:00.000Z"
    }'::jsonb
)
ON CONFLICT (user_id) 
DO UPDATE SET 
    workspace_data = EXCLUDED.workspace_data,
    updated_at = NOW();

-- ============================================================
-- QUERY EXAMPLES
-- ============================================================

-- Get user's workspace settings
SELECT workspace_data 
FROM sessions.user_command_center 
WHERE user_id = 1;

-- Get specific agent settings
SELECT workspace_data->'agents'->'1' AS agent_1_settings
FROM sessions.user_command_center 
WHERE user_id = 1;

-- Get all agents' view modes
SELECT 
    user_id,
    jsonb_object_keys(workspace_data->'agents') AS agent_id,
    workspace_data->'agents'->jsonb_object_keys(workspace_data->'agents')->>'viewMode' AS view_mode
FROM sessions.user_command_center
WHERE user_id = 1;

-- Update single agent's settings (merge with existing)
UPDATE sessions.user_command_center
SET 
    workspace_data = jsonb_set(
        workspace_data,
        '{agents,1}',
        '{"viewMode": "ai-collapsed", "columnWidth": 750, "collapsed": false, "order": 0}'::jsonb
    ),
    updated_at = NOW()
WHERE user_id = 1;

-- Update entire workspace (replace all settings)
UPDATE sessions.user_command_center
SET 
    workspace_data = '{
        "agents": {
            "1": {"viewMode": "ai-collapsed", "columnWidth": 613, "collapsed": false, "order": 0}
        },
        "prime": {"viewMode": "all-expanded"},
        "columnOrder": [1],
        "lastSyncedAt": "2025-12-12T10:35:00.000Z"
    }'::jsonb,
    updated_at = NOW()
WHERE user_id = 1;

-- Delete user's workspace (reset to defaults)
DELETE FROM sessions.user_command_center WHERE user_id = 1;

-- ============================================================
-- COLUMN WIDTH VALIDATION
-- ============================================================

-- Column width options:
-- 1. Named sizes: "collapsed" (60px), "default" (400px), "wide" (600px), "extra-wide" (800px)
-- 2. Custom px: Any integer >= 400 (e.g., 613, 750, 1200)
-- 3. Max width: 2000px (prevent oversized columns)
-- 4. Min width: 400px (prevent unusable columns)

-- Note: Validation is done via trigger (CHECK constraints can't use subqueries)
-- The trigger will validate column widths before INSERT/UPDATE

CREATE OR REPLACE FUNCTION sessions.validate_workspace_data()
RETURNS TRIGGER AS $$
DECLARE
    agent_key TEXT;
    agent_value JSONB;
    column_width_value JSONB;
    width_int INTEGER;
BEGIN
    -- Validate column widths for all agents
    FOR agent_key, agent_value IN SELECT * FROM jsonb_each(NEW.workspace_data->'agents')
    LOOP
        column_width_value := agent_value->'columnWidth';
        
        -- Skip if columnWidth not present
        CONTINUE WHEN column_width_value IS NULL;
        
        -- If it's a number, validate range
        IF jsonb_typeof(column_width_value) = 'number' THEN
            width_int := (column_width_value#>>'{}')::integer;
            IF width_int < 400 OR width_int > 2000 THEN
                RAISE EXCEPTION 'Column width for agent % must be between 400 and 2000 pixels (got: %)', 
                    agent_key, width_int;
            END IF;
        
        -- If it's a string, validate named sizes
        ELSIF jsonb_typeof(column_width_value) = 'string' THEN
            IF (column_width_value#>>'{}') NOT IN ('collapsed', 'default', 'wide', 'extra-wide') THEN
                RAISE EXCEPTION 'Invalid column width name for agent %: %. Valid names: collapsed, default, wide, extra-wide',
                    agent_key, (column_width_value#>>'{}');
            END IF;
        END IF;
    END LOOP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_validate_workspace_data
    BEFORE INSERT OR UPDATE ON sessions.user_command_center
    FOR EACH ROW
    EXECUTE FUNCTION sessions.validate_workspace_data();

-- ============================================================
-- MIGRATION FROM EXISTING THREADS TABLE (OPTIONAL)
-- ============================================================

-- OPTIONAL: Migrate location data from threads table to user_command_center
-- This creates initial workspace settings based on which threads are currently loaded

-- NOTE: This migration is OPTIONAL and only needed if you want to pre-populate
-- workspace settings based on existing thread assignments. New users will get
-- default settings automatically when they first use the system.

INSERT INTO sessions.user_command_center (user_id, workspace_data)
SELECT 
    user_id,
    jsonb_build_object(
        'agents', jsonb_object_agg(
            agent_id::text,
            jsonb_build_object(
                'viewMode', 'all-expanded',  -- Default view mode
                'columnWidth', 400,           -- Default width
                'collapsed', false
            )
        ),
        'prime', jsonb_build_object('viewMode', 'all-expanded'),
        'columnOrder', array_agg(agent_id ORDER BY agent_id),
        'lastSyncedAt', NOW()
    ) AS workspace_data
FROM (
    SELECT DISTINCT
        user_id,
        SUBSTRING(location FROM 'agent-(\d+)')::integer AS agent_id
    FROM sessions.threads
    WHERE 
        location ~ '^agent-\d+$'  -- Only threads currently loaded in agents
        AND user_id IS NOT NULL
) AS agent_locations
GROUP BY user_id
ON CONFLICT (user_id) DO NOTHING;  -- Don't overwrite existing workspaces

-- Explanation:
-- - Extracts agent numbers from location field (e.g., 'agent-3' → 3)
-- - Creates workspace entry for users who have threads loaded in agents
-- - Sets default view modes and widths
-- - columnOrder is sorted by agent ID (agent-1, agent-2, agent-3, etc.)
-- - Does NOT include 'order' field per agent (not needed for column display order)

-- ============================================================
-- SUPABASE ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS
ALTER TABLE sessions.user_command_center ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own workspace
CREATE POLICY user_command_center_select_policy ON sessions.user_command_center
    FOR SELECT
    USING (user_id = current_setting('app.current_user_id')::integer);

-- Policy: Users can only update their own workspace
CREATE POLICY user_command_center_update_policy ON sessions.user_command_center
    FOR UPDATE
    USING (user_id = current_setting('app.current_user_id')::integer);

-- Policy: Users can insert their own workspace
CREATE POLICY user_command_center_insert_policy ON sessions.user_command_center
    FOR INSERT
    WITH CHECK (user_id = current_setting('app.current_user_id')::integer);

-- Policy: Users can delete their own workspace
CREATE POLICY user_command_center_delete_policy ON sessions.user_command_center
    FOR DELETE
    USING (user_id = current_setting('app.current_user_id')::integer);

-- ============================================================
-- TRIGGER: Auto-update updated_at timestamp
-- ============================================================

CREATE OR REPLACE FUNCTION sessions.update_user_command_center_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_user_command_center_updated_at
    BEFORE UPDATE ON sessions.user_command_center
    FOR EACH ROW
    EXECUTE FUNCTION sessions.update_user_command_center_updated_at();

-- ============================================================
-- UTILITY FUNCTIONS
-- ============================================================

-- Function: Get user's workspace settings
CREATE OR REPLACE FUNCTION sessions.get_user_workspace(p_user_id INTEGER)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT workspace_data 
        FROM sessions.user_command_center 
        WHERE user_id = p_user_id
    );
END;
$$ LANGUAGE plpgsql;

-- Function: Save user's workspace settings (upsert)
CREATE OR REPLACE FUNCTION sessions.save_user_workspace(
    p_user_id INTEGER,
    p_workspace_data JSONB
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO sessions.user_command_center (user_id, workspace_data)
    VALUES (p_user_id, p_workspace_data)
    ON CONFLICT (user_id) 
    DO UPDATE SET 
        workspace_data = EXCLUDED.workspace_data,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- STORAGE SIZE ANALYSIS
-- ============================================================

-- Estimate storage per user:
-- - Average workspace: ~500 bytes (5 agents × 100 bytes each)
-- - Max workspace: ~2KB (20 agents × 100 bytes each)
-- - 1000 users: ~500KB to 2MB
-- - 10,000 users: ~5MB to 20MB
-- ✅ Very efficient storage

-- Query to check workspace sizes:
SELECT 
    user_id,
    pg_column_size(workspace_data) AS size_bytes,
    pg_size_pretty(pg_column_size(workspace_data)::bigint) AS size_human,
    jsonb_array_length(workspace_data->'columnOrder') AS agent_count
FROM sessions.user_command_center
ORDER BY size_bytes DESC;

-- ============================================================
-- TESTING QUERIES
-- ============================================================

-- Test 1: Create workspace for user 999
SELECT sessions.save_user_workspace(
    999,
    '{
        "agents": {
            "1": {"viewMode": "ai-collapsed", "columnWidth": 613, "collapsed": false, "order": 0}
        },
        "prime": {"viewMode": "all-expanded"},
        "columnOrder": [1]
    }'::jsonb
);

-- Test 2: Retrieve workspace for user 999
SELECT sessions.get_user_workspace(999);

-- Test 3: Update agent 1's view mode
UPDATE sessions.user_command_center
SET workspace_data = jsonb_set(
    workspace_data,
    '{agents,1,viewMode}',
    '"ai-user"'
)
WHERE user_id = 999;

-- Test 4: Add new agent to workspace
UPDATE sessions.user_command_center
SET workspace_data = jsonb_set(
    workspace_data,
    '{agents,2}',
    '{"viewMode": "all-collapsed", "columnWidth": 450, "collapsed": false, "order": 1}'::jsonb
)
WHERE user_id = 999;

-- Test 5: Clean up test data
DELETE FROM sessions.user_command_center WHERE user_id = 999;

-- ============================================================
-- DEPLOYMENT CHECKLIST
-- ============================================================

-- [ ] Run CREATE TABLE statement on Supabase
-- [ ] Run CREATE INDEX statements
-- [ ] Run RLS policies
-- [ ] Run trigger creation
-- [ ] Run utility functions
-- [ ] Test with example data
-- [ ] Verify RLS works (users can't see other users' workspaces)
-- [ ] Monitor storage size after 1 week

-- ============================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================

-- DROP TRIGGER IF EXISTS trigger_update_user_command_center_updated_at ON sessions.user_command_center;
-- DROP FUNCTION IF EXISTS sessions.update_user_command_center_updated_at();
-- DROP FUNCTION IF EXISTS sessions.save_user_workspace(INTEGER, JSONB);
-- DROP FUNCTION IF EXISTS sessions.get_user_workspace(INTEGER);
-- DROP TABLE IF EXISTS sessions.user_command_center CASCADE;
