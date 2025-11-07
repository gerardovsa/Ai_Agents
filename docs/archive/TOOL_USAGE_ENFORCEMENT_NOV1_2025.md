# Tool Usage Enforcement - November 1, 2025

## ✅ COMPLETE - System Prompt Reinforced

## Problem
AI was sometimes responding with "I cannot access..." or "Here's what you should do..." instead of actually using the 584+ tools available to complete requests.

## Solution Applied

### **Added Two Strong Enforcement Sections**

---

## **Section 1: Top of System Prompt (Lines 6-59)**

Added **"🚨 CRITICAL RULE: ALWAYS USE TOOLS FOR ACTIONS"** section at the very beginning, before any other instructions.

### **Key Mandates:**

#### **MUST Use Tools For:**
- ✅ **Creating** - documents, emails, forms, spreadsheets, files, products, records
- ✅ **Editing** - updating, changing, deleting existing content
- ✅ **Looking up** - searching emails, checking calendars, querying databases, fetching data
- ✅ **Testing** - checking existence, validating data, running tests
- ✅ **Sending** - emails, messages, notifications, API calls
- ✅ **Calculating** - quotes, pricing, analytics, reports
- ✅ **Organizing** - moving files, sorting data, categorizing items

#### **NEVER Say These:**
- ❌ "I cannot access your Gmail" → **USE gmail tools**
- ❌ "I don't have permission" → **USE OAuth tools available**
- ❌ "You would need to manually..." → **USE tools to do it**
- ❌ "Here's what you should do..." → **USE tools and DO IT**
- ❌ "I can help you with that" → **USE tools, don't just help, DO IT**

#### **Correct Examples Provided:**
```
User: "Can you check my emails?"
❌ Wrong: "I cannot access your Gmail account..."
✅ Correct: *Uses gmail_list_messages() tool* "You have 5 unread emails..."

User: "Create a document about our meeting"
❌ Wrong: "Here's what you should include..."
✅ Correct: *Uses google_docs_smart_create_from_markdown()* "Document created: [link]"

User: "Is there a product called Widget Pro?"
❌ Wrong: "You would need to check your store..."
✅ Correct: *Uses woocommerce_search_products()* "Yes, found Widget Pro (ID: 123)"
```

#### **Tool Discovery Pattern:**
1. Use `list_available_platforms()` to see all platforms
2. Use `list_platform_tools(platform="name")` to see specific tools
3. Execute the appropriate tool
4. Never stop at "I don't know" - discover and use tools

#### **Execution Pattern:**
1. **Identify** what action is needed (create/edit/lookup/test/send)
2. **Find** the right tool (use discovery if needed)
3. **Execute** the tool with proper parameters
4. **Report** the results with IDs, URLs, or data returned
5. **Follow up** if additional tools needed

---

## **Section 2: End of System Prompt (Lines 850-897)**

Added **"🚨 MANDATORY TOOL USAGE - FINAL ENFORCEMENT"** section at the end, reinforcing the rules one more time.

### **Categorized by Action Type:**

#### **Creating Content:**
- Documents, spreadsheets, forms → **USE Google Workspace tools**
- Emails, messages → **USE Gmail/Slack/Twilio tools**
- Products, orders → **USE WooCommerce/Stripe tools**
- Files, folders → **USE Google Drive/Supabase tools**
- Events, meetings → **USE Google Calendar tools**

#### **Editing/Modifying:**
- Update documents → **USE google_docs_update_content()**
- Modify products → **USE woocommerce_update_product()**
- Change events → **USE google_calendar_update_event()**
- Edit drafts → **USE gmail_update_draft()**

#### **Looking Up/Searching:**
- Find emails → **USE gmail_search_messages() or gmail_list_messages()**
- Search products → **USE woocommerce_search_products()**
- Check calendar → **USE google_calendar_list_events()**
- Find files → **USE google_drive_search_files()**

#### **Testing/Verifying:**
- Check existence → **USE search/list tools**
- Validate data → **USE get/fetch tools**
- Test webhooks → **USE ngrok tools**
- Verify status → **USE status check tools**

### **Absolute Prohibitions:**
1. **Never** say "I cannot access..." → You CAN via OAuth tools
2. **Never** say "You'll need to manually..." → Use tools to automate
3. **Never** give instructions without executing → DO IT with tools
4. **Never** assume limitations → 584+ tools cover almost everything

### **Correct Response Pattern:**
```
User request → Identify action type → Select tool → Execute → Report results

NOT: "Here's how you can do this..."
BUT: *executes tool* "Done! Here's what I created/found/updated..."
```

---

## **File Modified**

**File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`

**Changes:**
- **Section 1 (Lines 6-59)**: Added critical rule at top of prompt (53 lines)
- **Section 2 (Lines 850-897)**: Added mandatory enforcement at end (47 lines)
- **Total:** 100 lines of strong enforcement added

---

## **Impact**

### **Before:**
```
User: "Check my Gmail for messages from John"
AI: "I'm sorry, I cannot directly access your Gmail account. You would need to 
     log into Gmail and search for messages from John yourself."
```

### **After:**
```
User: "Check my Gmail for messages from John"
AI: *Uses gmail_search_messages(query="from:john")* 
    "Found 3 messages from John:
    1. [Oct 30] Re: Project Update
    2. [Oct 28] Meeting Notes
    3. [Oct 25] Budget Approval"
```

---

## **System Prompt Flow**

The system prompt is now structured as:

1. **🚨 CRITICAL RULE** (Lines 6-59) - Mandatory tool usage enforcement
2. **STEP 1: Understand Request** - Analyze user intent
3. **STEP 2: Plan Approach** - Determine complexity
4. **STEP 3: Choose Right Tool** - SMART vs basic tools
5. **STEP 4: Execute with Tools** - Platform-specific guides
6. **STEP 5: Track Complex Work** - Synergy Dashboard usage
7. **STEP 6: Present Results** - Professional reporting
8. **🚨 FINAL ENFORCEMENT** (Lines 850-897) - Repeat mandatory rules

---

## **Key Message to AI**

**"You have 584+ tools. There is ALWAYS a tool to complete the request. Your job is to USE THEM, not explain what the user should do manually."**

This is now stated explicitly twice in the system prompt:
- Once at the beginning (before any other instructions)
- Once at the end (as final reminder before execution)

---

## **Testing Scenarios**

### **Test 1: Email Access**
```
User: "Do I have any emails from support@example.com?"
Expected: AI uses gmail_search_messages() and reports results
Not: "I cannot access your Gmail..."
```

### **Test 2: Document Creation**
```
User: "Create a meeting notes document"
Expected: AI uses google_docs_smart_create_from_markdown() and returns link
Not: "Here's a template you can use..."
```

### **Test 3: Product Lookup**
```
User: "Check if we have a product called 'Premium Widget'"
Expected: AI uses woocommerce_search_products() and reports findings
Not: "You would need to check your WooCommerce store..."
```

### **Test 4: Calendar Check**
```
User: "What meetings do I have tomorrow?"
Expected: AI uses google_calendar_list_events() and lists meetings
Not: "I don't have access to your calendar..."
```

### **Test 5: File Search**
```
User: "Find my project proposal document"
Expected: AI uses google_drive_search_files() and returns matches
Not: "You should search your Google Drive for..."
```

---

## **Success Criteria**

✅ AI **NEVER** says "I cannot access..." for OAuth-connected platforms  
✅ AI **ALWAYS** uses tools for create/edit/lookup/test/send actions  
✅ AI **NEVER** gives manual instructions when tools are available  
✅ AI **DISCOVERS** tools via meta-tools when unsure  
✅ AI **EXECUTES** and **REPORTS** results, not just explains  

---

## **Cost Impact**

**System Prompt Size:**
- **Before:** ~12,000 tokens (estimated)
- **After:** ~12,700 tokens (added ~700 tokens)
- **Per conversation turn:** +700 tokens × API calls

**Trade-off:** Small token cost increase (+5-6%) for significantly better tool usage compliance.

**Result:** AI will actually complete tasks instead of saying "I can't" → **Better user experience** outweighs minimal cost increase.

---

**Created:** November 1, 2025  
**Status:** ✅ Complete - System prompt reinforced  
**Impact:** AI now strongly enforced to use tools for ALL action requests  
**File Modified:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`
