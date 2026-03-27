-- Message Persistence Schema
-- Stores direct messages and broadcasts for history/search

CREATE TABLE IF NOT EXISTS realtime_messages (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('direct', 'broadcast')),
    
    -- Sender info
    sender_user_id INTEGER NOT NULL,
    sender_user_name VARCHAR(255) NOT NULL,
    sender_session_token VARCHAR(255),
    
    -- Recipient info (NULL for broadcasts)
    recipient_user_id INTEGER,
    recipient_session_token VARCHAR(255),
    
    -- Message content
    message_text TEXT NOT NULL,
    message_metadata JSONB DEFAULT '{}',
    
    -- Delivery tracking
    room VARCHAR(100) DEFAULT 'synergy_board',
    delivered_to INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    read_by INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    delivered_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ
);

-- Create indexes separately
CREATE INDEX IF NOT EXISTS idx_messages_sender ON realtime_messages (sender_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_recipient ON realtime_messages (recipient_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_room ON realtime_messages (room, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_type ON realtime_messages (message_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_message_id ON realtime_messages (message_id);

-- Message reactions (quick replies)
CREATE TABLE IF NOT EXISTS message_reactions (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL REFERENCES realtime_messages(message_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    reaction_type VARCHAR(50) NOT NULL, -- 'thumbs_up', 'thumbs_down', 'check', 'question', 'heart', etc.
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(message_id, user_id, reaction_type)
);

-- Create indexes for message_reactions
CREATE INDEX IF NOT EXISTS idx_reactions_message ON message_reactions (message_id);
CREATE INDEX IF NOT EXISTS idx_reactions_user ON message_reactions (user_id);

-- Typing indicators log (optional, for analytics)
CREATE TABLE IF NOT EXISTS typing_indicators_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    room VARCHAR(100) NOT NULL,
    agent_id VARCHAR(50),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    duration_seconds INTEGER
);

-- Create indexes for typing_indicators_log
CREATE INDEX IF NOT EXISTS idx_typing_user ON typing_indicators_log (user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_typing_room ON typing_indicators_log (room, started_at DESC);

-- Message delivery status tracking
CREATE TABLE IF NOT EXISTS message_delivery_status (
    id BIGSERIAL PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('sent', 'delivered', 'read')),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(message_id, user_id, status)
);

-- Create indexes for message_delivery_status
CREATE INDEX IF NOT EXISTS idx_delivery_message ON message_delivery_status (message_id);
CREATE INDEX IF NOT EXISTS idx_delivery_user ON message_delivery_status (user_id, timestamp DESC);

-- Create notification preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    user_id INTEGER PRIMARY KEY,
    
    -- Notification toggles
    enable_direct_messages BOOLEAN DEFAULT TRUE,
    enable_broadcast_messages BOOLEAN DEFAULT TRUE,
    enable_agent_mentions BOOLEAN DEFAULT TRUE,
    enable_typing_indicators BOOLEAN DEFAULT TRUE,
    enable_sound BOOLEAN DEFAULT TRUE,
    
    -- Toast preferences
    toast_duration_seconds INTEGER DEFAULT 5,
    toast_position VARCHAR(20) DEFAULT 'bottom-left' CHECK (toast_position IN ('top-right', 'top-left', 'bottom-right', 'bottom-left')),
    auto_close_messages BOOLEAN DEFAULT FALSE,
    
    -- Do not disturb
    dnd_enabled BOOLEAN DEFAULT FALSE,
    dnd_start_time TIME,
    dnd_end_time TIME,
    
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for message search
CREATE INDEX IF NOT EXISTS idx_messages_fulltext ON realtime_messages USING gin(to_tsvector('english', message_text));
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON realtime_messages (created_at DESC);

-- Cleanup old messages (optional: run periodically)
-- DELETE FROM realtime_messages WHERE created_at < NOW() - INTERVAL '30 days';
