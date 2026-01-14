# Tool Discovery System - Implementation Checklist

**Status**: 🚧 Ready to Implement  
**Estimated Time**: 11 hours (3 days)  
**Files Modified**: 2 files (meta_tools.py, calculator_tools.json)

---

## Pre-Implementation Setup

- [ ] Read `TOOL_DISCOVERY_EXECUTIVE_SUMMARY.md` (high-level overview)
- [ ] Read `CALCULATOR_TOOL_DISCOVERY_IMPROVEMENT_PLAN.md` (technical details)
- [ ] Create feature branch: `git checkout -b feature/tool-discovery-improvements`
- [ ] Backup current meta_tools.py: `cp tools/implementations/meta_tools.py tools/implementations/meta_tools.py.backup`

---

## Phase 1: Search Algorithm Enhancement (2 hours)

**File**: `tools/implementations/meta_tools.py`  
**Function**: `search_tools()` starting at line 472

### Checklist

- [ ] **Step 1.1**: Add synonym expansion dictionary (50 lines)
  - [ ] Copy synonym_map from improvement plan (section "Phase 1")
  - [ ] Test: `search_tools("calculator")` should expand to `["calculator", "calculate", "quote", "pricing"]`

- [ ] **Step 1.2**: Implement multi-strategy search (80 lines)
  - [ ] Strategy 1: Tool name substring matching (highest relevance)
  - [ ] Strategy 2: Description substring matching (medium relevance)
  - [ ] Strategy 3: Platform name matching (lowest relevance)
  - [ ] Add relevance scores (1.0, 0.8, 0.6)

- [ ] **Step 1.3**: Sort results by relevance (10 lines)
  - [ ] Primary sort: relevance score (desc)
  - [ ] Secondary sort: tool name (asc)

- [ ] **Step 1.4**: Update response format (20 lines)
  - [ ] Add `match_type` field to each tool
  - [ ] Add `relevance` score to each tool
  - [ ] Add `search_strategies` list to response
  - [ ] Add `synonyms_used` list to response

### Testing

```python
# Test 1: Calculator search
result = search_tools("calculator")
assert result['match_count'] >= 27, f"Expected 27+ tools, got {result['match_count']}"
print(f"✅ Test 1 passed: Found {result['match_count']} calculator tools")

# Test 2: Synonym expansion
result = search_tools("booklet")
tool_names = [t['name'] for t in result['tools']]
assert 'calculate_booklets' in tool_names, "Should find calculate_booklets"
assert 'calculate_saddle_stitch_books' in tool_names, "Should find saddle stitch"
print(f"✅ Test 2 passed: Synonym expansion working ({len(tool_names)} tools)")

# Test 3: Name matching priority
result = search_tools("gmail")
first_tool = result['tools'][0]
assert first_tool['match_type'] == 'name_match', "Name matches should be first"
assert first_tool['relevance'] == 1.0, "Name matches should have 1.0 relevance"
print(f"✅ Test 3 passed: Name matching prioritized")

# Test 4: Platform matching
result = search_tools("google")
platforms = set(t['platform'] for t in result['tools'])
assert 'gmail' in platforms, "Should match gmail platform"
assert 'google_sheets' in platforms, "Should match google_sheets platform"
print(f"✅ Test 4 passed: Platform matching working ({len(platforms)} platforms)")
```

**Success Criteria**: All 4 tests pass

- [ ] Run tests
- [ ] Fix any failures
- [ ] Commit: `git commit -m "Phase 1: Enhanced search algorithm with synonym expansion and multi-strategy matching"`

---

## Phase 2: Intelligent Recommendations (3 hours)

**File**: `tools/implementations/meta_tools.py`  
**Function**: `recommend_tools_for_task()` starting at line 775

### Checklist

- [ ] **Step 2.1**: Add intent detection patterns (40 lines)
  - [ ] Copy intent_patterns dict from improvement plan
  - [ ] 10 intents: calculate_quote, send_email, create_document, schedule_meeting, etc.
  - [ ] Test: `"generate quote"` → detects `calculate_quote` intent

- [ ] **Step 2.2**: Add entity extraction patterns (40 lines)
  - [ ] Copy product_patterns dict from improvement plan
  - [ ] Patterns for: booklets, business_cards, flyers, books, signs, etc.
  - [ ] Test: `"quote for 500 booklets"` → extracts product="booklets", quantity=500

- [ ] **Step 2.3**: Build recommendation database (150 lines)
  - [ ] Copy recommendations dict from improvement plan
  - [ ] Structure: intent → product → {primary_tool, alternatives, workflow, params}
  - [ ] Cover: calculate_quote (5 products), send_email, create_document, etc.

- [ ] **Step 2.4**: Implement matching logic (60 lines)
  - [ ] Extract intent from task description
  - [ ] Extract product/entity from task description
  - [ ] Extract quantity (regex: `\d+`)
  - [ ] Look up recommendation in database
  - [ ] Fallback to enhanced search if no match

- [ ] **Step 2.5**: Format response (40 lines)
  - [ ] Return: primary_tool, workflow steps, alternatives, required_parameters
  - [ ] Add: detected_intent, detected_product, detected_quantity
  - [ ] Include: common_use_case, next_step

### Testing

```python
# Test 1: Booklet quote
rec = recommend_tools_for_task("Generate a quote for 500 booklets")
assert rec['primary_tool'] == 'calculate_booklets', "Should recommend booklets tool"
assert rec['detected_intent'] == 'calculate_quote', "Should detect quote intent"
assert rec['detected_product'] == 'booklets', "Should extract booklets"
assert rec['detected_quantity'] == 500, "Should extract 500"
assert len(rec['workflow']) >= 3, "Should provide workflow steps"
print("✅ Test 1 passed: Booklet recommendation working")

# Test 2: Business cards
rec = recommend_tools_for_task("I need pricing for 1000 business cards")
assert rec['primary_tool'] == 'calculate_business_cards', "Should recommend cards"
assert rec['detected_quantity'] == 1000, "Should extract 1000"
print("✅ Test 2 passed: Business card recommendation working")

# Test 3: Email
rec = recommend_tools_for_task("Send an email to john@example.com")
assert 'gmail_send_email' in [rec['primary_tool']] + rec.get('alternatives', []), "Should recommend email"
assert rec['detected_intent'] == 'send_email', "Should detect email intent"
print("✅ Test 3 passed: Email recommendation working")

# Test 4: Fallback to search
rec = recommend_tools_for_task("Some vague unstructured task")
assert rec['success'] == True, "Should return success"
assert rec['recommendation_type'] == 'search_based', "Should fall back to search"
print("✅ Test 4 passed: Fallback working")

# Test 5: Workflow steps
rec = recommend_tools_for_task("Generate quote for booklets")
assert 'workflow' in rec, "Should have workflow"
assert len(rec['workflow']) >= 3, "Should have 3+ steps"
assert any('get_tool_schema' in step.lower() for step in rec['workflow']), "Should mention schema"
print("✅ Test 5 passed: Workflow guidance present")
```

**Success Criteria**: All 5 tests pass

- [ ] Run tests
- [ ] Fix any failures
- [ ] Commit: `git commit -m "Phase 2: Intelligent tool recommendations with intent detection and workflow guidance"`

---

## Phase 3: Platform Metadata Enhancement (2 hours)

**File**: `tools/implementations/meta_tools.py`  
**Function**: `list_available_platforms()` starting at line 11

### Checklist

- [ ] **Step 3.1**: Add platform_metadata dictionary (100 lines)
  - [ ] Copy platform_metadata dict from improvement plan
  - [ ] Include: calculator, gmail, google_sheets, microsoft_outlook, xero_quotes
  - [ ] Each entry has: description, categories, tags, use_cases, related_platforms

- [ ] **Step 3.2**: Update platform collection logic (40 lines)
  - [ ] Loop through registry.tools and group by platform
  - [ ] Count tools per platform
  - [ ] Collect tool names per platform

- [ ] **Step 3.3**: Build rich platform objects (60 lines)
  - [ ] For each platform, combine tool data with metadata
  - [ ] Create platform object with 7 fields (name, tool_count, description, categories, tags, use_cases, related_platforms)
  - [ ] Provide default metadata for platforms not in dictionary

- [ ] **Step 3.4**: Update response format (20 lines)
  - [ ] Return platforms as array of objects (not just names)
  - [ ] Add usage_guide section
  - [ ] Keep backward compatibility (still return platform_count, total_tools)

### Testing

```python
# Test 1: Response structure
result = list_available_platforms()
assert 'platforms' in result, "Should have platforms key"
assert isinstance(result['platforms'], list), "Platforms should be a list"
first_platform = result['platforms'][0]
assert 'name' in first_platform, "Should have name"
assert 'description' in first_platform, "Should have description"
assert 'tool_count' in first_platform, "Should have tool_count"
print("✅ Test 1 passed: Response structure correct")

# Test 2: Rich metadata fields
assert 'categories' in first_platform, "Should have categories"
assert 'tags' in first_platform, "Should have tags"
assert 'use_cases' in first_platform, "Should have use_cases"
assert 'related_platforms' in first_platform, "Should have related_platforms"
print("✅ Test 2 passed: Metadata fields present")

# Test 3: Calculator platform
calculator = next((p for p in result['platforms'] if p['name'] == 'calculator'), None)
assert calculator is not None, "Should have calculator platform"
assert len(calculator['categories']) > 0, "Should have categories"
assert 'print' in calculator['categories'], "Should have print category"
assert len(calculator['use_cases']) > 0, "Should have use cases"
print("✅ Test 3 passed: Calculator metadata correct")

# Test 4: Backward compatibility
assert 'platform_count' in result, "Should have platform_count"
assert 'total_tools' in result, "Should have total_tools"
assert result['platform_count'] >= 50, "Should have 50+ platforms"
assert result['total_tools'] >= 700, "Should have 700+ tools"
print("✅ Test 4 passed: Backward compatibility maintained")
```

**Success Criteria**: All 4 tests pass

- [ ] Run tests
- [ ] Fix any failures
- [ ] Commit: `git commit -m "Phase 3: Rich platform metadata with descriptions, categories, tags, and use cases"`

---

## Phase 4: Calculator Platform Reorganization (4 hours)

**File**: `tools/schemas/calculator_tools.json`

### Checklist

- [ ] **Step 4.1**: Backup original file
  - [ ] `cp tools/schemas/calculator_tools.json tools/schemas/calculator_tools.json.backup`

- [ ] **Step 4.2**: Add sub_platforms section (20 lines)
  - [ ] Add top-level "sub_platforms" object
  - [ ] Define 5 sub-platforms: calculator_print, calculator_books, calculator_signs, calculator_stationery, calculator_specialty
  - [ ] Add descriptions for each

- [ ] **Step 4.3**: Update tool definitions (27 tools × 3 fields = 81 changes)
  - [ ] Print tools (4): calculate_flyers, calculate_business_cards, calculate_printed_letterheads, calculate_with_compliments_slips
    - [ ] Change platform to "calculator_print"
    - [ ] Add category: "print"
    - [ ] Add product_type
  
  - [ ] Book tools (4): calculate_booklets, calculate_saddle_stitch_books, calculate_spiral_bound_books, calculate_perfect_bound_books
    - [ ] Change platform to "calculator_books"
    - [ ] Add category: "books"
    - [ ] Add product_type
  
  - [ ] Sign tools (8): calculate_corflute_signs, calculate_bollard_signs, calculate_election_signs, calculate_construction_signs, calculate_corflute_insert_a_frame, calculate_metal_face_a_frame, calculate_strut_cards_a3, calculate_strut_cards_a4
    - [ ] Change platform to "calculator_signs"
    - [ ] Add category: "signs"
    - [ ] Add product_type
  
  - [ ] Stationery tools (4): calculate_notepads_a4, calculate_notepads_a5, calculate_notepads_a6, calculate_premium_bookmarks
    - [ ] Change platform to "calculator_stationery"
    - [ ] Add category: "stationery"
    - [ ] Add product_type
  
  - [ ] Specialty tools (7): calculate_selfie_frames, calculate_stackable_cubes, calculate_luxury_classic_pull_up_banners, calculate_custom_poster_printing, calculate_custom_vinyl_stickers, etc.
    - [ ] Change platform to "calculator_specialty"
    - [ ] Add category: "specialty"
    - [ ] Add product_type

- [ ] **Step 4.4**: Validate JSON syntax
  - [ ] Use JSON linter or `python -m json.tool calculator_tools.json`
  - [ ] Fix any syntax errors

### Testing

```python
# Test 1: Sub-platform exists
result = list_platform_tools("calculator_books")
assert result['success'] == True, "calculator_books platform should exist"
assert len(result['tools']) >= 4, "Should have 4+ book tools"
print(f"✅ Test 1 passed: calculator_books has {len(result['tools'])} tools")

# Test 2: Book tools correctly categorized
tool_names = [t['name'] for t in result['tools']]
assert 'calculate_booklets' in tool_names, "Should include booklets"
assert 'calculate_saddle_stitch_books' in tool_names, "Should include saddle stitch"
assert 'calculate_spiral_bound_books' in tool_names, "Should include spiral"
assert 'calculate_perfect_bound_books' in tool_names, "Should include perfect bound"
print("✅ Test 2 passed: All book tools present")

# Test 3: Sign platform
result = list_platform_tools("calculator_signs")
assert result['success'] == True, "calculator_signs platform should exist"
assert len(result['tools']) >= 6, "Should have 6+ sign tools"
print(f"✅ Test 3 passed: calculator_signs has {len(result['tools'])} tools")

# Test 4: Print platform
result = list_platform_tools("calculator_print")
assert result['success'] == True, "calculator_print platform should exist"
assert len(result['tools']) >= 4, "Should have 4+ print tools"
print(f"✅ Test 4 passed: calculator_print has {len(result['tools'])} tools")

# Test 5: Platform count increase
platforms = list_available_platforms()
assert platforms['platform_count'] >= 56, "Should have 56+ platforms (52 + 5 new)"
print(f"✅ Test 5 passed: Total platforms = {platforms['platform_count']}")

# Test 6: Search by category still works
result = search_tools("booklet")
tool_names = [t['name'] for t in result['tools']]
assert 'calculate_booklets' in tool_names, "Search should still find booklets"
print("✅ Test 6 passed: Search still works after reorganization")
```

**Success Criteria**: All 6 tests pass

- [ ] Run tests
- [ ] Fix any failures
- [ ] Reload registry: `python -m tools.registry_v3` (test initialization)
- [ ] Commit: `git commit -m "Phase 4: Reorganized calculator tools into 5 logical sub-platforms"`

---

## Post-Implementation

### Testing

- [ ] **Integration Test**: Run full test suite
  ```python
  python test_tool_discovery.py
  ```

- [ ] **Regression Test**: Verify existing functionality still works
  ```python
  # Test original functions
  list_available_platforms()  # Should return 56+ platforms
  list_platform_tools("gmail")  # Should return Gmail tools
  search_tools("email")  # Should find email tools
  get_tool_schema("gmail_send_email")  # Should return schema
  ```

- [ ] **Performance Test**: Measure overhead
  ```python
  import time
  
  # Search performance
  start = time.time()
  search_tools("calculator")
  print(f"Search time: {(time.time() - start) * 1000:.0f}ms")  # Should be <50ms
  
  # Recommendation performance
  start = time.time()
  recommend_tools_for_task("Generate quote for booklets")
  print(f"Recommendation time: {(time.time() - start) * 1000:.0f}ms")  # Should be <100ms
  ```

### Documentation

- [ ] Update `AI_AGENT_INSTRUCTIONS.md`
  - [ ] Add recommendation workflow examples
  - [ ] Update search examples with new features
  - [ ] Add platform metadata examples

- [ ] Update `MCP_CLIENT_SUCCESS.md`
  - [ ] Update tool discovery section
  - [ ] Add recommendation examples

- [ ] Update `QUICK_START_CLIENT.md`
  - [ ] Add "How to get tool recommendations" section
  - [ ] Update search examples

- [ ] Update `README.md`
  - [ ] Update tool count (if changed)
  - [ ] Update platform count (52 → 56)

### Git & Deployment

- [ ] Review all changes: `git diff feature/tool-discovery-improvements v10`
- [ ] Create PR: "Tool Discovery System Improvements - Search, Recommendations, Metadata, Organization"
- [ ] Add PR description with:
  - [ ] Summary of changes
  - [ ] Test results (all passing)
  - [ ] Performance impact (minimal)
  - [ ] Breaking changes (none - backward compatible)
- [ ] Merge to v10 branch
- [ ] Tag release: `git tag -a v10.1-tool-discovery -m "Enhanced tool discovery system"`
- [ ] Push: `git push origin v10 --tags`

---

## Success Validation

### Quantitative Metrics

Run these tests and record results:

```python
# Metric 1: Search accuracy
calculator_result = search_tools("calculator")
print(f"Calculator tools found: {calculator_result['match_count']}/27 ({calculator_result['match_count']/27*100:.0f}%)")
# Target: 27/27 (100%)

# Metric 2: Recommendation success
test_tasks = [
    "Generate quote for 500 booklets",
    "I need pricing for 1000 business cards",
    "Send email to john@example.com",
    "Create a new document",
    "Schedule a meeting tomorrow"
]
success_count = 0
for task in test_tasks:
    rec = recommend_tools_for_task(task)
    if rec.get('primary_tool'):
        success_count += 1
print(f"Recommendation success: {success_count}/{len(test_tasks)} ({success_count/len(test_tasks)*100:.0f}%)")
# Target: 4+/5 (80%+)

# Metric 3: Platform metadata
platforms = list_available_platforms()
metadata_complete = sum(1 for p in platforms['platforms'] if len(p.get('categories', [])) > 0)
print(f"Platforms with metadata: {metadata_complete}/{len(platforms['platforms'])} ({metadata_complete/len(platforms['platforms'])*100:.0f}%)")
# Target: 5+/56 (critical platforms have metadata)

# Metric 4: Calculator organization
calc_platforms = ['calculator_print', 'calculator_books', 'calculator_signs', 'calculator_stationery', 'calculator_specialty']
found_platforms = sum(1 for cp in calc_platforms if list_platform_tools(cp)['success'])
print(f"Calculator sub-platforms: {found_platforms}/{len(calc_platforms)} ({found_platforms/len(calc_platforms)*100:.0f}%)")
# Target: 5/5 (100%)
```

### Qualitative Assessment

- [ ] AI agents can find tools with fewer queries
- [ ] AI agents understand recommended workflows
- [ ] AI agents can filter by category/use case
- [ ] Reduced confusion about tool relationships

---

## Rollback Plan (if needed)

If critical issues are discovered:

1. **Phase 4 rollback**: Restore calculator_tools.json.backup
2. **Phase 3 rollback**: Revert list_available_platforms() changes
3. **Phase 2 rollback**: Revert recommend_tools_for_task() changes
4. **Phase 1 rollback**: Revert search_tools() changes
5. **Full rollback**: `git checkout v10 -- tools/`

Each phase is independent, so you can rollback selectively.

---

## Timeline Summary

| Phase | Duration | Day | Status |
|-------|----------|-----|--------|
| Phase 1: Search | 2 hours | Day 1 | ⬜ Not started |
| Phase 2: Recommendations | 3 hours | Day 1 | ⬜ Not started |
| Phase 3: Metadata | 2 hours | Day 2 | ⬜ Not started |
| Phase 4: Organization | 4 hours | Day 3 | ⬜ Not started |
| Testing & Docs | 2 hours | Day 3 | ⬜ Not started |
| **Total** | **13 hours** | **3 days** | ⬜ Not started |

---

**Start Date**: TBD  
**Target Completion**: TBD + 3 days  
**Owner**: TBD  
**Status**: ✅ Ready to begin
