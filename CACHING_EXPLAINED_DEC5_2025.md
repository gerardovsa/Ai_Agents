# How Smart Caching Works - Explained Simply

**Date:** December 5, 2025  
**For:** Understanding when to cache vs re-query FRED data

---

## The Problem You Raised

> "How does the AI know it's cached already? How does the AI access it? Data can change - maybe it needs to be done each time?"

Great question! Let me explain how this works.

---

## What is Caching?

**Caching = Temporarily remembering a result so you don't have to ask the database again**

Think of it like this:
- ❌ **Without cache:** Every time someone asks "What's the revenue?", you drive to the office, open the filing cabinet, count everything, drive back
- ✅ **With cache:** First person asks, you do the work. Second person asks 5 minutes later, you say "I just checked - it's $45,678"

---

## When Should We Cache? (The Smart Part)

Not all data ages the same way. We categorize queries:

### 1. Real-Time Data (Cache: 2 minutes)

**Examples:**
- "How many orders are pending RIGHT NOW?"
- "What's today's sales so far?"
- "Current stock levels"

**Why short cache?**
- Changes every few minutes
- Users expect current data
- But querying every 10 seconds is wasteful

**Rule:** If someone asks twice within 2 minutes, use cache. After 2 minutes, re-query.

```
10:00 AM - User asks "Sales today?" → Query database: $5,234
10:01 AM - User asks again "Sales today?" → Use cache: $5,234 (1 min old)
10:03 AM - User asks again "Sales today?" → Re-query: $5,456 (cache expired)
```

---

### 2. Recent Data (Cache: 15 minutes)

**Examples:**
- "Show me this week's orders"
- "Customer activity this month"
- "Recent production jobs"

**Why 15 minutes?**
- Changes throughout the day
- But not EVERY minute
- Balance between fresh and efficient

---

### 3. Historical Data (Cache: 1 hour)

**Examples:**
- "Revenue trend for last 6 months"
- "Customer order history from last year"
- "Monthly sales comparison"

**Why 1 hour?**
- Historical data doesn't change!
- November's revenue is November's revenue forever
- Only current month might change

**Smart detail:** If user asks for "last 6 months" in December:
- Months Jun-Nov → Never change (historical)
- Month Dec → Still changing (current)
- We cache the whole result for 1 hour because Dec won't change THAT much

---

### 4. Static Data (Cache: 24 hours)

**Examples:**
- "List all customers"
- "What products do we offer?"
- "Chart of accounts"

**Why 24 hours?**
- Rarely changes
- Safe to cache for a full day
- Reduces database load significantly

---

## How Does the AI Know to Use Cache?

The AI doesn't "know" - the system automatically handles it based on **keywords and query type**.

### Automatic Cache Detection

```python
# The system looks at the query name
if 'today' in query_name or 'current' in query_name:
    cache_ttl = 2 minutes
elif 'this_week' in query_name or 'recent' in query_name:
    cache_ttl = 15 minutes
elif 'monthly' in query_name or 'history' in query_name:
    cache_ttl = 1 hour
else:
    cache_ttl = 30 minutes  # Safe default
```

### User Can Override

**User says:** "Show me the LATEST sales numbers"

Keywords detected: "LATEST", "RIGHT NOW", "CURRENT"

**System response:** Skip cache, always query fresh

**User says:** "What was that report you showed me before?"

Keywords detected: "before", "earlier", "showed me"

**System response:** Use cache if available (even if old)

---

## How AI Knows What's Cached

### Behind the Scenes (Cache Key)

Every query gets a unique "fingerprint":

```
Query: monthly_revenue_trend
Parameters: {months: 6}
User: 14

Cache Key: "fred_query:monthly_revenue_trend:a3f2d1:14"
```

When executing:
```python
1. Generate cache key
2. Check: "Do I have this key in memory?"
3. If YES: Check age
   - If age < TTL: Return cached result
   - If age > TTL: Delete old cache, run fresh query
4. If NO: Run query, store in cache with TTL
```

---

## Cache Information Returned to AI

The AI gets told whether result is cached:

```json
{
    "data": [...],
    "cache_info": {
        "cache_hit": true,          ← Was this cached?
        "cache_age_seconds": 245,   ← How old is it?
        "cached_at": "2025-12-05T10:00:00Z"
    }
}
```

**AI can then tell user:**
- ✅ "This is live data (just queried)"
- ⏱️ "This is cached data from 4 minutes ago"
- 🔄 "Would you like me to refresh this?"

---

## Why Cache at All? (The Benefits)

### 1. Speed

**Without cache:**
```
User: "Show revenue"
→ Query SQL Server (500ms)
→ Format data (200ms)
→ Create Google Sheet (2000ms)
Total: 2.7 seconds
```

**With cache:**
```
User: "Show revenue again"
→ Retrieve from memory (5ms)
→ Return stored Google Sheet link
Total: 0.005 seconds (540x faster!)
```

### 2. Database Load

**Scenario:** 10 users all looking at monthly revenue dashboard

**Without cache:**
- 10 users × same query = 10 database hits
- SQL Server does same calculation 10 times
- Waste of resources

**With cache:**
- First user: Query database
- Users 2-10: Use cached result
- 90% reduction in database load

### 3. Cost Savings

If using cloud databases (like we will eventually):
- Databases charge per query/compute time
- Cached queries = Free (after first one)
- Can save hundreds of dollars per month

---

## When Cache Becomes Stale (Your Concern)

You're right - **data can change**. That's why we have different TTLs.

### Example Scenario

**Monday 10:00 AM:** User asks "What's November's revenue?"
- Query runs: $45,678.90
- Cached for 1 hour

**Monday 10:30 AM:** User asks same question
- Cache still valid (30 minutes old)
- Returns: $45,678.90
- **Is this accurate?** YES - November is historical, doesn't change

**Monday 11:05 AM:** User asks again
- Cache expired (65 minutes old)
- Re-query: $45,678.90
- **Still the same?** YES - as expected for historical data

**But what if they ask "What's DECEMBER's revenue?"**
- This is CURRENT month (still accumulating)
- Different cache key: `december_revenue`
- Shorter TTL: 15 minutes
- Re-queries more frequently

---

## Force Refresh (Always Available)

Users (via AI) can ALWAYS override cache:

**User:** "I know you showed me this before, but I need the LATEST numbers"

**AI detects keyword:** "LATEST"

**AI adds parameter:** `_force_refresh=True`

**System response:** 
- Ignore cache completely
- Run fresh query
- Update cache with new result
- Tell user: "✓ This is fresh data from 30 seconds ago"

---

## Cache Storage (Where Is It?)

### Option 1: In-Memory (RAM)

**Pros:**
- Extremely fast (microseconds)
- Simple to implement
- No database queries

**Cons:**
- Lost if server restarts
- Not shared across multiple servers

**Best for:** Small deployments, development

### Option 2: Redis (Distributed Cache)

**Pros:**
- Persistent (survives restarts)
- Shared across multiple servers
- Still very fast (milliseconds)
- Can handle millions of cached items

**Cons:**
- Requires Redis server
- Slightly more complex

**Best for:** Production, multi-server deployments

**We'll start with Option 1, upgrade to Option 2 later**

---

## Visual Example: Timeline

```
Timeline: Monday, Dec 5, 2025

10:00 AM - User A asks: "Revenue for last 6 months"
           ↓
           Execute SQL query (500ms)
           Store in cache (TTL: 1 hour)
           Result: $234,567.89
           ↓
           Cache: {revenue_6mo: $234,567.89, expires: 11:00 AM}

10:15 AM - User B asks: "Revenue for last 6 months"
           ↓
           Check cache: Found! (15 minutes old)
           Return cached: $234,567.89
           (No SQL query needed!)

10:45 AM - User C asks: "Revenue for last 6 months"
           ↓
           Check cache: Found! (45 minutes old)
           Return cached: $234,567.89
           (Still valid, 15 minutes until expiry)

11:05 AM - User D asks: "Revenue for last 6 months"
           ↓
           Check cache: Expired! (65 minutes old)
           Execute SQL query (500ms)
           Update cache (TTL: 1 hour)
           Result: $234,567.89
           ↓
           Cache: {revenue_6mo: $234,567.89, expires: 12:05 PM}
```

**Result:** 4 requests, only 2 SQL queries (50% reduction)

---

## What About Storage vs Caching?

These are **different things**:

### Caching (Temporary Memory)

**Purpose:** Speed up repeated requests  
**Duration:** Minutes to hours  
**Storage:** RAM or Redis  
**Lost when:** TTL expires or server restarts  

### Document Storage (Permanent Record)

**Purpose:** Keep history, allow sharing  
**Duration:** 30 days (or forever)  
**Storage:** Google Sheets, Excel, Supabase  
**Lost when:** Manual deletion or expiry  

### They Work Together!

```
User asks: "Show me revenue for last 6 months"
    ↓
1. Check cache (for speed)
   - Miss → Execute query
   - Hit → Skip to step 3
    ↓
2. Execute SQL query
   - Store in cache (for next request)
   - Store in Google Sheets (for user to keep)
    ↓
3. Return to AI:
   - data: [JSON results]
   - markdown_table: "..."
   - storage: {google_sheets_url}
   - cache_info: {cache_hit: false}
    ↓
AI shows user:
   "Here's your revenue report:
   
   [Table]
   
   📊 Full details saved to Google Sheets:
   https://docs.google.com/spreadsheets/d/abc123
   
   ✓ Live data (just queried)"
```

**Next time same user asks (within 1 hour):**
```
Check cache → HIT!
Return same Google Sheets link (still valid)
Show user: "⏱️ Cached result from 15 minutes ago
           (Same Google Sheets link as before)"
```

---

## Configuration: User Control

Users can control caching behavior:

### Via User Preferences Table

```sql
user_storage_preferences
    user_id: 14
    allow_cached_results: true
    max_cache_age_minutes: 30
```

**If user sets:** `allow_cached_results: false`
→ System ALWAYS queries fresh (no cache)

**If user sets:** `max_cache_age_minutes: 5`
→ Cache expires after 5 minutes (overrides default TTLs)

### Via AI Conversation

**User:** "Always give me fresh data, don't cache"
**AI:** Updates user preference to `allow_cached_results: false`

**User:** "You can cache reports for up to 10 minutes"
**AI:** Updates `max_cache_age_minutes: 10`

---

## Summary: Should We Do This?

### YES, because:

✅ **Faster responses** (5ms vs 500ms)  
✅ **Reduced database load** (50-70% fewer queries)  
✅ **Better user experience** (instant results for repeated questions)  
✅ **Cost savings** (fewer database queries)  
✅ **User control** (can disable or force refresh)  
✅ **Smart TTLs** (historical data cached longer than real-time)  
✅ **Always correct** (expires before data becomes stale)  

### Your concern: "Data can change"

**Answer:** We handle this with:
1. ✅ **Smart TTLs** - Real-time data cached only 2 minutes
2. ✅ **Force refresh** - User can always override
3. ✅ **Cache info** - AI tells user age of data
4. ✅ **Expiry logic** - Automatic re-query when stale
5. ✅ **User control** - Can disable caching entirely

---

## Recommendation

**Implement caching with these defaults:**

- Real-time queries: 2 minutes
- Recent queries: 15 minutes  
- Historical queries: 1 hour
- Static queries: 24 hours
- User can override with `_force_refresh=True`
- AI tells user if data is cached

**This gives you:**
- 50-70% reduction in database queries
- Instant responses for repeated questions
- Always accurate data (smart expiry)
- User control when they need fresh data

---

**Questions?**

Ready to implement this? It's about 2-3 hours of work for basic caching, and it'll make a huge difference in performance.
