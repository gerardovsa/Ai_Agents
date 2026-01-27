# Printed Flyers - Website Validation Tests
**Date:** January 24, 2026  
**Calculator:** PrintedFlyers_Shopify_Calculator.py  
**Website:** https://inhouseprint.com.au/product/printed-flyers/

---

## Test Configuration

### Backend Test Command
```powershell
# Run individual test
python UI\modules_external\quote-calculator\implementations\PrintedFlyers_Shopify_Calculator.py

# Or use Python directly
python -c "from UI.modules_external.quote-calculator.implementations.PrintedFlyers_Shopify_Calculator import PrintedFlyersShopifyCalculator; calc = PrintedFlyersShopifyCalculator(); result = calc.calculate(quantity=100, print_sides='Double', print_type='Colour', finish_size='DL - 99mm x 210mm', paper_stock='Satin 128GSM', artworks=1); print(f'Total: ${result.total_price:.2f} inc GST')"
```

---

## TEST 1: Minimum Margin Test (170% Tier)

**Purpose:** Verify lowest cost tier with 170% profit margin

**Configuration:**
- **Quantity:** 100
- **Finish Size:** DL - 99mm x 210mm
- **Paper Stock:** Satin 128GSM
- **Print Type:** Colour
- **Print Sides:** Double
- **Artworks:** 1

**Backend Calculation:**
```
Setup Cost: $27.00 ($15 imposition + $12 guillotine)
Sheets Needed: 17.50 (100 / 6 items per sheet × 1.05 waste)
Stock Cost: $0.79 (17.50 / 1000 × $45)
Click Cost: $1.54 (17.50 × 2 sides × $0.044)
Cutting Cost: $0.39 (17.50 / 500 × $11)
Subtotal: $29.71
Profit Margin: 170% → $50.51
Before GST: $80.23
GST (10%): $8.02
TOTAL: $88.25 inc GST
Unit Price: $0.88
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Select: Quantity = 100
3. Select: Print Sides = Double
4. Select: Print Type = Colour
5. Select: Finish Size = DL - 99mm x 210mm
6. Select: Paper Stock = Satin 128GSM
7. Set: Artworks = 1
8. Note website total price

**Expected Result:** Website price should be **~$88.25** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 2: Mid-Range Test (115% Tier)

**Purpose:** Verify mid-tier margin with economical stock

**Configuration:**
- **Quantity:** 500
- **Finish Size:** A5 - 148mm x 210mm
- **Paper Stock:** Uncoated Bond 80GSM
- **Print Type:** Black & White
- **Print Sides:** Single
- **Artworks:** 1

**Backend Calculation:**
```
Setup Cost: $27.00
Sheets Needed: 131.25 (500 / 4 items per sheet × 1.05 waste)
Stock Cost: $3.46 (131.25 / 1000 × $26.34)
Click Cost: $2.63 (131.25 × 1 side × $0.02)
Cutting Cost: $2.89 (131.25 / 500 × $11)
Subtotal: $35.97
Profit Margin: 135% → $48.56
Before GST: $84.53
GST (10%): $8.45
TOTAL: $92.98 inc GST
Unit Price: $0.19
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Select: Quantity = 500
3. Select: Print Sides = Single
4. Select: Print Type = Black & White
5. Select: Finish Size = A5 - 148mm x 210mm
6. Select: Paper Stock = Uncoated Bond 80GSM
7. Set: Artworks = 1
8. Note website total price

**Expected Result:** Website price should be **~$92.98** (within $0.50)

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 3: Discount Threshold Test (1000 units = 10% off)

**Purpose:** Verify 10% discount applies at exactly 1000 units

**Configuration:**
- **Quantity:** 1000
- **Finish Size:** A4 - 210mm x 297mm
- **Paper Stock:** Satin 150GSM
- **Print Type:** Colour
- **Print Sides:** Double
- **Artworks:** 2 (Extra artwork: +$15)

**Backend Calculation:**
```
Setup Cost: $42.00 ($15 + $12 + $15 extra artwork)
Sheets Needed: 525 (1000 / 2 items per sheet × 1.05 waste)
Stock Cost: $28.35 (525 / 1000 × $54)
Click Cost: $46.20 (525 × 2 sides × $0.044)
Cutting Cost: $11.55 (525 / 500 × $11)
Subtotal: $128.10
Profit Margin: 130% → $166.53
Before GST: $294.63
GST (10%): $29.46
Before Discount: $324.09
10% Discount: -$32.41
TOTAL: $291.68 inc GST (WITH DISCOUNT)
Unit Price: $0.29
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Select: Quantity = 1000
3. Select: Print Sides = Double
4. Select: Print Type = Colour
5. Select: Finish Size = A4 - 210mm x 297mm
6. Select: Paper Stock = Satin 150GSM
7. Set: Artworks = 2
8. **VERIFY:** Discount message appears on website
9. Note website total price

**Expected Result:** Website price should be **~$291.68** (within $0.50) with visible discount

**Actual Website Price:** _____________

**Difference:** _____________

**Discount Applied on Website:** ⬜ YES ⬜ NO

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 4: Bulk Order Test (Lower Margin Tier)

**Purpose:** Verify large quantity with lower profit margins (30%)

**Configuration:**
- **Quantity:** 5000
- **Finish Size:** A3 - 297mm x 420mm
- **Paper Stock:** Satin 250GSM
- **Print Type:** Colour
- **Print Sides:** Double
- **Artworks:** 1

**Backend Calculation:**
```
Setup Cost: $27.00
Sheets Needed: 5250 (5000 / 1 item per sheet × 1.05 waste)
Stock Cost: $551.25 (5250 / 1000 × $105)
Click Cost: $462.00 (5250 × 2 sides × $0.044)
Cutting Cost: $115.50 (5250 / 500 × $11)
Subtotal: $1155.75
Profit Margin: 30% → $346.73
Before GST: $1502.48
GST (10%): $150.25
Before Discount: $1652.72
10% Discount: -$165.27
TOTAL: $1487.45 inc GST (WITH DISCOUNT)
Unit Price: $0.30
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Select: Quantity = 5000
3. Select: Print Sides = Double
4. Select: Print Type = Colour
5. Select: Finish Size = A3 - 297mm x 420mm
6. Select: Paper Stock = Satin 250GSM
7. Set: Artworks = 1
8. **VERIFY:** Discount message appears on website
9. Note website total price

**Expected Result:** Website price should be **~$1487.45** (within $1.00) with discount

**Actual Website Price:** _____________

**Difference:** _____________

**Discount Applied on Website:** ⬜ YES ⬜ NO

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 5: Satin 170GSM Verification (NEW STOCK)

**Purpose:** Verify newly added Satin 170GSM stock option exists on website

**Configuration:**
- **Quantity:** 250
- **Finish Size:** A5 - 148mm x 210mm
- **Paper Stock:** Satin 170GSM (NEW - $105 per 1000 sheets)
- **Print Type:** Colour
- **Print Sides:** Double
- **Artworks:** 1

**Backend Calculation:**
```
Setup Cost: $27.00
Sheets Needed: 65.63 (250 / 4 items per sheet × 1.05 waste)
Stock Cost: $6.89 (65.63 / 1000 × $105)
Click Cost: $5.78 (65.63 × 2 sides × $0.044)
Cutting Cost: $1.44 (65.63 / 500 × $11)
Subtotal: $41.11
Profit Margin: 155% → $63.72
Before GST: $104.83
GST (10%): $10.48
TOTAL: $115.31 inc GST
Unit Price: $0.46
```

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Select: Quantity = 250
3. Select: Print Sides = Double
4. Select: Print Type = Colour
5. Select: Finish Size = A5 - 148mm x 210mm
6. **VERIFY:** Paper Stock dropdown includes "Satin 170GSM" option
7. Select: Paper Stock = Satin 170GSM
8. Set: Artworks = 1
9. Note website total price

**Expected Result:** 
- ✅ Satin 170GSM option exists in dropdown
- Website price should be **~$115.31** (within $0.50)

**Satin 170GSM Available:** ⬜ YES ⬜ NO

**Actual Website Price:** _____________

**Difference:** _____________

**Status:** ⬜ PASS ⬜ FAIL

---

## TEST 6: Satin 200GSM Verification (REMOVED STOCK)

**Purpose:** Verify Satin 200GSM is NOT available on website (should be removed)

**Configuration:**
- **Quantity:** 500
- **Finish Size:** A4 - 210mm x 297mm
- **Paper Stock:** Satin 200GSM (SHOULD NOT EXIST)
- **Print Type:** Colour
- **Print Sides:** Double
- **Artworks:** 1

**Website Steps:**
1. Navigate to: https://inhouseprint.com.au/product/printed-flyers/
2. Click on Paper Stock dropdown
3. **VERIFY:** Satin 200GSM is NOT in the list
4. Available Satin options should be:
   - Satin 128GSM
   - Satin 150GSM
   - Satin 170GSM
   - Satin 250GSM
   - Satin 300GSM
   - Satin 350GSM

**Expected Result:** Satin 200GSM should NOT be available

**Satin 200GSM Available:** ⬜ YES (FAIL) ⬜ NO (PASS)

**Status:** ⬜ PASS ⬜ FAIL

---

## Summary Results

| Test | Description | Backend Price | Website Price | Difference | Status |
|------|-------------|---------------|---------------|------------|--------|
| 1 | 100 DL Satin 128GSM | $88.25 | __________ | __________ | ⬜ |
| 2 | 500 A5 Uncoated 80GSM | $92.98 | __________ | __________ | ⬜ |
| 3 | 1000 A4 Satin 150GSM (discount) | $291.68 | __________ | __________ | ⬜ |
| 4 | 5000 A3 Satin 250GSM (discount) | $1487.45 | __________ | __________ | ⬜ |
| 5 | 250 A5 Satin 170GSM (NEW) | $115.31 | __________ | __________ | ⬜ |
| 6 | Satin 200GSM removed | N/A | N/A | N/A | ⬜ |

---

## Acceptance Criteria

✅ **PASS:** Backend price matches website within $0.50 (or $1.00 for TEST 4)  
✅ **PASS:** 10% discount applies at 1000+ units on both backend and website  
✅ **PASS:** Satin 170GSM exists on website  
✅ **PASS:** Satin 200GSM does NOT exist on website  
❌ **FAIL:** Price difference > tolerance → Extract website formula for debugging

---

## Next Steps

### If All Tests Pass:
1. ✅ Mark Printed Flyers calculator as **VALIDATED**
2. Move to next calculator:
   - **Option A:** Folded Flyers (backend exists)
   - **Option B:** GOD Flyers (database-driven)
   - **Option C:** Other product categories

### If Tests Fail:
1. Extract actual JavaScript formula from website (browser DevTools)
2. Compare line-by-line with backend implementation
3. Identify calculation differences
4. Fix backend to match website precisely
5. Re-run all tests until 100% alignment

---

## Formula Verification Reference

**11-Tier Profit Margin System:**
| Tier | Subtotal Range | Margin | Applied To |
|------|----------------|--------|------------|
| 1 | $1 - $50.99 | 1.7 (170%) | TEST 1 |
| 2 | $51 - $74.99 | 1.55 (155%) | TEST 5 |
| 3 | $75 - $100.99 | 1.35 (135%) | - |
| 4 | $101 - $150.99 | 1.30 (130%) | TEST 2, TEST 3 |
| 5 | $151 - $200.99 | 1.15 (115%) | - |
| 6 | $201 - $300.99 | 0.70 (70%) | - |
| 7 | $301 - $400.99 | 0.53 (53%) | - |
| 8 | $401 - $500.99 | 0.40 (40%) | - |
| 9 | $501 - $1000.99 | 0.30 (30%) | - |
| 10 | $1001 - $5000.99 | 0.30 (30%) | TEST 4 |
| 11 | $5001+ | 0.25 (25%) | - |

**Items Per Sheet:**
- DL (99×210mm): 6 items
- A6 (105×148mm): 8 items
- A5 (148×210mm): 4 items
- A4 (210×297mm): 2 items
- A3 (297×420mm): 1 item

**Stock Waste:** All calculations include 5% waste (×1.05)

**Discount Logic:**
- Quantity < 1000: No discount
- Quantity ≥ 1000: 10% off final price (×0.9)

---

**Ready for Website Testing!** 🚀
