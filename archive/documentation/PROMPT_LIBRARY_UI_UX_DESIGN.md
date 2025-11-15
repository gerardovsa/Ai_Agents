# Prompt Library UI/UX Design - Complete Specification

## Overview

This document defines the complete user interface, search mechanisms, and interaction patterns for the Prompt Library system.

---

## 1. Search & Discovery Mechanisms

### 1.1 Search Strategies

**Primary Search Methods:**
1. **Fuzzy Text Search** - Search by name, description, keywords
2. **Category/Tag Filtering** - Filter by category badges
3. **Recent/Favorites** - Quick access to frequently used prompts
4. **Recommended** - AI-suggested prompts based on context

### 1.2 Search Implementation

**Search Query Logic:**
```sql
SELECT * FROM prompt_library 
WHERE 
    -- Text search (fuzzy matching)
    (
        LOWER(prompt_name) LIKE '%' || LOWER(:search_term) || '%'
        OR LOWER(prompt_description) LIKE '%' || LOWER(:search_term) || '%'
        OR LOWER(prompt_key) LIKE '%' || LOWER(:search_term) || '%'
        OR LOWER(tags) LIKE '%' || LOWER(:search_term) || '%'
    )
    -- Category filter
    AND (:category IS NULL OR category = :category)
    -- Type filter
    AND (:prompt_type IS NULL OR prompt_type = :prompt_type)
    -- Visibility (user access check)
    AND (
        visibility = 'public'
        OR created_by_user_id = :user_id
        OR prompt_id IN (SELECT prompt_id FROM prompt_shares WHERE shared_with_user_id = :user_id)
    )
    AND is_active = 1
    AND deleted_at IS NULL
ORDER BY 
    -- Prioritize exact matches
    CASE WHEN LOWER(prompt_name) = LOWER(:search_term) THEN 0 ELSE 1 END,
    -- Then by usage popularity
    use_count DESC,
    -- Then alphabetically
    prompt_name ASC;
```

**Search Fields Needed:**
- `prompt_name` - Primary display name (searchable)
- `prompt_key` - Unique identifier (searchable, used in API calls)
- `prompt_slug` - **NEW** URL-friendly version for deep linking
- `prompt_description` - Longer description (searchable)
- `tags` - JSON array of keywords (searchable)
- `search_keywords` - **NEW** Additional search terms (hidden from UI)

### 1.3 Prompt Slug System

**What is a Slug?**
- URL-friendly unique identifier: `expert-coder`, `sql-performance-optimizer`
- Used for: Deep linking, sharing, bookmarking
- Generated from `prompt_name` automatically

**Slug Generation:**
```python
def generate_slug(prompt_name: str, prompt_id: int = None) -> str:
    """Generate URL-friendly slug from prompt name"""
    import re
    
    # Convert to lowercase
    slug = prompt_name.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Ensure uniqueness (append ID if needed)
    # Check if slug exists in database
    # If exists, append: expert-coder-2, expert-coder-3, etc.
    
    return slug
```

**Examples:**
- "Expert Coder" → `expert-coder`
- "SQL Performance Optimizer" → `sql-performance-optimizer`
- "Email Composer (Professional)" → `email-composer-professional`

**Usage:**
```
https://app.com/prompts/expert-coder
https://app.com/prompts/sql-performance-optimizer
```

---

## 2. UI Layout & Components

### 2.1 Main Chat Interface with Prompt Controls

```
┌────────────────────────────────────────────────────────────────────────┐
│  InHouse AI Agent - Chat                                    [User Menu]│
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─ Quick Actions Bar ─────────────────────────────────────────────┐  │
│  │  ⚡ Expert Coder  🔍 Code Review  🐛 Debugger  📊 Detailed      │  │
│  │  🗄️ SQL Expert   ⚡ Concise      💼 Professional  📧 Email     │  │
│  │  [+ More Actions] [📚 Prompt Library] [⭐ Favorites] [🔍 Search]│  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌─ Active Prompts ─────────────────────────────────────────────────┐ │
│  │  ✓ Expert Coder   ✓ SQL Expert   ✓ Custom: "Use TypeScript"    │ │
│  │  [Clear All]                                                     │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─ Conversation Area ─────────────────────────────────────────────┐  │
│  │  [Previous messages displayed here]                              │  │
│  │                                                                   │  │
│  │  User: Create a login component                                  │  │
│  │                                                                   │  │
│  │  AI: [Response with Expert Coder + SQL Expert applied]           │  │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─ Message Input ──────────────────────────────────────────────────┐ │
│  │  Type your message...                                            │ │
│  │                                                                   │ │
│  │  [📎 Attach] [🎨 Format] [📝 Custom Instructions]    [Send 🚀]  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Quick Actions Bar (Lightning Strike Buttons)

**Design:**
```
┌─ Quick Actions ────────────────────────────────────────────────────┐
│                                                                     │
│  Development                                                        │
│  ┌────────┐ ┌────────┐ ┌────────┐                                │
│  │⚡      │ │🔍      │ │🐛      │                                │
│  │Expert  │ │Code    │ │Debugger│                                │
│  │Coder   │ │Review  │ │        │                                │
│  └────────┘ └────────┘ └────────┘                                │
│                                                                     │
│  Analysis                                                           │
│  ┌────────┐ ┌────────┐ ┌────────┐                                │
│  │📊      │ │📝      │ │🧠      │                                │
│  │Detailed│ │Step by │ │Critical│                                │
│  │        │ │Step    │ │Thinking│                                │
│  └────────┘ └────────┘ └────────┘                                │
│                                                                     │
│  Data & SQL                                                         │
│  ┌────────┐ ┌────────┐                                            │
│  │🗄️      │ │📈      │                                            │
│  │SQL     │ │Data    │                                            │
│  │Expert  │ │Analyst │                                            │
│  └────────┘ └────────┘                                            │
│                                                                     │
│  Style                                                              │
│  ┌────────┐ ┌────────┐ ┌────────┐                                │
│  │⚡      │ │🎓      │ │💼      │                                │
│  │Concise │ │ELI5    │ │Pro     │                                │
│  └────────┘ └────────┘ └────────┘                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Interaction:**
- **Click once** → Toggle ON (blue highlight)
- **Click again** → Toggle OFF
- **Hover** → Show tooltip with full description
- **Right-click** → Quick menu (Edit, Share, Remove)
- **Drag** → Reorder buttons

**State Indicators:**
```css
/* Inactive state */
.quick-action-btn {
  background: white;
  border: 1px solid #ddd;
  color: #333;
}

/* Active state */
.quick-action-btn.active {
  background: #007bff;
  border: 1px solid #0056b3;
  color: white;
  box-shadow: 0 2px 8px rgba(0,123,255,0.3);
}

/* Hover state */
.quick-action-btn:hover {
  border-color: #007bff;
  transform: translateY(-2px);
}
```

### 2.3 Prompt Library Modal (Extended Prompts)

**Trigger:**
```
[📚 Prompt Library] button in top bar
```

**Modal Layout:**
```
┌─ Prompt Library ───────────────────────────────────────────────────────┐
│  [X]                                                                    │
│                                                                         │
│  ┌─ Search & Filter ─────────────────────────────────────────────────┐│
│  │  [🔍 Search prompts...]                                [Advanced ▼]││
│  │                                                                     ││
│  │  Category: [All ▼] Type: [All ▼] Sort: [Popular ▼]                ││
│  │                                                                     ││
│  │  Quick Filters:                                                     ││
│  │  [🌟 Favorites] [📅 Recent] [👤 My Prompts] [🌍 Public]           ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Prompt Cards ─────────────────────────────────────────────────────┐│
│  │                                                                     ││
│  │  ┌──────────────────────┐  ┌──────────────────────┐               ││
│  │  │ 🏗️ System Architect  │  │ 🔒 Security Analyst  │               ││
│  │  │                      │  │                      │               ││
│  │  │ High-level system    │  │ Security & vulner-   │               ││
│  │  │ design and archi-    │  │ ability assessment   │               ││
│  │  │ tecture              │  │                      │               ││
│  │  │                      │  │                      │               ││
│  │  │ 📊 Development       │  │ 🔐 Development       │               ││
│  │  │ 👤 User: You         │  │ 🌍 Public            │               ││
│  │  │ 🔢 Used 23 times     │  │ 🔢 Used 456 times    │               ││
│  │  │                      │  │                      │               ││
│  │  │ [Select] [Share] [★] │  │ [Select] [Clone] [★] │               ││
│  │  └──────────────────────┘  └──────────────────────┘               ││
│  │                                                                     ││
│  │  ┌──────────────────────┐  ┌──────────────────────┐               ││
│  │  │ 📊 BI Analyst        │  │ 📝 Technical Writer  │               ││
│  │  │                      │  │                      │               ││
│  │  │ KPI tracking and BI  │  │ Documentation and    │               ││
│  │  │ analysis             │  │ technical guides     │               ││
│  │  │                      │  │                      │               ││
│  │  │ 💼 Business          │  │ 📚 Development       │               ││
│  │  │ 👥 Workspace: Sales  │  │ 👤 User: Alex        │               ││
│  │  │ 🔢 Used 12 times     │  │ 🔢 Used 8 times      │               ││
│  │  │                      │  │                      │               ││
│  │  │ [Select] [View] [★]  │  │ [Select] [Clone] [★] │               ││
│  │  └──────────────────────┘  └──────────────────────┘               ││
│  │                                                                     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Selected Prompts ─────────────────────────────────────────────────┐│
│  │  ✓ System Architect  ✓ Security Analyst                 [Clear All]││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  [Cancel]                                      [Apply Selected (2)] ││
└─────────────────────────────────────────────────────────────────────────┘
```

**Prompt Card Design:**
```
┌──────────────────────────────────────────┐
│ [Icon] Prompt Name            [★ Favorite]│
│                                           │
│ Short description preview...              │
│                                           │
│ [Badge] Category                          │
│ [Badge] Visibility (👤/👥/🌍)            │
│ [Badge] 123 uses                          │
│                                           │
│ Created by: Username                      │
│ Last used: 2 hours ago                    │
│                                           │
│ ┌───────────────────────────────────────┐│
│ │ [✓ Select] [👁️ View] [🔗 Share] [⋯] ││
│ └───────────────────────────────────────┘│
└──────────────────────────────────────────┘
```

### 2.4 Prompt Detail View

**Clicking a prompt opens expanded view:**
```
┌─ System Architect ─────────────────────────────────────────────────────┐
│  [← Back to Library]                                              [X]  │
│                                                                         │
│  ┌─ Header ───────────────────────────────────────────────────────────┐│
│  │  🏗️  System Architect                                              ││
│  │                                                                     ││
│  │  📊 Development | 🌍 Public | Created by: Admin                    ││
│  │  Used 456 times | Rating: ⭐⭐⭐⭐⭐ (4.8/5)                         ││
│  │                                                                     ││
│  │  [✓ Select] [⭐ Add to Favorites] [🔗 Share] [📋 Clone] [⚙️ Edit] ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Description ──────────────────────────────────────────────────────┐│
│  │  You are a senior system architect with 15+ years of experience    ││
│  │  designing scalable, distributed systems. Focus on:                ││
│  │                                                                     ││
│  │  - System architecture and design patterns                         ││
│  │  - Scalability and performance optimization                        ││
│  │  - Security and reliability considerations                         ││
│  │  - Technology stack recommendations                                ││
│  │  - Trade-off analysis for architectural decisions                  ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Full Prompt Text ─────────────────────────────────────────────────┐│
│  │  [View Full Prompt] [Copy Prompt] [Export as Text]                ││
│  │                                                                     ││
│  │  SYSTEM ARCHITECT MODE ACTIVATED:                                  ││
│  │  - Design high-level system architecture                           ││
│  │  - Choose appropriate design patterns                              ││
│  │  - Consider scalability, reliability, and maintainability          ││
│  │  - Evaluate technology stack options                               ││
│  │  - Document architectural decisions and trade-offs                 ││
│  │  - Create system diagrams and data flow models                     ││
│  │  - Address non-functional requirements (performance, security)     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Usage Statistics ─────────────────────────────────────────────────┐│
│  │  📈 Trending: +45% this week                                       ││
│  │  👥 Used by 89 users                                               ││
│  │  📅 Created: Nov 1, 2025                                           ││
│  │  🔄 Last updated: Nov 10, 2025                                     ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Tags ─────────────────────────────────────────────────────────────┐│
│  │  [architecture] [design-patterns] [scalability] [distributed]     ││
│  │  [microservices] [system-design]                                   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Reviews & Ratings ────────────────────────────────────────────────┐│
│  │  ⭐⭐⭐⭐⭐  Sarah K. - "Perfect for system design interviews!"      ││
│  │  ⭐⭐⭐⭐    John D. - "Very detailed, helped me design my API"      ││
│  │                                                                     ││
│  │  [Add Your Review]                                                 ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
│  ┌─ Related Prompts ──────────────────────────────────────────────────┐│
│  │  [🔒 Security Analyst] [⚡ Performance Engineer] [📊 BI Analyst]   ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.5 Search Interface

**Advanced Search Panel:**
```
┌─ Advanced Search ──────────────────────────────────────────────────────┐
│                                                                         │
│  Text Search                                                            │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ [🔍] Search by name, description, keywords...                     │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  Filters                                                                │
│  ┌─────────────────────┐ ┌─────────────────────┐ ┌──────────────────┐│
│  │ Category            │ │ Type                │ │ Visibility       ││
│  │ [All ▼]             │ │ [All ▼]             │ │ [All ▼]          ││
│  │ ☐ Development       │ │ ☐ Quick Action      │ │ ☐ My Prompts     ││
│  │ ☐ Analysis          │ │ ☐ Library           │ │ ☐ Shared with Me ││
│  │ ☐ Data              │ │ ☐ Template          │ │ ☐ Workspace      ││
│  │ ☐ Style             │ │ ☐ Custom            │ │ ☐ Public         ││
│  │ ☐ Business          │ │                     │ │                  ││
│  │ ☐ Creative          │ │                     │ │                  ││
│  └─────────────────────┘ └─────────────────────┘ └──────────────────┘│
│                                                                         │
│  Sort By                                                                │
│  ⚫ Most Popular  ⚪ Recently Used  ⚪ Newest  ⚪ Alphabetical          │
│                                                                         │
│  Tags                                                                   │
│  [python] [javascript] [sql] [api] [optimization]                      │
│                                                                         │
│  [Clear Filters]                            [Search]                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Additional Database Columns Needed

### 3.1 Updated `prompt_library` Table Schema

```sql
CREATE TABLE IF NOT EXISTS prompt_library (
    -- Existing columns
    prompt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_by_user_id INTEGER NOT NULL,
    workspace_id INTEGER NULL,
    visibility TEXT NOT NULL DEFAULT 'private',
    prompt_name TEXT NOT NULL,
    prompt_key TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    prompt_description TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    tags TEXT,
    icon TEXT,
    display_color TEXT,
    sort_order INTEGER DEFAULT 0,
    prompt_type TEXT NOT NULL,
    is_system_prompt BOOLEAN DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    effectiveness_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT 1,
    version INTEGER DEFAULT 1,
    parent_prompt_id INTEGER,
    share_count INTEGER DEFAULT 0,
    clone_count INTEGER DEFAULT 0,
    
    -- NEW COLUMNS FOR UI/UX
    prompt_slug TEXT UNIQUE NOT NULL,  -- URL-friendly identifier
    search_keywords TEXT,  -- Additional hidden search terms (JSON array)
    short_description TEXT,  -- Brief description for cards (50-100 chars)
    banner_image_url TEXT,  -- Optional banner image for detail view
    preview_text TEXT,  -- First few lines of prompt for preview
    is_featured BOOLEAN DEFAULT 0,  -- Featured prompts (homepage)
    featured_order INTEGER DEFAULT 0,  -- Order for featured section
    tooltip_text TEXT,  -- Hover tooltip text
    badge_text TEXT,  -- Badge to display (e.g., "NEW", "TRENDING", "PRO")
    badge_color TEXT,  -- Badge color
    total_ratings INTEGER DEFAULT 0,  -- Number of ratings
    average_rating REAL DEFAULT 0.0,  -- Average star rating (0-5)
    trending_score REAL DEFAULT 0.0,  -- Calculated trending score
    last_trending_update TIMESTAMP,  -- When trending score was calculated
    view_count INTEGER DEFAULT 0,  -- How many times viewed (detail page)
    clone_enabled BOOLEAN DEFAULT 1,  -- Allow users to clone this prompt
    edit_enabled BOOLEAN DEFAULT 1,  -- Allow original creator to edit
    related_prompt_ids TEXT,  -- JSON array of related prompt IDs
    prerequisites TEXT,  -- Required knowledge/setup (markdown)
    examples TEXT,  -- Usage examples (JSON array)
    changelog TEXT,  -- Version history (JSON array)
    
    FOREIGN KEY (created_by_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE SET NULL
);

-- Additional indexes for new columns
CREATE INDEX idx_prompt_library_slug ON prompt_library(prompt_slug);
CREATE INDEX idx_prompt_library_featured ON prompt_library(is_featured, featured_order);
CREATE INDEX idx_prompt_library_trending ON prompt_library(trending_score DESC);
CREATE INDEX idx_prompt_library_rating ON prompt_library(average_rating DESC);
CREATE INDEX idx_prompt_library_views ON prompt_library(view_count DESC);
CREATE INDEX idx_prompt_library_search ON prompt_library(prompt_name, search_keywords);
```

### 3.2 New Table: `prompt_ratings` (User Reviews)

```sql
CREATE TABLE IF NOT EXISTS prompt_ratings (
    rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    review_text TEXT,
    helpful_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified_user BOOLEAN DEFAULT 0,  -- User has actually used the prompt
    
    UNIQUE(prompt_id, user_id),  -- One rating per user per prompt
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_prompt_ratings_prompt ON prompt_ratings(prompt_id);
CREATE INDEX idx_prompt_ratings_user ON prompt_ratings(user_id);
CREATE INDEX idx_prompt_ratings_rating ON prompt_ratings(rating);
```

### 3.3 New Table: `prompt_views` (View Tracking)

```sql
CREATE TABLE IF NOT EXISTS prompt_views (
    view_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    view_duration_seconds INTEGER,  -- How long they viewed it
    converted_to_use BOOLEAN DEFAULT 0,  -- Did they actually use it?
    
    FOREIGN KEY (prompt_id) REFERENCES prompt_library(prompt_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_prompt_views_prompt ON prompt_views(prompt_id);
CREATE INDEX idx_prompt_views_user ON prompt_views(user_id);
CREATE INDEX idx_prompt_views_timestamp ON prompt_views(viewed_at);
```

---

## 4. Search & Discovery Features

### 4.1 Full-Text Search Implementation

**Using SQLite FTS5:**
```sql
-- Create virtual table for full-text search
CREATE VIRTUAL TABLE prompt_search_fts USING fts5(
    prompt_id,
    prompt_name,
    prompt_description,
    short_description,
    search_keywords,
    tags,
    content='prompt_library'
);

-- Trigger to keep FTS index updated
CREATE TRIGGER prompt_library_ai AFTER INSERT ON prompt_library BEGIN
    INSERT INTO prompt_search_fts(prompt_id, prompt_name, prompt_description, short_description, search_keywords, tags)
    VALUES (new.prompt_id, new.prompt_name, new.prompt_description, new.short_description, new.search_keywords, new.tags);
END;

CREATE TRIGGER prompt_library_au AFTER UPDATE ON prompt_library BEGIN
    UPDATE prompt_search_fts 
    SET prompt_name = new.prompt_name,
        prompt_description = new.prompt_description,
        short_description = new.short_description,
        search_keywords = new.search_keywords,
        tags = new.tags
    WHERE prompt_id = new.prompt_id;
END;

CREATE TRIGGER prompt_library_ad AFTER DELETE ON prompt_library BEGIN
    DELETE FROM prompt_search_fts WHERE prompt_id = old.prompt_id;
END;
```

**Search Query:**
```sql
SELECT pl.* 
FROM prompt_library pl
INNER JOIN prompt_search_fts fts ON pl.prompt_id = fts.prompt_id
WHERE prompt_search_fts MATCH :search_term
AND pl.is_active = 1
AND pl.deleted_at IS NULL
ORDER BY rank;
```

### 4.2 Trending Algorithm

**Calculate Trending Score:**
```python
def calculate_trending_score(prompt_id: int, days_window: int = 7) -> float:
    """
    Calculate trending score based on:
    - Recent usage spike
    - Recent ratings
    - Recent shares
    - Recent clones
    
    Score = (recent_uses * 1.0) + (recent_ratings * 0.5) + 
            (recent_shares * 0.3) + (recent_clones * 0.2)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get metrics from last N days
    cursor.execute('''
        SELECT 
            (SELECT COUNT(*) FROM prompt_usage_history 
             WHERE prompt_id = ? 
             AND used_at >= datetime('now', '-' || ? || ' days')) as recent_uses,
             
            (SELECT COUNT(*) FROM prompt_ratings 
             WHERE prompt_id = ? 
             AND created_at >= datetime('now', '-' || ? || ' days')) as recent_ratings,
             
            (SELECT COUNT(*) FROM prompt_shares 
             WHERE prompt_id = ? 
             AND created_at >= datetime('now', '-' || ? || ' days')) as recent_shares,
             
            (SELECT COUNT(*) FROM prompt_library 
             WHERE parent_prompt_id = ? 
             AND created_at >= datetime('now', '-' || ? || ' days')) as recent_clones
    ''', (prompt_id, days_window, prompt_id, days_window, 
          prompt_id, days_window, prompt_id, days_window))
    
    row = cursor.fetchone()
    
    trending_score = (
        row[0] * 1.0 +   # Recent uses
        row[1] * 0.5 +   # Recent ratings
        row[2] * 0.3 +   # Recent shares
        row[3] * 0.2     # Recent clones
    )
    
    # Update prompt with trending score
    cursor.execute('''
        UPDATE prompt_library 
        SET trending_score = ?,
            last_trending_update = CURRENT_TIMESTAMP
        WHERE prompt_id = ?
    ''', (trending_score, prompt_id))
    
    conn.commit()
    conn.close()
    
    return trending_score
```

### 4.3 Recommendation Engine

**Recommend Prompts Based on Context:**
```python
def recommend_prompts(user_id: int, context: str, limit: int = 5) -> List[Dict]:
    """
    Recommend prompts based on:
    1. User's recent prompts
    2. Context/query keywords
    3. What similar users use
    4. Popular prompts in same category
    """
    
    # Extract keywords from context
    keywords = extract_keywords(context)
    
    # Get user's frequently used categories
    user_categories = get_user_frequent_categories(user_id)
    
    # Build recommendation query
    query = '''
        SELECT pl.*, 
               (
                   -- Keyword match score
                   (CASE WHEN pl.tags LIKE '%' || :keyword1 || '%' THEN 2 ELSE 0 END) +
                   (CASE WHEN pl.tags LIKE '%' || :keyword2 || '%' THEN 2 ELSE 0 END) +
                   
                   -- Category preference score
                   (CASE WHEN pl.category IN (:user_categories) THEN 3 ELSE 0 END) +
                   
                   -- Popularity score
                   (pl.use_count / 100.0) +
                   
                   -- Rating score
                   (pl.average_rating / 5.0 * 2)
                   
               ) as recommendation_score
        FROM prompt_library pl
        WHERE pl.is_active = 1
        AND pl.deleted_at IS NULL
        AND (
            pl.visibility = 'public'
            OR pl.created_by_user_id = :user_id
            OR pl.prompt_id IN (
                SELECT prompt_id FROM prompt_shares 
                WHERE shared_with_user_id = :user_id
            )
        )
        ORDER BY recommendation_score DESC, pl.trending_score DESC
        LIMIT :limit
    '''
    
    # Execute and return results
    # ...
```

---

## 5. User Workflows

### 5.1 Quick Action Workflow

**User Journey:**
1. User opens chat interface
2. Sees Quick Actions bar with 16 buttons
3. Clicks "⚡ Expert Coder" → Button turns blue
4. Clicks "🗄️ SQL Expert" → Button turns blue
5. Types message: "Create a user authentication API"
6. Clicks Send
7. Backend injects both prompts into system prompt
8. AI responds with expert code + SQL best practices

**Data Flow:**
```
User clicks button → Update UI state → Store in request payload
                                      ↓
POST /api/agent/chat-streaming: {
    message: "Create a user authentication API",
    quick_actions: ["expert_coder", "sql_expert"],
    user_id: 12
}
                                      ↓
Backend: prompt_manager.inject_prompts(
    quick_actions=["expert_coder", "sql_expert"]
)
                                      ↓
System prompt enhanced with both prompts → Send to AI
```

### 5.2 Library Prompt Workflow

**User Journey:**
1. User clicks "📚 Prompt Library" button
2. Modal opens with search and prompt cards
3. User searches "security"
4. Results filtered: "🔒 Security Analyst", "🛡️ Security Architect"
5. User clicks "🔒 Security Analyst" card
6. Detail view opens with full description
7. User clicks "✓ Select"
8. Modal shows "Selected Prompts: Security Analyst (1)"
9. User clicks "Apply Selected"
10. Modal closes, selected prompt active in chat
11. User types message, prompt is injected

### 5.3 Sharing Workflow

**User Journey:**
1. User creates custom prompt "TypeScript Expert"
2. Uses it successfully several times
3. Wants to share with team
4. Opens Prompt Library → "My Prompts" tab
5. Finds "TypeScript Expert" card
6. Clicks "🔗 Share" button
7. Share modal opens with options:
   - Share with specific user (email input)
   - Share with workspace (dropdown)
   - Make public (everyone)
8. Selects "Share with workspace" → Chooses "Development Team"
9. Sets permission: "Can use" (not edit)
10. Clicks "Share"
11. Success message: "Prompt shared with Development Team"
12. All Development Team members now see prompt in their library

---

## 6. Mobile Responsive Design

### 6.1 Mobile Quick Actions

**Collapsed by default, expandable:**
```
┌──────────────────────────────┐
│  [⚡ Quick Actions ▼]        │
├──────────────────────────────┤
│  [Message input...]          │
│                              │
│  [Send]                      │
└──────────────────────────────┘

When expanded:
┌──────────────────────────────┐
│  [⚡ Quick Actions ▲]        │
├──────────────────────────────┤
│  ┌──────┐  ┌──────┐          │
│  │⚡     │  │🔍    │          │
│  │Expert│  │Review│          │
│  └──────┘  └──────┘          │
│  ┌──────┐  ┌──────┐          │
│  │🐛     │  │📊    │          │
│  │Debug │  │Detail│          │
│  └──────┘  └──────┘          │
│  [See All 16 Actions →]      │
├──────────────────────────────┤
│  [Message input...]          │
│  [Send]                      │
└──────────────────────────────┘
```

---

## 7. Analytics Dashboard (Admin View)

### 7.1 Prompt Analytics Page

```
┌─ Prompt Analytics Dashboard ───────────────────────────────────────────┐
│                                                                         │
│  ┌─ Overview ──────────────────────────────────────────────────────────┐
│  │  📊 Total Prompts: 245                                              │
│  │  👥 Active Users: 1,234                                             │
│  │  🔥 Total Usage: 45,678 (this month)                                │
│  │  ⭐ Avg Rating: 4.6/5                                               │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                         │
│  ┌─ Top Prompts ───────────────────────────────────────────────────────┐
│  │  1. ⚡ Expert Coder          - 2,345 uses  - 4.8★                  │
│  │  2. 🗄️ SQL Expert            - 1,876 uses  - 4.7★                  │
│  │  3. 🏗️ System Architect      - 1,234 uses  - 4.9★                  │
│  │  4. 🔍 Code Reviewer          - 1,123 uses  - 4.6★                  │
│  │  5. 📊 Data Analyst           - 987 uses   - 4.5★                  │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                         │
│  ┌─ Trending This Week ────────────────────────────────────────────────┐
│  │  🔥 TypeScript Expert         - +145% usage                         │
│  │  🔥 API Designer              - +89% usage                          │
│  │  🔥 Security Analyst          - +67% usage                          │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                         │
│  ┌─ Usage Over Time ───────────────────────────────────────────────────┐
│  │  [Line chart showing prompt usage trends]                           │
│  └─────────────────────────────────────────────────────────────────────┘
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Summary: Required Database Changes

### Critical New Columns:
1. ✅ `prompt_slug` - URL-friendly unique identifier (REQUIRED)
2. ✅ `search_keywords` - Hidden search terms (REQUIRED for discovery)
3. ✅ `short_description` - Card preview text (REQUIRED for UI)
4. ✅ `tooltip_text` - Hover descriptions (NICE TO HAVE)
5. ✅ `badge_text` / `badge_color` - UI badges (NICE TO HAVE)
6. ✅ `trending_score` - Algorithmic trending (REQUIRED for discovery)
7. ✅ `average_rating` / `total_ratings` - User ratings (REQUIRED for quality)
8. ✅ `view_count` - Analytics (NICE TO HAVE)
9. ✅ `related_prompt_ids` - Recommendations (NICE TO HAVE)
10. ✅ `examples` - Usage examples (REQUIRED for detail view)

### New Tables Required:
1. ✅ `prompt_ratings` - User reviews and ratings
2. ✅ `prompt_views` - View tracking
3. ⚠️ `prompt_search_fts` - Full-text search (virtual table)

**Total: 10 new columns + 3 new tables = Complete UI/UX support**
