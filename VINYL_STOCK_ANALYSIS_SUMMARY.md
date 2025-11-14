# Vinyl Stock Analysis Summary
**Date:** November 13, 2025  
**Database:** `c:\Users\gpoli\GIT\AI_agents\data\stock_data.db`  
**Table:** `unified_stocks`

---

## Summary

Found **19 vinyl-related stock items** in the unified_stocks table. Analysis reveals:

1. **ACTUAL VINYL STICKER MATERIAL:** Only 1 proper vinyl roll stock (R1) - Monomeric white vinyl
2. **DIGITAL SHEET STOCKS:** 8 Adestor adhesive sheet stocks (not roll media)
3. **LAMINATE:** 1 laminate roll (R34) - Digitac POPDOT matte laminate
4. **TEMPORARY PLACEHOLDERS:** 3 temp stocks (monomeric, polymeric, poly_vinyl)
5. **OTHER ROLL MEDIA:** Banner (R10), Mesh (R15), Fabric (R20), One Way Vision (R25)
6. **RIGID SUBSTRATES:** ACM (T20), Foam PVC (T30), Foamcore (T35) - used with vinyl application

---

## Key Findings for Vinyl Stickers Calculator

### ✅ FOUND: Vinyl Roll Stock

**STOCK ID: R1 - Vinyl (Monomeric)**
- **Description:** White monomeric PVC vinyl with permanent acrylic adhesive
- **Roll Dimensions:** 1370mm width × 50m length (matches calculator spec!)
- **Cost per Roll:** $240.00
- **Cost per Linear Metre:** $9.00
- **Markup:** 30%
- **Material Type:** Vinyl
- **Finish:** Glossy (100 micron calendered film)
- **Adhesive:** Permanent acrylic
- **Durability:** Short to medium-term (3-5 years outdoor)
- **Compatible Printers:** Eco-solvent, solvent, UV, latex
- **Active:** Yes ✅

**Calculator Mapping:**
- Maps to: **"Standard (Monomeric)"** vinyl family option
- Adhesive: **"Permanent"** option
- Roll width: **1370mm** (exact match with calculator spec!)

### ✅ FOUND: Laminate Roll Stock

**STOCK ID: R34 - Laminate**
- **Description:** Digitac POPDOT White Matt SLUV laminate
- **Roll Dimensions:** 1372mm width × 50m length
- **Cost per Roll:** $398.00
- **Finish:** Matte
- **Material Type:** Laminate
- **Active:** No ⚠️ (but still in database)

**Calculator Mapping:**
- Maps to: **"Matte Laminate"** option
- Roll width: **1372mm** (2mm wider than vinyl - acceptable tolerance)
- **NOTE:** This stock is marked inactive - may need to update or find active laminate supplier

### ❌ MISSING: Polymeric Vinyl Stock

**NOT FOUND in actual stock:**
- No polymeric (long-term outdoor ~5 years) vinyl roll stock
- Temporary placeholder exists: `TEMP_polymeric_0` (no specs, no cost)

**Impact on Calculator:**
- Calculator offers **"Premium (Polymeric)"** option but no actual stock exists
- **RECOMMENDATION:** Either:
  1. Remove polymeric option from calculator until stock acquired, OR
  2. Add placeholder cost multiplier (e.g., 1.5× monomeric cost)

### ❌ MISSING: Gloss Laminate

**NOT FOUND in active stock:**
- Only matte laminate found (R34, inactive)
- No gloss laminate roll stock

**Impact on Calculator:**
- Calculator offers **"Gloss Laminate"** option but no stock
- **RECOMMENDATION:** Either:
  1. Remove gloss laminate option, OR
  2. Add cost multiplier vs matte laminate

### ❌ MISSING: Removable Adhesive Vinyl Roll

**FOUND in sheet form only:**
- Stock ID 249: Adestor Gloss Removable (sheet stock for digital printing)
- No removable adhesive vinyl on roll for plotter cutting

**Impact on Calculator:**
- Calculator offers **"Removable"** adhesive option
- **RECOMMENDATION:** Use cost multiplier (e.g., 1.25× permanent vinyl cost)

---

## Digital Sheet Stocks (Not Roll Media)

**Adestor Adhesive Stocks (for digital printing, not vinyl plotters):**

1. **Stock ID 182** - ADESTOR CAST GLOSS OPAQUE (450×320mm, $691.16/1000)
2. **Stock ID 161** - ADESTOR CAST GLOSS Solid Back (483×330mm, $345/1000)
3. **Stock ID 167** - ADESTOR VELLUM Uncoated (483×330mm, $332/1000)
4. **Stock ID 198** - Adestor Fluro Green (450×320mm, $737/1000)
5. **Stock ID 199** - Adestor Fluro Green (660×320mm, $985/1000)
6. **Stock ID 249** - Adestor Gloss Removable (450×320mm, $400/1000)
7. **Stock ID 146** - Adestor Synthetic (450×320mm, $280/1000)

**Usage:** These are **sheet-fed adhesive stocks** for digital printing (Canon/KM/Ricoh), not roll-to-roll vinyl for plotter cutting.

**Not applicable to vinyl stickers calculator** (different production method).

---

## Other Roll Media (Not Vinyl Stickers)

**STOCK ID: R10 - Banner**
- PVC banner material, 1370mm × 50m
- Cost: $280/roll ($5.60/linear metre)
- Not suitable for die-cut stickers

**STOCK ID: R15 - Mesh**
- PVC mesh banner, 1370mm × 50m
- Cost: $320/roll ($6.40/linear metre)
- Not suitable for stickers

**STOCK ID: R20 - Fabric**
- Fabric banner, 1370mm × 50m
- Cost: $550/roll ($11/linear metre)
- Not suitable for stickers

**STOCK ID: R25 - One Way Vision**
- Perforated window vinyl, 1370mm × 50m
- Cost: $680/roll ($13.60/linear metre)
- Not suitable for stickers

---

## Rigid Substrates (Vinyl Application Surfaces)

**STOCK ID: T20 - ACM (Aluminum Composite)**
- 1220×2440mm sheets, 3mm thick
- Cost: $65/sqm
- Used as substrate for vinyl mounting

**STOCK ID: T30 - Foam PVC**
- 1220×2440mm sheets, 5mm thick
- Cost: $55/sqm
- Accepts vinyl application

**STOCK ID: T35 - Foamcore**
- 210×297mm sheets, 5mm thick
- Cost: $2.20/sqm
- Small format substrate

---

## Recommendations for Calculator Implementation

### 1. **Use Actual Stock Costs (R1 Vinyl)**

**Current Calculator JSON uses placeholder rates:**
- Square metre rates from $950/sqm (micro stickers) down to $14/sqm (bulk)

**Actual Stock Cost (R1):**
- $9.00 per linear metre
- Roll width: 1.37m
- Cost per square metre: $9.00 / 1.37 = **$6.57/sqm** (base material cost)

**Recommendation:**
- Update JSON `square_meter_rates` to use $6.57/sqm as **base cost**
- Apply markup % (currently 30% in stock) = $8.54/sqm wholesale
- Apply calculator profit margins on top (150% for small jobs, 50% for bulk)

### 2. **Material Family Multipliers**

Since we only have monomeric vinyl stock (R1), add cost multipliers:

```json
"material_multipliers": {
  "Standard (Monomeric)": 1.0,     // Base - actual stock R1
  "Premium (Polymeric)": 1.5       // 50% premium for long-term outdoor
}
```

### 3. **Adhesive Type Multipliers**

```json
"adhesive_multipliers": {
  "Permanent": 1.0,     // Base - actual stock R1
  "Removable": 1.25     // 25% premium for removable adhesive
}
```

### 4. **Laminate Costs**

**Actual laminate stock (R34):**
- Cost: $398 per 50m roll (1372mm width)
- Cost per linear metre: $398 / 50 = **$7.96/linear metre**
- Cost per sqm: $7.96 / 1.372 = **$5.80/sqm**

**Add laminate multipliers:**

```json
"laminate_multipliers": {
  "No Lamination": 0.0,           // No extra cost
  "Gloss Laminate": 5.80,         // Add $5.80/sqm (placeholder - no active stock)
  "Matte Laminate": 5.80          // Add $5.80/sqm (R34 inactive but use cost)
}
```

### 5. **Update JSON Calculator Config**

Current JSON has:
- 51-tier square metre rates (hardcoded $950 down to $14/sqm)
- No material multipliers
- No adhesive multipliers
- No laminate cost additions

**Proposed changes:**
1. Replace 51-tier rates with formula: `base_sqm_cost × material_mult × adhesive_mult + laminate_cost`
2. Base material cost: $6.57/sqm (from R1 stock)
3. Apply markup: 30% (from R1 stock) = $8.54/sqm
4. Apply profit margin tiers (150% small jobs, 50% bulk jobs)
5. Add material/adhesive/laminate multipliers

### 6. **Stock Availability Warnings**

Add validation in calculator:

```python
# Check stock availability
AVAILABLE_MATERIALS = {
    "Standard (Monomeric)": True,    # R1 active
    "Premium (Polymeric)": False     # No stock - placeholder pricing
}

AVAILABLE_LAMINATES = {
    "Gloss Laminate": False,         # No stock
    "Matte Laminate": False          # R34 inactive
}
```

---

## Summary Table: Calculator Options vs Actual Stock

| Calculator Option | Actual Stock | Stock ID | Status | Cost Basis |
|-------------------|-------------|----------|--------|------------|
| **Vinyl Family** |
| Standard (Monomeric) | ✅ YES | R1 | Active | $9/linear m ($6.57/sqm) |
| Premium (Polymeric) | ❌ NO | TEMP_polymeric_0 | Placeholder | Use 1.5× multiplier |
| **Adhesive Type** |
| Permanent | ✅ YES | R1 | Active | Included in base cost |
| Removable | ❌ NO | - | - | Use 1.25× multiplier |
| **Laminate** |
| No Lamination | ✅ YES | - | - | $0 |
| Gloss Laminate | ❌ NO | - | - | Use $5.80/sqm estimate |
| Matte Laminate | ⚠️ INACTIVE | R34 | Inactive | $7.96/linear m ($5.80/sqm) |
| **Roll Specs** |
| Roll Width | ✅ MATCH | R1 | 1370mm | Exact match! |
| Roll Length | ✅ MATCH | R1 | 50m | Exact match! |

---

## Collated Information for Calculator

### From Specification Document:
- ✅ 51-tier square metre pricing model
- ✅ Roll dimensions: 1370mm × 50m (matches R1 stock)
- ✅ Linear metre calculation formulas
- ✅ 10% wastage factor
- ✅ Per-roll setup fee: $15
- ✅ Laminating costs: $15 setup + labour
- ✅ Cutting costs: 5 min/linear metre
- ✅ Kiss-cut surcharge: $15/linear metre
- ✅ Minimum order: $45 + $10 handling

### From Stock Database:
- ✅ Actual vinyl material: R1 (monomeric, permanent, 1370mm × 50m)
- ✅ Base cost: $9/linear metre or $6.57/sqm
- ✅ Stock markup: 30%
- ⚠️ Laminate: R34 exists but inactive ($7.96/linear m)
- ❌ No polymeric vinyl stock (use multiplier)
- ❌ No removable adhesive on roll (use multiplier)
- ❌ No gloss laminate (use multiplier)

### From JSON Config:
- ✅ 10 input fields defined
- ✅ Roll constants match stock (1370mm × 50m)
- ✅ Laminating labour rates: $70/hr trade, $90/hr non-trade
- ✅ Cutting rates: 5 min/linear metre
- ✅ All pricing constants defined
- ⚠️ Square metre rates need updating with actual stock costs
- ⚠️ Need to add material/adhesive/laminate multipliers

---

## Next Steps

1. **Update JSON config** with actual stock costs and multipliers
2. **Implement calculator logic** in CustomVinylStickers_Shopify_Calculator.py:
   - Replace NotImplementedError with full calculation
   - Use R1 stock costs as base
   - Apply material/adhesive/laminate multipliers
   - Implement all formulas from specification
3. **Add stock validation** warnings for unavailable options
4. **Test calculator** with real-world examples
5. **Update stock database:**
   - Activate R34 laminate if available
   - Add polymeric vinyl stock
   - Add removable adhesive vinyl stock
   - Add gloss laminate stock

---

## Cost Calculation Example

**Example: 500 × 75mm Circle stickers, Standard vinyl, Gloss laminate, Kiss-cut**

**Material Cost (R1):**
- Sticker dimensions: 75mm diameter = ~75mm × 75mm square
- Stickers per row: floor(1370 / 75) = 18 stickers/row
- Stickers per linear metre: 18 × floor(1000 / 75) = 18 × 13 = 234 stickers/linear m
- Raw linear metres: 500 / 234 = 2.14 linear m
- With 10% waste: 2.14 × 1.10 = 2.35 linear m
- Material cost: 2.35 × $9.00 = **$21.15**

**Laminate Cost (R34 or estimate):**
- Linear metres: 2.35 linear m
- Laminate cost: 2.35 × $7.96 = **$18.70**

**Roll Setup:**
- Rolls needed: ceil(2.35 / 50) = 1 roll
- Extra roll fee: $15 × (1 - 1) = **$0**

**Laminating Labour:**
- Setup: $15
- Labour: 1 roll × $70/hr (trade) = $70
- Total laminating: **$85.00**

**Cutting Labour:**
- Minutes: 2.35 linear m × 5 min/m = 11.75 minutes
- Labour: 11.75 / 60 × $70/hr = **$13.71**

**Kiss-Cut Surcharge:**
- $15 × 2.35 linear m = **$35.25**

**Subtotal:**
- $21.15 + $18.70 + $0 + $85.00 + $13.71 + $35.25 = **$173.81**

**With Profit Margin (assume 100% for mid-range):**
- $173.81 × 2.0 = **$347.62**

**GST (10%):**
- $347.62 × 1.1 = **$382.38**

**Final Price: $382.38** (above $45 minimum, so no handling fee)

---

## Conclusion

**Calculator Status:**
- ✅ Specification complete (869 lines)
- ✅ JSON config created (needs cost updates)
- ✅ Tool schema registered (Calculator #27)
- ⏳ Python implementation pending (NotImplementedError)
- ✅ Stock analysis complete (19 items found)
- ✅ Cost basis identified (R1 vinyl $9/linear m)
- ⚠️ Some material options not in stock (use multipliers)

**Ready to proceed with:**
1. Updating JSON with actual costs and multipliers
2. Implementing full calculator logic in Python
3. Testing with real-world examples
