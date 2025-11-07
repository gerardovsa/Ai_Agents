# System Prompt - Server Tools Documentation Update

**Date:** November 4, 2025  
**Status:** ✅ COMPLETE  
**File Updated:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

---

## 🎯 WHAT WAS ADDED

### New Section: "🌐 SERVER TOOLS: WEB SEARCH & WEB FETCH"

Added **comprehensive documentation** (300+ lines) about server-side web search and web fetch capabilities immediately after the 5 critical rules, making it highly visible to the AI.

---

## 📋 DOCUMENTATION STRUCTURE

### 1. **Introduction - "YOU HAVE REAL-TIME INTERNET ACCESS"**
- Clear statement that AI has TWO powerful server tools
- Emphasizes these are Anthropic server-side tools (not local)
- Always available and reliable

### 2. **web_search Documentation**

**What it does:**
- Real-time web search for current information
- Returns URLs, titles, content snippets, page age
- Localized to Brisbane, Australia
- Max 5 searches per conversation

**When to use:**
```
✅ Current events, news, trends
✅ Latest pricing or market data
✅ Technical standards/specifications
✅ Real-time information
✅ Recent updates
✅ Anything beyond knowledge cutoff
```

**When NOT to use:**
```
❌ General knowledge (Python basics)
❌ Foundational concepts (how HTTP works)
❌ Math calculations
```

**Examples provided:**
- Good usage: "What's the latest AI news?"
- Bad usage: "What is Python?" (use existing knowledge)

**Result format documented:**
```json
{
  "type": "web_search_tool_result",
  "content": [{
    "url": "...",
    "title": "...",
    "page_age": "2 days ago"
  }]
}
```

---

### 3. **web_fetch Documentation**

**What it does:**
- Fetches full content from specific URLs
- Supports PDFs, web pages, documents
- Returns complete document content
- Max 10 fetches per conversation
- Content limit: 100,000 tokens per fetch
- Citations enabled

**When to use:**
```
✅ Analyze specific URL
✅ Read webpage content
✅ Extract info from PDF link
✅ Summarize document at URL
✅ Compare multiple URLs
```

**When NOT to use:**
```
❌ No specific URL provided (use search first)
❌ Obviously broken/invalid URLs
❌ Homepage URLs with no useful content
```

**Examples provided:**
- Good usage: "Analyze https://example.com/article"
- Bad usage: "Find articles about AI" (use search first)

**Result format documented:**
```json
{
  "type": "web_fetch_tool_result",
  "content": {
    "url": "...",
    "content": {
      "type": "document",
      "source": {"type": "text", "data": "..."},
      "citations": {"enabled": true}
    }
  }
}
```

---

### 4. **Combining web_search AND web_fetch - POWERFUL WORKFLOWS**

**Pattern 1: Search → Fetch → Analyze**
```
User: "What are the best React practices in 2025?"

Step 1: web_search("React best practices 2025")
Step 2: web_fetch(top_result_url)
Step 3: Analyze and provide answer with citations

Result: Deep, current analysis!
```

**Pattern 2: Search → Email/Document**
```
User: "Find latest AI news and email my team"

Step 1: web_search("latest AI news 2025")
Step 2: Analyze results
Step 3: gmail_smart_compose_and_send(...)

Result: Current info + automated communication!
```

**Pattern 3: Fetch → Analyze → Save**
```
User: "Read this article and create summary"

Step 1: web_fetch(article_url)
Step 2: Analyze and extract key points
Step 3: google_docs_smart_create_from_markdown(...)

Result: Analyzed content saved to document!
```

---

### 5. **Server Tools Execution Pattern**

**Mandated format:**
```markdown
📄 **Actions Taken:**

1. web_search → Query: "[query]"
   - Status: ✅ Success
   - Result: Found 5 results about [topic]
   - Top result: [Title] ([URL])

2. web_fetch → URL: [url]
   - Status: ✅ Success
   - Result: Fetched [length] from [source]

---

**Analysis Based on Retrieved Information:**
[Analysis with citations]

**Sources:**
1. [Title] - [URL] (Retrieved via web_search)
2. [Title] - [URL] (Retrieved via web_fetch)
```

---

### 6. **Error Handling Documentation**

**If web_search fails:**
```
📄 **Actions Taken:**
1. web_search → Query: "[query]"
   - Status: ❌ Failed
   - Result: [Error message]

Would you like me to:
1. Try different search query?
2. Use existing knowledge?
3. Suggest alternatives?
```

**If web_fetch fails:**
```
📄 **Actions Taken:**
1. web_fetch → URL: [url]
   - Status: ❌ Failed
   - Result: [404/403/timeout/etc.]

Possible solutions:
1. URL might be incorrect
2. Site requires authentication
3. Content behind paywall
4. Try alternative URL?
```

---

### 7. **CRITICAL SERVER TOOLS RULES**

Added 10 mandatory rules:

✅ **ALWAYS** use web_search for current information beyond knowledge cutoff
✅ **ALWAYS** use web_fetch when user provides specific URL
✅ **ALWAYS** cite sources with URLs
✅ **ALWAYS** show "Retrieved at" timestamp
✅ **ALWAYS** combine server + client tools
✅ **PROACTIVELY** use web_search for current data
✅ **NEVER** say "I cannot access the internet"
✅ **NEVER** guess at current information
✅ **NEVER** refuse to read a URL
✅ **CONFIDENCE** - Server tools run on Anthropic's servers (always work)

---

## 🎨 DOCUMENTATION STYLE

### Key Features:
1. **Clear hierarchical structure** (##, ###, ####)
2. **Visual indicators** (✅, ❌, 🔥, ⚠️)
3. **Code blocks** with syntax highlighting
4. **Examples for every concept** (good vs bad usage)
5. **Result formats documented** (JSON examples)
6. **Workflow patterns** (how to combine tools)
7. **Error handling** (what to do when fails)
8. **Mandatory rules** (never say "can't access internet")

### Writing Style:
- **Bold** for emphasis
- **ALL CAPS** for critical points
- **Examples** for every "when to use" case
- **Anti-examples** for "when NOT to use"
- **Step-by-step workflows** for complex patterns
- **Result previews** showing what AI will receive

---

## 📊 CONTENT METRICS

- **Total lines added:** ~300 lines
- **Section count:** 7 major sections
- **Examples provided:** 15+ usage examples
- **Workflows documented:** 3 powerful patterns
- **Error scenarios:** 2 complete error handling guides
- **Critical rules:** 10 mandatory guidelines

---

## 🎯 IMPACT ON AI BEHAVIOR

### Before This Update:
- AI didn't know it had real-time internet access
- Would say "I cannot search the web"
- Would provide outdated information
- Wouldn't proactively use server tools
- No guidance on combining search + fetch

### After This Update:
- ✅ AI knows it has TWO server tools (search + fetch)
- ✅ Clear when to use each tool
- ✅ Proactive usage for current information
- ✅ Powerful workflows combining tools
- ✅ Proper citation and source attribution
- ✅ Error handling patterns
- ✅ Confidence to use tools (they always work!)

---

## 💡 KEY INSIGHTS FOR AI

### 1. **Server Tools Are DIFFERENT from Client Tools**
- Run on Anthropic's servers (not user's machine)
- ALWAYS available (no authentication needed)
- Return real-time internet data
- Can be combined with client tools

### 2. **Proactive Usage is Encouraged**
```
User: "What's the best way to do X in 2025?"

AI should think:
- "2025" implies need for CURRENT information
- My knowledge cutoff might be outdated
- I should PROACTIVELY use web_search
- Better to search than give outdated advice
```

### 3. **Powerful Workflow Combinations**
```
web_search → web_fetch → client_tool

Example:
search for "Python tutorials 2025"
  → fetch top result for detailed content
    → create Google Doc with tutorial summary
```

### 4. **Citations are MANDATORY**
- Always show which URLs you accessed
- Always show "Retrieved at" timestamp
- Always cite specific sections when quoting
- Build trust through transparency

---

## 📝 PLACEMENT IN DOCUMENT

**Location:** Right after "CRITICAL RULE #5" and before "STEP 1: UNDERSTAND THE REQUEST"

**Why this placement:**
- Immediately after critical rules (high visibility)
- Before execution steps (foundational knowledge)
- Part of core instruction set (not buried)
- Consistent with other critical sections

---

## ✅ VERIFICATION CHECKLIST

- [x] Documentation is comprehensive (300+ lines)
- [x] Clear "when to use" guidance for both tools
- [x] Examples for good vs bad usage
- [x] Result formats documented
- [x] Error handling patterns included
- [x] Workflow combinations explained
- [x] Critical rules emphasized
- [x] Visual formatting (✅, ❌, 🔥)
- [x] Code blocks with examples
- [x] Mandatory citation format
- [x] Proactive usage encouraged
- [x] "Never say can't access internet" rule

---

## 🚀 EXPECTED OUTCOMES

### AI Will Now:
1. ✅ Use web_search when users ask about current events
2. ✅ Use web_fetch when users provide URLs to analyze
3. ✅ Combine server tools with client tools
4. ✅ Proactively search for current information
5. ✅ Cite sources properly with URLs
6. ✅ Handle errors gracefully with alternatives
7. ✅ Never say "I cannot access the internet"
8. ✅ Provide current, accurate information

### Users Will Experience:
1. 📈 More current, accurate information
2. 🔗 Proper source citations with URLs
3. 🤖 Proactive AI that searches without being asked
4. 📊 Powerful workflows (search → analyze → document)
5. 🎯 Confidence in AI's internet access
6. ✅ Better error handling when searches fail
7. 🌐 Real-time data integration

---

## 📚 RELATED DOCUMENTATION

**Also Updated:**
- `AI_infrastructure/core/unified_ai_client.py` - Fallback system prompt includes server tools
- `WEB_SEARCH_FETCH_FILE_ATTACHMENTS_COMPLETE.md` - Complete implementation guide

**UI Changes:**
- `UI/business-ai-platform-v2.html` - Renders [WEBSEARCH] and [WEBFETCH] bubbles
- Visual feedback shows AI is searching/fetching in real-time

**Backend Changes:**
- `unified_ai_client.py` - Converts server tool events to SSE format
- Streams search results and fetch content to UI

---

## 🎉 CONCLUSION

**Status:** ✅ **DOCUMENTATION COMPLETE**

The AI now has **clear, comprehensive guidance** on:
- How to use web_search for real-time information
- How to use web_fetch for URL analysis
- When to use each tool proactively
- How to combine tools for powerful workflows
- How to handle errors gracefully
- How to cite sources properly

**The AI will no longer say "I cannot access the internet" - it knows it CAN and SHOULD use server tools!**

---

**Last Updated:** November 4, 2025  
**Version:** 2.1  
**Lines Added:** ~300 lines  
**Status:** Production Ready
