# Real Vinyl Stock Analysis - NO MULTIPLIERS NEEDED
**Date:** November 13, 2025  
**Databases Searched:** 4 SQLite databases (AI_agents, Quote_Calculator, Inventory, Inv-Stock)

---

## ✅ ACTUAL VINYL & LAMINATE STOCK FOUND

### **R1 - Monomeric White Vinyl Roll** (Standard Vinyl)
```
Stock ID: R1
Type: Vinyl (Monomeric PVC)
Description: White monomeric PVC vinyl with permanent acrylic adhesive
Roll Dimensions: 1370mm width × 50m length
Cost per Roll: $240.00
Cost per Linear Metre: $240 / 50 = $4.80/linear m
Cost per SQM: $4.80 / 1.37 = $3.50/sqm (base material cost)
Markup: 30%
Adhesive: Permanent acrylic
Finish: Glossy (100 micron calendered film)
Durability: Short to medium-term (3-5 years outdoor)
Compatible: Eco-solvent, solvent, UV, latex printers
Active: YES ✅
```

**Calculator Mapping:**
- Maps to: **"Standard (Monomeric)" + "Permanent"** adhesive option
- Roll width: **1370mm** ✅ Exact match with calculator spec!
- Base cost: **$3.50/sqm** (before markup and profit)

---

### **R32 - Polymeric Laminate Roll** (5-Year Outdoor)
```
Stock ID: R32
Type: Poly Lam (Polymeric Laminate)
Description: Rolam 5yr SAV/LAM GCP (SLUV) - Self-adhesive laminate film
Roll Dimensions: 1524mm width × 50m length
Cost per Roll: $99.00
Cost per Linear Metre: $99 / 50 = $1.98/linear m
Cost per SQM: $1.98 / 1.524 = $1.30/sqm
Supplier: Rocal/Rolam
Durability: 5+ years outdoor
Active: YES ✅
```

**Calculator Mapping:**
- Maps to: **"Gloss Laminate"** option (polymeric grade)
- 5-year outdoor durability rating
- **THIS IS YOUR POLYMERIC OPTION!** (as laminate)
- Cost: **$1.30/sqm** additional

---

### **R34 - Monomeric Matte Laminate Roll**
```
Stock ID: R34
Type: Laminate (Monomeric grade)
Description: Digitac POPDOT White Matt SLUV
Roll Dimensions: 1372mm width × 50m length
Cost per Roll: $398.00
Cost per Linear Metre: $398 / 50 = $7.96/linear m
Cost per SQM: $7.96 / 1.372 = $5.80/sqm
Supplier: Digitac
Finish: Matte
Active: NO (but cost data available)
```

**Calculator Mapping:**
- Maps to: **"Matte Laminate"** option
- Cost: **$5.80/sqm** additional
- **NOTE:** Currently inactive but cost is known

---

## 🎯 NO MULTIPLIERS NEEDED - USE REAL COSTS!

### Material Options with Real Stock:

**1. Standard (Monomeric) - R1**
- Base vinyl cost: **$3.50/sqm**
- With 30% markup: $3.50 × 1.30 = **$4.55/sqm** wholesale cost
- No laminate: Add **$0**
- Gloss laminate (R32): Add **$1.30/sqm**
- Matte laminate (R34): Add **$5.80/sqm**

**2. Premium (Polymeric) - NOT STOCKED AS VINYL**
- **SOLUTION:** Use R1 vinyl + R32 polymeric laminate
- Base vinyl: **$3.50/sqm** (R1 monomeric)
- REQUIRED laminate: **$1.30/sqm** (R32 polymeric - 5yr outdoor)
- Total material cost: **$4.80/sqm** before markup
- With markup: **$6.24/sqm** wholesale

**Logic:** Monomeric vinyl + polymeric laminate = polymeric-grade durability (5+ years outdoor)

**3. Adhesive Types:**
- **Permanent:** R1 stock (included in $3.50/sqm base)
- **Removable:** NOT IN STOCK - use R1 vinyl cost as baseline

---

## Calculator Implementation Strategy

### Option 1: Use Real Stock Combinations (RECOMMENDED)

```python
# Base costs from actual stock
BASE_VINYL_COST_PER_SQM = 3.50          # R1 monomeric vinyl
POLY_LAMINATE_COST_PER_SQM = 1.30       # R32 polymeric laminate (5yr)
MONO_LAMINATE_GLOSS_PER_SQM = 1.30      # R32 also works as gloss
MONO_LAMINATE_MATTE_PER_SQM = 5.80      # R34 matte laminate

VINYL_MARKUP = 0.30                      # 30% from R1 stock

def calculate_material_cost(vinyl_family, laminate_type, sqm):
    """Calculate material cost using REAL stock"""
    
    # Base vinyl (always R1 monomeric)
    vinyl_cost = BASE_VINYL_COST_PER_SQM * sqm
    
    # Laminate selection
    if vinyl_family == "Standard (Monomeric)":
        if laminate_type == "No Lamination":
            laminate_cost = 0
        elif laminate_type == "Gloss Laminate":
            laminate_cost = MONO_LAMINATE_GLOSS_PER_SQM * sqm  # R32
        elif laminate_type == "Matte Laminate":
            laminate_cost = MONO_LAMINATE_MATTE_PER_SQM * sqm  # R34
    
    elif vinyl_family == "Premium (Polymeric)":
        # ALWAYS require polymeric laminate for 5yr durability
        if laminate_type == "No Lamination":
            # Force polymeric laminate - can't have "premium" without it
            laminate_cost = POLY_LAMINATE_COST_PER_SQM * sqm  # R32 required
        elif laminate_type == "Gloss Laminate":
            laminate_cost = POLY_LAMINATE_COST_PER_SQM * sqm  # R32
        elif laminate_type == "Matte Laminate":
            # No polymeric matte laminate in stock - use R32 gloss
            laminate_cost = POLY_LAMINATE_COST_PER_SQM * sqm  # R32
    
    # Apply markup
    material_cost = (vinyl_cost + laminate_cost) * (1 + VINYL_MARKUP)
    
    return material_cost
```

### Option 2: Removable Adhesive Solution

Since we don't have removable adhesive vinyl rolls in stock:

**A. Don't offer removable option** (simplest)
- Remove "Removable" from adhesive dropdown
- Only offer "Permanent" (R1 stock)

**B. Estimate removable cost** (if you must offer it)
- Use R1 cost + 25% premium
- Base: $3.50/sqm × 1.25 = **$4.38/sqm** for removable
- Add note: "Removable vinyl pricing estimated - confirm with production"

---

## Updated Calculator Material Costs

### Scenario 1: 500 × 75mm circles, Standard vinyl, Gloss laminate

**Material (R1 + R32):**
- Stickers: 75mm × 75mm = 0.005625 sqm each
- Total: 500 × 0.005625 = 2.8125 sqm
- Vinyl cost: 2.8125 × $3.50 = **$9.84**
- Gloss laminate (R32): 2.8125 × $1.30 = **$3.66**
- Subtotal material: $9.84 + $3.66 = **$13.50**
- With 30% markup: $13.50 × 1.30 = **$17.55**

**Linear Metres Calculation:**
- Stickers per row: floor(1370 / 75) = 18
- Stickers per linear m: 18 × floor(1000 / 75) = 18 × 13 = 234
- Raw linear m: 500 / 234 = 2.14 linear m
- With 10% waste: 2.14 × 1.10 = **2.35 linear m**

**Verification:**
- Linear m SQM: 2.35 × 1.37 = 3.22 sqm (14% waste from layout)
- Cost check: 3.22 × $3.50 = $11.27 vinyl (vs $9.84 from sticker sqm)
- Use linear metre calculation for material costs!

**Corrected Material Cost:**
- Vinyl: 2.35 linear m × 1.37m width × $3.50/sqm = **$11.27**
- Laminate: 2.35 linear m × 1.37m width × $1.30/sqm = **$4.18**
- Subtotal: $11.27 + $4.18 = **$15.45**
- With 30% markup: $15.45 × 1.30 = **$20.09** material cost

---

### Scenario 2: 500 × 75mm circles, Premium (Polymeric), Gloss laminate

**Material (R1 + R32 required):**
- Vinyl (R1): 2.35 linear m × 1.37m × $3.50/sqm = **$11.27**
- Polymeric laminate (R32 required): 2.35 × 1.37 × $1.30/sqm = **$4.18**
- Subtotal: $11.27 + $4.18 = **$15.45**
- With 30% markup: **$20.09**

**Note:** Premium option uses same vinyl (R1) but REQUIRES polymeric laminate (R32) for 5-year durability rating.

---

## Summary: Real Stock Mapping

| Calculator Option | Stock Used | Cost/SQM | Notes |
|-------------------|------------|----------|-------|
| **Vinyl Family** |
| Standard (Monomeric) | R1 | $3.50 | Base vinyl, 3-5yr durability |
| Premium (Polymeric) | R1 + R32 required | $3.50 + $1.30 | Monomeric vinyl + polymeric laminate = 5yr+ |
| **Adhesive** |
| Permanent | R1 | Included | Only option in stock |
| Removable | NOT STOCKED | Estimate $4.38 | 25% premium over R1 |
| **Laminate** |
| No Lamination | - | $0 | Not recommended for Premium |
| Gloss Laminate | R32 (poly) or R32 | $1.30 | Polymeric grade, 5yr outdoor |
| Matte Laminate | R34 (mono) | $5.80 | Monomeric grade (inactive) |

---

## ✅ FINAL RECOMMENDATION

**Use real stock costs - NO multipliers:**

1. **Standard Monomeric vinyl:** R1 at $3.50/sqm base
2. **Premium Polymeric option:** R1 vinyl + R32 laminate (required) = $4.80/sqm base
3. **Laminates:** R32 (gloss, poly) at $1.30/sqm or R34 (matte, mono) at $5.80/sqm
4. **Adhesive:** Only offer "Permanent" (R1 stock) unless you add removable vinyl roll to inventory

**Key Insight:**
You don't need separate polymeric vinyl roll stock - you can achieve polymeric-grade durability (5+ years outdoor) by laminating monomeric vinyl (R1) with polymeric laminate (R32). This is industry-standard practice.

---

## Cost Comparison: Multiplier vs Real Stock

**500 × 75mm circles, Premium with laminate:**

**OLD (with 1.5× multiplier):**
- Base vinyl: $3.50/sqm
- Premium multiplier: $3.50 × 1.5 = $5.25/sqm
- Laminate: $1.30/sqm
- Total: $6.55/sqm
- Linear metres: 2.35 × 1.37 = 3.22 sqm
- Material cost: $21.09

**NEW (with real stock R1+R32):**
- Base vinyl (R1): $3.50/sqm
- Polymeric laminate (R32): $1.30/sqm
- Total: $4.80/sqm
- Linear metres: 2.35 × 1.37 = 3.22 sqm
- Material cost: **$15.45**

**Savings: $5.64 per job (27% cheaper using real stock!)**

---

## Next Steps

1. ✅ Use R1 ($3.50/sqm) for all vinyl base calculations
2. ✅ Use R32 ($1.30/sqm) for gloss/polymeric laminate
3. ✅ Use R34 ($5.80/sqm) for matte laminate (or estimate until reactivated)
4. ✅ Premium = Standard vinyl + Polymeric laminate (industry practice)
5. ⚠️ Remove "Removable" adhesive option OR add removable vinyl roll to stock
6. ✅ Update JSON config with real costs (no multipliers)
7. ✅ Implement calculator logic using real stock costs
