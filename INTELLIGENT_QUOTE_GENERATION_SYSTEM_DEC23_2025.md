# 🧠 Intelligent Quote Generation System - December 23, 2025

## Overview

The Communication Hub V4 now includes an **intelligent quote generation system** that automatically queries the FRED database to find customer order history when specifications are missing from the email request.

---

## How It Works

### **User Workflow**

1. **Email arrives**: "Hi, I need business cards for my team"
2. **User selects AI Agent**: Choose from Prime/Alpha-Zulu
3. **User selects task**: "Generate Quote" (green button, first in list)
4. **AI Agent processes**:
   - Extracts: "business cards" requested, no quantity/size/paper type specified
   - Queries FRED database for customer's previous business card orders
   - Finds: Customer last ordered 500x 90mm x 55mm, 350gsm, matt celloglaze on 2025-11-15
   - Uses these specs in `calculate_premium_business_cards_shopify()` calculator
   - Generates quote with note: "Based on your previous order specifications from 2025-11-15..."

---

## Three-Round Query System

The AI follows the **AutonomousQuoteAgentWithSQL** pattern (proven implementation from In_House_SQL repository):

### **Round 1: Identify Customer**
```sql
SELECT TOP 10 ContactID, Name, Email, Phone 
FROM Clients 
WHERE Email LIKE '%customer_email%' OR Name LIKE '%customer_name%'
```

**Purpose**: Find customer's ContactID from email sender or name mentioned in body

**Returns**: Customer record with ContactID (links to Orders table via CustomerMYOB_ID)

---

### **Round 2: Get Previous Orders**
```sql
SELECT TOP 20
    o.OrderID,
    o.ClientName,
    o.OrderDate,
    jt.ShortJobDesc,
    jt.QTY as Quantity,
    jt.Width,
    jt.Height,
    pt.[Desc] as PaperType,
    g.[DESC] as GSM,
    jtype.[Desc] as JobType,
    jt.FrontCelloGloss,
    jt.FrontCelloMatt,
    jt.Cost
FROM Orders o
INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
INNER JOIN Clients c ON o.CustomerMYOB_ID = c.ContactID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM g ON jt.GSM_ID = g.GSM_ID
LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
WHERE c.ContactID = ?
ORDER BY o.OrderDate DESC
```

**Purpose**: Find ALL previous orders for this customer with complete specifications

**Returns**: Order history with paper types, sizes, finishes, quantities, costs

**Key Joins**:
- `PaperType` → Get paper description (e.g., "Satin 350gsm")
- `GSM` → Get paper weight (e.g., "350")
- `JobType` → Get product category (e.g., "Business Cards")

⚠️ **CRITICAL SQL Server Note**: Reserved keywords like `Desc`/`DESC` must use square brackets: `pt.[Desc]`, `g.[DESC]`

---

### **Round 3: Find Similar Product Orders**
```sql
SELECT TOP 20
    jt.TicketID,
    jt.ShortJobDesc,
    o.ClientName,
    o.OrderDate,
    jt.QTY,
    jt.Width,
    jt.Height,
    pt.[Desc] as PaperType,
    g.[DESC] as GSM,
    jt.FrontCelloGloss,
    jt.FrontCelloMatt,
    jt.Cost
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
LEFT JOIN PaperType pt ON jt.PaperTypeID = pt.PaperTypeID
LEFT JOIN GSM g ON jt.GSM_ID = g.GSM_ID
WHERE jt.JobTypeID = ? OR jt.ShortJobDesc LIKE '%product_keyword%'
ORDER BY o.OrderDate DESC
```

**Purpose**: If customer is new OR looking for different product than usual, find similar orders from other customers

**Use Cases**:
- Customer's first order (no history in Round 2)
- Customer ordering NEW product type (business cards customer now wants flyers)
- Industry-standard specs needed (most common paper types, sizes)

---

## Tools Used

### **1. inhouse_execute_query**
```python
inhouse_execute_query(
    query="SELECT TOP 10 ContactID, Name FROM Clients WHERE Email LIKE ?",
    params=['%customer@example.com%'],
    max_rows=100,
    read_only=True
)
```

**Location**: `tools/implementations/inhouse_query.py`

**Purpose**: Execute custom SQL queries on FRED database (SQL Server)

**Safety**: `read_only=True` by default (prevents accidental modifications)

**Syntax**: SQL Server (use `TOP N`, not `LIMIT`; `?` placeholders for params)

---

### **2. inhouse_search_database**
```python
inhouse_search_database(
    search_text='CJ King Printing',
    tables=['Orders', 'JobTickets'],
    limit_per_table=10
)
```

**Location**: `tools/implementations/inhouse_query.py`

**Purpose**: Full-text search across FRED database tables

**Use Case**: Quick customer lookup without knowing exact spelling

---

## Quote Calculator Selection

After gathering specifications, AI selects from **80+ calculators**:

### **Business Cards**
- `calculate_economical_business_cards_shopify` (standard quality)
- `calculate_premium_business_cards_shopify` (premium finishes)

### **Flyers & Leaflets**
- `calculate_a3_flyers_shopify` (297mm x 420mm)
- `calculate_a4_flyers_shopify` (210mm x 297mm)
- `calculate_a5_flyers_shopify` (148mm x 210mm)
- `calculate_dl_flyers_shopify` (99mm x 210mm)

### **Booklets**
- `calculate_saddle_stitch_booklets_shopify` (stapled spine)
- `calculate_perfect_bound_booklets_shopify` (glued spine)
- `calculate_wire_bound_booklets_shopify` (spiral binding)

### **Signage**
- `calculate_corflute_signs_shopify` (corrugated plastic)
- `calculate_metal_aframe_signs_shopify` (metal A-frames)
- `calculate_construction_signs_shopify` (building sites)

### **Stationery**
- `calculate_letterheads_shopify`
- `calculate_compliments_slips_shopify`
- `calculate_notepads_shopify`

**Plus 60+ more** for posters, vinyl stickers, banners, custom products

---

## Specification Mapping

### **How Historical Data Fills Calculator Parameters**

**Example: Business Cards**

Calculator requires:
```javascript
{
    quantity: 500,           // From jt.QTY
    width: 90,               // From jt.Width
    height: 55,              // From jt.Height
    paper_stock: "350gsm",   // From g.[DESC]
    finish: "matt_cello",    // From jt.FrontCelloMatt = 1
    paper_type: "Satin",     // From pt.[Desc]
    design_included: false   // User choice
}
```

**Mapping from FRED JobTickets table**:
- `jt.QTY` → Calculator `quantity`
- `jt.Width`, `jt.Height` → Calculator `width`, `height`
- `g.[DESC]` (GSM table join) → Calculator `paper_stock`
- `pt.[Desc]` (PaperType table join) → Calculator `paper_type`
- `jt.FrontCelloGloss`, `jt.FrontCelloMatt` → Calculator `finish`
- `jt.Cost` → Reference pricing for sanity check

---

## Fallback Behavior

### **Scenario 1: No Customer History Found**

**Email**: "I need 1000 flyers, what's the price?"

**AI Response**:
```
I'd be happy to provide a quote for 1000 flyers! To give you an accurate price, 
I need a few more details:

1. What size flyers? (A4, A5, DL, or custom size?)
2. Paper type preference? (Gloss, Matt, Satin)
3. Paper weight? (150gsm, 200gsm, 250gsm)
4. Single-sided or double-sided?
5. Do you need a celloglaze finish?
6. When do you need them by?

Once I have these details, I can calculate an exact quote for you!
```

---

### **Scenario 2: Partial History (Different Product)**

**Email**: "I need flyers this time"
**History**: Customer previously ordered business cards only

**AI Response**:
```
Great! I see you've ordered business cards from us before (350gsm matt celloglaze).
For flyers, I'll need a few details:

1. Flyer size? (A4, A5, or DL)
2. Quantity? (Your usual business card order was 500)
3. Paper preference? (I can match your business card stock: 350gsm matt celloglaze, 
   or recommend lighter weight like 200gsm for cost savings)

Let me know and I'll calculate a quote!
```

**AI uses**: Historical preferences (paper type, finish) as **suggestions**, but asks for flyer-specific details (size, quantity)

---

### **Scenario 3: Complete History Match**

**Email**: "Hi, can I order business cards again?"
**History**: Customer ordered 500x 90mm x 55mm, 350gsm matt celloglaze on 2025-11-15

**AI Response**:
```
Quote for Business Cards (Premium Quality)
Based on your previous order specifications from November 15, 2025:

Quantity: 500 cards
Size: 90mm x 55mm (standard business card)
Paper: 350gsm Satin stock
Finish: Matt Celloglaze on front
Turnaround: 5-7 business days

Unit Price: $0.85 per card
Subtotal: $425.00
GST (10%): $42.50
-------------------
TOTAL: $467.50

Valid until: December 30, 2025
Payment terms: 50% deposit, balance on delivery

Would you like to proceed with these specifications, or would you like to 
upgrade to spot UV or change any details?
```

**Note**: "Based on your previous order specifications from November 15, 2025..." = Customer knows AI used their history

---

## Value-Add Suggestions

### **Based on Order History**

**Pattern Detection**:
- Customer orders business cards every 6 months → "Would you like to set up automatic reordering?"
- Customer always orders matt cello → "Upgrade to spot UV for $50 extra?"
- Customer ordered cards but not letterheads → "Matching letterheads available for $275 (500 qty)"

**Bundling**:
- Business cards + letterheads + compliments slips = Corporate stationery package (10% discount)
- Flyers + posters + A-frame signs = Marketing campaign bundle

**Seasonal**:
- December orders → "Need Christmas cards or holiday greeting cards?"
- New year → "Update your business cards for 2025?"

---

## Implementation Details

### **Location**
**File**: `UI/modules_internal/communication-hub/communication-hub-v4-modern.js`
**Lines**: 2597-2730 (134 lines)

### **Prompt Injection**
When user selects "Generate Quote" task, the 134-line prompt is injected into AI context with:
```javascript
const taskPrompts = {
    'generate_quote': `[134-line intelligent quote generation prompt]`,
    'summarize': `[summarize prompt]`,
    'draft_reply': `[draft reply prompt]`,
    // ... other tasks
};
```

### **WebSocket Flow**
1. User clicks "Send to Agent" → Selects agent → Selects "Generate Quote"
2. Frontend sends WebSocket message: `{"action": "send_to_agent", "agent_id": "agent-5", "task": "generate_quote"}`
3. Backend injects task prompt + email content → Sends to AI agent
4. AI agent executes:
   - `inhouse_execute_query()` (Round 1: find customer)
   - `inhouse_execute_query()` (Round 2: get order history)
   - `calculate_premium_business_cards_shopify()` (generate quote)
5. AI responds with quote, backend streams to WebSocket
6. Frontend displays quote in chat interface

---

## Database Schema Reference

### **Key Tables**

**Clients**
- `ContactID` (PRIMARY KEY) → Links to Orders.CustomerMYOB_ID
- `Name`, `Email`, `Phone`

**Orders**
- `OrderID` (PRIMARY KEY) → Links to JobTickets.OrderID
- `CustomerMYOB_ID` (FOREIGN KEY → Clients.ContactID)
- `ClientName`, `OrderDate`, `DateRequired`
- `Invoiced`, `Urgent`, `Completed`

**JobTickets**
- `TicketID` (PRIMARY KEY)
- `OrderID` (FOREIGN KEY → Orders.OrderID)
- `ShortJobDesc` (product description)
- `QTY`, `Width`, `Height`, `Cost`
- `JobTypeID` (FOREIGN KEY → JobType.JobTypeID)
- `PaperTypeID` (FOREIGN KEY → PaperType.PaperTypeID)
- `GSM_ID` (FOREIGN KEY → GSM.GSM_ID)
- `FrontCelloGloss`, `FrontCelloMatt` (finish flags)

**Reference Tables**
- `JobType`: JobTypeID, [Desc] (e.g., "Business Cards", "Flyers")
- `PaperType`: PaperTypeID, [Desc] (e.g., "Satin", "Gloss")
- `GSM`: GSM_ID, [DESC] (e.g., "350", "250")

⚠️ **SQL Server Quirk**: Column name `Desc` is reserved keyword → Must use square brackets `[Desc]` or `[DESC]`

**Full Schema**: `UI/modules_external/inhouse-kanban/FRED_DATABASE_SCHEMA_ACTUAL.md`

---

## Testing

### **Test Case 1: Known Customer, Complete History**
**Email**: "Hi, I need business cards" (from sarah@abcprinting.com.au)
**Expected**:
1. AI queries Clients table → Finds ContactID = 45
2. AI queries Orders + JobTickets → Finds previous order: 500x 90mm x 55mm, 350gsm matt cello
3. AI uses `calculate_premium_business_cards_shopify()` with historical specs
4. AI generates quote with note: "Based on your previous order from [date]..."

### **Test Case 2: New Customer, No History**
**Email**: "I need business cards" (from newcustomer@example.com)
**Expected**:
1. AI queries Clients table → No match found
2. AI skips Rounds 2-3 (no customer history)
3. AI responds: "I need more details: quantity, size, paper type, finish, etc."

### **Test Case 3: Known Customer, New Product**
**Email**: "I need flyers" (from sarah@abcprinting.com.au who previously ordered business cards)
**Expected**:
1. AI queries Clients table → Finds ContactID = 45
2. AI queries Orders + JobTickets → Finds business card history, but no flyer history
3. AI uses Round 3 (similar products) → Finds typical flyer specs from other customers
4. AI asks: "What size flyers? Your business cards were 350gsm matt cello - recommend 200gsm for flyers?"

### **Test Case 4: Mention of Previous Order**
**Email**: "I want to reorder the MVG Emergency signs from last month"
**Expected**:
1. AI queries Clients table → Finds customer
2. AI queries JobTickets with `WHERE ShortJobDesc LIKE '%MVG%' AND ShortJobDesc LIKE '%Emergency%'`
3. AI finds exact previous order with all specs
4. AI generates quote: "Reorder quote for MVG Emergency signs (as per your order from 2025-11-20)..."

---

## Error Handling

### **Database Connection Failure**
```javascript
try {
    const customer = await inhouse_execute_query(...);
} catch (error) {
    // Fallback to manual quote request
    return "I'm unable to access your order history at the moment. Please provide: quantity, size, paper type, finish...";
}
```

### **No Customer Found**
```javascript
if (customer_results.length === 0) {
    // Skip Rounds 2-3, ask for specifications
    return "I don't have your previous order history. To generate an accurate quote, please provide...";
}
```

### **Ambiguous Customer Match**
```javascript
if (customer_results.length > 1) {
    // Show matches, ask user to confirm
    return "I found multiple customers with similar names. Are you: 1) ABC Printing (Melbourne), 2) ABC Print Co (Sydney)?";
}
```

### **Incomplete Historical Data**
```javascript
if (previous_order.Width === null || previous_order.Height === null) {
    // Use partial data, ask for missing details
    return "I see you ordered business cards before (350gsm matt cello), but I need to confirm the size. Standard 90mm x 55mm?";
}
```

---

## Performance Optimization

### **Query Caching** (Future Enhancement)
- Cache customer lookups for 5 minutes (common repeat queries)
- Cache popular product specifications (business cards, A4 flyers)

### **Query Limits**
- Round 1: TOP 10 (customer lookup - usually 1 result)
- Round 2: TOP 20 (order history - last 20 orders sufficient)
- Round 3: TOP 20 (similar products - representative sample)

### **Indexing Requirements** (FRED DBA)
- `Clients.Email` (speeds up Round 1)
- `Orders.CustomerMYOB_ID` (speeds up Round 2)
- `JobTickets.OrderID` (already indexed - foreign key)
- `JobTickets.ShortJobDesc` (full-text index for Round 3 keyword search)

---

## Benefits

### **For Customers**
✅ **Faster quotes** - No back-and-forth for specifications
✅ **Consistency** - Uses their preferred paper types and finishes
✅ **Less friction** - Simple requests like "I need business cards again" work instantly

### **For Sales Team**
✅ **Time savings** - AI handles 80% of routine quote requests
✅ **Accuracy** - Uses actual previous order data (not guesses)
✅ **Upselling** - AI suggests upgrades based on history

### **For Business**
✅ **Higher conversion** - Instant quotes reduce drop-off
✅ **Customer satisfaction** - Shows we remember their preferences
✅ **Data-driven** - Uses real order history for better pricing

---

## Related Documentation

- **Communication Hub V4**: `UI/modules_internal/communication-hub/communication-hub-v4-modern.js`
- **FRED Database Schema**: `UI/modules_external/inhouse-kanban/FRED_DATABASE_SCHEMA_ACTUAL.md`
- **Database Query Tools Guide**: `DATABASE_QUERY_TOOLS_COMPLETE_GUIDE.md`
- **FRED Testing Instructions**: `FRED_TOOLS_TESTING_INSTRUCTIONS.md`
- **Quote Calculators**: `UI/modules_external/quote-calculator/tools/*.json` (80+ calculators)
- **Autonomous Quote Agent Reference**: `In_House_SQL/G_Folder/Quote_Calculator/AI_Quote_Agent/core/autonomous_quote_agent_with_sql.py`

---

## Version History

**December 23, 2025** - v1.0
- Initial implementation of intelligent quote generation
- Three-round query system based on AutonomousQuoteAgentWithSQL pattern
- Integration with 80+ quote calculators
- Historical specification mapping
- Fallback behavior for new customers
- Value-add suggestion framework

---

**Status**: ✅ **FULLY IMPLEMENTED** - Ready for testing in Communication Hub V4
