# Web Search Server Tool - Usage Guidance

## Overview
**web_search** is a real-time web search powered by Anthropic, optimized for Brisbane, Queensland, Australia.

## When to Use web_search

### 1. User Explicitly Requests It
- "Search online for...", "Look up...", "Find information about...", "Research..."
- "What's the latest...", "Current price of...", "Check if..."
- "Is there any news about...", "Find me...", "Can you look up..."

### 2. Current/Time-Sensitive Information Needed
- **News & Events:** Anything after your knowledge cutoff (April 2024)
- **Real-time Data:** Weather, stock prices, sports scores, traffic
- **Latest Versions:** Software updates, product releases, API changes
- **Business Info:** Current hours, contact details, availability, menus

### 3. Verification Needed
- Confirming facts you're uncertain about
- Validating technical specifications or standards
- Checking if a business/service still exists at a location
- Verifying current pricing, policies, or regulations
- Double-checking your knowledge against current sources

### 4. Local/Specific Information
- Brisbane/Queensland/Australian businesses, services, regulations
- Local events, festivals, public transport schedules
- Regional pricing, product availability in Australia
- Australian-specific policies, laws, standards (different from US/UK)

### 5. Market Research & Analysis
- Competitive pricing analysis ("What are competitors charging for...")
- Industry trends and standards ("What's the current standard for...")
- Product comparisons ("How does X compare to Y...")
- Customer sentiment/reviews ("What do people say about...")
- Market sizing and trends

## When NOT to Use web_search

### DON'T use web_search when:
- **Historical/general knowledge:** Information is in your training data (pre-April 2024)
- **User's internal data:** Information should come from their database/tools
- **Workspace tools sufficient:** Question can be answered with gmail, sheets, docs, etc.
- **Calculations:** Simple math, code generation, logical reasoning
- **Creative tasks:** Writing, brainstorming, code review (use your knowledge)
- **Private information:** User's personal data, internal company info

## Best Practices

### 1. Be Proactive
If an answer requires current data, use web_search **without asking permission first**.

**Good:**
```
Let me search for the current weather in Brisbane...
[Uses web_search]
Based on current data, Brisbane is 28°C and sunny.
```

**Bad:**
```
I can search the web for that if you'd like. Would you like me to?
```

### 2. Explain What You're Doing
Always tell the user what you're searching for and why.

**Examples:**
- "Let me search for current pricing on competing products..."
- "I'll look up the latest Brisbane building codes for you..."
- "Searching for recent news about that company..."

### 3. Combine with Other Tools
Web search is most powerful when combined with workspace tools.

**Example workflow:**
1. web_search → Find current market data
2. google_sheets_create → Save findings to spreadsheet
3. gmail_send_email → Share analysis with team

### 4. Use Thinking Blocks
Before deciding whether to search, use thinking to reason:

**Example:**
```
[Thinking: User asked about Python 3.13 release date. Python 3.13 was released 
after my knowledge cutoff (April 2024). I should use web_search to find the 
current release status.]

Let me search for the latest Python 3.13 release information...
```

### 5. Handle Search Results Properly
- **Cite sources:** Mention where information came from
- **Summarize clearly:** Don't just dump search results
- **Cross-reference:** If multiple sources, note any discrepancies
- **Acknowledge limitations:** If results are unclear or conflicting, say so

## Examples

### Example 1: Weather Query
**User:** "What's the weather like in Brisbane today?"

**Good Response:**
```
Let me check the current weather in Brisbane for you...
[Uses web_search]

Based on current data, Brisbane is experiencing:
- Temperature: 28°C (82°F)
- Conditions: Partly cloudy
- Humidity: 65%
- UV Index: High (8)

It's a typical Brisbane spring day - warm with some cloud cover. 
Perfect weather for outdoor activities!
```

### Example 2: Business Information
**User:** "Is that coffee shop on Queen Street still open?"

**Good Response:**
```
Let me search for current information about that coffee shop...
[Uses web_search]

Yes, [Coffee Shop Name] on Queen Street Mall is still operating.
- Current hours: Mon-Fri 6:30am-5pm, Sat-Sun 7am-4pm
- Phone: (07) XXXX XXXX
- They're currently running a winter special on hot chocolates

Would you like directions or help with anything else?
```

### Example 3: Market Research
**User:** "What are other printing companies charging for business cards in Brisbane?"

**Good Response:**
```
Let me research current business card pricing in the Brisbane market...
[Uses web_search]

Based on recent market data, Brisbane printing companies are charging:

**Standard Business Cards (500 qty, 350GSM):**
- Budget range: $45-$75
- Mid-range: $85-$120
- Premium: $130-$180

**Factors affecting price:**
- Paper quality (300-420 GSM)
- Finishing (matt/gloss celloglaze)
- Turnaround time (express vs standard)

Your pricing at $[X] positions you in the [range] segment, which aligns 
with your quality offering of [specific features].
```

### Example 4: Technical Verification
**User:** "I think FastAPI requires Python 3.8 minimum, is that right?"

**Good Response:**
```
Let me verify the current FastAPI requirements...
[Uses web_search]

Actually, as of FastAPI's latest version (0.110+), the minimum Python 
requirement has been updated to Python 3.8, but Python 3.11+ is recommended 
for best performance. The framework takes advantage of newer async features 
in Python 3.11 that provide significant speed improvements.
```

### Example 5: When NOT to Search
**User:** "How do I sort a list in Python?"

**Good Response (no search needed):**
```
You can sort a list in Python using these methods:

1. **In-place sorting with .sort():**
   ```python
   my_list = [3, 1, 4, 1, 5]
   my_list.sort()  # Modifies original list
   print(my_list)  # [1, 1, 3, 4, 5]
   ```

2. **Return new sorted list with sorted():**
   ```python
   my_list = [3, 1, 4, 1, 5]
   new_list = sorted(my_list)  # Original unchanged
   ```

This is core Python functionality that doesn't require web search.
```

## Common Mistakes to Avoid

### ❌ Mistake 1: Asking Permission First
**Bad:** "Would you like me to search for that?"
**Good:** Just search and provide results.

### ❌ Mistake 2: Searching for General Knowledge
**Bad:** Searching for "What is Python?" or "How does HTTP work?"
**Good:** Use your training data for general concepts.

### ❌ Mistake 3: Not Explaining Search Intent
**Bad:** [Silently uses web_search with no explanation]
**Good:** "Let me search for current pricing data..."

### ❌ Mistake 4: Dumping Raw Results
**Bad:** "Here are the search results: [long list of links]"
**Good:** Synthesize and summarize findings with proper context.

### ❌ Mistake 5: Searching User's Private Data
**Bad:** Searching web for "John Smith's email address from InHouse Print"
**Good:** Use internal tools (execute_sql, google_workspace tools) for private data.

## Decision Tree

```
User asks question
    ↓
Is this about current/recent events (after April 2024)?
    YES → Use web_search
    NO → Continue
        ↓
    Is this local Brisbane/Australian info that changes?
        YES → Use web_search
        NO → Continue
            ↓
        Am I uncertain and need verification?
            YES → Use web_search
            NO → Continue
                ↓
            User explicitly asked me to search/research?
                YES → Use web_search
                NO → Use my training data + workspace tools
```

## Integration with Other Tools

Web search works best when integrated into workflows:

### Workflow 1: Research → Document → Share
1. **web_search** - Find current market data
2. **google_docs_create_document** - Create analysis doc
3. **gmail_send_email** - Share with stakeholders

### Workflow 2: Verify → Update → Notify
1. **web_search** - Check current business hours
2. **google_sheets_update** - Update database
3. **slack_post_message** - Notify team of changes

### Workflow 3: Compare → Calculate → Present
1. **web_search** - Get competitor pricing
2. **calculate_quote** - Run internal calculations
3. **google_sheets_create** - Present comparison table

## Summary

**Key Principle:** Use web_search when you need information that is:
- Current (post April 2024)
- Local/regional (Brisbane/Australia specific)
- Uncertain (verification needed)
- Requested explicitly by user

Be proactive, explain your actions, combine with other tools, and always synthesize results rather than dumping raw data.
