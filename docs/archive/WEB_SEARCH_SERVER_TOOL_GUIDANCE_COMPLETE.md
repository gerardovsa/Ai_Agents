# Web Search/Fetch Server Tool Guidance - Implementation Complete
**Date:** November 5, 2025  
**Status:** Production Ready

---

## Problem Solved

Claude has `web_search` and `web_fetch` as **server tools** (enabled by default in `unified_ai_client.py`), but it doesn't realize it has them because:
- Server tools aren't in the 646-tool registry
- Claude searches for "web search", "tavily", "brave search", etc.
- Gets no results and thinks it needs to find external search tools

---

## Solution Implemented

Added intelligent detection in `search_tools()` meta-tool to intercept searches for web search/fetch capabilities and return guidance about server tools.

---

## Implementation Details

### File Modified
`tools/implementations/meta_tools.py`

### Changes Made

1. **Added query detection lists** (lines 326-333):
```python
web_search_queries = ['websearch', 'web_search', 'web search', 'search web', 'search internet', 
                      'internet search', 'tavily', 'brave', 'brave search', 'search engine',
                      'online search', 'web query']
web_fetch_queries = ['webfetch', 'web_fetch', 'web fetch', 'fetch url', 'fetch web', 
                    'read url', 'get url', 'scrape', 'scrape web', 'download url',
                    'read webpage', 'fetch page', 'get webpage']
```

2. **Added web_search guidance** (lines 335-381):
   - Explains it's a SERVER TOOL (no execute_tool needed)
   - Shows exact usage pattern with content blocks
   - Includes max limits (5 searches/conversation)
   - Lists when to use (current events, news, trends, etc.)
   - Emphasizes "YOU ALREADY HAVE IT!"

3. **Added web_fetch guidance** (lines 383-429):
   - Explains it's a SERVER TOOL (no execute_tool needed)
   - Shows exact usage pattern with content blocks
   - Includes max limits (10 fetches/conversation)
   - Lists when to use (analyze URLs, PDFs, etc.)
   - Emphasizes "YOU ALREADY HAVE IT!"

4. **Removed duplicate search_tools function** (lines 548-664):
   - There was a duplicate definition causing the old logic to override
   - Removed to ensure new logic is active

---

## How It Works

### Before (Problem):
```
Claude: "I need to search the web for latest AI news"
Claude calls: search_tools("web search")
Result: 0 tools found
Claude: "I don't have web search tools, let me ask user to add Tavily API"
```

### After (Solution):
```
Claude: "I need to search the web for latest AI news"
Claude calls: search_tools("web search")
Result: {
  "guidance": "SERVER TOOL AVAILABLE: web_search\n\n You have a web_search SERVER TOOL...",
  "tools": [{
    "name": "web_search",
    "type": "server_tool",
    "platform": "anthropic_server_tools"
  }]
}
Claude: "Oh! I can use web_search directly!"
Claude uses: {
  "type": "tool_use",
  "name": "web_search",
  "input": { "query": "latest AI news November 2025" }
}
```

---

## Test Results

All 5 tests passing:

### Test 1: search_tools('web search')
- Status: PASS
- Result: 1 tool found (web_search)
- Guidance: PROVIDED
- Platform: anthropic_server_tools

### Test 2: search_tools('tavily')
- Status: PASS
- Result: 1 tool found (web_search guidance)
- Guidance: PROVIDED
- Critical note: "Don't search for alternatives"

### Test 3: search_tools('web fetch')
- Status: PASS
- Result: 1 tool found (web_fetch)
- Guidance: PROVIDED
- Platform: anthropic_server_tools

### Test 4: search_tools('scrape')
- Status: PASS
- Result: 1 tool found (web_fetch guidance)
- Guidance: PROVIDED
- Critical note: "Don't search for alternatives"

### Test 5: search_tools('email')
- Status: PASS
- Result: 92 tools found (normal client-side tools)
- No server tool guidance (works normally)

---

## Queries That Trigger Guidance

### Web Search Triggers:
- "websearch", "web_search", "web search"
- "search web", "search internet", "internet search"
- "tavily", "brave", "brave search"
- "search engine", "online search", "web query"

### Web Fetch Triggers:
- "webfetch", "web_fetch", "web fetch"
- "fetch url", "fetch web", "read url"
- "get url", "scrape", "scrape web"
- "download url", "read webpage", "fetch page"

---

## Guidance Content

### web_search Guidance Includes:
- Explanation: It's a server tool (no client execution)
- Usage pattern: Content block with tool_use type
- Limits: Max 5 searches per conversation
- Capabilities: URLs, titles, snippets, page age
- Location: Brisbane, Queensland, Australia
- When to use: Current events, news, trends, recent data
- Emphasis: "NEVER say 'I need to find a web search tool' - YOU ALREADY HAVE IT!"

### web_fetch Guidance Includes:
- Explanation: It's a server tool (no client execution)
- Usage pattern: Content block with tool_use type
- Limits: Max 10 fetches per conversation
- Capabilities: Fetches PDFs, web pages, documents
- Max size: 100,000 tokens per fetch
- When to use: Analyze URLs, read documents, summarize content
- Emphasis: "NEVER say 'I need to find a web fetch tool' - YOU ALREADY HAVE IT!"

---

## Benefits

1. **No Duplicate Tools**: Doesn't create duplicate web_search/web_fetch in registry
2. **Smart Guidance**: Teaches Claude correct usage when it searches for these capabilities
3. **No Schema Conflicts**: Server tools remain separate from client tools
4. **Backward Compatible**: Normal searches still work (Test 5 proves this)
5. **Future Proof**: Easy to add more server tool guidance as needed

---

## Testing

### Test File
`test_web_search_guidance.py`

### Run Test
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_web_search_guidance.py
```

### Expected Output
All 5 tests should pass with guidance provided for web search/fetch queries and normal results for other queries.

---

## Related Files

### Modified
- `tools/implementations/meta_tools.py` - Added web search/fetch detection

### Server Tools Configuration
- `AI_infrastructure/core/unified_ai_client.py` - Enables server tools by default
- Lines 236-258 contain progressive tool loading that includes server tools

### System Prompt
- `AI_infrastructure/prompts/tool_usage_system_prompt.md` - Could be updated to mention server tools

---

## Next Steps (Optional Enhancements)

1. **Update System Prompt**: Add note about server tools in tool usage instructions
2. **Add More Server Tool Guidance**: If Anthropic adds more server tools, add detection here
3. **Analytics**: Track how often Claude searches for web tools (before vs after fix)
4. **Documentation**: Update main README with server tool explanation

---

## Status

**PRODUCTION READY**
- All tests passing (5/5)
- No breaking changes to existing functionality
- Backward compatible with normal searches
- Provides clear guidance when Claude looks for web capabilities

**Deploy Status**: Ready to deploy - no additional changes needed

---

**Last Updated:** November 5, 2025  
**Implemented By:** GitHub Copilot  
**Tested:** PASS (5/5 tests)
