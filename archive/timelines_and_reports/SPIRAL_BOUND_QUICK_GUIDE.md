# Spiral Bound Books - Quick Validation Guide

## Backend Test Results

| Test | Price | Status |
|------|-------|--------|
| 1. 100 books, A5, 40pp, B&W | **$507.30** | ⏳ Test on website |
| 2. 500 books, A4, 100pp, Color | **$3,425.73** | ⏳ Test on website |
| 3. 1000 books, A4, 200pp, B&W | **$8,125.50** | ⏳ Test on website |
| 4. 250 books, A6, 50pp, B&W | **$978.21** | ⏳ Test on website |
| 5. 100 books, A4, 60pp, Premium | **$1,021.85** | ⏳ Test on website |

---

## Critical Validation Points

- ✅ **15% GST** (not 10% like other calculators)
- ✅ **Fixed $44 surcharge** added after GST
- ✅ **A6/DL/A5 Landscape** wire price halved (Test 4)
- ✅ **Celloglaze setup $25** when either front OR back selected (Test 5)
- ✅ **18-tier wire pricing** based on book thickness
- ✅ **12-tier profit margins** (90% down to 41%)

---

## Test 1: Basic Spiral Bound
```
Qty: 100 | Content: 40pp, Bond 80GSM, B&W | Size: A5
Front: 300GSM Satin, 1pp Color | Back: None | Cello: None
→ $507.30
```

## Test 2: Medium Color
```
Qty: 500 | Content: 100pp, Satin 128GSM, Full Color | Size: A4
Front: 350GSM Satin, 2pp Color | Back: 350GSM Blank | Cello: None
→ $3,425.73
```

## Test 3: Large Thick Book
```
Qty: 1000 | Content: 200pp, Bond 80GSM, B&W | Size: A4
Front: 350GSM Satin, 1pp Color | Back: Black Leather | Cello: None | Arts: 2
→ $8,125.50
```

## Test 4: Small Format (A6)
```
Qty: 250 | Content: 50pp, Bond 90GSM, B&W | Size: A6 Portrait
Front: 250GSM Satin, 1pp Color | Back: None | Cello: None
→ $978.21 (wire cost HALVED)
```

## Test 5: Premium Celloglaze
```
Qty: 100 | Content: 60pp, Satin 150GSM, Full Color | Size: A4
Front: 350GSM + PVC, 2pp Color, 2-Side Matt | Back: 350GSM + PVC, 1pp Color, 1-Side Gloss
→ $1,021.85 (cello setup $25 once)
```

---

## Website Testing

**URL:** https://gerardovsa.myshopify.com/products/spiral-bound-books

**Quick Check:**
1. Enter configuration from test
2. Verify price matches backend
3. Check for 15% GST + $44 surcharge pattern
4. Document any discrepancies

**Expected Success:** All 5 tests should match within $1-2 (rounding)
