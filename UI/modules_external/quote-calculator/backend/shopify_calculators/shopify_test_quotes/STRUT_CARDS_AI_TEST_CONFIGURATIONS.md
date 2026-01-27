# Strut Cards Calculator - Test Configurations

## Calculator Name
**strut_cards**

## AI Instructions for Testing

To get a quote for Strut Cards:

```
Please calculate a quote for Strut Cards with these specifications:
[paste specifications from tests below]
```

All prices listed below include GST and are actual website results.

---

# Strut Cards - Actual Website Test Configurations

## STRUT CARDS A3

### TEST 1: Small Quantity A3

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A3 (297mm × 420mm)
- Quantity: 5
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $96.80**

---

### TEST 2: Minimum Order A3

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A3 (297mm × 420mm)
- Quantity: 2
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $86.90**

---

### TEST 3: Medium Quantity A3

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A3 (297mm × 420mm)
- Quantity: 100
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $931.70**

---

### TEST 4: Multiple Artworks A3

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A3 (297mm × 420mm)
- Quantity: 50
- Artworks: 5
- Stock: 2mm Screenboard

**Regular price: $665.50**

---

### TEST 5: Large Quantity A3

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A3 (297mm × 420mm)
- Quantity: 1000
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $6,558.20**

---

## STRUT CARDS A4

### TEST 6: Small Quantity A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A4 (210mm × 297mm)
- Quantity: 10
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $108.90**

---

### TEST 7: Minimum Order A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A4 (210mm × 297mm)
- Quantity: 5
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $86.90**

---

### TEST 8: Medium Quantity A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A4 (210mm × 297mm)
- Quantity: 100
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $586.85**

---

### TEST 9: Multiple Artworks A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A4 (210mm × 297mm)
- Quantity: 50
- Artworks: 3
- Stock: 2mm Screenboard

**Regular price: $393.25**

---

### TEST 10: Large Quantity A4

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A4 (210mm × 297mm)
- Quantity: 1500
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $6,733.65**

---

## STRUT CARDS A5

### TEST 11: Minimum Order A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A5 (148mm × 210mm)
- Quantity: 15
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $94.80**

---

### TEST 12: Small Quantity A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A5 (148mm × 210mm)
- Quantity: 25
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $145.20**

---

### TEST 13: Medium Quantity A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A5 (148mm × 210mm)
- Quantity: 100
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $451.44**

---

### TEST 14: Multiple Artworks A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A5 (148mm × 210mm)
- Quantity: 50
- Artworks: 4
- Stock: 2mm Screenboard

**Regular price: $293.70**

---

### TEST 15: Large Quantity A5

**ACTUAL WEBSITE PARAMETERS AND RESULT (inc GST)**

**Basics**
- Size: A5 (148mm × 210mm)
- Quantity: 1000
- Artworks: 1
- Stock: 2mm Screenboard

**Regular price: $3,762.00**

---

## Technical Notes (Internal Reference)

### Business Rules:
- **Stock:** All tests use 2mm Screenboard (fixed option)
- **Sizes:** Fixed per product variant
  - A3: 297mm × 420mm
  - A4: 210mm × 297mm
  - A5: 148mm × 210mm
- **Artwork Pricing:** First artwork included ($5 base), then $5 per additional artwork
- **Minimum Order:** $79 minimum applies before markups
- **Markup Structure:**
  - A3/A4: ×1.1 ×1.1 (double markup)
  - A5: ×1.1 ×1.2 (asymmetric markup)
- **GST:** 10% applied to final price

### Validation Status:
- **Total Tests:** 15 (5 per size)
- **Accuracy:** 100% website validated
- **Date Validated:** January 26, 2026
- **Test Coverage:**
  - Minimum order scenarios (Tests 2, 7, 11)
  - Small quantities (Tests 1, 6, 12)
  - Medium quantities (Tests 3, 8, 13)
  - Multiple artworks (Tests 4, 9, 14)
  - Large quantities (Tests 5, 10, 15)
