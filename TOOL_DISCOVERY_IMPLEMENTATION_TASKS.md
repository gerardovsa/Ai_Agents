# Tool Discovery System - Implementation Tasks for AI Agent

**Date:** December 10, 2025  
**Status:** Ready for Implementation  
**Estimated Time:** 7 hours total (3 independent tasks)  
**Dependencies:** None - all tasks are standalone

---

## Overview

This document contains **3 independent implementation tasks** to improve the tool discovery system. Each task can be completed by a separate AI agent without dependencies on the others.

**Current File to Modify:** `tools/implementations/meta_tools.py`

---

## 📋 **TASK 1: Fix search_tools() Algorithm**

**Time Estimate:** 2 hours  
**Priority:** CRITICAL  
**Current Issue:** Only finds 41% of relevant tools

### Problem Description

```python
# Current behavior (line 727):
search_tools("calculator")
# Returns: 11 tools (missing 16 calculator tools)

# Why: Searches for substring "calculator" but tool names have "calculate"
# "calculator" ≠ "calculate" → no match
```

### Implementation Steps

1. **Add Synonym Mapping**

Create synonym dictionary before the search function (around line 700):

```python
# Add this BEFORE search_tools() function
SEARCH_SYNONYMS = {
    "calculator": ["calculate", "calculator", "pricing", "quote", "cost"],
    "calculate": ["calculator", "calculate", "pricing", "quote", "cost"],
    "quote": ["quote", "pricing", "cost", "calculate", "calculator"],
    "booklet": ["booklet", "book", "saddle_stitch", "stapled", "bound"],
    "book": ["book", "booklet", "bound", "perfect_bound", "wire_bound", "spiral_bound"],
    "card": ["card", "business_card", "visiting_card"],
    "flyer": ["flyer", "leaflet", "brochure", "handbill"],
    "sign": ["sign", "signage", "corflute", "banner", "display"],
    "print": ["print", "printing", "printed"],
    "email": ["email", "mail", "message", "send_email"],
    "database": ["database", "db", "sql", "query", "data"],
}

def expand_search_keywords(keyword: str) -> List[str]:
    """
    Expand search keyword with synonyms
    
    Args:
        keyword: Original search term
    
    Returns:
        List of keywords including synonyms
    """
    keyword_lower = keyword.lower()
    
    # Check if keyword has synonyms
    if keyword_lower in SEARCH_SYNONYMS:
        return SEARCH_SYNONYMS[keyword_lower]
    
    # Also check if keyword is IN any synonym list (reverse lookup)
    for main_key, synonyms in SEARCH_SYNONYMS.items():
        if keyword_lower in synonyms:
            return synonyms
    
    # No synonyms found, return original
    return [keyword_lower]
```

2. **Update search_tools() Function**

Find the `search_tools()` function (around line 710) and update the matching logic:

```python
def search_tools(
    query: str,
    platform: Optional[str] = None,
    max_results: int = 50,
    **kwargs
) -> List[Dict[str, Any]]:
    """Search for tools by keyword - IMPROVED VERSION"""
    
    matched_tools = []
    keywords = [k.strip().lower() for k in query.split() if k.strip()]
    
    # Expand keywords with synonyms
    expanded_keywords = []
    for keyword in keywords:
        expanded_keywords.extend(expand_search_keywords(keyword))
    
    # Remove duplicates while preserving order
    expanded_keywords = list(dict.fromkeys(expanded_keywords))
    
    for tool in available_tools:
        # Skip if platform filter specified
        if platform and tool.get("platform") != platform:
            continue
        
        tool_name = tool.get("name", "").lower()
        description = tool.get("description", "").lower()
        tool_platform = tool.get("platform", "").lower()
        
        # Calculate match score
        score = 0
        matched = False
        
        for keyword in expanded_keywords:
            # Priority 1: Tool name exact match (highest score)
            if keyword == tool_name:
                score += 100
                matched = True
            
            # Priority 2: Tool name contains keyword
            elif keyword in tool_name:
                score += 50
                matched = True
            
            # Priority 3: Platform name match
            elif keyword in tool_platform:
                score += 30
                matched = True
            
            # Priority 4: Description contains keyword
            elif keyword in description:
                score += 10
                matched = True
        
        if matched:
            matched_tools.append({
                "tool": tool,
                "score": score
            })
    
    # Sort by score (highest first) and limit results
    matched_tools.sort(key=lambda x: x["score"], reverse=True)
    
    return [item["tool"] for item in matched_tools[:max_results]]
```

### Testing

Run these tests to validate the fix:

```python
# Test 1: Should now find 27/27 calculator tools
result = search_tools("calculator")
print(f"Found {len(result)} calculator tools (expected: 27)")

# Test 2: Should find same tools with synonym
result = search_tools("calculate")
print(f"Found {len(result)} calculate tools (expected: 27)")

# Test 3: Should find booklet tools
result = search_tools("booklet")
print(f"Found {len(result)} booklet tools (expected: 3+)")

# Test 4: Should rank exact matches higher
result = search_tools("quote")
print(f"First result: {result[0]['name']}")  # Should be a quote tool
```

### Success Criteria

- ✅ `search_tools("calculator")` finds 27/27 tools (currently 11/27)
- ✅ Synonym expansion works (e.g., "calculate" finds same tools)
- ✅ Exact name matches ranked first
- ✅ No performance degradation (<500ms for any search)

---

## 📋 **TASK 2: Implement Intelligent recommend_tools_for_task()**

**Time Estimate:** 3 hours  
**Priority:** CRITICAL  
**Current Issue:** Just calls search_tools() - no intelligence

### Problem Description

```python
# Current implementation (line 775):
def recommend_tools_for_task(task_description: str, **kwargs):
    return search_tools(task_description, **kwargs)

# User asks: "Generate a quote for 50 business cards"
# Returns: Generic search results (not helpful)
# Should return: Workflow with specific tools and parameters
```

### Implementation Steps

1. **Add Intent Detection Patterns**

Create intent patterns before the function (around line 765):

```python
# Add this BEFORE recommend_tools_for_task() function
INTENT_PATTERNS = {
    "calculate_quote": {
        "keywords": ["calculate", "quote", "price", "cost", "how much"],
        "products": {
            "business_cards": ["business card", "visiting card", "card"],
            "booklets": ["booklet", "book", "saddle stitch", "stapled"],
            "flyers": ["flyer", "leaflet", "brochure"],
            "signs": ["sign", "signage", "corflute", "banner"],
            "letterheads": ["letterhead", "stationery"],
            "perfect_bound": ["perfect bound", "glued spine"],
        },
        "recommended_tools": {
            "business_cards": "calculate_business_cards",
            "booklets": "calculate_saddle_stitch_books",
            "flyers": "calculate_flyers",
            "signs": "calculate_corflute_signs",
            "letterheads": "calculate_letterheads",
        }
    },
    "send_communication": {
        "keywords": ["send", "email", "message", "notify"],
        "recommended_tools": ["send_email", "send_sms", "create_notification"]
    },
    "database_query": {
        "keywords": ["query", "select", "get data", "database", "sql"],
        "recommended_tools": ["db_execute_query", "db_get_available_queries"]
    },
}

def detect_intent(task_description: str) -> Dict[str, Any]:
    """
    Detect user intent from task description
    
    Returns:
        {
            "intent": "calculate_quote",
            "product": "business_cards",
            "confidence": 0.95,
            "entities": {"quantity": 50}
        }
    """
    task_lower = task_description.lower()
    
    # Try to match each intent
    for intent_name, intent_data in INTENT_PATTERNS.items():
        # Check if any intent keywords match
        intent_keywords = intent_data.get("keywords", [])
        if any(keyword in task_lower for keyword in intent_keywords):
            
            result = {
                "intent": intent_name,
                "confidence": 0.8,
                "entities": {}
            }
            
            # For quote intent, detect product type
            if intent_name == "calculate_quote":
                products = intent_data.get("products", {})
                for product_type, product_keywords in products.items():
                    if any(kw in task_lower for kw in product_keywords):
                        result["product"] = product_type
                        result["confidence"] = 0.95
                        break
                
                # Extract quantity if present
                import re
                qty_match = re.search(r'(\d+)\s*(units?|pieces?|items?)?', task_lower)
                if qty_match:
                    result["entities"]["quantity"] = int(qty_match.group(1))
            
            return result
    
    return {"intent": "unknown", "confidence": 0.0, "entities": {}}
```

2. **Rewrite recommend_tools_for_task()**

Replace the current function (around line 775):

```python
def recommend_tools_for_task(
    task_description: str,
    include_workflow: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Intelligently recommend tools for a task - IMPROVED VERSION
    
    Args:
        task_description: Natural language task description
        include_workflow: If True, include step-by-step workflow
    
    Returns:
        {
            "intent": "calculate_quote",
            "recommended_tools": [...],
            "workflow": [...],
            "confidence": 0.95
        }
    """
    
    # Detect intent
    intent_result = detect_intent(task_description)
    
    if intent_result["confidence"] < 0.5:
        # Low confidence - fall back to search
        search_results = search_tools(task_description, **kwargs)
        return {
            "intent": "unknown",
            "recommended_tools": search_results[:5],
            "workflow": [],
            "confidence": 0.0,
            "message": "Low confidence - showing search results"
        }
    
    # High confidence - provide intelligent recommendations
    intent = intent_result["intent"]
    product = intent_result.get("product")
    entities = intent_result.get("entities", {})
    
    # Get intent data
    intent_data = INTENT_PATTERNS.get(intent, {})
    
    # Get recommended tools
    if product:
        # Product-specific recommendation
        recommended_tool_names = [intent_data.get("recommended_tools", {}).get(product)]
    else:
        # Generic recommendations for intent
        recommended_tool_names = intent_data.get("recommended_tools", [])
    
    # Get tool details
    recommended_tools = []
    for tool_name in recommended_tool_names:
        if tool_name:
            tool = next((t for t in available_tools if t["name"] == tool_name), None)
            if tool:
                recommended_tools.append(tool)
    
    # Build workflow
    workflow = []
    if include_workflow and intent == "calculate_quote":
        workflow = [
            {
                "step": 1,
                "action": "Get tool schema",
                "tool": "get_tool_schema",
                "parameters": {"tool_name": recommended_tools[0]["name"]},
                "description": "Learn what parameters are required"
            },
            {
                "step": 2,
                "action": "Check stock availability (optional)",
                "tool": "get_stock_list",
                "parameters": {},
                "description": "Get available paper stocks if needed"
            },
            {
                "step": 3,
                "action": "Calculate quote",
                "tool": recommended_tools[0]["name"],
                "parameters": {
                    "quantity": entities.get("quantity", 100),
                    "# Add other parameters from schema": "..."
                },
                "description": f"Generate quote for {product or 'product'}"
            }
        ]
    
    return {
        "intent": intent,
        "product": product,
        "recommended_tools": recommended_tools,
        "workflow": workflow,
        "confidence": intent_result["confidence"],
        "entities": entities,
        "message": f"Detected intent: {intent}" + (f" for {product}" if product else "")
    }
```

### Testing

```python
# Test 1: Quote intent
result = recommend_tools_for_task("Calculate a quote for 50 business cards")
print(f"Intent: {result['intent']}")  # Should be "calculate_quote"
print(f"Product: {result['product']}")  # Should be "business_cards"
print(f"Tool: {result['recommended_tools'][0]['name']}")  # Should be "calculate_business_cards"

# Test 2: Workflow generation
result = recommend_tools_for_task("How much for 100 booklets?")
print(f"Workflow steps: {len(result['workflow'])}")  # Should be 3

# Test 3: Entity extraction
result = recommend_tools_for_task("Price for 250 flyers")
print(f"Quantity extracted: {result['entities']['quantity']}")  # Should be 250
```

### Success Criteria

- ✅ Detects "calculate_quote" intent with 95%+ confidence
- ✅ Identifies product type (business_cards, booklets, etc.)
- ✅ Extracts quantities from text
- ✅ Provides 3-step workflow for quote tasks
- ✅ Falls back to search for unknown intents

---

## 📋 **TASK 3: Add Platform Metadata**

**Time Estimate:** 2 hours  
**Priority:** HIGH  
**Current Issue:** Platforms only have name + tool count

### Problem Description

```python
# Current platform data (line 650):
{
    "name": "quote_calculator",
    "tools": 27
}

# Should have:
{
    "name": "quote_calculator",
    "tools": 27,
    "description": "Print product quote calculators",
    "category": "commerce",
    "tags": ["printing", "quotes", "pricing"],
    "use_cases": ["Generate customer quotes", "Price comparison"],
    "related_platforms": ["inhouse_database"]
}
```

### Implementation Steps

1. **Create Platform Metadata Dictionary**

Add this before `list_available_platforms()` function (around line 640):

```python
# Add this BEFORE list_available_platforms() function
PLATFORM_METADATA = {
    "quote_calculator": {
        "description": "Print product quote calculators for business cards, flyers, books, signs, and more",
        "category": "commerce",
        "tags": ["printing", "quotes", "pricing", "calculators", "commerce"],
        "use_cases": [
            "Generate customer quotes for print products",
            "Calculate pricing for various quantities",
            "Compare pricing across different stock types",
            "Estimate production costs"
        ],
        "related_platforms": ["inhouse_database"],
        "icon": "calculator"
    },
    "inhouse_database": {
        "description": "Direct database access for quotes, inventory, and customer data",
        "category": "data",
        "tags": ["database", "sql", "queries", "data"],
        "use_cases": [
            "Execute complex SQL queries",
            "Access real-time pricing data",
            "Query customer information",
            "Generate custom reports"
        ],
        "related_platforms": ["quote_calculator"],
        "icon": "database"
    },
    "communication": {
        "description": "Email, SMS, and notification tools",
        "category": "communication",
        "tags": ["email", "sms", "messaging", "notifications"],
        "use_cases": [
            "Send transactional emails",
            "Send SMS notifications",
            "Create system notifications",
            "Manage communication templates"
        ],
        "related_platforms": [],
        "icon": "envelope"
    },
    "file_management": {
        "description": "File upload, download, and management tools",
        "category": "storage",
        "tags": ["files", "storage", "documents", "media"],
        "use_cases": [
            "Upload files to cloud storage",
            "Download files from URLs",
            "Manage document libraries",
            "Process file attachments"
        ],
        "related_platforms": ["vector_database"],
        "icon": "folder"
    },
    "vector_database": {
        "description": "Vector database for semantic search and AI embeddings",
        "category": "ai",
        "tags": ["vectors", "embeddings", "semantic_search", "ai"],
        "use_cases": [
            "Semantic document search",
            "Store AI embeddings",
            "Similarity matching",
            "Knowledge base queries"
        ],
        "related_platforms": ["file_management"],
        "icon": "brain"
    },
}

def get_platform_metadata(platform_name: str) -> Dict[str, Any]:
    """
    Get metadata for a platform
    
    Args:
        platform_name: Platform identifier
    
    Returns:
        Metadata dictionary with description, tags, use cases, etc.
    """
    return PLATFORM_METADATA.get(platform_name, {
        "description": "",
        "category": "other",
        "tags": [],
        "use_cases": [],
        "related_platforms": [],
        "icon": "tool"
    })
```

2. **Update list_available_platforms()**

Find the function (around line 645) and enhance the return data:

```python
def list_available_platforms(
    include_metadata: bool = True,
    category: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List all available platforms - IMPROVED VERSION
    
    Args:
        include_metadata: Include descriptions, tags, use cases
        category: Filter by category (commerce, data, communication, etc.)
    """
    platforms = {}
    
    # Group tools by platform
    for tool in available_tools:
        platform_name = tool.get("platform", "unknown")
        if platform_name not in platforms:
            platforms[platform_name] = {
                "name": platform_name,
                "tools": 0,
                "tool_names": []
            }
        platforms[platform_name]["tools"] += 1
        platforms[platform_name]["tool_names"].append(tool.get("name"))
    
    # Add metadata if requested
    result = []
    for platform_name, platform_data in platforms.items():
        
        # Get metadata
        if include_metadata:
            metadata = get_platform_metadata(platform_name)
            platform_data.update(metadata)
        
        # Filter by category if specified
        if category:
            platform_category = platform_data.get("category", "other")
            if platform_category != category:
                continue
        
        result.append(platform_data)
    
    # Sort by tool count (descending)
    result.sort(key=lambda x: x["tools"], reverse=True)
    
    return result
```

### Testing

```python
# Test 1: Basic listing (backward compatible)
platforms = list_available_platforms(include_metadata=False)
print(f"Found {len(platforms)} platforms")

# Test 2: With metadata
platforms = list_available_platforms(include_metadata=True)
platform = next(p for p in platforms if p["name"] == "quote_calculator")
print(f"Description: {platform['description']}")
print(f"Use cases: {platform['use_cases']}")

# Test 3: Filter by category
commerce_platforms = list_available_platforms(category="commerce")
print(f"Commerce platforms: {[p['name'] for p in commerce_platforms]}")
```

### Success Criteria

- ✅ Metadata added for top 5 platforms (quote_calculator, inhouse_database, communication, file_management, vector_database)
- ✅ `list_available_platforms()` returns enriched data
- ✅ Backward compatible (include_metadata=False works)
- ✅ Category filtering functional

---

## 📄 **Implementation Checklist**

### Before Starting

- [ ] Read full task description
- [ ] Locate `tools/implementations/meta_tools.py`
- [ ] Back up current file
- [ ] Review current code structure

### Task 1: Search Algorithm

- [ ] Add `SEARCH_SYNONYMS` dictionary (line 700)
- [ ] Add `expand_search_keywords()` function
- [ ] Update `search_tools()` matching logic
- [ ] Add scoring system
- [ ] Run tests
- [ ] Validate 100% discovery rate

### Task 2: Recommendations

- [ ] Add `INTENT_PATTERNS` dictionary (line 765)
- [ ] Add `detect_intent()` function
- [ ] Rewrite `recommend_tools_for_task()` function
- [ ] Add workflow generation
- [ ] Run tests
- [ ] Validate intent detection

### Task 3: Platform Metadata

- [ ] Add `PLATFORM_METADATA` dictionary (line 640)
- [ ] Add `get_platform_metadata()` function
- [ ] Update `list_available_platforms()` function
- [ ] Add category filtering
- [ ] Run tests
- [ ] Validate metadata returned

### After Completion

- [ ] Run full test suite
- [ ] Update `AI_AGENT_INSTRUCTIONS.md` (document new features)
- [ ] Commit changes with message: "Improve tool discovery: search algorithm, recommendations, platform metadata"
- [ ] Create documentation examples

---

## 🚀 **Deployment Notes**

### No Breaking Changes

All enhancements are **backward compatible**:
- `search_tools()` - Same signature, better results
- `recommend_tools_for_task()` - Same signature, richer response
- `list_available_platforms()` - New optional parameter

### Performance

- Synonym expansion: <10ms overhead
- Intent detection: <50ms overhead
- Platform metadata: <5ms overhead
- **Total impact: <100ms** (negligible for user experience)

### Rollback Plan

If issues arise, simply revert changes to `meta_tools.py`. No database changes or external dependencies.

---

## 📚 **Reference Materials**

### Files to Review

1. `tools/implementations/meta_tools.py` - Main file to modify
2. `CALCULATOR_TOOL_DISCOVERY_IMPROVEMENT_PLAN.md` - Full technical spec
3. `TOOL_DISCOVERY_EXECUTIVE_SUMMARY.md` - Business context

### Test Calculator Tools

Use these to validate search improvements:
- `calculate_booklets`
- `calculate_business_cards`
- `calculate_flyers`
- `calculate_saddle_stitch_books`
- `db_calculate_quote`

### Current Discovery Success Rate

- `search_tools("calculator")`: 11/27 tools (41%)
- `search_tools("booklet")`: 3/3 tools (100%)
- `recommend_tools_for_task(...)`: 0% functional

### Target Success Rate

- `search_tools("calculator")`: 27/27 tools (100%)
- `search_tools("booklet")`: 3+/3+ tools (100% with synonyms)
- `recommend_tools_for_task(...)`: 85%+ task match

---

## ✅ **Success Validation**

### Run These Commands After Implementation

```python
# Test Suite 1: Search Algorithm
print("=== SEARCH ALGORITHM TESTS ===")
result = search_tools("calculator")
print(f"1. Calculator search: {len(result)}/27 tools (target: 27)")

result = search_tools("calculate")
print(f"2. Synonym expansion: {len(result)} tools (target: 27)")

result = search_tools("booklet")
print(f"3. Booklet search: {len(result)} tools (target: 3+)")

# Test Suite 2: Recommendations
print("\n=== RECOMMENDATION TESTS ===")
result = recommend_tools_for_task("Calculate quote for 50 business cards")
print(f"1. Intent: {result.get('intent')} (target: calculate_quote)")
print(f"2. Product: {result.get('product')} (target: business_cards)")
print(f"3. Confidence: {result.get('confidence')} (target: >0.9)")
print(f"4. Workflow steps: {len(result.get('workflow', []))} (target: 3)")

# Test Suite 3: Platform Metadata
print("\n=== PLATFORM METADATA TESTS ===")
platforms = list_available_platforms(include_metadata=True)
calc_platform = next((p for p in platforms if p["name"] == "quote_calculator"), None)
if calc_platform:
    print(f"1. Description: {calc_platform.get('description', 'MISSING')[:50]}...")
    print(f"2. Tags: {len(calc_platform.get('tags', []))} tags (target: 5)")
    print(f"3. Use cases: {len(calc_platform.get('use_cases', []))} cases (target: 4)")
```

### Expected Output

```
=== SEARCH ALGORITHM TESTS ===
1. Calculator search: 27/27 tools (target: 27) ✅
2. Synonym expansion: 27 tools (target: 27) ✅
3. Booklet search: 3 tools (target: 3+) ✅

=== RECOMMENDATION TESTS ===
1. Intent: calculate_quote (target: calculate_quote) ✅
2. Product: business_cards (target: business_cards) ✅
3. Confidence: 0.95 (target: >0.9) ✅
4. Workflow steps: 3 (target: 3) ✅

=== PLATFORM METADATA TESTS ===
1. Description: Print product quote calculators for business card... ✅
2. Tags: 5 tags (target: 5) ✅
3. Use cases: 4 cases (target: 4) ✅
```

---

## 🎯 **For the AI Agent Implementing This**

### Key Points

1. **All code snippets are copy-paste ready** - Just find the line numbers and insert
2. **Tasks are independent** - Do them in any order
3. **Tests included** - Validate each task before moving to next
4. **No external dependencies** - Everything is in meta_tools.py
5. **Backward compatible** - Won't break existing code

### What Success Looks Like

- AI agents find tools 100% of the time (up from 41%)
- AI agents get intelligent workflow guidance (up from 0%)
- AI agents understand platform relationships better
- User experience improves significantly

### Questions to Ask if Stuck

1. "What line number is the function at?" (use grep/search)
2. "What's the current implementation?" (read existing code)
3. "How do I test this?" (run the test commands provided)
4. "Did I break anything?" (run full test suite)

---

**Ready to implement? Start with Task 1 (Search Algorithm) - it has the highest impact!**

**Good luck! 🚀**
