# Vector Database Sidebar Redesign Plan

## Current Issues
1. ❌ `switchTab()` crashes with "Cannot read properties of undefined (reading 'querySelectorAll')"
2. ❌ Ugly color scheme - not using global CSS variables
3. ❌ Inconsistent with Automations/Synergy sidebar design
4. ❌ Poor structure - needs organized sub-tabs

## Target Design: Match Automations Sidebar

### Structure Template (from Automations):
```
┌─────────────────────────────────────────┐
│ HEADER                                   │
│  🗄️ Vector Database          [↻] [✕]   │
│  ┌─────┬─────┬─────┐                    │
│  │  0  │  0  │  0  │ Stats               │
│  │ Docs│Vecs │NSpc │                     │
│  └─────┴─────┴─────┘                    │
│  🔍 [Search...]                         │
│  [ All | Upload | Docs | Manage | ...]  │
└─────────────────────────────────────────┘
│ CONTENT (Scrollable)                     │
│                                          │
│  [Tab-specific content here]            │
│                                          │
└─────────────────────────────────────────┘
```

## New Sub-Tab Structure

### Tab 1: 📤 Upload
- **Purpose**: Upload documents to vector database
- **Content**:
  - File drop zone
  - Batch upload progress
  - Supported formats list
  - Upload history

### Tab 2: 📄 Documents
- **Purpose**: Browse uploaded documents
- **Content**:
  - Document list with metadata
  - Search/filter documents
  - Preview/download
  - Delete actions

### Tab 3: 🔍 Search
- **Purpose**: Semantic search interface
- **Content**:
  - Search input
  - Results list with similarity scores
  - Advanced filters
  - Export results

### Tab 4: 🧠 Embeddings
- **Purpose**: Configure embedding AI
- **Content**:
  - Provider selection (OpenAI, Cohere, etc.)
  - Model selection
  - Dimension settings
  - Test embedding

### Tab 5: 🗄️ Vector DB
- **Purpose**: Vector database configuration
- **Content**:
  - Provider selection (Pinecone, Qdrant, pgvector)
  - Connection settings
  - Index management
  - Namespace management

### Tab 6: ⚙️ Settings
- **Purpose**: Global settings
- **Content**:
  - Chunk size
  - Overlap settings
  - Metadata extraction
  - Auto-sync options

## Data Storage in Supabase

### New Tables Needed:

#### 1. `vector_db_config`
```sql
CREATE TABLE vector_db_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(user_id),
    provider VARCHAR(50), -- 'pinecone', 'qdrant', 'pgvector', 'voyager'
    connection_config JSONB, -- API keys, endpoints, etc.
    embedding_provider VARCHAR(50), -- 'openai', 'cohere', 'huggingface'
    embedding_model VARCHAR(100),
    chunk_size INTEGER DEFAULT 1000,
    chunk_overlap INTEGER DEFAULT 200,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 2. `vector_documents`
```sql
CREATE TABLE vector_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(user_id),
    filename VARCHAR(500),
    file_type VARCHAR(50),
    file_size BIGINT,
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    processing_status VARCHAR(50), -- 'pending', 'processing', 'completed', 'failed'
    chunk_count INTEGER,
    namespace VARCHAR(200),
    metadata JSONB,
    vector_db_id UUID REFERENCES vector_db_config(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. `vector_search_history`
```sql
CREATE TABLE vector_search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES users(user_id),
    query_text TEXT,
    results_count INTEGER,
    avg_similarity DECIMAL(5,4),
    namespace VARCHAR(200),
    search_date TIMESTAMPTZ DEFAULT NOW(),
    filters JSONB
);
```

## CSS Variable Alignment

### Colors to Use (from global design system):
```css
--bg-primary: #0d1117;          /* Main background */
--bg-secondary: #161b22;        /* Secondary background */
--bg-tertiary: #1f2937;         /* Tertiary background */
--bg-hover: #30363d;            /* Hover states */

--text-primary: #e6edf3;        /* Primary text */
--text-secondary: #8b949e;      /* Secondary text */
--text-muted: #6e7681;          /* Muted text */

--accent-primary: #58a6ff;      /* Primary accent (blue) */
--accent-success: #3fb950;      /* Success (green) */
--accent-warning: #f59e0b;      /* Warning (yellow) */
--accent-danger: #dc2626;       /* Danger (red) */

--border-default: #30363d;      /* Default borders */

--space-1: 4px;                 /* Spacing scale */
--space-2: 8px;
--space-3: 16px;
--space-4: 24px;
```

## Implementation Phases

### Phase 1: Fix JavaScript Error ✅
- Added container safety check in `switchTab()`
- Fixed undefined `this.container` issue

### Phase 2: Redesign HTML Structure (Next)
- Create new tab structure matching Automations
- Organize content into 6 sub-tabs
- Add proper filter chips

### Phase 3: Update CSS (In Progress)
- Replace all hardcoded colors with CSS variables
- Match Automations sidebar styling
- Ensure consistent spacing

### Phase 4: Backend Integration (After UI)
- Create Supabase tables
- Build API endpoints
- Connect frontend to backend

### Phase 5: Testing
- Test all tabs
- Verify color consistency
- Test responsive behavior

## Quick Wins
1. ✅ Fix `switchTab()` crash
2. ⏳ Add proper stats row styling
3. ⏳ Create filter chip component
4. ⏳ Implement provider selector dropdown
5. ⏳ Add tab icons

## Success Criteria
- [ ] No JavaScript errors
- [ ] Matches Automations sidebar design
- [ ] All 6 tabs functional
- [ ] Uses global CSS variables
- [ ] Data persists to Supabase
- [ ] Search works across documents
- [ ] Upload progress visible
