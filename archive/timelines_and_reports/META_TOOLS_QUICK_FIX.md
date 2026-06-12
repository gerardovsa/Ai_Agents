# META TOOLS - Quick Fix Reference Card

**Status:** ✅ **ALL META TOOLS ARE WORKING**

---

## 🔧 How to Use Meta Tools (for Claude AI / Copilot)

### ❌ WRONG (Don't do this):
```python
Tool: search_tools
{}
# Error: Tool not found
```

### ✅ CORRECT (Do this instead):
```python
Tool: execute_tool
{
  "tool_name": "search_tools",
  "query": "keyword"
}
```

---

## 📖 All 4 Meta Tools

### 1. List All Platforms
```python
Tool: execute_tool
{
  "tool_name": "list_available_platforms"
}
```
Returns: 74 platforms with tool counts

### 2. List Platform's Tools
```python
Tool: execute_tool
{
  "tool_name": "list_platform_tools",
  "platform": "microsoft_outlook"
}
```
Returns: All tools for that platform (names + descriptions)

### 3. Search Tools by Keyword
```python
Tool: execute_tool
{
  "tool_name": "search_tools",
  "query": "outlook read email"
}
```
Returns: Matching tools across all platforms

### 4. Get Tool Schema
```python
Tool: execute_tool
{
  "tool_name": "get_tool_schema",
  "tool_name_param": "microsoft_outlook_read_message"
}
```
Returns: Full parameter schema for that tool

---

## 🎯 Key Points

1. **Meta tools ARE registered** (verified: 4/4 working)
2. **Call through `execute_tool`** (not directly)
3. **Total tools available:** 1,076 across 74 platforms
4. **Implementation file:** `tools/implementations/meta_tools.py`

---

**Last Verified:** January 21, 2026  
**Test File:** `test_meta_simple.py` (run to verify)
