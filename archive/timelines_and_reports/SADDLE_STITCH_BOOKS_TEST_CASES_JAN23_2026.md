# SADDLE STITCH BOOKS - TEST CASES
**Calculator:** Saddle Stitch Books  
**Formula Source:** Lines 3054-3120 in SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt  
**Backend:** SaddleStitchBooks_Shopify_Calculator.py  
**Date:** January 23, 2026

---

## 📋 TXT FORMULA SUMMARY

### Constants:
```
guiloSetup = 12
imposSetup = 15
stockWaste = 1.05
extraArts = 15
cuttingBlk = 500
cutCost = 11
binderSetup = 30
binderPerBook = 0.2
binderyLaborperhour = 60
bindersheetsperhour = 5000
```

### Formula Steps:
1. **Artwork Cost:** `artwork_extra = (artworks × 15) - 15` if artworks > 1, else 0
2. **Celloglaze Setup:** `celloSetup = 25` if celloglaze != 'None', else 0
3. **Total Setup:** `imposSetup + guiloSetup + artwork_extra + celloSetup + binderSetup`
4. **Cover Sheets:** `(qty × finish_multiplier) × 1.05` (or 0 if Self Cover)
5. **Cover Cost:** `(cover_sheets × stock_price) + (cover_sheets × print_price)`
6. **Content Sheets:** `((qty × pages_sheet_count) × 1.05) × finish_multiplier`
7. **Content Cost:** `(content_sheets × stock_price) + (content_sheets × print_price)`
8. **Cutting Cost:** `(total_sheets_printed / 500) × 11`
9. **Celloglaze Cost:** `cover_sheets × cello_price` (if not None)
10. **Binding Cost:** `((total_sheets / 5000) × 60) + (qty × 0.2)`
11. **Subtotal:** Sum of all costs
12. **Profit Margin:** 14-tier system (1.7 to 0.37)
13. **Apply Margin:** `subtotal × (1 + margin)`
14. **First GST:** `× 1.1`
15. **Second GST:** `× 1.1` ❗ **DOUBLE GST = 21% total**

---

## ✅ TEST CASE 1: Basic Small Order

### Inputs:
```python
quantity = "100"
artworks = 1
cover_option = "Hard Cover"
cover_stock = "Satin 200GSM"  # $0.075/sheet
cover_print_type = "2 side colour (4pp)"  # $0.096/sheet
celloglaze = "None"
printed_pages = "16pp"  # price = 4 sheets
finish_size = "A4 Portrait"  # multiplier = 1
content_print_type = "Black & White"  # $0.01/sheet
content_stock_type = "Uncoated Bond 80GSM"  # $0.03/sheet
```

### Manual Calculation:

**Step 1: Artwork**
- `artwork_extra = (1 × 15) - 15 = 0` (first artwork free)

**Step 2: Setup Costs**
- `celloSetup = 0` (None selected)
- `totalSetupCost = 15 + 12 + 0 + 0 + 30 = 57`

**Step 3: Cover Sheets**
- `totalCoverSheetsA3 = (100 × 1) × 1.05 = 105 sheets`

**Step 4: Cover Cost**
- `coverClickCost = 0.096 × 105 = 10.08`
- `totalCoverCost = (105 × 0.075) + 10.08 = 7.875 + 10.08 = 17.955`

**Step 5: Content Sheets**
- `totalContentSheets = ((100 × 4) × 1.05) × 1 = 420 sheets`

**Step 6: Content Cost**
- `contentClickCost = 420 × 0.01 = 4.20`
- `totalContentCost = (420 × 0.03) + 4.20 = 12.60 + 4.20 = 16.80`

**Step 7: Cutting Cost**
- `totalSheetsPrinted = 420 + 105 = 525`
- `cuttingCost = (525 / 500) × 11 = 1.05 × 11 = 11.55`

**Step 8: Celloglaze Cost**
- `celloCost = 0` (None)

**Step 9: Binding Cost**
- `bindRunCost = ((525 / 5000) × 60) + (100 × 0.2)`
- `bindRunCost = (0.105 × 60) + 20 = 6.30 + 20 = 26.30`

**Step 10: Subtotal**
- `subTotal = 57 + 17.955 + 16.80 + 11.55 + 0 + 26.30 = 129.605`

**Step 11: Profit Margin**
- Subtotal = $129.605 (between $100-$199.999)
- Margin = 1.24 (124%)

**Step 12: Apply Margin**
- `subtotal_with_margin = 129.605 × (1 + 1.24) = 129.605 × 2.24 = 290.3152`

**Step 13: First GST**
- `total_after_first_gst = 290.3152 × 1.1 = 319.34672`

**Step 14: Second GST (DOUBLE GST)**
- `total_inc_double_gst = 319.34672 × 1.1 = 351.281392`

**✅ EXPECTED RESULT: $351.28**

---

## ✅ TEST CASE 2: With Celloglaze & Multiple Artworks

### Inputs:
```python
quantity = "250"
artworks = 3
cover_option = "Hard Cover"
cover_stock = "Satin 250GSM"  # $0.09/sheet
cover_print_type = "2 side colour (4pp)"  # $0.096/sheet
celloglaze = "Gloss outside only"  # $0.41/sheet
printed_pages = "24pp"  # price = 6 sheets
finish_size = "A4 Portrait"  # multiplier = 1
content_print_type = "Colour"  # $0.096/sheet
content_stock_type = "Satin 128GSM"  # $0.054/sheet
```

### Manual Calculation:

**Step 1: Artwork**
- `artwork_extra = (3 × 15) - 15 = 45 - 15 = 30`

**Step 2: Setup Costs**
- `celloSetup = 25` (Gloss selected)
- `totalSetupCost = 15 + 12 + 30 + 25 + 30 = 112`

**Step 3: Cover Sheets**
- `totalCoverSheetsA3 = (250 × 1) × 1.05 = 262.5 sheets`

**Step 4: Cover Cost**
- `coverClickCost = 0.096 × 262.5 = 25.20`
- `totalCoverCost = (262.5 × 0.09) + 25.20 = 23.625 + 25.20 = 48.825`

**Step 5: Content Sheets**
- `totalContentSheets = ((250 × 6) × 1.05) × 1 = 1575 sheets`

**Step 6: Content Cost**
- `contentClickCost = 1575 × 0.096 = 151.20`
- `totalContentCost = (1575 × 0.054) + 151.20 = 85.05 + 151.20 = 236.25`

**Step 7: Cutting Cost**
- `totalSheetsPrinted = 1575 + 262.5 = 1837.5`
- `cuttingCost = (1837.5 / 500) × 11 = 3.675 × 11 = 40.425`

**Step 8: Celloglaze Cost**
- `celloCost = 262.5 × 0.41 = 107.625`

**Step 9: Binding Cost**
- `bindRunCost = ((1837.5 / 5000) × 60) + (250 × 0.2)`
- `bindRunCost = (0.3675 × 60) + 50 = 22.05 + 50 = 72.05`

**Step 10: Subtotal**
- `subTotal = 112 + 48.825 + 236.25 + 40.425 + 107.625 + 72.05 = 617.175`

**Step 11: Profit Margin**
- Subtotal = $617.175 (between $500-$749.999)
- Margin = 0.88 (88%)

**Step 12: Apply Margin**
- `subtotal_with_margin = 617.175 × (1 + 0.88) = 617.175 × 1.88 = 1160.289`

**Step 13: First GST**
- `total_after_first_gst = 1160.289 × 1.1 = 1276.3179`

**Step 14: Second GST (DOUBLE GST)**
- `total_inc_double_gst = 1276.3179 × 1.1 = 1403.94969`

**✅ EXPECTED RESULT: $1403.95**

---

## ✅ TEST CASE 3: Self Cover (No Separate Cover)

### Inputs:
```python
quantity = "500"
artworks = 1
cover_option = "Self Cover"  # ❗ No separate cover
cover_stock = "Satin 200GSM"  # (ignored)
cover_print_type = "2 side colour (4pp)"  # (ignored)
celloglaze = "None"
printed_pages = "32pp"  # price = 8 sheets
finish_size = "A5 Portrait"  # multiplier = 0.5
content_print_type = "Black & White"  # $0.01/sheet
content_stock_type = "Uncoated Bond 80GSM"  # $0.03/sheet
```

### Manual Calculation:

**Step 1: Artwork**
- `artwork_extra = 0`

**Step 2: Setup Costs**
- `celloSetup = 0`
- `totalSetupCost = 15 + 12 + 0 + 0 + 30 = 57`

**Step 3: Cover Sheets**
- `totalCoverSheetsA3 = 0` (Self Cover)

**Step 4: Cover Cost**
- `totalCoverCost = 0`

**Step 5: Content Sheets**
- `totalContentSheets = ((500 × 8) × 1.05) × 0.5 = 2100 sheets`

**Step 6: Content Cost**
- `contentClickCost = 2100 × 0.01 = 21.00`
- `totalContentCost = (2100 × 0.03) + 21.00 = 63.00 + 21.00 = 84.00`

**Step 7: Cutting Cost**
- `totalSheetsPrinted = 2100 + 0 = 2100`
- `cuttingCost = (2100 / 500) × 11 = 4.2 × 11 = 46.20`

**Step 8: Celloglaze Cost**
- `celloCost = 0`

**Step 9: Binding Cost**
- `bindRunCost = ((2100 / 5000) × 60) + (500 × 0.2)`
- `bindRunCost = (0.42 × 60) + 100 = 25.20 + 100 = 125.20`

**Step 10: Subtotal**
- `subTotal = 57 + 0 + 84.00 + 46.20 + 0 + 125.20 = 312.40`

**Step 11: Profit Margin**
- Subtotal = $312.40 (between $300-$499.999)
- Margin = 1.04 (104%)

**Step 12: Apply Margin**
- `subtotal_with_margin = 312.40 × (1 + 1.04) = 312.40 × 2.04 = 637.296`

**Step 13: First GST**
- `total_after_first_gst = 637.296 × 1.1 = 701.0256`

**Step 14: Second GST (DOUBLE GST)**
- `total_inc_double_gst = 701.0256 × 1.1 = 771.12816`

**✅ EXPECTED RESULT: $771.13**

---

## ✅ TEST CASE 4: Large Order (High Volume, Low Margin)

### Inputs:
```python
quantity = "2000"
artworks = 2
cover_option = "Hard Cover"
cover_stock = "Satin 300GSM"  # $0.14/sheet
cover_print_type = "2 side colour (4pp)"  # $0.096/sheet
celloglaze = "Matt outside only"  # $0.41/sheet
printed_pages = "48pp"  # price = 12 sheets
finish_size = "A4 Landscape"  # multiplier = 1.5
content_print_type = "Colour"  # $0.096/sheet
content_stock_type = "Satin 200GSM"  # $0.075/sheet
```

### Manual Calculation:

**Step 1: Artwork**
- `artwork_extra = (2 × 15) - 15 = 15`

**Step 2: Setup Costs**
- `celloSetup = 25`
- `totalSetupCost = 15 + 12 + 15 + 25 + 30 = 97`

**Step 3: Cover Sheets**
- `totalCoverSheetsA3 = (2000 × 1.5) × 1.05 = 3150 sheets`

**Step 4: Cover Cost**
- `coverClickCost = 0.096 × 3150 = 302.40`
- `totalCoverCost = (3150 × 0.14) + 302.40 = 441.00 + 302.40 = 743.40`

**Step 5: Content Sheets**
- `totalContentSheets = ((2000 × 12) × 1.05) × 1.5 = 37,800 sheets`

**Step 6: Content Cost**
- `contentClickCost = 37800 × 0.096 = 3628.80`
- `totalContentCost = (37800 × 0.075) + 3628.80 = 2835.00 + 3628.80 = 6463.80`

**Step 7: Cutting Cost**
- `totalSheetsPrinted = 37800 + 3150 = 40950`
- `cuttingCost = (40950 / 500) × 11 = 81.9 × 11 = 900.90`

**Step 8: Celloglaze Cost**
- `celloCost = 3150 × 0.41 = 1291.50`

**Step 9: Binding Cost**
- `bindRunCost = ((40950 / 5000) × 60) + (2000 × 0.2)`
- `bindRunCost = (8.19 × 60) + 400 = 491.40 + 400 = 891.40`

**Step 10: Subtotal**
- `subTotal = 97 + 743.40 + 6463.80 + 900.90 + 1291.50 + 891.40 = 10,388.00`

**Step 11: Profit Margin**
- Subtotal = $10,388.00 (≥ $3,000)
- Margin = 0.37 (37%) ⚠️ **CORRECTION: $3,000+ tier, not $10,001+ tier**

**Step 12: Apply Margin**
- `subtotal_with_margin = 10388.00 × (1 + 0.37) = 10388.00 × 1.37 = 14,231.56`

**Step 13: First GST**
- `total_after_first_gst = 14,231.56 × 1.1 = 15,654.716`

**Step 14: Second GST (DOUBLE GST)**
- `total_inc_double_gst = 15,654.716 × 1.1 = 17,220.1876`

**✅ EXPECTED RESULT: $17,220.19** (CORRECTED)

---

## 📊 TEST SUMMARY

| Test | Qty | Pages | Cover | Cello | Artworks | Expected Price | Notes |
|------|-----|-------|-------|-------|----------|----------------|-------|
| 1 | 100 | 16pp | Hard, Satin 200 | None | 1 | **$351.28** | Basic order, 124% margin |
| 2 | 250 | 24pp | Hard, Satin 250 | Gloss | 3 | **$1,403.95** | With celloglaze, 88% margin |
| 3 | 500 | 32pp | Self Cover | None | 1 | **$771.13** | Self cover = no separate cover sheets |
| 4 | 2000 | 48pp | Hard, Satin 300 | Matt | 2 | **$17,220.19** | Large order, 37% margin, A4 Landscape |

---

## 🎯 VALIDATION CHECKLIST

- [ ] Test 1: Backend returns $351.28 (±$0.02)
- [ ] Test 2: Backend returns $1,403.95 (±$0.02)
- [ ] Test 3: Backend returns $771.13 (±$0.02)
- [ ] Test 4: Backend returns $17,848.66 (±$0.02)
- [ ] Breakdown shows: first_gst_10pct, second_gst_10pct, effective_gst_rate = 21%
- [ ] Unit prices calculated correctly
- [ ] Self Cover test shows 0 cover sheets

---

## 🔍 KEY VALIDATION POINTS

1. **Double GST:** All tests MUST show 21% effective GST (1.1 × 1.1)
2. **Self Cover:** Test 3 should have 0 cover sheets
3. **Profit Margins:** Different tiers applied based on subtotal
4. **Celloglaze Setup:** $25 added only when celloglaze selected
5. **Artwork Cost:** First free, $15 each additional
6. **Cutting Cost:** Based on total_sheets_printed, not quantity
7. **Finish Multiplier:** A5=0.5, A4=1.0, A4 Landscape=1.5

---

**Next Step:** Run these test cases against the fixed backend to validate implementation.
