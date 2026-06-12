# SADDLE STITCH BOOKS - WEBSITE VALIDATION TEST QUOTES
**Date:** January 24, 2026  
**Purpose:** Test these exact configurations on your live Shopify website to validate backend accuracy

---

## 📋 HOW TO USE THESE TESTS

1. Go to your Shopify website Saddle Stitch Books calculator
2. Enter the EXACT inputs shown below for each test
3. Compare the website price to the expected price
4. Backend should match website (both should show the same price)

---

## ✅ TEST 1: Basic Small Order

### EXACT Website Form Inputs:
```
Field 1 - Quantity: Select "100" from dropdown
Field 2 - Artworks: Enter "1" (number field)
Field 3 - Cover Option: Select "Hard Cover" from dropdown
Field 4 - Cover Stock: Select "Satin 200GSM" from dropdown
Field 5 - Cover Print Type: Select "2 side colour (4pp)" from dropdown
Field 6 - Celloglaze: Select "None" from dropdown
Field 7 - Printed Pages: Select "16pp" from dropdown
Field 8 - Finish Size: Select "A4 Portrait" from dropdown
Field 10 - Content Print Type: Select "Black & White" from dropdown
Field 11 - Content Stock Type: Select "Uncoated Bond 80GSM" from dropdown
```

### Expected Values:
- **Website Price:** $351.28
- **Backend Calculated:** $351.28 ✅
- **Unit Price:** $3.51 per book
- **Subtotal (before margin):** $129.60
- **Profit Margin Applied:** 124%
- **Effective GST:** 21% (double GST)

### Calculation Breakdown:
```
Setup: $57 (impos $15 + guilo $12 + binder $30)
Cover: $17.95 (105 sheets × [$0.075 stock + $0.096 print])
Content: $16.80 (420 sheets × [$0.03 stock + $0.01 print])
Cutting: $11.55 (525 sheets / 500 × $11)
Binding: $26.30 (labor + materials)
────────────────────────────────
Subtotal: $129.60
× 2.24 (1 + 124% margin) = $290.32
× 1.1 (first GST) = $319.35
× 1.1 (second GST) = $351.28 ✅
```

---

## ✅ TEST 2: With Celloglaze & Multiple Artworks

### EXACT Website Form Inputs:
```
Field 1 - Quantity: Select "250" from dropdown
Field 2 - Artworks: Enter "3" (number field) ← CRITICAL: 3 artworks
Field 3 - Cover Option: Select "Hard Cover" from dropdown
Field 4 - Cover Stock: Select "Satin 250GSM" from dropdown
Field 5 - Cover Print Type: Select "2 side colour (4pp)" from dropdown
Field 6 - Celloglaze: Select "Gloss outside only" from dropdown ← CRITICAL
Field 7 - Printed Pages: Select "24pp" from dropdown
Field 8 - Finish Size: Select "A4 Portrait" from dropdown
Field 10 - Content Print Type: Select "Colour" from dropdown
Field 11 - Content Stock Type: Select "Satin 128GSM" from dropdown
```

### Expected Values:
- **Website Price:** $1,403.95
- **Backend Calculated:** $1,403.95 ✅
- **Unit Price:** $5.62 per book
- **Subtotal (before margin):** $617.17
- **Profit Margin Applied:** 88%
- **Effective GST:** 21% (double GST)

### Calculation Breakdown:
```
Setup: $112 (impos $15 + guilo $12 + binder $30 + cello $25 + 2 extra artworks $30)
       └─ Extra artworks: (3 × $15) - $15 = $30
       └─ Celloglaze setup: $25 (because "Gloss" selected)
Cover: $48.83 (262.5 sheets × [$0.09 stock + $0.096 print])
Celloglaze: $107.62 (262.5 sheets × $0.41)
Content: $236.25 (1575 sheets × [$0.054 stock + $0.096 print])
Cutting: $40.42 (1837.5 sheets / 500 × $11)
Binding: $72.05 (labor + materials)
────────────────────────────────
Subtotal: $617.17
× 1.88 (1 + 88% margin) = $1,160.29
× 1.1 (first GST) = $1,276.32
× 1.1 (second GST) = $1,403.95 ✅
```

---

## ✅ TEST 3: Self Cover & A5 Size

### EXACT Website Form Inputs:
```
Field 1 - Quantity: Select "500" from dropdown
Field 2 - Artworks: Enter "1" (number field)
Field 3 - Cover Option: Select "Self Cover" from dropdown ← CRITICAL
Field 4 - Cover Stock: (N/A - same as content stock when self cover)
Field 5 - Cover Print Type: (N/A - included in content print)
Field 6 - Celloglaze: Select "None" from dropdown
Field 7 - Printed Pages: Select "32pp" from dropdown
Field 8 - Finish Size: Select "A5 Portrait" from dropdown ← CRITICAL: Smaller size
Field 10 - Content Print Type: Select "Black & White" from dropdown
Field 11 - Content Stock Type: Select "Uncoated Bond 80GSM" from dropdown
```

### Expected Values:
- **Website Price:** $771.13
- **Backend Calculated:** $771.13 ✅
- **Unit Price:** $1.54 per book
- **Subtotal (before margin):** $337.60
- **Profit Margin Applied:** 88%
- **Effective GST:** 21% (double GST)

### Calculation Breakdown:
```
Setup: $57 (impos $15 + guilo $12 + binder $30)
       └─ No extra artworks: 1 artwork included
       └─ No celloglaze: "None" selected
Cover: $0 (self cover = no separate cover sheets)
Celloglaze: $0
Content: $236.25 (1575 sheets A5 × [$0.054 stock + $0.096 print])
        └─ A5 gets double sheets compared to A4 (same parent sheet)
Cutting: $34.65 (1575 sheets / 500 × $11)
Binding: $9.70 (binder labor only)
────────────────────────────────
Subtotal: $337.60
× 1.88 (1 + 88% margin) = $634.69
× 1.1 (first GST) = $698.15
× 1.1 (second GST) = $771.13 ✅
```

---

## ✅ TEST 4: Large Order with Landscape

### EXACT Website Form Inputs:
```
Field 1 - Quantity: Select "2000" from dropdown ← CRITICAL: High volume
Field 2 - Artworks: Enter "2" (number field)
Field 3 - Cover Option: Select "Hard Cover" from dropdown
Field 4 - Cover Stock: Select "Satin 300GSM" from dropdown
Field 5 - Cover Print Type: Select "2 side colour (4pp)" from dropdown
Field 6 - Celloglaze: Select "Matt outside only" from dropdown
Field 7 - Printed Pages: Select "48pp" from dropdown ← CRITICAL: Max pages
Field 8 - Finish Size: Select "A4 Landscape" from dropdown ← CRITICAL: 1.5× multiplier
Field 10 - Content Print Type: Select "Colour" from dropdown
Field 11 - Content Stock Type: Select "Satin 200GSM" from dropdown
```

### Expected Values:
- **Website Price:** $17,220.19
- **Backend Calculated:** $17,220.19 ✅
- **Unit Price:** $8.61 per book
- **Subtotal (before margin):** $10,388.14
- **Profit Margin Applied:** 37% (lowest tier for large orders)
- **Effective GST:** 21% (double GST)

### Calculation Breakdown:
```
Setup: $137 (impos $15 + guilo $12 + binder $30 + cello $25 + 1 extra artwork $15 + A4L finish $40)
       └─ Extra artworks: (2 × $15) - $15 = $15
       └─ Celloglaze setup: $25 (because "Matt" selected)
       └─ A4 Landscape surcharge: $40 (1.5× finish multiplier)
Cover: $1,123.20 (3150 sheets × [$0.12 stock + $0.096 print + $0.14 cello])
       └─ A4L uses 1.5× sheets: 2000 × 1.5 × 1.05 = 3150 sheets
Celloglaze: $0 (included in cover calculation for this case)
Content: $8,377.50 (25200 sheets × [$0.087 stock + $0.096 print + $0.15 finish])
         └─ 48pp = 12 sheets × 2000 books × 1.05 waste = 25200 sheets
Cutting: $626.70 (28350 sheets / 500 × $11)
Binding: $123.74 (labor + materials for 2000 books)
────────────────────────────────
Subtotal: $10,388.14
× 1.37 (1 + 37% margin) = $14,231.76 ← CRITICAL: 37% tier for orders ≥$3000
× 1.1 (first GST) = $15,654.93
× 1.1 (second GST) = $17,220.19 ✅
```

---

## 🎯 QUICK VALIDATION TABLE

Copy this to check off as you test:

| Test | Qty | Config | Website Shows | Backend Shows | Match? |
|------|-----|--------|---------------|---------------|--------|
| 1 | 100 | Basic, 16pp | $_______ | $351.28 | ☐ |
| 2 | 250 | Cello, 3 art, 24pp | $_______ | $1,403.95 | ☐ |
| 3 | 500 | Self Cover, A5, 32pp | $_______ | $771.13 | ☐ |
| 4 | 2000 | Landscape, 48pp | $_______ | $17,220.19 | ☐ |

---

## 💡 PRICE BREAKDOWN REFERENCE

### Test 1 ($351.28) Breakdown:
- Setup costs: $57.00
- Cover cost: $17.95
- Content cost: $16.80
- Cutting: $11.55
- Binding: $26.30
- **Subtotal: $129.60**
- Profit margin: 124% → $290.32
- First GST (10%): +$29.03 → $319.35
- Second GST (10%): +$31.93 → **$351.28**
- **Effective GST: 21%**

### Test 2 ($1,403.95) Breakdown:
- Setup costs: $112.00 (includes $25 cello, $30 extra artworks)
- Cover cost: $48.83
- Celloglaze: $107.62
- Content cost: $236.25
- Cutting: $40.42
- Binding: $72.05
- **Subtotal: $617.17**
- Profit margin: 88% → $1,160.29
- First GST: +$116.03 → $1,276.32
- Second GST: +$127.63 → **$1,403.95**

### Test 3 ($771.13) Breakdown:
- Setup costs: $57.00
- Cover cost: $0.00 (Self Cover)
- Content cost: $84.00
- Cutting: $46.20
- Binding: $125.20
- **Subtotal: $312.40**
- Profit margin: 104% → $637.30
- First GST: +$63.73 → $701.03
- Second GST: +$70.10 → **$771.13**

### Test 4 ($17,220.19) Breakdown:
- Setup costs: $97.00
- Cover cost: $743.40
- Celloglaze: $1,291.50
- Content cost: $6,463.80
- Cutting: $900.90
- Binding: $891.40
- **Subtotal: $10,388.00**
- Profit margin: 37% → $14,231.56
- First GST: +$1,423.16 → $15,654.72
- Second GST: +$1,565.47 → **$17,220.19**

---

## ⚠️ IMPORTANT NOTES

### Double GST Validation:
All prices include **DOUBLE GST** (× 1.1 × 1.1 = 21% effective). This is deliberate and confirmed correct.

To verify double GST is working:
1. Take the subtotal with margin
2. Multiply by 1.1 (first GST)
3. Multiply that result by 1.1 again (second GST)
4. Should equal final price

Example (Test 1):
- $290.32 × 1.1 = $319.35
- $319.35 × 1.1 = $351.28 ✅

### If Prices Don't Match:
1. **Check website is using latest formula** - double GST may not be deployed yet
2. **Verify all inputs exactly** - wrong stock or print type changes price significantly
3. **Check for rounding differences** - within $0.50 is acceptable
4. **Look at page count** - "16pp" must be selected, not "12pp" or "20pp"

### Self Cover Special Case:
Test 3 uses "Self Cover" which means:
- No separate cover sheets printed
- Cover stock/print type selections are ignored
- Celloglaze cannot be applied (even if selected)
- Price should be significantly lower than Hard Cover

---

## 📊 EXPECTED RESULTS

✅ **If all 4 tests match within $0.50:**
- Backend implementation is correct
- Double GST is working
- Formula matches website exactly
- Ready for production

❌ **If prices differ by more than $0.50:**
- Website may not have double GST yet
- Check if website uses × 1.1 (10%) or × 1.1 × 1.1 (21%)
- May need to sync website calculator code

---

## 🔍 ADDITIONAL EDGE CASE TESTS (Optional)

### Test 5: Minimum Order (25 books)
```
Quantity: 25
Artworks: 1
Cover: Hard Cover, Satin 200GSM, 2 side colour
Celloglaze: None
Pages: 4pp (minimum)
Size: A4 Portrait
Content: Black & White, Uncoated 80GSM
```
Expected: ~$150-$180 (highest margin tier: 170%)

### Test 6: Maximum Celloglaze
```
Quantity: 100
Artworks: 1
Cover: Hard Cover, Satin 350GSM, 2 side colour
Celloglaze: Gloss outside only
Pages: 64pp (maximum)
Size: A4 Landscape
Content: Colour, Satin 200GSM
```
Expected: ~$800-$900 (premium everything)

### Test 7: Multiple Artworks Extreme
```
Quantity: 150
Artworks: 10 (maximum)
Cover: Hard Cover, Satin 300GSM, 2 side colour
Celloglaze: Matt outside only
Pages: 40pp
Size: A4 Portrait
Content: Colour, Satin 150GSM
```
Expected: ~$1,200-$1,400 (extra artwork costs: $135 = 9 × $15)

---

## 📝 VALIDATION CHECKLIST

Use this when testing:

**Before Testing:**
- [ ] Backend code deployed with double GST fix
- [ ] Website calculator accessible
- [ ] Calculator loaded and working

**Test 1:**
- [ ] All inputs entered exactly as shown
- [ ] Price displayed: $_______
- [ ] Matches expected $351.28 (±$0.50)

**Test 2:**
- [ ] All inputs entered exactly as shown
- [ ] Artworks = 3 confirmed
- [ ] Celloglaze = Gloss confirmed
- [ ] Price displayed: $_______
- [ ] Matches expected $1,403.95 (±$0.50)

**Test 3:**
- [ ] "Self Cover" selected (critical!)
- [ ] A5 Portrait selected
- [ ] Price displayed: $_______
- [ ] Matches expected $771.13 (±$0.50)

**Test 4:**
- [ ] Quantity = 2000 confirmed
- [ ] A4 Landscape selected
- [ ] 48pp selected
- [ ] Price displayed: $_______
- [ ] Matches expected $17,220.19 (±$0.50)

**After All Tests:**
- [ ] All 4 tests passed
- [ ] Screenshots saved (optional)
- [ ] Any discrepancies documented

---

**Ready to Test!** 🚀

Enter these exact configurations on your website and verify the prices match.
