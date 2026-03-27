-- ============================================================================
-- Migration 038: Team System Refactor (March 26, 2026)
-- ============================================================================
-- PURPOSE: Restructure team management with proper Email + Team Name + Password model
-- Each team is tied to a primary user's email and has its own team name + password
-- Team members inherit credentials from primary user
-- ============================================================================

BEGIN;

-- Create teams table with Email + Team Name + Password structure
CREATE TABLE IF NOT EXISTS ai_infrastructure.teams (
    id SERIAL PRIMARY KEY,
    parent_user_id INT NOT NULL,
    parent_email VARCHAR(255) NOT NULL,        -- gerardo@company.com (for unique identification)
    team_name VARCHAR(100) NOT NULL,           -- sales_team, support_team
    team_password_hash TEXT NOT NULL,          -- Bcrypt hash of team password
    display_name VARCHAR(255),                 -- "Sales Team", "Support Operations"
    description TEXT,                          -- Purpose/notes
    color VARCHAR(7) DEFAULT '#3498db',        -- Sidebar color
    is_active BOOLEAN DEFAULT TRUE,
    member_count INT DEFAULT 0,                -- Cached count (for UI)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INT,
    
    CONSTRAINT fk_teams_parent_user FOREIGN KEY (parent_user_id) 
        REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    CONSTRAINT fk_teams_created_by FOREIGN KEY (created_by) 
        REFERENCES ai_infrastructure.users(id) ON DELETE SET NULL,
    CONSTRAINT teams_unique_per_email UNIQUE (parent_email, team_name)
);

-- Create team_members table (optional: for tracking team membership beyond just parent_user_id)
CREATE TABLE IF NOT EXISTS ai_infrastructure.team_members (
    id SERIAL PRIMARY KEY,
    team_id INT NOT NULL,
    parent_user_id INT NOT NULL,               -- Person using the team
    member_display_name VARCHAR(255),          -- "Sarah (Operations)", "Josh (Finance)"
    data_access_scope VARCHAR(50) DEFAULT 'own',  -- own | team | all
    usage_limit_daily INT DEFAULT 1000,        -- Max messages per day
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT fk_team_members_team FOREIGN KEY (team_id) 
        REFERENCES ai_infrastructure.teams(id) ON DELETE CASCADE,
    CONSTRAINT fk_team_members_user FOREIGN KEY (parent_user_id) 
        REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_teams_parent_user_id ON ai_infrastructure.teams(parent_user_id);
CREATE INDEX IF NOT EXISTS idx_teams_parent_email ON ai_infrastructure.teams(parent_email);
CREATE INDEX IF NOT EXISTS idx_teams_team_name ON ai_infrastructure.teams(team_name);
CREATE INDEX IF NOT EXISTS idx_teams_is_active ON ai_infrastructure.teams(is_active);
CREATE INDEX IF NOT EXISTS idx_teams_email_team_name ON ai_infrastructure.teams(parent_email, team_name);

CREATE INDEX IF NOT EXISTS idx_team_members_team_id ON ai_infrastructure.team_members(team_id);
CREATE INDEX IF NOT EXISTS idx_team_members_parent_user ON ai_infrastructure.team_members(parent_user_id);
CREATE INDEX IF NOT EXISTS idx_team_members_is_active ON ai_infrastructure.team_members(is_active);

-- Add team_id column to messages table (for team-based filtering)
ALTER TABLE sessions.messages ADD COLUMN IF NOT EXISTS team_id INT;
CREATE INDEX IF NOT EXISTS idx_messages_team_id ON sessions.messages(team_id);

-- Add team_id column to threads table
ALTER TABLE sessions.threads ADD COLUMN IF NOT EXISTS team_id INT;
CREATE INDEX IF NOT EXISTS idx_threads_team_id ON sessions.threads(team_id);
CREATE INDEX IF NOT EXISTS idx_threads_user_team_id ON sessions.threads(user_id, team_id);

-- Add comments
COMMENT ON TABLE ai_infrastructure.teams IS 
    'Login teams: Email + Team Name + Password. Each team is tied to a primary user email and has separate password. Team members inherit API credentials from primary user.';

COMMENT ON COLUMN ai_infrastructure.teams.parent_email IS 
    'Primary user email (gerardo@company.com). Used as unique identifier along with team_name. Constraint: (parent_email, team_name) must be unique.';

COMMENT ON COLUMN ai_infrastructure.teams.team_name IS 
    'Team login name (sales_team, support_team). Combined with parent_email for global uniqueness.';

COMMENT ON COLUMN ai_infrastructure.teams.team_password_hash IS 
    'Bcrypt hash of team password. Team members log in with: email + team_name + this_password.';

COMMENT ON TABLE ai_infrastructure.team_members IS 
    'Team member registry (optional tracking). Primarily for display names and data scope per member.';

-- Function to validate team credentials (email + team_name + password)
CREATE OR REPLACE FUNCTION ai_infrastructure.validate_team_login(
    p_email VARCHAR(255),
    p_team_name VARCHAR(100),
    p_password TEXT
)
RETURNS TABLE (
    success BOOLEAN,
    message TEXT,
    team_id INT,
    parent_user_id INT,
    team_name VARCHAR(100)
) AS $$
DECLARE
    v_team RECORD;
    v_password_matches BOOLEAN;
BEGIN
    -- Find team by email + team_name
    SELECT * INTO v_team FROM ai_infrastructure.teams
    WHERE parent_email = p_email AND team_name = p_team_name AND is_active = TRUE;
    
    IF v_team IS NULL THEN
        RETURN QUERY SELECT FALSE, 'Team not found or inactive', NULL::INT, NULL::INT, NULL::VARCHAR(100);
        RETURN;
    END IF;
    
    -- Verify password using pgcrypto
    -- Note: For bcrypt, you'll need to call Python/bcrypt in the application layer
    -- This function validates structure; app verifies bcrypt hash
    
    RETURN QUERY SELECT TRUE, 'Team found', v_team.id::INT, v_team.parent_user_id::INT, v_team.team_name::VARCHAR(100);
END;
$$ LANGUAGE plpgsql STABLE;

-- Function to get team credentials (parent user's API keys)
CREATE OR REPLACE FUNCTION ai_infrastructure.get_team_credentials(
    p_team_id INT
)
RETURNS TABLE (
    parent_user_id INT,
    parent_email VARCHAR(255),
    anthropic_api_key TEXT,
    openai_api_key TEXT,
    xero_client_id TEXT
) AS $$
DECLARE
    v_team RECORD;
BEGIN
    -- Get team
    SELECT * INTO v_team FROM ai_infrastructure.teams WHERE id = p_team_id;
    
    IF v_team IS NULL THEN
        RETURN;
    END IF;
    
    -- Return parent user's credentials
    RETURN QUERY
    SELECT 
        v_team.parent_user_id::INT,
        v_team.parent_email::VARCHAR(255),
        NULL::TEXT,  -- Credentials are retrieved from user_platform_credentials in app layer
        NULL::TEXT,
        NULL::TEXT;
END;
$$ LANGUAGE plpgsql STABLE;

-- Summary message
DO $$
BEGIN
    RAISE NOTICE '✅ Migration 038 Complete: Teams System Refactored';
    RAISE NOTICE '   Tables created:';
    RAISE NOTICE '   - ai_infrastructure.teams (Email + Team Name + Password)';
    RAISE NOTICE '   - ai_infrastructure.team_members (Optional member tracking)';
    RAISE NOTICE '   Columns added:';
    RAISE NOTICE '   - sessions.messages.team_id';
    RAISE NOTICE '   - sessions.threads.team_id';
    RAISE NOTICE '   Functions added:';
    RAISE NOTICE '   - validate_team_login()';
    RAISE NOTICE '   - get_team_credentials()';
END $$;

COMMIT;
