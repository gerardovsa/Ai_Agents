# Calculator & Quote Generation Transparency Protocol
**Purpose: Prevent quote errors failures by transparently verbalizing all parameters and results - allowing AI and user to track quote generation process**

---

## THE PROBLEM THIS SOLVES

**Scenario:** AI calls calculator with `double_sided=false` but calculator returns `double_sided_cost=$972`

**Without Protocol:**
- Round 1: AI calls tool, gets wrong result, reports wrong price
- Round 2: AI cannot see Round 1 tool result anymore (not in conversation history)
- Round 3: User has to manually catch the error

**With Protocol:**
- Round 1: AI states "double_sided=false" in text BEFORE calling tool
- Round 1: AI states "double_sided_cost=$972" in text AFTER calling tool
- Round 1: **AI SEES THE CONTRADICTION** and self-corrects
- Result: Error caught automatically before user sees it

---

## MANDATORY PROTOCOL FOR ALL CALCULATOR/QUOTE OPERATIONS

### **STAGE 1: PRE-CALL TRANSPARENCY** (Before executing calculator)

**YOU MUST verbalize ALL parameters in your text response BEFORE calling the calculator tool.**

#### Template:

```
I'm calculating a [PRODUCT TYPE] quote with these specifications:

**Parameters from User/Email:**
- [Parameter 1]: [Value] (source: [email/database/user])
- [Parameter 2]: [Value] (source: [email/database/user])
- [Parameter N]: [Value]

**Parameters from Research:**
- [Parameter X]: [Value] (source: database lookup - Order #12345)
- [Parameter Y]: [Value] (source: client history)

**Default Parameters:**
- [Parameter Z]: [Default Value] (using standard default)

**Missing Parameters - Need Clarification:**
- [Parameter]: Options are [A, B, C] - which do you prefer?

Proceeding to calculate quote...
```

#### Rules:
1. State EVERY parameter you're passing to calculator
2. Cite SOURCE for each parameter (email, database, user, default)
3. List MISSING parameters and ask user BEFORE calling calculator
4. Use plain English: "double-sided=false" → "Single-sided print only"
5. This text becomes PERMANENT RECORD in conversation history

---

### **STAGE 2: TOOL EXECUTION** (Silent - No Text)

Execute the calculator tool immediately after Stage 1.

---

### **STAGE 3: POST-CALL TRANSPARENCY** (After calculator returns)

**YOU MUST verbalize the COMPLETE BREAKDOWN in your text response.**

#### Template:

```
**Calculator Results:**

**Breakdown:**
- [Line Item 1]: $[Amount] ([Calculation details])
- [Line Item 2]: $[Amount] ([Calculation details])
- [Line Item N]: $[Amount]

**Subtotal:** $[Amount]
**Discounts:** -$[Amount] ([Reason])
**TOTAL (ex GST):** $[Amount]
**TOTAL (inc GST):** $[Amount]

**Per Unit Cost:** $[Amount] per [unit]
**Turnaround:** [X] business days
```

#### Rules:
1. Show EVERY line item from breakdown (base cost, options, discounts)
2. Include calculation details (e.g., "162 sqm × $10.54/sqm = $1,707.48")
3. Show both ex GST and inc GST prices
4. State per-unit cost
5. This becomes PERMANENT RECORD for future reference

---

### **STAGE 4: COGNITIVE VALIDATION** (Critical!)

**YOU MUST cross-check the breakdown against your pre-call parameters.**

#### Validation Checklist:

**For EACH line item in breakdown, ask:**

```
Parameter Check:
└─ Did I specify [parameter]=false?
   └─ YES → [parameter]_cost should be $0
      └─ Breakdown shows [parameter]_cost=$[X]
         └─ ❌ MISMATCH DETECTED!

Example:
└─ Did I specify double_sided=false?
   └─ YES → double_sided_cost should be $0
      └─ Breakdown shows double_sided_cost=$972
         └─ ❌ VALIDATION FAILED
```

#### Template:

```
**Validation Check:**

✅ Base cost: $1,707.48 aligns with 600x900mm size (0.54 sqm × 300 units)
❌ **DISCREPANCY:** Double-sided cost shows $972 but I specified single-sided print
✅ Eyelet cost: $0 aligns with no eyelets requested
✅ Artwork cost: $0 aligns with 1 artwork (5 free)

**VALIDATION RESULT: FAILED**
Reason: Calculator added double-sided charge when parameter was false
```

#### Rules:
1. ✅ Check EVERY line item against your pre-call parameters
2. ✅ Flag ANY discrepancies immediately
3. ✅ Use ✅ for aligned items, ❌ for mismatches
4. ✅ If validation fails, STOP and explain the issue
5. ✅ **DO NOT report wrong price to user**

---

### **STAGE 5: CORRECTIVE ACTION** (If validation fails)

**If you detect a mismatch, YOU MUST correct before reporting to user.**

#### Template:

```
⚠️ **CALCULATOR ERROR DETECTED**

**What I Found:**
- I specified: [parameter]=false (single-sided)
- Calculator charged: [parameter]_cost=$[Amount]
- **This is incorrect** - should be $0

**Manual Correction:**
Original calculator result:
- Subtotal: $2,679.48
- Minus incorrect charge: -$972.00
- Correct subtotal: $1,707.48
- 5% discount: -$85.37
- **CORRECTED TOTAL: $1,622.11 ex GST ($1,784.32 inc GST)**

**Reporting corrected price to user...**
```

#### Rules:
1. ✅ Clearly state what was wrong
2. ✅ Show manual correction calculation
3. ✅ Provide CORRECTED price to user
4. ✅ Flag the calculator bug for system improvement
5. ✅ NEVER report uncorrected price

---

### **STAGE 6: USER CLARIFICATION** (Before calculating if parameters missing)

**If you're missing parameters, ASK BEFORE calculating.**

#### Template:

```
I found these specifications from [source]:
- Quantity: 300 units
- Size: 600x900mm
- Thickness: 3mm

I need clarification on:
- **Print sides:** Single-sided or double-sided?
  - Single-sided: Standard pricing
  - Double-sided: +$6/sqm (adds $972 to quote)
  
- **Eyelets:** Do you need mounting holes?
  - No eyelets: Standard pricing
  - 4 corners: +$8 total
  - Custom placement: +$2 per eyelet

Please select:
A. Single-sided, no eyelets (most economical)
B. Double-sided, 4 corner eyelets (+$980)
C. Custom configuration (please specify)
```

#### Rules:
1. ✅ List what you KNOW vs what you NEED
2. ✅ Explain cost impact of each option
3. ✅ Provide clear choices with pricing
4. ✅ WAIT for user response before calculating
5. ✅ Never assume or use defaults for critical parameters

---

### **STAGE 7: RE-CALCULATION** (If parameters change)

**If user changes parameters, re-run calculator with new values.**

#### Template:

```
Updated parameters based on your selection:
- [Changed parameter]: [New value] (previously: [Old value])
- [Impact]: [Cost change explanation]

Recalculating quote with updated specifications...

[Return to STAGE 1 with new parameters]
```

---

### **STAGE 8: FINAL REPORTING** (Show your work)

**Present the final quote with full transparency.**

#### Template:

```
**Final Quote Summary:**

**Product:** [Product type]
**Specifications:**
- [Spec 1]: [Value]
- [Spec 2]: [Value]
- [Spec N]: [Value]

**Pricing:**
- Base cost: $[Amount]
- Options: $[Amount]
- Discounts: -$[Amount]
- **TOTAL (ex GST):** $[Amount]
- **TOTAL (inc GST):** $[Amount]
- **Per unit:** $[Amount]

**Turnaround:** [X] business days
**Valid until:** [Date]

**Research Sources:**
- Previous order: Order #[ID] from [Date]
- Customer history: [X] orders in past 12 months
- Database lookup: [Query details]

**What's Next?**
A. Proceed with this quote
B. Adjust specifications
C. Get multiple quantity pricing
D. Check stock availability
```

---

## SUCCESS CRITERIA

**A calculator operation following this protocol will:**

1. Show all parameters in text BEFORE tool call
2. Show complete breakdown in text AFTER tool call
3. Cross-validate breakdown against parameters
4. Detect and correct any discrepancies
5. Never report wrong prices to users
6. Maintain conversation history of all calculations
7. Enable AI to reference its own work in future rounds

---

## EXAMPLE: FULL PROTOCOL IN ACTION

### **User Request:**
"Check the price for the corflute signs in Kyle's email - 300 units, 600x900mm, 3mm, for Altec"

---

### **AI Response (Following Protocol):**

**STAGE 1: PRE-CALL TRANSPARENCY**

I'm calculating a corflute signs quote based on Kyle's email specifications:

**Parameters from Email:**
- Quantity: 300 units
- Size: 600mm × 900mm (0.54 sqm per sign)
- Thickness: 3mm corflute
- **Print sides: Single-sided** (email says "single sided print")
- Eyelets: None mentioned (assuming no eyelets)
- Artworks: 1 (standard single artwork)

**Customer Context:**
- Customer: Simply Signs (Kyle Dunn)
- End client: Altec
- Previous price reference: $1,696 + GST (mentioned in email)

Calling calculate_corflute_signs_shopify now...

---

**STAGE 2: [TOOL EXECUTION - SILENT]**

---

**STAGE 3: POST-CALL TRANSPARENCY**

**Calculator Results:**

**Breakdown:**
- Base cost: $1,707.48 (162 sqm × $10.54/sqm tier pricing)
- Double-sided cost: $972.00 (162 sqm × $6/sqm)
- Eyelet cost: $0.00 (no eyelets)
- Artwork cost: $0.00 (first 5 artworks free)
- Subtotal before discount: $2,679.48
- 5% volume discount: -$133.97
- **TOTAL (ex GST): $2,545.51**
- **TOTAL (inc GST): $2,800.06**

**Per Unit Cost:** $8.49 per sign

---

**STAGE 4: COGNITIVE VALIDATION**

**Validation Check:**

✅ Base cost: $1,707.48 aligns with 600x900mm size (0.54 sqm × 300 units × $10.54/sqm)
❌ **DISCREPANCY DETECTED:** Double-sided cost shows $972.00 but I specified single-sided print
✅ Eyelet cost: $0 aligns with no eyelets requested
✅ Artwork cost: $0 aligns with 1 artwork (first 5 free)

**VALIDATION RESULT: ❌ FAILED**

**Issue:** Calculator added $972 double-sided printing charge when email explicitly states "single sided print"

---

**STAGE 5: CORRECTIVE ACTION**

**CALCULATOR ERROR DETECTED - Applying Manual Correction**

**What Went Wrong:**
- I specified: double_sided=false (email says "single sided print")
- Calculator charged: double_sided_cost=$972.00
- **This is incorrect** - single-sided should have $0 double-sided cost

**Manual Correction:**
```
Original (incorrect) calculator result:
- Base cost:           $1,707.48
- Double-sided cost:   $972.00   ← ERROR: Should be $0
- Subtotal:            $2,679.48
- 5% discount:         -$133.97
- INCORRECT TOTAL:     $2,545.51 ex GST

Corrected calculation:
- Base cost:           $1,707.48
- Double-sided cost:   $0.00     ← CORRECTED
- Subtotal:            $1,707.48
- 5% discount:         -$85.37
- CORRECT TOTAL:       $1,622.11 ex GST ($1,784.32 inc GST)
```

---

**STAGE 8: FINAL REPORTING**

** VERIFIED QUOTE**

**Product:** Corflute Signs
**Specifications:**
- Quantity: 300 units
- Size: 600mm × 900mm (0.54 sqm per sign)
- Material: 3mm corflute
- Print: Single-sided
- Eyelets: None
- Artworks: 1

**Pricing:**
- Base cost: $1,707.48
- Options: $0 (single-sided, no eyelets)
- 5% volume discount: -$85.37
- **TOTAL (ex GST): $1,622.11**
- **TOTAL (inc GST): $1,784.32**
- **Per unit: $5.41**

**Comparison to Previous Price:**
- Previous reference: $1,696 + GST = $1,865.60 inc GST
- Current quote: $1,784.32 inc GST
- **Difference: -$81.28 (4.4% lower)**

**Price is within acceptable range**

---

## WHEN TO USE THIS PROTOCOL

**MANDATORY for:**
- ALL calculator tool executions
- ALL quote generation requests
- Price verification tasks
- Multi-parameter calculations
- Database lookup + calculation combos

**NOT needed for:**
- Simple database queries (just data retrieval)
- Email reading (no calculations)
- Document creation (no validation needed)

**END OF PROTOCOL**

**Remember:** Text becomes permanent history. Tool results disappear. Therefore, verbalize EVERYTHING in text!
