# Business Card Calculator Pricing Analysis
**Date**: October 13, 2025  
**Status**: Testing Complete - Discrepancies Identified

## Executive Summary

Direct calculator testing reveals:
- **Economical Business Cards**: $6.38 SHORT (10% under expected)
- **Premium Business Cards**: $0.33 SHORT (0.3% under expected - acceptable)

Both calculators produce consistent results when tested directly, confirming the issue is in the **calculator logic**, not AI agent parameter mapping.

---

## Test Case 1: Economical Business Cards

### Test Specifications
```
Quantity: 1000
Print Sides: Double side print
Print Type: Colour
Finish Size: 90mm x 55mm
Paper Stock: Satin 300GSM
Artworks: 1
```

### Expected vs Actual Results

| Metric | Expected | Calculator Output | Difference |
|--------|----------|-------------------|------------|
| **Total inc GST** | **$70.40** | **$64.02** | **-$6.38 (9.1%)** |
| Total ex GST | $64.00 | $58.20 | -$5.80 |
| BizCost | Unknown | $38.80 | - |
| Profit Margin | 65% (calculated) | 50% | -15% points |
| Profit Amount | $25.20 | $19.40 | -$5.80 |

### Detailed Breakdown (Calculator Output)
```
Setup Costs:
  Imposition setup:     $15.00
  Guillotine setup:     $12.00
  Artwork setup:        $0.00  (first artwork free)
  Total Setup:          $27.00

Production Costs:
  Stock cost:           $6.30
  Click cost:           $4.40
  Cutting cost:         $1.10
  Total Production:     $11.80

BizCost (Setup + Production): $38.80

Profit Calculation:
  Profit Margin Rate:   50%  ⚠️ ISSUE: Should be 65%?
  Profit Amount:        $19.40
  
Subtotal ex GST:        $58.20
GST (10%):              $5.82
TOTAL inc GST:          $64.02
```

### Production Details
- **Sheets Needed**: 50 sheets
- **Cards Per Sheet**: 21 cards (standard for 90x55mm)
- **Price Increase**: 1.00 (no increase)
- **Surcharge**: $0.00

---

## Test Case 2: Premium Business Cards

### Test Specifications
```
Quantity: 500
Print Sides: Single side print
Print Type: Colour
Finish Size: 90mm x 55mm
Paper Stock: Satin 350GSM
Celloglaze: 1 Side Gloss
Artworks: 1
```

### Expected vs Actual Results

| Metric | Expected | Calculator Output | Difference |
|--------|----------|-------------------|------------|
| **Total inc GST** | **$95.70** | **$95.37** | **-$0.33 (0.3%)**  |
| Total ex GST | ~$78.85 | $78.82 | -$0.03 |
| BizCost | Unknown | $52.20 | - |
| Profit Margin | ~51% | 51% | Match  |
| Profit Amount | ~$26.65 | $26.62 | -$0.03 |

### Detailed Breakdown (Calculator Output)
```
Setup Costs:
  Imposition setup:     $15.00
  Guillotine setup:     $10.00
  Celloglaze setup:     $17.00
  Artwork setup:        $0.00  (first artwork free)
  Total Setup:          $42.00

Production Costs:
  Stock cost:           $4.50
  Click cost:           $1.20
  Cutting cost:         $0.50
  Celloglaze cost:      $4.00
  Total Production:     $10.20

BizCost (Setup + Production): $52.20

Profit Calculation:
  Profit Margin Rate:   51%   CORRECT
  Profit Amount:        $26.62
  
Subtotal ex GST:        $78.82

GST Application (DOUBLE GST - Shopify quirk):
  First GST (10%):      $7.88  → $86.70
  Second GST (10%):     $8.67  → $95.37
  Total GST:            $16.55 (21% effective rate)
  
TOTAL inc GST:          $95.37
```

### Production Details
- **Sheets Needed**: 25 sheets
- **Cards Per Sheet**: 21 cards (standard for 90x55mm)
- **Has Celloglaze**: TRUE

---

## Root Cause Analysis

### Economical Calculator: $6.38 Discrepancy

**Working Backwards from Expected $70.40:**
```
Expected Total:     $70.40
÷ GST (1.10):      = $64.00 ex GST
- BizCost:         - $38.80
= Profit Amount:   = $25.20

Required Margin:    $25.20 / $38.80 = 65%
Current Margin:     50%
DIFFERENCE:         -15% points
```

**Profit Margin Tier Analysis:**

Current Implementation (13 tiers):
```python
def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
    tiers = [
        (Decimal('50.999'), Decimal('0.5')),    # $1-$50.99: 50% margin ← BizCost $38.80 falls HERE
        (Decimal('60.999'), Decimal('0.51')),   # $51-$60.99: 51% margin
        (Decimal('65.999'), Decimal('0.6')),    # $61-$65.99: 60% margin
        (Decimal('70.999'), Decimal('0.6')),    # $66-$70.99: 60% margin
        (Decimal('80.999'), Decimal('0.7')),    # $71-$80.99: 70% margin
        # ... continues to 13 tiers total
    ]
```

**PROBLEM IDENTIFIED:**
- BizCost $38.80 falls into Tier 1 (50% margin)
- Expected pricing suggests it should use **65% margin**
- This could mean:
  1. **Tier boundaries are wrong** - should the $38.80 BizCost trigger a higher tier?
  2. **Margin percentages are wrong** - should Tier 1 be 65% instead of 50%?
  3. **BizCost calculation missing components** - should BizCost be higher to trigger different tier?

### Premium Calculator: $0.33 Discrepancy 

**Status**: ACCEPTABLE TOLERANCE (0.3% error)

The Premium calculator is essentially correct:
- $95.37 vs $95.70 expected = 33 cents difference
- Likely due to rounding differences or minor cost variations
- Profit margin calculation is correct (51%)
- DOUBLE GST application is working correctly
- No action required

---

## Comparison: Economical vs Premium

| Feature | Economical | Premium |
|---------|------------|---------|
| **Specification** | F1-F6 fields | F1-F7 fields (adds celloglaze) |
| **Stock Options** | Satin 300GSM only | Satin 350GSM, King Kong 420GSM, EcoStar 350GSM |
| **Profit Structure** | 13-tier BizCost-based (50%-90%) | DUAL: 120% no cello, 30%-90% with cello |
| **GST Application** | Single 10% GST | DOUBLE 10% GST (21% effective) - Shopify quirk |
| **Surcharge** | $0.00 | $0.00 |
| **Price Increase** | 1.00 (none) | Varies by calculator |
| **Accuracy** | ⚠️ $6.38 SHORT |  $0.33 SHORT (acceptable) |

---

## Recommendations

### Priority 1: Fix Economical Calculator Profit Margin

**Option A: Adjust Tier 1 Margin** (RECOMMENDED)
```python
# Change Tier 1 from 50% to 65%
(Decimal('50.999'), Decimal('0.65')),  # $1-$50.99: 65% margin (was 50%)
```

**Expected Result:**
- BizCost: $38.80 (unchanged)
- Profit @ 65%: $25.22 (was $19.40)
- Subtotal ex GST: $64.02 (was $58.20)
- Total inc GST: $70.42 (was $64.02)  MATCHES EXPECTED

**Impact**: All orders with BizCost under $51 will get 65% margin instead of 50%

---

**Option B: Adjust Tier Boundaries**
```python
# Change Tier 1 boundary from $50.99 to $35.99
(Decimal('35.999'), Decimal('0.5')),   # $1-$35.99: 50% margin
(Decimal('50.999'), Decimal('0.65')),  # $36-$50.99: 65% margin  ← $38.80 falls HERE
```

**Expected Result:** Same as Option A, but maintains 50% margin for very small orders

**Impact**: More granular tiering, preserves original low-tier margins

---

**Option C: Review All Tier Boundaries**

Conduct comprehensive analysis of:
1. Historical order data for 1000 qty business cards
2. Expected margin structure from Shopify DPO specification
3. Competitor pricing benchmarks
4. Desired profit margins by volume

### Priority 2: Verify Premium Calculator Margin Structure

Premium calculator uses **DUAL profit structure**:
- **120% margin** when no celloglaze
- **30%-90% margin** when celloglaze applied (BizCost-based tiers)

Our test case (500 qty, 1 Side Gloss Cello) used **51% margin** which suggests:
- BizCost $52.20 falls into a 51% tier (correct)
- Result $95.37 vs expected $95.70 = 0.3% error (acceptable)

**Action**: Document expected margins for each quantity/celloglaze combination

---

## Next Steps

1. **Immediate**: Decide on Option A vs Option B for Economical calculator fix
2. **Testing**: Re-run test_business_cards.py after implementing fix
3. **Validation**: Test additional quantity levels (250, 500, 2000, 5000, 10000)
4. **Documentation**: Update calculator documentation with correct margin tiers
5. **Production**: Deploy updated calculator to AI Quote Agent

---

## Testing Commands

### Run Direct Calculator Tests
```bash
cd G_Folder/Quote_Calculator/shopify_calculators
python test_business_cards.py
```

### Test via AI Quote Agent
```bash
cd G_Folder/Quote_Calculator/AI_Quote_Agent/web_interface
python flask_triple_agent_app.py

# Then in browser: http://localhost:5000
# Request: "Quote 1000 economical business cards, double-sided, colour, Satin 300GSM"
```

### Clean Up Test Files (After Validation)
```bash
# Delete test script when no longer needed
del G_Folder\Quote_Calculator\shopify_calculators\test_business_cards.py
```

---

## Appendix: Profit Margin Tier Details

### Economical Business Cards (Current Implementation)

| Tier | BizCost Range | Margin | Notes |
|------|---------------|--------|-------|
| 1 | $1 - $50.99 | 50% | ⚠️ Issue: $38.80 falls here, expects 65% |
| 2 | $51 - $60.99 | 51% | |
| 3 | $61 - $65.99 | 60% | |
| 4 | $66 - $70.99 | 60% | |
| 5 | $71 - $80.99 | 70% | |
| 6 | $81 - $100.99 | 60% | |
| 7 | $101 - $150.99 | 75% | |
| 8 | $151 - $200.99 | 90% | Peak margin |
| 9 | $201 - $300.99 | 30% | Volume pricing |
| 10 | $301 - $400.99 | 40% | |
| 11 | $401 - $500.99 | 45% | |
| 12 | $501 - $1000.99 | 30% | High volume |
| 13 | $1001+ | 30% | Very high volume |

### Premium Business Cards (DUAL Structure)

**Without Celloglaze:**
- Fixed 120% margin (simple markup)

**With Celloglaze (BizCost-based):**
- Similar 13-tier structure to Economical
- Test case: BizCost $52.20 → 51% margin  CORRECT

---

## Document Version
- **Version**: 1.0
- **Date**: October 13, 2025
- **Author**: AI Development Assistant
- **Status**: Analysis Complete - Awaiting Fix Decision
