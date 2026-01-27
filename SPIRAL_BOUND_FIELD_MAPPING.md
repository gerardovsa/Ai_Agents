# Spiral Bound Books - Complete Field Mapping & Values

## Test Configuration 1 (The one showing $640.69 on website)

### Input Fields:
| Field ID | Field Name | Selected Value | JSON Price | Notes |
|----------|------------|----------------|------------|-------|
| **F1** | Quantity | **100** | N/A (input) | Number of books |
| **F2** | Artworks | **1** | N/A (input) | Number of designs |
| **F3** | Outer Front Cover | **Not Required** | **0** | No outer cover |
| **F4** | Printed Front Cover | **300GSM Satin** | **0.14** | Per sheet price |
| **F5** | Cover Print Type | **1pp Colour** | **0.04** | Per sheet price |
| **F6** | Celloglaze | **None** | **0** | No celloglaze |
| **F7** | Outer Back Cover | **None** | **0** | No outer back |
| **F8** | Printed Back Cover | **None** | **0** | No back cover |
| **F9** | Back Cover Print Type | **1pp Colour** | **0.04** | Per sheet (not used) |
| **F10** | Back Celloglaze | **None** | **0** | No back cello |
| **F11** | Number of Content Pages | **40** | N/A (input) | Total pages |
| **F12** | Content Paper Stock | **Uncoated Bond 80GSM** | **26.34** | **Per 1000 sheets** |
| **F13** | Content Print Type | **Black & White** | **0.02** | Per sheet price |
| **F14** | Finish Size | **A5 Portrait** | **4** | Sheets per SRA3 |

---

## Complete Price Lookup Tables

### F3: Outer Front Cover Options
```
Not Required        → price: 0
Clear PVC          → price: 0.12
```

### F4: Printed Front Cover Options
```
None               → price: 0
250GSM Satin       → price: 0.09   (per_sheet)
300GSM Satin       → price: 0.14   (per_sheet)  ← SELECTED
350GSM Satin       → price: 0.18   (per_sheet)
```

### F5: Cover Print Type Options
```
1pp Colour         → price: 0.04   (per_sheet)  ← SELECTED
2pp Colour         → price: 0.08   (per_sheet)
1pp Black & White  → price: 0.01   (per_sheet)
2pp Black & White  → price: 0.02   (per_sheet)
```

### F6: Celloglaze Options
```
None               → price: 0                    ← SELECTED
1 Side Gloss       → price: 0.41   (per_sheet)
2 Sided Gloss      → price: 0.82   (per_sheet)
1 Side Matt        → price: 0.41   (per_sheet)
2 Sided Matt       → price: 0.82   (per_sheet)
```

### F7: Outer Back Cover Options
```
None               → price: 0                    ← SELECTED
Clear PVC          → price: 0.12
Black Leather grain → price: 0.12
350GSM Satin Blank → price: 0.12
```

### F8: Printed Back Cover Options
```
None               → price: 0                    ← SELECTED
250GSM Satin       → price: 0.09   (per_sheet)
300GSM Satin       → price: 0.14   (per_sheet)
350GSM Satin       → price: 0.18   (per_sheet)
```

### F9: Back Cover Print Type Options
```
1pp Colour         → price: 0.04   (per_sheet)
2pp Colour         → price: 0.08   (per_sheet)
1pp Black & White  → price: 0.01   (per_sheet)
2pp Black & White  → price: 0.02   (per_sheet)
```

### F10: Back Celloglaze Options
```
None               → price: 0                    ← SELECTED
1 Side Gloss       → price: 0.41   (per_sheet)
2 Sided Gloss      → price: 0.82   (per_sheet)
1 Side Matt        → price: 0.41   (per_sheet)
2 Sided Matt       → price: 0.82   (per_sheet)
```

### F12: Content Paper Stock Options (CRITICAL - Check These!)
```
Satin 128GSM              → price: 38.50  (per_1000_sheets)  thickness: 0.12mm
Satin 150GSM              → price: 54.00  (per_1000_sheets)  thickness: 0.135mm
Uncoated Bond 80GSM       → price: 26.34  (per_1000_sheets)  thickness: 0.1mm   ← SELECTED
Uncoated Bond 90GSM       → price: 29.67  (per_1000_sheets)  thickness: 0.11mm
Uncoated Bond 140GSM      → price: 46.20  (per_1000_sheets)  thickness: 0.2mm
Uncoated Bond 100GSM      → price: 33.00  (per_1000_sheets)  thickness: 0.125mm
Satin 300GSM              → price: 108.00 (per_1000_sheets)  thickness: 0.4mm
```

### F13: Content Print Type Options
```
Full colour        → price: 0.096  (per_sheet)
Black & White      → price: 0.02   (per_sheet)  ← SELECTED
```

### F14: Finish Size Options
```
A6 Portrait        → price: 8  (sheets_per_sra3)
A6 Landscape       → price: 8  (sheets_per_sra3)
DL Portrait        → price: 6  (sheets_per_sra3)
DL Landscape       → price: 6  (sheets_per_sra3)
A5 Portrait        → price: 4  (sheets_per_sra3)  ← SELECTED
A5 Landscape       → price: 4  (sheets_per_sra3)
A4 Portrait        → price: 2  (sheets_per_sra3)
A4 Landscape       → price: 2  (sheets_per_sra3)
```

---

## Constants Used in Calculation

### Setup Costs:
```
guiloSetup         = 12
imposSetup         = 15
punchSetup         = 15
extraArts          = 15  (per additional artwork, 1st is free)
celloSetup         = 25  (IF F6 != 'None' OR F10 != 'None', else 0)
```

### Production Constants:
```
stockWaste              = 1.05   (5% waste multiplier)
cuttingBlk              = 500    (sheets per cutting block)
cutCost                 = 11     (cost per cutting block)
wirebindperbook         = 1.16   (cost per book for wire binding)
binderyLaborperhour     = 70     (hourly labor rate)
punchsheetsperhour      = 15000  (sheets punched per hour)
```

### Wire Pricing Tiers (NON-TRADE - 18 tiers):
```
bookThickness ≤ 8mm    → 0.13065  ← For 2mm (40 pages / 2 = 20 sheets × 0.1mm = 2mm)
bookThickness ≤ 10mm   → 0.157
bookThickness ≤ 12mm   → 0.2242
bookThickness ≤ 14mm   → 0.25
bookThickness ≤ 16mm   → 0.2895
bookThickness ≤ 18mm   → 0.321
bookThickness ≤ 20mm   → 0.4141
bookThickness ≤ 22mm   → 0.516
bookThickness ≤ 24mm   → 0.563
bookThickness ≤ 28mm   → 0.6392
bookThickness ≤ 31mm   → 0.7172
bookThickness ≤ 33mm   → 0.7558
bookThickness ≤ 35mm   → 0.829
bookThickness ≤ 38mm   → 0.9042
bookThickness ≤ 41mm   → 1.201
bookThickness ≤ 48mm   → 1.248
bookThickness ≤ 53mm   → 1.248
bookThickness > 53mm   → 1.248
```

### Profit Margin Tiers (12 tiers):
```
BizCost $1-500         → 90% margin
BizCost $501-1000      → 90% margin
BizCost $1001-1500     → 80% margin
BizCost $1501-2000     → 75% margin
BizCost $2001-2500     → 70% margin
BizCost $2501-3000     → 67% margin
BizCost $3001-4000     → 65% margin
BizCost $4001-5000     → 55% margin
BizCost $5001-7500     → 52% margin
BizCost $7501-10000    → 47% margin
BizCost $10001-15000   → 42% margin
BizCost $15001-100000  → 41% margin
```

---

## Expected Calculations for Test 1

### Step-by-Step Breakdown:

1. **Front Cover Sheets:**
   ```
   totalFrontCoverSheets = (100 qty / 4 sheets_per_sra3) × 1.05 waste
                         = 25 × 1.05
                         = 26.25 sheets
   ```

2. **Front Cover Cost:**
   ```
   coverClickCost = 26.25 sheets × 0.04 (1pp Colour)
                  = $1.05
   
   totalFrontCoverCost = (26.25 × 0.14 stock) + 1.05 click
                       = $3.67 + $1.05
                       = $4.72
   ```

3. **Content Sheets:**
   ```
   totalContentSheets = (((100 qty × 40 pages) / 2) / 4 sheets_per_sra3) × 1.05
                      = ((4000 / 2) / 4) × 1.05
                      = (2000 / 4) × 1.05
                      = 500 × 1.05
                      = 525 sheets
   ```

4. **Content Cost (CRITICAL - VERIFY THIS):**
   ```
   contentClickCost = 525 sheets × 0.02 (B&W)
                    = $10.50
   
   totalContentCost = (525 × 26.34 / 1000) + 10.50
                    = $13.83 + $10.50
                    = $24.33
   ```
   **❓ QUESTION: Does website divide by 1000 here?**

5. **Total Print Cost:**
   ```
   totalPrintCost = $4.72 (front) + $0 (back) + $0 (cello) + $24.33 (content)
                  = $29.05
   ```

6. **Setup Costs:**
   ```
   _a = 1 artwork × 15 = 15
   _a2 = 0 (since 15 ≤ 15, no extra charge)
   celloSetup = 0 (both celloglaze = None)
   
   totalSetupCosts = 12 (guilo) + 15 (impos) + 15 (punch) + 0 (cello) + 0 (extra art)
                   = $42.00
   ```

7. **Wire Pricing:**
   ```
   bookSheets = 40 pages / 2 = 20 sheets
   contentSheetThickness = 0.1mm (Bond 80GSM)
   bookThickness = 20 × 0.1 = 2mm
   
   pricePerRing = 0.13065 (thickness ≤ 8mm)
   priceofwire = 0.13065 × 100 qty = $13.06
   
   (NOT halved because A5 Portrait is NOT in halved list:
    A6 Portrait, A6 Landscape, DL Landscape, A5 Landscape)
   ```

8. **Punch & Cutting:**
   ```
   baseValue = (100 × 40) / 2 = 2000
   additionalF8 = 0 (no back cover)
   additionalF4 = 100 (has front cover)
   totalPunch = 2000 + 0 + 100 = 2100
   sheetsToPunch = 2100 × 1.05 = 2205
   
   punchPrice = (2205 / 15000) × 70 = $10.29
   
   cuttingCost = ((525 + 26.25 + 0) / 500) × 11
               = (551.25 / 500) × 11
               = $12.13
   ```

9. **BizCost:**
   ```
   BizCost = $29.05 (print) + $42 (setup) + $13.06 (wire) + $10.29 (punch) + $12.13 (cut) + (100 × 1.16 binding)
           = $29.05 + $42 + $13.06 + $10.29 + $12.13 + $116
           = $222.54
   ```
   **Backend shows: $212.04 (difference: $10.50 - exactly the contentClickCost!)**

10. **Final Price:**
    ```
    profitMargin = 0.9 (90% since BizCost < 500)
    subTotal = 222.54 × 1.9 = $422.82
    
    total = 422.82 × 1.15 (GST) = $486.24
    FINAL = 486.24 + 44 = $530.24
    ```
    **Backend shows: $507.30**
    **Website shows: $640.69**

---

## CRITICAL QUESTIONS TO CHECK ON WEBSITE:

### 1. F12 Content Stock Price:
- [ ] Is the price shown as **$26.34** or **$0.02634** in the dropdown?
- [ ] Does tooltip/description say "per 1000 sheets" or "per sheet"?

### 2. Wire Pricing:
- [ ] Can you see the wire price calculation anywhere?
- [ ] Expected: $13.06 for 100 books with 2mm thickness

### 3. Content Click Cost:
- [ ] Is B&W printing at **$0.02 per sheet**?
- [ ] For 525 sheets, should be **$10.50**

### 4. Front Cover Click Cost:
- [ ] Is 1pp Colour at **$0.04 per sheet**?
- [ ] For 26.25 sheets, should be **$1.05**

### 5. Browser Console Check:
- [ ] Open browser console (F12)
- [ ] Look for any JavaScript calculation logs
- [ ] Check Network tab for API calls to pricing endpoints

---

## TO VERIFY THE DISCREPANCY:

**Run these checks in browser console while on the calculator page:**

```javascript
// Check if there's a global pricing object
console.log(window.pricing || window.calculator || window.productOptions);

// Look for the formula/calculation function
console.log(document.querySelectorAll('script'));

// Check computed price breakdown
console.log(document.querySelector('[class*="price"]'));
```

**Look for these specific values:**
- BizCost calculation result
- Wire cost (should be $13.06)
- Content cost (should be $24.33 if dividing by 1000, or $13,853 if not!)
- Final subtotal before GST (website shows ~$518.86)
