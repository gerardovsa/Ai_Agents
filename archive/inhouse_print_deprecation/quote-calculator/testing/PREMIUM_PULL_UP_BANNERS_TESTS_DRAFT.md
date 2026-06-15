# Premium Pull Up Banners Calculator - Test Configurations (DRAFT)
**Created:** January 27, 2026  
**Status:** Awaiting website validation  
**Calculator:** `calculate_premium_pull_up_banners`

---

## Quick Test Summary

| Test | Qty | Size | Base Colour | Artworks | Expected Price |
|------|-----|------|-------------|----------|----------------|
| 1 | 1 | 850×2000mm | Silver | 1 | TBD |
| 2 | 5 | 850×2000mm | Black | 1 | TBD |
| 3 | 10 | 850×1500mm | Silver | 1 | TBD |
| 4 | 20 | 850×1400mm Shopping Center | Silver | 1 | TBD |
| 5 | 50 | 850×2000mm | Silver | 3 | TBD |
| 6 | 3 | 850×2000mm | Silver | 5 | TBD |

---

## Test Overview

Based on backend calculator structure with 25-tier pricing. Tests cover:
- ✅ Different sizes (850×2000mm, 850×1500mm, 850×1400mm)
- ✅ Various quantities to test tier pricing (1, 3, 5, 10, 20, 50)
- ✅ Both base colours (Silver, Black - cosmetic only)
- ✅ Different artwork counts (1, 3, 5 - adds COUNT directly)

**CRITICAL FORMULA NOTE:**  
This calculator has an **unusual formula** - it adds artwork COUNT directly to subtotal, NOT artwork cost!

Formula: `((quantity × tier_rate) + artworks + $15) × 1.1 × 1.1`

---

## TEST 1: Single Banner Standard Size

**Configuration:**
- Quantity: 1
- Size: 850mm W x 2000mm H
- Base Colour: Silver
- Artworks: 1

**Expected Calculation:**
- Tier rate (qty 1, 2000mm): $97.00
- Subtotal: 1 × $97.00 = $97.00
- Artworks added: +$1.00 (COUNT added directly!)
- Production setup: +$15.00
- Pre-markup total: $97.00 + $1.00 + $15.00 = $113.00
- First markup (×1.1): $113.00 × 1.1 = $124.30
- Second markup (×1.1): $124.30 × 1.1 = **$136.73**

**Website Price:** ___________

---

## TEST 2: Small Order Tier (5 Units)

**Configuration:**
- Quantity: 5
- Size: 850mm W x 2000mm H
- Base Colour: Black (cosmetic, no price difference)
- Artworks: 1

**Expected Calculation:**
- Tier rate (qty 5, 2000mm): $88.61
- Subtotal: 5 × $88.61 = $443.05
- Artworks added: +$1.00
- Production setup: +$15.00
- Pre-markup total: $443.05 + $1.00 + $15.00 = $459.05
- First markup (×1.1): $459.05 × 1.1 = $504.96
- Second markup (×1.1): $504.96 × 1.1 = **$555.45**

**Website Price:** ___________

---

## TEST 3: Medium Order Different Size (1500mm)

**Configuration:**
- Quantity: 10
- Size: 850mm W x 1500mm H
- Base Colour: Silver
- Artworks: 1

**Expected Calculation:**
- Tier rate (qty 10, 1500mm): $76.81 (other sizes tier)
- Subtotal: 10 × $76.81 = $768.10
- Artworks added: +$1.00
- Production setup: +$15.00
- Pre-markup total: $768.10 + $1.00 + $15.00 = $784.10
- First markup (×1.1): $784.10 × 1.1 = $862.51
- Second markup (×1.1): $862.51 × 1.1 = **$948.76**

**Website Price:** ___________

---

## TEST 4: Range Tier Shopping Center Size

**Configuration:**
- Quantity: 20
- Size: 850mm W x 1400mm H Shopping Center
- Base Colour: Silver
- Artworks: 1

**Expected Calculation:**
- Tier rate (qty 20, 1400mm): $73.06 (range tier 20-24 for other sizes)
- Subtotal: 20 × $73.06 = $1,461.20
- Artworks added: +$1.00
- Production setup: +$15.00
- Pre-markup total: $1,461.20 + $1.00 + $15.00 = $1,477.20
- First markup (×1.1): $1,477.20 × 1.1 = $1,624.92
- Second markup (×1.1): $1,624.92 × 1.1 = **$1,787.41**

**Website Price:** ___________

---

## TEST 5: High Volume with Multiple Artworks

**Configuration:**
- Quantity: 50
- Size: 850mm W x 2000mm H
- Base Colour: Silver
- Artworks: 3

**Expected Calculation:**
- Tier rate (qty 50, 2000mm): $74.85 (range tier 50-54)
- Subtotal: 50 × $74.85 = $3,742.50
- Artworks added: +$3.00 (COUNT = 3, added directly!)
- Production setup: +$15.00
- Pre-markup total: $3,742.50 + $3.00 + $15.00 = $3,760.50
- First markup (×1.1): $3,760.50 × 1.1 = $4,136.55
- Second markup (×1.1): $4,136.55 × 1.1 = **$4,550.21**

**Website Price:** ___________

---

## TEST 6: Small Order High Artwork Count

**Configuration:**
- Quantity: 3
- Size: 850mm W x 2000mm H
- Base Colour: Silver
- Artworks: 5

**Expected Calculation:**
- Tier rate (qty 3, 2000mm): $95.28
- Subtotal: 3 × $95.28 = $285.84
- Artworks added: +$5.00 (COUNT = 5, added directly!)
- Production setup: +$15.00
- Pre-markup total: $285.84 + $5.00 + $15.00 = $305.84
- First markup (×1.1): $305.84 × 1.1 = $336.42
- Second markup (×1.1): $336.42 × 1.1 = **$370.06**

**Website Price:** ___________

---

## Validation Checklist

For each test:
1. ✅ Go to: https://www.inhouseprint.com.au/products/premium-pull-up-banners (or relevant product page)
2. ✅ Enter exact configuration
3. ✅ Compare website price with expected price
4. ✅ Document actual price in table above
5. ✅ Note any discrepancies or validation errors

---

## Notes for Testing

**Critical Formula Elements:**
- **25-tier quantity-based pricing** (different tiers for 2000mm vs other sizes)
- **Unusual artwork handling:** Adds artwork COUNT directly, not cost ($1 per artwork, not $5)
- **Double markup:** ×1.1 ×1.1 = ×1.21 total
- **$15 production setup fee** added before markups
- **Base colour cosmetic only:** Silver vs Black doesn't affect price

**Tier Pricing Notes:**
- **850×2000mm:** $97 (qty 1-2) down to $73.72 (qty 70+)
- **Other sizes:** $90 (qty 1-2) down to $68.40 (qty 70+)
- Range tiers apply for qty 15-70+ (12 range tiers)

**Website Testing Tips:**
- Use "Calculate Price" or "Get Quote" button
- Verify size dropdown matches exact format ("850mm W x 2000mm H")
- Base colour should be cosmetic (no price change)
- Artwork field may show/hide based on quantity (visible when qty > 2 per backend comments)
- Final price should match expected calculation within $0.50 tolerance

