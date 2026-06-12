# AI Agent Instructions: Add Short Descriptions to All Tool Schemas

**Date:** December 10, 2025  
**Purpose:** Add vectorization-optimized `short_description` field to all 749+ tools  
**Priority:** CRITICAL for hybrid tool discovery system  
**Estimated Time:** 4-6 hours (automated processing recommended)

---

## 🎯 **Why This Matters**

### **Three Search Systems Working Together:**

Your tool discovery architecture uses **THREE complementary search strategies**:

#### **1. Keyword Search (75% accuracy)**
- **Location:** `tools/implementations/meta_tools.py` → `search_tools()`
- **Method:** Substring matching with synonym expansion
- **Speed:** Instant (no computation)
- **Limitation:** Misses semantic variations ("quote" vs "pricing")
- **Uses:** Direct API calls, explicit tool searches

#### **2. Semantic Search (90% accuracy)**
- **Location:** `tools/intelligent_discovery.py` → `SemanticToolSearch`
- **Method:** Vector embeddings with cosine similarity
- **Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)
- **Speed:** 30s initial load, then instant
- **Strength:** Understands intent ("I need to quote a brochure" → calculate_booklets)
- **Uses:** AI agent requests, natural language queries

#### **3. Hybrid Search (95% accuracy)**
- **Location:** `tools/intelligent_discovery.py` → `IntelligentToolSuggestion`
- **Method:** Combines keyword (0.8x) + semantic (1.0x) + context (1.3x) + platform auth (2.0x)
- **Strength:** Best of both worlds with personalization AND security
- **Platform Filtering:** **HARD EXCLUSION** - Tools from unauthenticated platforms are completely removed from results
- **Uses:** Production AI agent (line 2010 in `combined_agent_worker.py`)

**🔒 Platform Authentication Filtering (CRITICAL):**
- If user has Google auth only → **ONLY Google tools shown** (Gmail, Docs, Drive)
- If user has no Microsoft auth → **Microsoft tools EXCLUDED entirely** (not just penalized)
- If user explicitly mentions platform ("send Outlook email") → Filter bypassed (respects intent)
- **Result:** AI can NEVER suggest tools the user cannot execute
- **Validation:** See `test_intelligent_discovery.py` for test suite

### **The Problem:**

All three systems rely on tool descriptions for matching. Currently:

❌ **No `short_description` field exists** → Search results must return full 500+ line descriptions  
❌ **Token bloat** → 150K tokens per request just for tool metadata  
❌ **Poor vectorization** → 500-line descriptions create noisy embeddings dominated by "CRITICAL", "RULES", "WARNING"  
❌ **Slow AI comprehension** → AI must parse massive descriptions to pick tools  
❌ **Test Results:** Semantic search failing on 25% of queries ("hardcover binding" returned wrong tools)

**Evidence:** `test_intelligent_discovery.py` shows query "I need pricing for hardcover binding" failed to find calculator tools because current descriptions don't contain clean, action-focused keywords.  

### **The Solution:**

✅ **Add `short_description`** → Compact, vectorization-optimized summaries  
✅ **Keyword-rich** → Improves substring matching accuracy  
✅ **Semantic-optimized** → Clean embeddings for similarity search  
✅ **Token-efficient** → 50-120 chars vs 5000+ chars  
✅ **Fast AI scanning** → Quick tool identification before schema retrieval  

---

## 📊 **Current Tool Schema Structure Analysis**

After analyzing 30+ tool JSON files, here's the unified structure:

### **Variation 1: Platform-Level Schema (Most Common)**
```json
{
  "platform": "calculator_tools",  // ← Platform field CRITICAL for auth filtering
  "description": "Platform-level description of all tools in this file",
  "tools": [
    {
      "name": "calculate_flyers",
      "short_description": "Calculate flyer quotes with sizing and finishing options",  // ← ADD THIS
      "description": "FULL DETAILED DESCRIPTION (100-500 lines)",  // ← Keep this
      "parameters": { ... }
    }
  ]
}
```
**Files:** calculator_tools.json, adobe_indesign_*.json, google_*.json, microsoft_*.json  
**Count:** ~85% of all schemas  
**Note:** `platform` field is used for authentication filtering (hard exclusion of unavailable platforms)

### **Variation 2: No Platform Field (Legacy)**
```json
{
  "tools": [
    {
      "name": "some_tool",
      "short_description": "Short action-focused summary",  // ← ADD THIS
      "description": "Full description",
      "parameters": { ... }
    }
  ]
}
```
**Files:** Some older tool definitions  
**Count:** ~10% of schemas  
**Action:** Add `platform` field if these tools need auth filtering

### **Variation 3: Category-Based (Meta Tools)**
```json
{
  "platform": "adobe_indesign_meta",
  "description": "Meta tools for tool discovery",
  "categories": {
    "document_creation": ["tool1", "tool2"],
    "data_merge": ["tool3", "tool4"]
  },
  "tools": [ ... ]
}
```
**Files:** *_meta_tools.json  
**Count:** ~5% of schemas

---

## 🎯 **Target JSON Structure**

### **Add This Field to EVERY Tool:**

```json
{
  "platform": "calculator",
  "description": "Platform description (KEEP AS-IS)",
  "tools": [
    {
      "name": "calculate_flyers",
      "short_description": "Calculate printing quotes for flyers with sizing and finishing options",
      "description": "🚨 CRITICAL EXECUTION RULES:\n(1) Execute THIS tool NOW...\n\n[KEEP ALL EXISTING CONTENT - DO NOT MODIFY]",
      "parameters": { ... }
    }
  ]
}
```

### **Critical Rules:**

1. ✅ **ADD** `short_description` field (NEW)
2. ✅ **KEEP** `description` field (UNCHANGED - all existing content must remain)
3. ✅ **PRESERVE** all other fields exactly as they are
4. ✅ **MAINTAIN** JSON formatting and structure

---

## 📝 **Short Description Writing Guidelines**

### **Format Template:**
```
[ACTION_VERB] [PRIMARY_OBJECT] [KEY_FEATURES/CRITERIA]
```

### **Length Requirements:**
- **Minimum:** 50 characters (8 words)
- **Optimal:** 60-100 characters (10-14 words)
- **Maximum:** 120 characters (18 words)

### **Required Elements:**

#### **1. Lead with Action Verb**
```
✅ Calculate, Search, Create, Generate, Send, Read, Update, Delete, Export, Import
❌ This tool, A tool for, Used to, Helps with
```

#### **2. Include Platform/Domain Context**
```
✅ "Search Gmail inbox for emails by sender or subject"
✅ "Calculate Shopify product pricing with bulk discounts"
✅ "Create InDesign catalog from CSV data with images"
❌ "Search for items" (missing platform)
❌ "Calculate prices" (missing domain)
```

#### **3. Specify Key Capabilities**
```
✅ "with sizing, stock, and finishing options"
✅ "by sender, subject, date, or keywords"
✅ "from CSV data with automatic layout"
❌ "with options" (too vague)
❌ "by parameters" (not specific)
```

#### **4. Use Natural Conversational Language**
```
✅ "Search Gmail inbox for emails by sender"
❌ "Query gmail_messages table by sender_email field"
❌ "GET /gmail/messages?from={sender}"
```

#### **5. Include Common Synonyms**
```
✅ "Calculate quote/pricing for booklets and brochures"
✅ "Search/find emails in Gmail inbox by keyword"
❌ "Calculate booklet pricing" (missing synonyms)
```

### **Special Markers:**

#### **For Multi-Step/Smart Tools:**
```json
{
  "name": "indesign_create_catalog_from_data",
  "short_description": "SMART: Create complete catalog from CSV with images, layout, TOC, and PDF export",
  "description": "..."
}
```

#### **For Workflow Tools:**
```json
{
  "name": "synergy_project_manager",
  "short_description": "WORKFLOW: Manage multi-platform projects with task automation and status tracking",
  "description": "..."
}
```

---

## ❌ **DO NOT Add Category Field**

**Decision:** After analysis, we determined `category` field is **NOT NEEDED**.

**Why Category Is Unnecessary:**
1. **Platform field is sufficient** - Already groups tools by service (google_gmail, microsoft_excel, calculator_tools)
2. **Semantic search handles categorization** - Automatically clusters similar tools (all email tools score high for "send message" queries)
3. **Short description contains keywords** - Natural language is more flexible than rigid taxonomy
4. **Maintenance burden** - Another field to validate, another taxonomy to maintain
5. **No clear benefit** - Testing showed semantic search works without explicit categories

**Example:**
```json
// ❌ DON'T DO THIS
{
  "platform": "calculator_tools",
  "category": "printing_calculation",  // ← NOT NEEDED!
  "tools": [...]
}

// ✅ DO THIS INSTEAD
{
  "platform": "calculator_tools",  // ← Platform is enough
  "tools": [
    {
      "short_description": "Calculate printing cost for flyers"  // ← Keywords do the job
    }
  ]
}
```

**Platform field provides:**
- Authentication filtering (hard exclusion)
- OAuth credential injection (_user_id parameter)
- Service grouping (Gmail vs Outlook)

**Short description provides:**
- Semantic clustering (printing vs emailing)
- Keyword matching (flyer, quote, cost)
- Natural language search

No need for a rigid category taxonomy!

---

## 🔍 **Vectorization Optimization**

### **Why This Matters for Semantic Search:**

The sentence-transformer model (`all-MiniLM-L6-v2`) creates 384-dimensional embeddings from text. Quality matters:

#### **Good Embedding (High Information Density):**
```python
# Input: "Calculate printing quotes for flyers with sizing and finishing"
# Embedding: Strong signals for [calculate, pricing, quote, print, flyer, size, finish]
# Cosine similarity with "I need a flyer quote": 0.87 ✅

# Query: "I need to quote a brochure"
# Matches: calculate_booklets (0.89), calculate_flyers (0.81), calculate_saddle_stitch (0.78)
```

#### **Bad Embedding (Noisy, Diluted):**
```python
# Input: "🚨 CRITICAL EXECUTION RULES:\n(1) Execute THIS tool NOW - NEVER use cached data...\n\n[500 more lines]"
# Embedding: Weak signals (dominated by "CRITICAL", "RULES", "NEVER", "cached")
# Cosine similarity with "I need a flyer quote": 0.31 ❌

# Query: "I need to quote a brochure"
# Matches: [random tools with similar warning text]
```

### **Semantic Clustering Strategy:**

Good short descriptions create natural clusters in embedding space:

```python
# CLUSTER 1: Printing/Quoting Tools (high similarity 0.85-0.95)
"Calculate flyer quotes with sizing and stock options"
"Calculate booklet quotes with binding and page count"
"Calculate business card quotes with dimensions and finish"
"Calculate sign quotes with material and size specifications"

# CLUSTER 2: Email Search Tools (high similarity 0.88-0.94)
"Search Gmail inbox for emails by sender, subject, or date"
"Search Outlook mailbox for messages by keyword or folder"
"Search Microsoft Teams messages by channel or user"

# CLUSTER 3: Document Creation Tools (high similarity 0.86-0.92)
"Create InDesign document from template with data merge"
"Create Word document from template with dynamic content"
"Generate PDF export with bleed and crop marks"
```

When a user asks "I need to quote a brochure", semantic search:
1. Converts query to 384-dim embedding
2. Computes cosine similarity with all tool embeddings
3. Returns top matches from CLUSTER 1 (0.85+ similarity)
4. Ignores noise from CLUSTER 2 and CLUSTER 3

---

## 📋 **Task Execution Steps**

### **Phase 1: Analyze Tool Structure (30 minutes)**

1. Read each JSON file in `tools/schemas/`
2. Identify structure variation (platform-level, legacy, meta)
3. Document any unusual structures
4. Create backup: `tools/schemas_backup_[DATE]/`

### **Phase 2: Generate Short Descriptions (3-4 hours)**

For each tool in each JSON file:

1. **Read existing `description` field**
2. **Extract core purpose** (ignore execution rules, examples, parameters)
3. **Identify action verb** (Calculate, Search, Create, etc.)
4. **Identify primary object** (flyers, emails, documents, etc.)
5. **Identify key features** (sizing options, search criteria, etc.)
6. **Construct short description** using template
7. **Validate length** (50-120 characters)
8. **Insert `short_description` field** BEFORE `description` field
9. **Preserve all existing content**

### **Phase 3: Validation (30 minutes)**

1. **JSON Syntax Check:**
   ```bash
   python -c "import json; [json.load(open(f)) for f in glob.glob('tools/schemas/*.json')]"
   ```

2. **Field Presence Check:**
   ```python
   # Verify all tools have short_description
   missing = []
   for schema_file in schemas:
       for tool in schema['tools']:
           if 'short_description' not in tool:
               missing.append(tool['name'])
   ```

3. **Length Validation:**
   ```python
   # Check length requirements
   for tool in all_tools:
       sd = tool['short_description']
       if len(sd) < 50 or len(sd) > 120:
           warnings.append(f"{tool['name']}: {len(sd)} chars")
   ```

4. **Test Semantic Search:**
   ```python
   # Run test queries
   queries = [
       "I need to quote a brochure",
       "search my gmail for invoices",
       "create a PDF from InDesign"
   ]
   for q in queries:
       results = semantic_search.search(q, top_k=5)
       print(f"Query: {q}")
       print(f"Top 5: {[r['tool_name'] for r in results]}")
   ```

### **Phase 4: Registry Update (15 minutes)**

Update `tools/registry_v3.py` to expose `short_description`:

```python
# In RegistryV3._load_schemas() method
for tool_def in tools_list:
    tool_info = {
        'function': tool_func,
        'schema': tool_def,
        'platform': platform_name,
        'description': tool_def.get('description', ''),
        'short_description': tool_def.get('short_description', ''),  # ADD THIS
        'parameters': tool_def.get('parameters', {})
    }
```

---

## 📖 **Example Transformations**

### **Example 1: Calculator Tool**

**BEFORE:**
```json
{
  "name": "calculate_flyers",
  "description": "🚨 CRITICAL EXECUTION RULES:\n(1) Execute THIS tool NOW - NEVER use cached/remembered data from conversation history\n(2) MUST cite resource: 'Read X from **[Resource Name]** (ID: `[id]` | URL: [url])'\n(3) Use EXACT [id] provided - NEVER substitute with different ID\n(4) If tool fails (404/403), say 'Failed to read [resource] ID: [id]' and explain error\n(5) NEVER make up data if read fails - acknowledge the failure clearly\n\nExample response:\nRead 45 rows from **Sales Spreadsheet**\n- ID: `xyz789`\n- URL: https://example.com/sheet/xyz789\n- Data: [actual data read]\n\nCalculate quote for digital flyers/leaflets. ALSO used for BUSINESS CARDS (90mm x 55mm). Supports various stock types, print modes (single/double sided), quantities, and cellophane finishes. Returns detailed quote with cost breakdown.",
  "parameters": { ... }
}
```

**AFTER:**
```json
{
  "name": "calculate_flyers",
  "short_description": "Calculate printing quotes for flyers and business cards with stock, sizing, and finish options",
  "description": "🚨 CRITICAL EXECUTION RULES:\n(1) Execute THIS tool NOW - NEVER use cached/remembered data from conversation history\n(2) MUST cite resource: 'Read X from **[Resource Name]** (ID: `[id]` | URL: [url])'\n(3) Use EXACT [id] provided - NEVER substitute with different ID\n(4) If tool fails (404/403), say 'Failed to read [resource] ID: [id]' and explain error\n(5) NEVER make up data if read fails - acknowledge the failure clearly\n\nExample response:\nRead 45 rows from **Sales Spreadsheet**\n- ID: `xyz789`\n- URL: https://example.com/sheet/xyz789\n- Data: [actual data read]\n\nCalculate quote for digital flyers/leaflets. ALSO used for BUSINESS CARDS (90mm x 55mm). Supports various stock types, print modes (single/double sided), quantities, and cellophane finishes. Returns detailed quote with cost breakdown.",
  "parameters": { ... }
}
```

### **Example 2: Email Tool**

**BEFORE:**
```json
{
  "name": "google_gmail_search_messages",
  "description": "Search Gmail messages using advanced query syntax. Supports filtering by sender, recipient, subject, date range, labels, attachments, and more. Returns message IDs, snippets, and metadata. Use this to find specific emails before reading their full content.",
  "parameters": { ... }
}
```

**AFTER:**
```json
{
  "name": "google_gmail_search_messages",
  "short_description": "Search Gmail inbox for emails by sender, subject, date range, or keywords",
  "description": "Search Gmail messages using advanced query syntax. Supports filtering by sender, recipient, subject, date range, labels, attachments, and more. Returns message IDs, snippets, and metadata. Use this to find specific emails before reading their full content.",
  "parameters": { ... }
}
```

### **Example 3: Smart Tool**

**BEFORE:**
```json
{
  "name": "indesign_create_catalog_from_data",
  "description": "SMART TOOL: Creates complete product catalog from CSV data and template. Executes: (1) Document creation, (2) Data merge setup, (3) Image placement, (4) Style application, (5) TOC generation, (6) Preflight check, (7) PDF export. All in one call.",
  "parameters": { ... }
}
```

**AFTER:**
```json
{
  "name": "indesign_create_catalog_from_data",
  "short_description": "SMART: Create complete catalog from CSV with images, layout, TOC, and PDF export",
  "description": "SMART TOOL: Creates complete product catalog from CSV data and template. Executes: (1) Document creation, (2) Data merge setup, (3) Image placement, (4) Style application, (5) TOC generation, (6) Preflight check, (7) PDF export. All in one call.",
  "parameters": { ... }
}
```

### **Example 4: Search/Meta Tool**

**BEFORE:**
```json
{
  "name": "search_tools",
  "description": "Search for tools by keyword or description. Returns matching tool names with brief descriptions. Use this when you're not sure which specific tool to use for a task.",
  "parameters": { ... }
}
```

**AFTER:**
```json
{
  "name": "search_tools",
  "short_description": "Search all available tools by keyword, platform, or capability description",
  "description": "Search for tools by keyword or description. Returns matching tool names with brief descriptions. Use this when you're not sure which specific tool to use for a task.",
  "parameters": { ... }
}
```

---

## ⚠️ **Critical Warnings**

### **DO NOT:**

❌ **Modify existing `description` fields** - These contain critical execution rules
❌ **Remove any fields** - Preserve complete schema structure
❌ **Change parameter definitions** - These are used for validation
❌ **Alter tool names** - These are function references
❌ **Break JSON syntax** - Validate after every file

### **DO:**

✅ **Add `short_description` as NEW field** - Insert before `description`
✅ **Preserve all existing content** - Copy-paste, don't rewrite
✅ **Validate JSON after changes** - Use linter or parser
✅ **Create backups** - Copy schemas before modifying
✅ **Test incrementally** - Process 5-10 files, then test

---

## 🧪 **Testing & Validation**

### **Test 1: Keyword Search Accuracy**

```python
from tools.implementations.meta_tools import search_tools

# Test queries
test_queries = [
    ("calculator", 27),  # Should find all 27 calculator tools
    ("quote", 30),       # Should find all quoting tools
    ("gmail", 15),       # Should find all Gmail tools
    ("create", 50),      # Should find all creation tools
]

for query, expected_min in test_queries:
    results = search_tools(query)
    print(f"Query: '{query}' → Found: {len(results)} (expected: {expected_min}+)")
    assert len(results) >= expected_min
```

### **Test 2: Semantic Search Quality**

```python
from tools.intelligent_discovery import SemanticToolSearch

semantic = SemanticToolSearch(registry)

# Natural language queries
test_queries = [
    "I need to quote a brochure",
    "search my gmail for invoice emails",
    "make a PDF from InDesign",
    "send a teams message to my colleague"
]

for query in test_queries:
    results = semantic.search(query, top_k=5)
    print(f"\nQuery: {query}")
    for r in results:
        print(f"  {r['tool_name']}: {r['short_description']} (sim: {r['similarity']:.2f})")
```

### **Test 3: Token Efficiency**

```python
import json

# Calculate token savings
total_tokens_before = 0
total_tokens_after = 0

for schema_file in schemas:
    for tool in schema['tools']:
        # Before: Full description only
        tokens_before = len(tool['description']) / 4  # Rough estimate
        
        # After: Short description for listings
        tokens_after = len(tool['short_description']) / 4
        
        total_tokens_before += tokens_before
        total_tokens_after += tokens_after

savings = (total_tokens_before - total_tokens_after) / total_tokens_before
print(f"Token reduction: {savings:.1%}")
print(f"Before: ~{total_tokens_before:,.0f} tokens")
print(f"After:  ~{total_tokens_after:,.0f} tokens")
```

---

## 📊 **Expected Results**

### **Search Accuracy Improvements:**

| Search Type | Before | After | Improvement |
|-------------|--------|-------|-------------|
| Keyword Search | 41% | 85%+ | +44% |
| Semantic Search | 75% | 95%+ | +20% |
| Hybrid Search | 80% | 98%+ | +18% |

### **Token Efficiency:**

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Tool List (10 tools) | ~25,000 tokens | ~500 tokens | 98% |
| Search Results (20 tools) | ~50,000 tokens | ~1,000 tokens | 98% |
| Full Schema Request | ~2,000 tokens | ~2,000 tokens | 0% (unchanged) |

### **AI Performance:**

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Tool Selection Time | 3-5 requests | 1-2 requests | 60% faster |
| First-Try Accuracy | 65% | 92%+ | +27% |
| Token Usage per Session | 180K avg | 45K avg | 75% reduction |

---

## 🚀 **Next Steps After Completion**

Once all tools have `short_description` fields:

### **1. Update hybrid_tool_search (NEW TOOL)**
Create unified search tool that returns short descriptions:
```python
def hybrid_tool_search(query, top_k=10):
    # Combine semantic + keyword + platform
    # Return: tool_name, platform, short_description, confidence
    pass
```

### **2. Update Passive Suggestions**
Inject top 5 tools into system prompt:
```python
# In combined_agent_worker.py (line 2057)
system_prompt += f"\n\nRECOMMENDED TOOLS:\n"
for tool in suggested_tools[:5]:
    system_prompt += f"- {tool['tool_name']}: {tool['short_description']}\n"
```

### **3. Update Meta Tools**
Modify `search_tools()` to return short descriptions:
```python
return {
    'tool_name': tool_name,
    'platform': platform,
    'short_description': tool_info['short_description'],
    'score': relevance_score
}
```

### **4. Update intelligent_discovery.py**
Return short descriptions in semantic search results:
```python
def search(self, query, top_k=10):
    # ... existing logic ...
    return {
        'tool_name': tool_name,
        'similarity': similarity,
        'short_description': self.registry.tools[tool_name]['short_description']
    }
```

---

## 📁 **Files to Process**

Total files: ~60 JSON schema files in `tools/schemas/`

**Priority Order:**

### **High Priority (User-Facing Tools):**
1. `calculator_tools.json` - 27 tools
2. `google_gmail_tools.json` - 15+ tools
3. `google_calendar_tools.json` - 12+ tools
4. `microsoft_outlook_tools.json` - 15+ tools
5. `microsoft_teams_tools.json` - 10+ tools
6. `shopify_*.json` - 30+ tools

### **Medium Priority (Developer Tools):**
7. `adobe_indesign_*.json` - 50+ tools
8. `slack_tools.json` - 10+ tools
9. `notion_tools.json` - 8+ tools
10. `synergy_*.json` - 20+ tools

### **Low Priority (Specialized Tools):**
11. All remaining schema files

---

## ✅ **Completion Checklist**

- [ ] Backup all schemas to `tools/schemas_backup_[DATE]/`
- [ ] Process all high-priority files (calculator, google, microsoft)
- [ ] Process all medium-priority files (adobe, slack, notion)
- [ ] Process all remaining schema files
- [ ] Validate JSON syntax (no parse errors)
- [ ] Verify all tools have `short_description` field
- [ ] Check length requirements (50-120 chars)
- [ ] Test keyword search accuracy
- [ ] Test semantic search quality
- [ ] Measure token efficiency gains
- [ ] Update registry_v3.py to expose short_description
- [ ] Update meta_tools.py to return short_description
- [ ] Update intelligent_discovery.py to return short_description
- [ ] Test hybrid search integration
- [ ] Document any unusual cases or exceptions
- [ ] Commit changes with clear message

---

## 🎯 **Success Criteria**

This task is complete when:

1. ✅ All 749+ tools have `short_description` field
2. ✅ All short descriptions are 50-120 characters
3. ✅ All short descriptions follow format guidelines
4. ✅ JSON syntax is valid across all files
5. ✅ Keyword search finds 85%+ of relevant tools
6. ✅ Semantic search achieves 95%+ accuracy
7. ✅ Token usage reduced by 75%+ for listings
8. ✅ Registry and discovery systems updated
9. ✅ Tests pass for all search strategies

---

**REMEMBER:** The goal is to enable efficient, accurate tool discovery across three search systems (keyword, semantic, hybrid) while preserving all existing critical execution rules in the full `description` field.
