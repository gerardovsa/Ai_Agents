# BOLLARD SIGNS - SHOPIFY VALIDATION TEST CASES
**Date:** January 23, 2026  
**Purpose:** Validate calculator against live Shopify store  
**Status:** Backend fixed to match JSON specification

---

## 🎯 HOW TO TEST ON SHOPIFY

1. Go to your Shopify store's Bollard Signs product page
2. Enter the test parameters below
3. Compare Shopify's calculated price to our calculator's price
4. They should match within $0.50 (GST rounding differences acceptable)

---

## 📋 TEST CASE 1: Minimum Order (Single Sign)

**Parameters:**
- **Quantity:** 1
- **Material:** 5mm Corflute
- **Size:** 270mm W x 1000mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $202.92

**Shopify Expected:** ~$202-203

**Formula Breakdown:**
```
Area: 0.91 m² per sign × 3 sides = 2.73 sqm
Price/sqm tier: $31.25 (tier for 2.73 sqm)
Material cost: 2.73 × $31.25 = $85.31
Setup: $5 (base artwork)
Business cost: $90.31
Minimum applied: $129 (90.31 < 129, so use 129)
After multiplier: $129 × 1.3 = $167.70
After GST: $167.70 × 1.1 × 1.1 = $202.92
```

**Why this test matters:** Verifies minimum order logic

---

## 📋 TEST CASE 2: Standard Order (10 Signs)

**Parameters:**
- **Quantity:** 10
- **Material:** 5mm Corflute
- **Size:** 270mm W x 1000mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $750.78

**Shopify Expected:** ~$750-751

**Formula Breakdown:**
```
Area: 0.91 m² per sign × 10 signs × 3 sides = 27.30 sqm
Price/sqm tier: $17.30 (tier for 27.30 sqm)
Material cost: 27.30 × $17.30 = $472.29
Setup: $5
Business cost: $477.29
After multiplier: $477.29 × 1.3 = $620.48
After GST: $620.48 × 1.1 × 1.1 = $750.78
```

**Why this test matters:** Verifies tiered pricing (27.30 sqm tier)

---

## 📋 TEST CASE 3: 3mm vs 5mm Material

**Test 3A - 3mm Corflute:**
- **Quantity:** 10
- **Material:** 3mm Corflute
- **Size:** 270mm W x 1000mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $621.09

**Shopify Expected:** ~$621

**Test 3B - 5mm Corflute:**
- **Quantity:** 10
- **Material:** 5mm Corflute
- **Size:** 270mm W x 1000mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $750.78

**Shopify Expected:** ~$751

**Why this test matters:** 
- Verifies correct material tier pricing
- 3mm uses 3mm_corflute pricing tiers
- 5mm uses 5mm_corflute pricing tiers
- 5mm should be ~20% more expensive

---

## 📋 TEST CASE 4: Multiple Artworks

**Parameters:**
- **Quantity:** 10
- **Material:** 5mm Corflute
- **Size:** 270mm W x 1000mm H - Three Sided
- **Artworks:** 3

**Our Calculator Result:** $774.14

**Shopify Expected:** ~$774

**Formula Breakdown:**
```
Material cost: $472.29 (same as Test 2)
Setup: $5 + (3-1) × $5 = $15
Business cost: $487.29
After multiplier: $487.29 × 1.3 = $633.48
After GST: $633.48 × 1.1 × 1.1 = $766.48
```

**Why this test matters:** Verifies artwork setup formula ($5 base + $5 per extra)

---

## 📋 TEST CASE 5: Large Order (Tier Pricing)

**Parameters:**
- **Quantity:** 100
- **Material:** 5mm Corflute
- **Size:** 300mm W x 1000mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $5,675.38

**Shopify Expected:** ~$5,675

**Formula Breakdown:**
```
Area: 1.0 m² per sign × 100 signs × 3 sides = 300.00 sqm
Price/sqm tier: $12.01 (tier for 300 sqm - much lower!)
Material cost: 300.00 × $12.01 = $3,603.00
Setup: $5
Business cost: $3,608.00
After multiplier: $3,608.00 × 1.3 = $4,690.40
After GST: $4,690.40 × 1.1 × 1.1 = $5,675.38
```

**Why this test matters:**
- Verifies tiered pricing benefits at scale
- 300 sqm gets $12.01/sqm (vs $31.25/sqm for small orders)
- Unit price drops from $75.08 to $56.75

---

## 📋 TEST CASE 6: Four-Sided Configuration

**Parameters:**
- **Quantity:** 10
- **Material:** 5mm Corflute
- **Size:** 175mm W x 1000mm H - Four Sided
- **Artworks:** 1

**Our Calculator Result:** $835.39

**Shopify Expected:** ~$835

**Formula Breakdown:**
```
Area: 0.80 m² per sign × 10 signs × 4 sides = 32.00 sqm
Price/sqm tier: $16.44 (tier for 32 sqm)
Material cost: 32.00 × $16.44 = $526.08
Setup: $5
Business cost: $531.08
After multiplier: $531.08 × 1.3 = $690.40
After GST: $690.40 × 1.1 × 1.1 = $835.39
```

**Why this test matters:** 
- Verifies four-sided calculation (4 panels instead of 3)
- Different total sqm affects tier pricing

---

## 📋 TEST CASE 7: Largest Size

**Parameters:**
- **Quantity:** 10
- **Material:** 5mm Corflute
- **Size:** 300mm W x 1800mm H - Three Sided
- **Artworks:** 1

**Our Calculator Result:** $1,284.54

**Shopify Expected:** ~$1,285

**Formula Breakdown:**
```
Area: 1.80 m² per sign × 10 signs × 3 sides = 54.00 sqm
Price/sqm tier: $15.03 (tier for 54 sqm)
Material cost: 54.00 × $15.03 = $811.62
Setup: $5
Business cost: $816.62
After multiplier: $816.62 × 1.3 = $1,061.61
After GST: $1,061.61 × 1.1 × 1.1 = $1,284.54
```

**Why this test matters:** Verifies largest size option pricing

---

## 📋 VALIDATION CHECKLIST

For each test case, verify:

- [ ] **Price Match:** Shopify price matches our calculator within $0.50
- [ ] **Unit Price:** Shopify unit price matches (Total ÷ Quantity)
- [ ] **Tier Logic:** Higher quantities get lower price/sqm
- [ ] **Material Difference:** 3mm cheaper than 5mm (same qty/size)
- [ ] **Sides Logic:** Four-sided more expensive than three-sided
- [ ] **Artwork Logic:** Each extra artwork adds ~$6 to total (after multipliers)
- [ ] **Minimum Order:** Single sign price never below ~$203

---

## 🔍 WHAT TO LOOK FOR

### ✅ GOOD SIGNS (Calculator is correct):
- Prices match within $0.50
- Tier pricing working (larger orders = lower unit price)
- Material pricing correct (3mm < 5mm)
- Setup costs scale correctly with artworks

### ⚠️ WARNING SIGNS (Need investigation):
- Prices differ by more than $1.00
- Tier pricing not working (unit price same for 10 vs 100)
- Material pricing wrong (3mm = 5mm or 3mm > 5mm)
- Setup costs don't match artwork count

### ❌ CRITICAL ISSUES (Backend still wrong):
- Prices differ by >$50
- Minimum order not applied (single sign < $200)
- No tier pricing benefit (100 signs same price/sqm as 1 sign)
- Final multiplier not applied (prices ~30% lower than expected)

---

## 📊 EXPECTED TIER PRICING BEHAVIOR

| Total SQM | Price/SQM (5mm) | Example Config |
|-----------|-----------------|----------------|
| 0-5 sqm | $31.25 | 1 sign, 270×1000, 3-sided |
| 5-6 sqm | $28.35 | 2 signs, 270×1000, 3-sided |
| 15-20 sqm | $19.50 | 7 signs, 270×1000, 3-sided |
| 25-30 sqm | $17.30 | 10 signs, 270×1000, 3-sided |
| 50-60 sqm | $15.03 | 10 signs, 300×1800, 3-sided |
| 100-110 sqm | $13.75 | 37 signs, 270×1000, 3-sided |
| 300-325 sqm | $12.01 | 100 signs, 300×1000, 3-sided |
| 700+ sqm | $10.97 | 230+ signs, 300×1000, 3-sided |

**Key Observation:** Price per sqm drops significantly with volume (31.25 → 10.97 = 65% discount at scale)

---

## 🎯 PRIORITY TESTS

**If you only have time for 3 tests:**

1. **TEST 2** (Standard Order - 10 signs) → Most common use case
2. **TEST 5** (Large Order - 100 signs) → Verifies tier pricing
3. **TEST 4** (Multiple Artworks) → Verifies setup costs

**These 3 tests cover:** Tier pricing, setup costs, final multiplier, GST calculation

---

## 📝 RECORDING RESULTS

For each test, record:

```
Test Case: [Number]
Shopify Price: $[amount]
Calculator Price: $[amount]
Difference: $[amount] ([%])
Status: ✅ PASS / ⚠️ CLOSE / ❌ FAIL
Notes: [any observations]
```

---

## 🚀 AFTER VALIDATION

**If all tests pass (prices within $0.50):**
- ✅ Backend is correctly aligned to JSON specification
- ✅ Ready for production
- ✅ Move to next calculator (Construction Signs)

**If tests fail:**
- ⚠️ Review Shopify's actual formula (may differ from JSON docs)
- ⚠️ Check if Shopify has been updated since JSON was created
- ⚠️ Compare tier breakpoints (sqm values) between Shopify and JSON
- ⚠️ Verify GST calculation (×1.1×1.1 vs ×1.21)

---

**Validation Ready:** January 23, 2026  
**Tests Created:** 7 comprehensive test cases  
**Coverage:** Minimum order, tier pricing, materials, artworks, sizes, sides  
**Next:** Validate against live Shopify, then move to Construction Signs
