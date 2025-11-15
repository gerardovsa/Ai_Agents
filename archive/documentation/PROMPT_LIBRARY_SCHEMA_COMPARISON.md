# Prompt Library - Schema Comparison & Migration Plan

## Current Implementation vs Required Changes

### 📊 What We Have Now (from prompt_injection_manager.py)

**Current Tables:**
```sql
-- Table 1: user_custom_prompts (SIMPLE VERSION)
CREATE TABLE user_custom_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt_name TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    category TEXT,
    is_quick_action BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)

-- Table 2: user_prompt_preferences (SIMPLE VERSION)
CREATE TABLE user_prompt_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preference_name TEXT NOT NULL,
    quick_actions TEXT,        -- JSON: ["expert_coder", "debugger"]
    library_prompts TEXT,       -- JSON: ["system_architect"]
    custom_prompt TEXT,         -- Free-form text
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

**What's Missing:**
- ❌ No sharing mechanism (can't share with other users)
- ❌ No workspace integration (can't share with workspace)
- ❌ No public/private visibility (can't make prompts public)
- ❌ No search optimization (no slugs, keywords, FTS)
- ❌ No UI metadata (icons, colors, badges, tooltips)
- ❌ No ratings/reviews (can't rate prompts)
- ❌ No analytics (usage tracking is basic)
- ❌ No trending algorithm (can't surface popular prompts)
- ❌ No related prompts (can't recommend similar)
- ❌ No version control (can't track prompt evolution)

---

## 🎯 What We Need (Full Implementation)

### Required Tables

#### 1. Enhanced Prompt Library Table

```sql
CREATE TABLE IF NOT EXISTS prompt_library (
    -- IDENTITY
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_key TEXT NOT NULL UNIQUE,        -- 'expert_coder', 'user_123_sql_optimizer'
    prompt_slug TEXT NOT NULL UNIQUE,       -- ⭐ NEW: 'expert-coder', 'sql-optimizer'
    prompt_name TEXT NOT NULL,              -- 'Expert Coder', 'SQL Optimizer'
    
    -- OWNERSHIP & VISIBILITY
    created_by_user_id INTEGER NOT NULL,
    workspace_id INTEGER,                   -- ⭐ NEW: NULL = personal, value = workspace
    visibility TEXT NOT NULL DEFAULT 'private',  -- ⭐ NEW: 'private', 'shared', 'workspace', 'public'
    is_system_prompt BOOLEAN DEFAULT 0,     -- ⭐ NEW: System prompts can't be deleted
    
    -- CONTENT
    prompt_text TEXT NOT NULL,
    prompt_description TEXT,
    short_description TEXT,                 -- ⭐ NEW: For card previews (50-100 chars)
    preview_text TEXT,                      -- ⭐ NEW: First few lines of prompt
    examples TEXT,                          -- ⭐ NEW: JSON array of usage examples
    
    -- CATEGORIZATION
    category TEXT NOT NULL,                 -- 'development', 'analysis', 'data', etc.
    subcategory TEXT,                       -- ⭐ NEW: More specific categorization
    prompt_type TEXT NOT NULL,              -- 'quick_action', 'library', 'template', 'custom'
    tags TEXT,                              -- JSON: ["python", "sql", "optimization"]
    search_keywords TEXT,                   -- ⭐ NEW: Hidden keywords for search
    
    -- UI/UX PROPERTIES
    icon TEXT,                              -- '⚡', '🔍', '🐛'
    display_color TEXT,                     -- ⭐ NEW: '#007bff'
    badge_text TEXT,                        -- ⭐ NEW: 'NEW', 'TRENDING', 'PRO'
    badge_color TEXT,                       -- ⭐ NEW: '#ff5722'
    tooltip_text TEXT,                      -- ⭐ NEW: Hover text
    banner_image_url TEXT,                  -- ⭐ NEW: Optional image
    sort_order INTEGER DEFAULT 0,
    
    -- USAGE & ANALYTICS
    use_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,           -- ⭐ NEW: Detail page views
    share_count INTEGER DEFAULT 0,
    clone_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- RATINGS & TRENDING
    total_ratings INTEGER DEFAULT 0,        -- ⭐ NEW: Number of ratings
    average_rating REAL DEFAULT 0.0,        -- ⭐ NEW: Average (0-5)
    effectiveness_score REAL DEFAULT 0.0,
    trending_score REAL DEFAULT 0.0,        -- ⭐ NEW: Calculated score
    last_trending_update TIMESTAMP,         -- ⭐ NEW: When score calculated
    
    -- FEATURES & PERMISSIONS
    is_featured BOOLEAN DEFAULT 0,          -- ⭐ NEW: Featured on homepage
    featured_order INTEGER DEFAULT 0,       -- ⭐ NEW: Order in featured section
    clone_enabled BOOLEAN DEFAULT 1,        -- ⭐ NEW: Allow cloning
    edit_enabled BOOLEAN DEFAULT 1,         -- ⭐ NEW: Allow editing
    
    -- RELATIONSHIPS
    parent_prompt_id INTEGER,               -- For cloned prompts
    related_prompt_ids TEXT,                -- ⭐ NEW: JSON array of related IDs
    
    -- VERSION CONTROL
    version INTEGER DEFAULT 1,              -- ⭐ NEW: Version number
    changelog TEXT,                         -- ⭐ NEW: JSON array of changes
    prerequisites TEXT,                     -- ⭐ NEW: Required setup (markdown)
    
    -- METADATA
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,                   -- ⭐ NEW: Soft delete
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE SET NULL
);

-- INDEXES (14 total)
CREATE INDEX idx_prompt_library_user ON prompt_library(created_by_user_id);
CREATE INDEX idx_prompt_library_workspace ON prompt_library(workspace_id);
CREATE INDEX idx_prompt_library_visibility ON prompt_library(visibility);
CREATE INDEX idx_prompt_library_category ON prompt_library(category);
CREATE INDEX idx_prompt_library_type ON prompt_library(prompt_type);
CREATE INDEX idx_prompt_library_key ON prompt_library(prompt_key);
CREATE INDEX idx_prompt_library_slug ON prompt_library(prompt_slug);
CREATE INDEX idx_prompt_library_active ON prompt_library(is_active, deleted_at);
CREATE INDEX idx_prompt_library_featured ON prompt_library(is_featured, featured_order);
CREATE INDEX idx_prompt_library_trending ON prompt_library(trending_score DESC);
CREATE INDEX idx_prompt_library_rating ON prompt_library(average_rating DESC);
CREATE INDEX idx_prompt_library_views ON prompt_library(view_count DESC);
CREATE INDEX idx_prompt_library_usage ON prompt_library(use_count DESC);
CREATE INDEX idx_prompt_library_search ON prompt_library(prompt_name, search_keywords);
```

#### 2. Prompt Shares Table (COMPLETELY NEW)

```sql
CREATE TABLE IF NOT EXISTS prompt_shares (
    share_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    shared_by_user_id INTEGER NOT NULL,
    
    -- TARGET (one will be populated)
    shared_with_user_id INTEGER,           -- Specific user
    shared_with_workspace_id INTEGER,      -- Entire workspace
    share_scope TEXT NOT NULL,             -- 'user', 'workspace', 'public'
    
    -- PERMISSIONS
    permission TEXT NOT NULL DEFAULT 'view',  -- 'view', 'use', 'edit', 'clone'
    can_reshare BOOLEAN DEFAULT 0,
    can_modify BOOLEAN DEFAULT 0,
    
    -- SHARING LINK
    share_link TEXT UNIQUE,
    share_token TEXT UNIQUE,
    
    -- TRACKING
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    
    -- STATUS
    is_active BOOLEAN DEFAULT 1,
    revoked_at TIMESTAMP,
    revoked_by_user_id INTEGER,
    revoke_reason TEXT,
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (shared_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_with_workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (revoked_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_prompt_shares_prompt ON prompt_shares(prompt_id);
CREATE INDEX idx_prompt_shares_shared_by ON prompt_shares(shared_by_user_id);
CREATE INDEX idx_prompt_shares_shared_with_user ON prompt_shares(shared_with_user_id);
CREATE INDEX idx_prompt_shares_shared_with_workspace ON prompt_shares(shared_with_workspace_id);
CREATE INDEX idx_prompt_shares_scope ON prompt_shares(share_scope);
CREATE INDEX idx_prompt_shares_active ON prompt_shares(is_active);
```

#### 3. Prompt Ratings Table (COMPLETELY NEW)

```sql
CREATE TABLE IF NOT EXISTS prompt_ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    review_title TEXT,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified_user BOOLEAN DEFAULT 0,  -- Has actually used the prompt
    
    UNIQUE(prompt_id, user_id),
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_prompt_ratings_prompt ON prompt_ratings(prompt_id);
CREATE INDEX idx_prompt_ratings_user ON prompt_ratings(user_id);
CREATE INDEX idx_prompt_ratings_rating ON prompt_ratings(rating);
```

#### 4. Prompt Views Table (COMPLETELY NEW)

```sql
CREATE TABLE IF NOT EXISTS prompt_views (
    view_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    view_duration_seconds INTEGER,
    converted_to_use BOOLEAN DEFAULT 0,  -- Did they use it after viewing?
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_prompt_views_prompt ON prompt_views(prompt_id);
CREATE INDEX idx_prompt_views_user ON prompt_views(user_id);
CREATE INDEX idx_prompt_views_timestamp ON prompt_views(viewed_at);
```

#### 5. Enhanced Usage History

```sql
CREATE TABLE IF NOT EXISTS prompt_usage_history (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    used_by_user_id INTEGER NOT NULL,
    thread_id INTEGER,
    message_id INTEGER,
    
    -- CONTEXT
    request_context TEXT,                  -- Original user request (truncated)
    combined_prompts TEXT,                 -- JSON: All prompts used together
    
    -- RESULTS
    success BOOLEAN,
    user_feedback_score INTEGER,           -- 1-5 rating
    user_feedback_text TEXT,
    
    -- TIMING
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    
    -- AI DETAILS
    ai_model TEXT,
    ai_temperature REAL,
    tokens_used INTEGER,
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (used_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE SET NULL
);

CREATE INDEX idx_usage_history_prompt ON prompt_usage_history(prompt_id);
CREATE INDEX idx_usage_history_user ON prompt_usage_history(used_by_user_id);
CREATE INDEX idx_usage_history_thread ON prompt_usage_history(thread_id);
CREATE INDEX idx_usage_history_timestamp ON prompt_usage_history(used_at);
```

#### 6. Enhanced Prompt Preferences

```sql
CREATE TABLE IF NOT EXISTS prompt_preferences (
    preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    workspace_id INTEGER,
    
    preference_name TEXT NOT NULL,
    preference_key TEXT NOT NULL,          -- ⭐ NEW: Unique identifier
    description TEXT,                      -- ⭐ NEW: What this preference is for
    
    quick_actions TEXT,                    -- JSON: ["expert_coder", "debugger"]
    library_prompts TEXT,                  -- JSON: ["system_architect"]
    custom_prompt TEXT,
    
    use_count INTEGER DEFAULT 0,           -- ⭐ NEW: How often used
    last_used_at TIMESTAMP,                -- ⭐ NEW: Last usage
    is_favorite BOOLEAN DEFAULT 0,         -- ⭐ NEW: Pinned to top
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE
);

CREATE INDEX idx_prompt_preferences_user ON prompt_preferences(user_id);
CREATE INDEX idx_prompt_preferences_workspace ON prompt_preferences(workspace_id);
CREATE INDEX idx_prompt_preferences_key ON prompt_preferences(preference_key);
CREATE INDEX idx_prompt_preferences_favorite ON prompt_preferences(is_favorite);
```

#### 7. Prompt Categories (COMPLETELY NEW)

```sql
CREATE TABLE IF NOT EXISTS prompt_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_key TEXT NOT NULL UNIQUE,     -- 'development', 'analysis'
    category_name TEXT NOT NULL,           -- 'Development', 'Analysis'
    category_description TEXT,
    
    icon TEXT,                             -- '💻', '📊'
    color TEXT,                            -- '#007bff'
    sort_order INTEGER DEFAULT 0,
    
    parent_category_id INTEGER,            -- Hierarchical categories
    
    is_active BOOLEAN DEFAULT 1,
    is_system_category BOOLEAN DEFAULT 0,  -- Built-in categories
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_category_id) REFERENCES prompt_categories(category_id) ON DELETE SET NULL
);

CREATE INDEX idx_categories_key ON prompt_categories(category_key);
CREATE INDEX idx_categories_parent ON prompt_categories(parent_category_id);
CREATE INDEX idx_categories_active ON prompt_categories(is_active);
```

#### 8. Full-Text Search (COMPLETELY NEW)

```sql
-- Virtual table for fast full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS prompt_search_fts USING fts5(
    prompt_id UNINDEXED,
    prompt_name,
    prompt_description,
    short_description,
    search_keywords,
    tags,
    content='prompt_library',
    content_rowid='prompt_id'
);

-- Triggers to keep FTS index synchronized
CREATE TRIGGER prompt_fts_insert AFTER INSERT ON prompt_library BEGIN
    INSERT INTO prompt_search_fts(
        prompt_id, prompt_name, prompt_description, 
        short_description, search_keywords, tags
    )
    VALUES (
        new.prompt_id, new.prompt_name, new.prompt_description,
        new.short_description, new.search_keywords, new.tags
    );
END;

CREATE TRIGGER prompt_fts_update AFTER UPDATE ON prompt_library BEGIN
    UPDATE prompt_search_fts 
    SET prompt_name = new.prompt_name,
        prompt_description = new.prompt_description,
        short_description = new.short_description,
        search_keywords = new.search_keywords,
        tags = new.tags
    WHERE prompt_id = new.prompt_id;
END;

CREATE TRIGGER prompt_fts_delete AFTER DELETE ON prompt_library BEGIN
    DELETE FROM prompt_search_fts WHERE prompt_id = old.prompt_id;
END;
```

---

## 🔄 Migration Strategy

### Phase 1: Core Tables (Day 1)
```
✅ Create prompt_library (enhanced version)
✅ Create prompt_shares (sharing mechanism)
✅ Migrate data from user_custom_prompts → prompt_library
✅ Create indexes
```

### Phase 2: Analytics & Search (Day 2)
```
✅ Create prompt_ratings (user reviews)
✅ Create prompt_views (view tracking)
✅ Create prompt_usage_history (enhanced)
✅ Create prompt_search_fts (full-text search)
✅ Create triggers for FTS sync
```

### Phase 3: Organization (Day 3)
```
✅ Create prompt_categories (category management)
✅ Update prompt_preferences (enhanced version)
✅ Seed system categories
✅ Seed 16 quick actions + 6 library prompts
```

### Phase 4: Testing & Validation (Day 4)
```
✅ Test sharing workflow
✅ Test search functionality
✅ Test trending algorithm
✅ Test recommendation engine
✅ Validate all indexes
```

---

## 📝 Column-by-Column Comparison

| Column Name | Current | Required | Purpose |
|-------------|---------|----------|---------|
| **IDENTITY** |
| `prompt_id` | ❌ | ✅ | Primary key |
| `id` | ✅ | ❌ | Renamed to prompt_id |
| `prompt_key` | ❌ | ✅ | API identifier ('expert_coder') |
| `prompt_slug` | ❌ | ✅ | URL-friendly ('expert-coder') |
| `prompt_name` | ✅ | ✅ | Display name |
| **OWNERSHIP** |
| `user_id` | ✅ | ❌ | Renamed to created_by_user_id |
| `created_by_user_id` | ❌ | ✅ | Owner of prompt |
| `workspace_id` | ❌ | ✅ | Workspace association |
| `visibility` | ❌ | ✅ | private/shared/workspace/public |
| `is_system_prompt` | ❌ | ✅ | Built-in prompts |
| **CONTENT** |
| `prompt_text` | ✅ | ✅ | Full prompt content |
| `prompt_description` | ❌ | ✅ | Long description |
| `short_description` | ❌ | ✅ | Card preview (50-100 chars) |
| `preview_text` | ❌ | ✅ | First few lines |
| `examples` | ❌ | ✅ | Usage examples |
| **CATEGORIZATION** |
| `category` | ✅ | ✅ | Main category |
| `subcategory` | ❌ | ✅ | Sub-category |
| `prompt_type` | ❌ | ✅ | quick_action/library/template |
| `is_quick_action` | ✅ | ❌ | Replaced by prompt_type |
| `tags` | ❌ | ✅ | JSON keywords |
| `search_keywords` | ❌ | ✅ | Hidden search terms |
| **UI/UX** |
| `icon` | ❌ | ✅ | Emoji icon |
| `display_color` | ❌ | ✅ | UI color |
| `badge_text` | ❌ | ✅ | 'NEW', 'TRENDING' |
| `badge_color` | ❌ | ✅ | Badge color |
| `tooltip_text` | ❌ | ✅ | Hover text |
| `banner_image_url` | ❌ | ✅ | Optional image |
| `sort_order` | ❌ | ✅ | Display order |
| **ANALYTICS** |
| `use_count` | ❌ | ✅ | Usage count |
| `view_count` | ❌ | ✅ | Detail views |
| `share_count` | ❌ | ✅ | Shares count |
| `clone_count` | ❌ | ✅ | Clones count |
| `last_used_at` | ❌ | ✅ | Last usage timestamp |
| **RATINGS** |
| `total_ratings` | ❌ | ✅ | Number of ratings |
| `average_rating` | ❌ | ✅ | Average (0-5) |
| `effectiveness_score` | ❌ | ✅ | User feedback score |
| `trending_score` | ❌ | ✅ | Trending algorithm |
| `last_trending_update` | ❌ | ✅ | Score calculation time |
| **FEATURES** |
| `is_featured` | ❌ | ✅ | Featured on homepage |
| `featured_order` | ❌ | ✅ | Featured sort order |
| `clone_enabled` | ❌ | ✅ | Allow cloning |
| `edit_enabled` | ❌ | ✅ | Allow editing |
| **RELATIONSHIPS** |
| `parent_prompt_id` | ❌ | ✅ | Cloned from |
| `related_prompt_ids` | ❌ | ✅ | Related prompts |
| **VERSION** |
| `version` | ❌ | ✅ | Version number |
| `changelog` | ❌ | ✅ | Change history |
| `prerequisites` | ❌ | ✅ | Required setup |
| **METADATA** |
| `created_at` | ✅ | ✅ | Creation time |
| `updated_at` | ❌ | ✅ | Last update |
| `deleted_at` | ❌ | ✅ | Soft delete |
| `is_active` | ❌ | ✅ | Active status |

**Summary:**
- Current: 6 columns
- Required: 50 columns
- **+44 new columns needed**

---

## 🎯 Critical vs Nice-to-Have

### CRITICAL (Must Have for MVP):
```
✅ prompt_slug          - URL sharing
✅ visibility           - Sharing permissions
✅ workspace_id         - Workspace integration
✅ prompt_shares table  - Sharing mechanism
✅ search_keywords      - Search functionality
✅ short_description    - UI card display
✅ icon                 - UI display
✅ prompt_type          - Quick action vs library
✅ average_rating       - Quality indicator
✅ trending_score       - Discovery
```

### NICE TO HAVE (Can Add Later):
```
⚪ banner_image_url     - Visual appeal
⚪ badge_text/color     - UI polish
⚪ tooltip_text         - Better UX
⚪ view_count           - Analytics
⚪ related_prompt_ids   - Recommendations
⚪ examples             - Better docs
⚪ changelog            - Version history
⚪ prerequisites        - Setup instructions
```

---

## 🚀 Implementation Recommendation

**Option 1: Full Migration (Recommended)**
- Create all new tables from scratch
- Migrate existing data
- **Timeline:** 5 days
- **Result:** Complete feature set

**Option 2: Phased Approach**
- Phase 1: Core tables + sharing (2 days)
- Phase 2: Search + analytics (2 days)
- Phase 3: Polish + features (1 day)
- **Timeline:** 5 days (same)
- **Result:** Complete feature set

**Option 3: MVP First**
- Only critical columns (10 columns)
- Only prompt_library + prompt_shares tables
- Basic search, no FTS
- **Timeline:** 2 days
- **Result:** Basic working system, missing polish

**Recommendation:** **Option 1 (Full Migration)** - Same timeline as Option 2, but cleaner implementation and no technical debt.

---

## Next Steps

1. **Review & Approve** - Confirm schema design
2. **Create Migration Script** - Generate SQL with data migration
3. **Update Manager** - Modify prompt_injection_manager.py
4. **Add API Routes** - Implement sharing, search, ratings endpoints
5. **Build UI** - Implement Quick Actions bar and Prompt Library modal
6. **Test** - End-to-end testing
7. **Deploy** - Roll out to production

**Status:** ✅ Design Complete - Ready for implementation approval
