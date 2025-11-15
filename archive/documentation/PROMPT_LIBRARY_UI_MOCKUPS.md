# Prompt Library - UI Mockups & User Flows

## Quick Reference: How Users Find & Use Prompts

### Method 1: Quick Actions (Lightning Strike Buttons) ⚡

**Discovery Method:** **Visual Browsing**
- User sees row of icon buttons above message input
- Icons are self-explanatory (⚡ = fast, 🐛 = debug, 🗄️ = database)
- Hover shows tooltip: "Expert Coder - Production-ready code"
- Click to toggle ON/OFF

**Search Method:** NOT searchable (always visible, pre-curated set)

**Access Pattern:**
```
User opens chat → Sees Quick Actions bar → Clicks buttons → Types message → Send
```

**Data Lookup:**
```
User clicks "⚡ Expert Coder" button
    ↓
Frontend: quick_actions.push('expert_coder')
    ↓
Backend: SELECT * FROM prompt_library WHERE prompt_key = 'expert_coder'
    ↓
Inject prompt_text into system prompt
```

**Why `prompt_key` is used:**
- Fast exact match lookup
- No spaces (API-friendly)
- Unique identifier
- Used in request payload: `quick_actions: ['expert_coder', 'sql_expert']`

---

### Method 2: Prompt Library (Extended Prompts) 📚

**Discovery Method:** **Search + Browse**
- User clicks "📚 Prompt Library" button
- Modal opens with search bar + category filters
- User can search OR browse by category
- Cards show prompt previews

**Search Methods:**
1. **Text Search** - Type keywords: "security", "python", "optimization"
2. **Category Filter** - Filter by: Development, Analysis, Data, etc.
3. **Tags** - Click tag badges: [python], [api], [performance]
4. **Quick Filters** - Favorites, Recent, My Prompts, Public

**Access Pattern:**
```
User clicks [📚 Prompt Library]
    ↓
Search "security" OR Browse "Development" category
    ↓
See prompt cards with previews
    ↓
Click card → See detail view
    ↓
Click [Select] → Prompt added to active set
    ↓
Type message → Send (prompt injected)
```

**Data Lookup Flow:**

**A. Search by text:**
```sql
-- Uses FTS (Full-Text Search)
SELECT pl.* 
FROM prompt_library pl
INNER JOIN prompt_search_fts fts ON pl.prompt_id = fts.prompt_id
WHERE prompt_search_fts MATCH 'security'
  AND pl.is_active = 1
ORDER BY rank;
```

**B. Browse by category:**
```sql
SELECT * FROM prompt_library
WHERE category = 'development'
  AND is_active = 1
  AND (visibility = 'public' OR created_by_user_id = :user_id)
ORDER BY trending_score DESC, use_count DESC;
```

**C. Direct link (using slug):**
```
URL: https://app.com/prompts/system-architect
    ↓
SELECT * FROM prompt_library
WHERE prompt_slug = 'system-architect'
  AND is_active = 1;
```

**Why BOTH `prompt_key` AND `prompt_slug` needed:**

| Field | Example | Used For | Format |
|-------|---------|----------|--------|
| `prompt_key` | `expert_coder` | API calls, JSON payloads | snake_case, no spaces |
| `prompt_slug` | `expert-coder` | URLs, sharing links | kebab-case, URL-safe |

**Example:**
```javascript
// API request payload uses prompt_key
{
  quick_actions: ['expert_coder', 'sql_expert'],
  library_prompts: ['system_architect']
}

// But URL sharing uses prompt_slug
https://app.com/prompts/system-architect
https://app.com/prompts/expert-coder
```

---

## UI Component Breakdown

### Component 1: Quick Actions Bar

```
┌─────────────────────────────────────────────────────────────┐
│  Development:                                               │
│  [⚡ Expert] [🔍 Review] [🐛 Debug]                         │
│                                                             │
│  Analysis:                                                  │
│  [📊 Detail] [📝 Step] [🧠 Critical]                        │
│                                                             │
│  Data:                                                      │
│  [🗄️ SQL] [📈 Data]                                         │
│                                                             │
│  Style:                                                     │
│  [⚡ Concise] [🎓 ELI5] [💼 Pro]                            │
└─────────────────────────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div class="quick-actions-bar" data-category-sections="4">
  <!-- Development Section -->
  <div class="qa-section" data-category="development">
    <span class="qa-category-label">Development:</span>
    
    <button class="qa-btn" 
            data-key="expert_coder"
            data-name="Expert Coder"
            title="Production-ready code with error handling">
      <span class="qa-icon">⚡</span>
      <span class="qa-label">Expert</span>
    </button>
    
    <button class="qa-btn" 
            data-key="code_reviewer"
            data-name="Code Reviewer"
            title="Analyze code for bugs and issues">
      <span class="qa-icon">🔍</span>
      <span class="qa-label">Review</span>
    </button>
    
    <!-- More buttons... -->
  </div>
  
  <!-- More sections... -->
</div>

<script>
// Track active quick actions
let activeQuickActions = [];

document.querySelectorAll('.qa-btn').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const key = btn.dataset.key;
    const isActive = btn.classList.contains('active');
    
    if (isActive) {
      // Deactivate
      activeQuickActions = activeQuickActions.filter(k => k !== key);
      btn.classList.remove('active');
    } else {
      // Activate
      activeQuickActions.push(key);
      btn.classList.add('active');
    }
    
    // Update UI indicator
    updateActivePromptsDisplay();
  });
});
</script>
```

**CSS:**
```css
.qa-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.qa-btn:hover {
  border-color: #007bff;
  transform: translateY(-2px);
}

.qa-btn.active {
  background: #007bff;
  border-color: #0056b3;
  color: white;
  box-shadow: 0 2px 8px rgba(0,123,255,0.3);
}
```

**State Management:**
```javascript
// When user sends message
function sendMessage(text) {
  fetch('/api/agent/chat-streaming', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      message: text,
      quick_actions: activeQuickActions,  // ['expert_coder', 'sql_expert']
      library_prompts: activeLibraryPrompts,  // ['system_architect']
      user_id: currentUserId
    })
  });
}
```

---

### Component 2: Prompt Library Modal

```
┌─ Prompt Library ────────────────────────────────────────────┐
│  [X Close]                                                   │
│                                                              │
│  ┌─ Search Bar ─────────────────────────────────────────┐  │
│  │  🔍 [Search prompts, keywords, categories...]         │  │
│  │  [Development ▼] [All Types ▼] [Sort: Popular ▼]     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Prompt Grid ───────────────────────────────────────┐   │
│  │                                                       │   │
│  │  ╔════════════════╗  ╔════════════════╗             │   │
│  │  ║ 🏗️ System      ║  ║ 🔒 Security    ║             │   │
│  │  ║ Architect      ║  ║ Analyst        ║             │   │
│  │  ║                ║  ║                ║             │   │
│  │  ║ High-level     ║  ║ Security &     ║             │   │
│  │  ║ system design  ║  ║ vulnerability  ║             │   │
│  │  ║                ║  ║                ║             │   │
│  │  ║ 💻 Development ║  ║ 🔐 Development ║             │   │
│  │  ║ 🌍 Public      ║  ║ 🌍 Public      ║             │   │
│  │  ║ ⭐⭐⭐⭐⭐ 4.8   ║  ║ ⭐⭐⭐⭐⭐ 4.7   ║             │   │
│  │  ║ 👥 456 uses    ║  ║ 👥 234 uses    ║             │   │
│  │  ║                ║  ║                ║             │   │
│  │  ║ [Select]   [★] ║  ║ [Select]   [★] ║             │   │
│  │  ╚════════════════╝  ╚════════════════╝             │   │
│  │                                                       │   │
│  │  [Load More Prompts...]                              │   │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌─ Selected (2) ────────────────────────────────────────┐ │
│  │  ✓ System Architect  ✓ Security Analyst  [Clear All] │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [Cancel]                              [Apply Selected (2)] │
└──────────────────────────────────────────────────────────────┘
```

**HTML Structure:**
```html
<div id="promptLibraryModal" class="modal">
  <div class="modal-content">
    <!-- Search Section -->
    <div class="search-section">
      <input type="text" 
             id="promptSearch" 
             placeholder="🔍 Search prompts..."
             oninput="searchPrompts(this.value)">
      
      <select id="categoryFilter" onchange="filterByCategory(this.value)">
        <option value="">All Categories</option>
        <option value="development">💻 Development</option>
        <option value="analysis">📊 Analysis</option>
        <option value="data">🗄️ Data & SQL</option>
        <option value="business">💼 Business</option>
        <option value="creative">✍️ Creative</option>
      </select>
      
      <select id="sortBy" onchange="sortPrompts(this.value)">
        <option value="popular">Most Popular</option>
        <option value="rating">Highest Rated</option>
        <option value="recent">Recently Added</option>
        <option value="trending">Trending</option>
      </select>
    </div>
    
    <!-- Prompt Cards Grid -->
    <div id="promptGrid" class="prompt-grid">
      <!-- Cards loaded dynamically via loadPromptCards() -->
    </div>
    
    <!-- Selected Prompts Bar -->
    <div class="selected-prompts">
      <span id="selectedCount">Selected (0)</span>
      <div id="selectedList"></div>
      <button onclick="clearSelectedPrompts()">Clear All</button>
    </div>
    
    <!-- Action Buttons -->
    <div class="modal-actions">
      <button onclick="closeLibrary()">Cancel</button>
      <button onclick="applySelectedPrompts()" class="primary">
        Apply Selected (<span id="applyCount">0</span>)
      </button>
    </div>
  </div>
</div>
```

**Search Implementation:**
```javascript
async function searchPrompts(searchTerm) {
  const category = document.getElementById('categoryFilter').value;
  const sortBy = document.getElementById('sortBy').value;
  
  // Call API
  const response = await fetch('/api/prompts/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      search_term: searchTerm,
      category: category || null,
      sort_by: sortBy,
      user_id: currentUserId
    })
  });
  
  const data = await response.json();
  
  // Render prompt cards
  renderPromptCards(data.prompts);
}

function renderPromptCards(prompts) {
  const grid = document.getElementById('promptGrid');
  
  grid.innerHTML = prompts.map(prompt => `
    <div class="prompt-card" data-key="${prompt.prompt_key}">
      <div class="card-header">
        <span class="card-icon">${prompt.icon}</span>
        <h3 class="card-title">${prompt.prompt_name}</h3>
        <button class="favorite-btn" onclick="toggleFavorite('${prompt.prompt_slug}')">
          ${prompt.is_favorite ? '★' : '☆'}
        </button>
      </div>
      
      <p class="card-description">${prompt.short_description}</p>
      
      <div class="card-badges">
        <span class="badge category">${prompt.category}</span>
        <span class="badge visibility">${getVisibilityIcon(prompt.visibility)}</span>
        ${prompt.badge_text ? `<span class="badge special">${prompt.badge_text}</span>` : ''}
      </div>
      
      <div class="card-stats">
        <span class="rating">⭐ ${prompt.average_rating.toFixed(1)}</span>
        <span class="uses">👥 ${prompt.use_count} uses</span>
      </div>
      
      <div class="card-actions">
        <button class="btn-select" onclick="selectPrompt('${prompt.prompt_key}')">
          Select
        </button>
        <button class="btn-view" onclick="viewPromptDetail('${prompt.prompt_slug}')">
          View
        </button>
      </div>
    </div>
  `).join('');
}

// When user clicks Select button
let selectedLibraryPrompts = [];

function selectPrompt(promptKey) {
  if (selectedLibraryPrompts.includes(promptKey)) {
    selectedLibraryPrompts = selectedLibraryPrompts.filter(k => k !== promptKey);
  } else {
    selectedLibraryPrompts.push(promptKey);
  }
  
  updateSelectedDisplay();
}

function applySelectedPrompts() {
  // Close modal
  closeLibrary();
  
  // Prompts are now active in chat
  // They'll be included when user sends next message
}
```

**Backend API:**
```python
@prompt_routes.route('/api/prompts/search', methods=['POST'])
@require_auth
def search_prompts():
    user_id = request.user_id
    data = request.json
    
    search_term = data.get('search_term', '')
    category = data.get('category')
    sort_by = data.get('sort_by', 'popular')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search_term:
        # Use full-text search
        query = '''
            SELECT pl.* 
            FROM prompt_library pl
            INNER JOIN prompt_search_fts fts ON pl.prompt_id = fts.prompt_id
            WHERE prompt_search_fts MATCH ?
            AND pl.is_active = 1
            AND (
                pl.visibility = 'public'
                OR pl.created_by_user_id = ?
                OR pl.prompt_id IN (
                    SELECT prompt_id FROM prompt_shares 
                    WHERE shared_with_user_id = ? AND is_active = 1
                )
            )
        '''
        params = [search_term, user_id, user_id]
    else:
        # Browse all available prompts
        query = '''
            SELECT * FROM prompt_library
            WHERE is_active = 1
            AND (
                visibility = 'public'
                OR created_by_user_id = ?
                OR prompt_id IN (
                    SELECT prompt_id FROM prompt_shares 
                    WHERE shared_with_user_id = ? AND is_active = 1
                )
            )
        '''
        params = [user_id, user_id]
    
    # Add category filter
    if category:
        query += ' AND category = ?'
        params.append(category)
    
    # Add sorting
    if sort_by == 'popular':
        query += ' ORDER BY use_count DESC'
    elif sort_by == 'rating':
        query += ' ORDER BY average_rating DESC'
    elif sort_by == 'trending':
        query += ' ORDER BY trending_score DESC'
    elif sort_by == 'recent':
        query += ' ORDER BY created_at DESC'
    
    cursor.execute(query, params)
    prompts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'prompts': prompts,
        'count': len(prompts)
    })
```

---

### Component 3: Prompt Detail View

```
┌─ System Architect ──────────────────────────────────────────┐
│  [← Back]                                              [X]   │
│                                                              │
│  🏗️  System Architect                          [★ Favorite] │
│  Senior system architect specializing in...                 │
│                                                              │
│  💻 Development | 🌍 Public | 👤 Created by: Admin         │
│  ⭐⭐⭐⭐⭐ 4.8 (123 ratings) | 👥 456 uses | 🔥 Trending    │
│                                                              │
│  [✓ Select] [🔗 Share] [📋 Clone] [👁️ View Full Prompt]    │
│                                                              │
│  ┌─ Description ───────────────────────────────────────┐   │
│  │  You are a senior system architect with 15+ years  │   │
│  │  of experience designing scalable, distributed...  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Tags ──────────────────────────────────────────────┐   │
│  │  [architecture] [design] [scalability] [systems]   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Usage Examples ────────────────────────────────────┐   │
│  │  1. "Design a microservices architecture"          │   │
│  │  2. "Review this system design"                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Related Prompts ───────────────────────────────────┐   │
│  │  [🔒 Security Analyst] [⚡ Performance Engineer]    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─ Reviews ───────────────────────────────────────────┐   │
│  │  ⭐⭐⭐⭐⭐  Sarah: "Perfect for interviews!"        │   │
│  │  ⭐⭐⭐⭐    John: "Very detailed"                    │   │
│  │  [Add Your Review]                                  │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

**URL Structure:**
```
Modal view: Opens in overlay, no URL change
Deep link: /prompts/system-architect (uses prompt_slug)
```

**Data Loading:**
```javascript
async function viewPromptDetail(promptSlug) {
  const response = await fetch(`/api/prompts/${promptSlug}`);
  const data = await response.json();
  
  renderPromptDetail(data.prompt);
  
  // Track view
  await fetch('/api/prompts/track-view', {
    method: 'POST',
    body: JSON.stringify({
      prompt_slug: promptSlug,
      user_id: currentUserId
    })
  });
}
```

**Backend:**
```python
@prompt_routes.route('/api/prompts/<slug>', methods=['GET'])
@require_auth
def get_prompt_by_slug(slug):
    user_id = request.user_id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get prompt by slug
    cursor.execute('''
        SELECT * FROM prompt_library
        WHERE prompt_slug = ?
        AND is_active = 1
        AND (
            visibility = 'public'
            OR created_by_user_id = ?
            OR prompt_id IN (
                SELECT prompt_id FROM prompt_shares 
                WHERE shared_with_user_id = ? AND is_active = 1
            )
        )
    ''', (slug, user_id, user_id))
    
    prompt = cursor.fetchone()
    
    if not prompt:
        return jsonify({'error': 'Prompt not found'}), 404
    
    # Get related prompts
    if prompt['related_prompt_ids']:
        related_ids = json.loads(prompt['related_prompt_ids'])
        cursor.execute(f'''
            SELECT prompt_id, prompt_name, prompt_slug, icon, short_description
            FROM prompt_library
            WHERE prompt_id IN ({','.join('?' * len(related_ids))})
            AND is_active = 1
        ''', related_ids)
        related_prompts = cursor.fetchall()
    else:
        related_prompts = []
    
    # Get reviews
    cursor.execute('''
        SELECT pr.*, u.username
        FROM prompt_ratings pr
        INNER JOIN users u ON pr.user_id = u.id
        WHERE pr.prompt_id = ?
        ORDER BY pr.created_at DESC
        LIMIT 10
    ''', (prompt['prompt_id'],))
    reviews = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'prompt': dict(prompt),
        'related_prompts': [dict(r) for r in related_prompts],
        'reviews': [dict(r) for r in reviews]
    })
```

---

## Summary: Search & Discovery Mechanisms

| Method | Uses | Best For | Searchable? |
|--------|------|----------|-------------|
| **Quick Actions** | `prompt_key` | Fast, common tasks | No (visual only) |
| **Library Search** | `prompt_slug` + FTS | Finding specific prompts | Yes (full-text) |
| **Category Browse** | `category` | Exploring by topic | Yes (filter) |
| **Deep Link** | `prompt_slug` | Sharing URLs | Direct access |
| **Tags** | `tags` (JSON) | Keyword discovery | Yes (filter) |
| **Related** | `related_prompt_ids` | Discovery after detail | No (algorithmic) |
| **Trending** | `trending_score` | Popular prompts | No (sorted) |
| **Favorites** | User preference | Personal shortcuts | No (filter) |

**Key Insight:** 
- `prompt_key` = Internal API identifier (snake_case)
- `prompt_slug` = External URL identifier (kebab-case)
- Both are needed for different use cases!

**Status:** ✅ UI/UX Design Complete - Ready for implementation
