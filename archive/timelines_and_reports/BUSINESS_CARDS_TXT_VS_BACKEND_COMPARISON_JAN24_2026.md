# Business Cards - TXT vs Backend Comparison
Date: January 24, 2026
Calculators: `shopify_premium_business_cards` and `shopify_economical_business_cards`
TXT source: `UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt`
Backend: `UI/modules_external/quote-calculator/backend/shopify_calculators/business_card_calculator_shopify.py`

---

## Summary
- I extracted the Premium and Economical Business Cards JSON blocks and the backend implementation.
- The backend implements the DPO logic closely; most constants and formulas match.
- Two items need attention before marking complete:
  1. `King Kong High Bulk` price differs between TXT (300) and backend (250).
  2. TXT notes an apparent "double GST" line in the premium calculator; backend applies GST once. This is ambiguous in TXT (marked as "apparent error").

---

## Quick Matches
- Setup costs (imposition, guillotine, extra artwork) match:
  - Premium: `impos_setup=15`, `guilo_setup=10`, `cello_setup=17`, `extra_arts=15` ✅
  - Economical: `impos_setup=15`, `guilo_setup=12`, `extra_arts=15` ✅
- Production constants match: `stock_waste=1.05`, `cutting_block=500` ✅
- Click rates match TXT:
  - Economical color: 0.044 ✅
  - Premium color: 0.048 ✅
  - B&W: 0.02 ✅
- Card-per-sheet values match: 21 for 90x55, 30 for 90x45 (premium) ✅
- Celloglaze per-sheet rates and setup costs match (premium): 0.16/0.32 and setup 17 ✅
- Profit-margin tier logic implemented and aligns with TXT structure:
  - Economical uses `_calculate_profit_margin_standard` matching TXT tiers ✅
  - Premium uses dual-tier (`_calculate_profit_margin_premium`) matching TXT rules (no_cello vs with_cello) ✅
- Calculation steps (sheets, click, cutting, subtotal, profit, GST) match TXT steps ✅

---

## Discrepancies / Action Items
1. King Kong stock price
   - TXT: `King Kong High Bulk` price = 300 (per 1000)
   - Backend: `STOCK_PRICES_PREMIUM.KINGKONG_420GSM = 250` (marked "Estimated (not in screenshot)")
   - Recommendation: Update backend to use `300` to match TXT exactly (or confirm correct value).

2. Double GST mention in TXT (Premium)
   - TXT `calculation_formula` includes steps 11-13 and notes `Apply final GST multiplication: Total * 1.1 (double GST application)` and `double_gst` in key_differences.
   - Backend applies GST once (total_ex_gst * 1.1) — which is probably correct; TXT flags double-GST as an "apparent error".
   - Recommendation: Do NOT apply double GST unless the website actually charges GST twice. Verify with live website examples; if site shows doubled multiplier we should replicate, otherwise keep single GST.

3. KingKong and EcoStar mapping
   - TXT lists EcoStar 350GSM at 500 — backend matches.
   - KingKong mismatch is the only stock discrepancy.

4. Minor: Backend returns profit_margin_pct as multiplier*100; verify display code expects percentage (this matches existing pattern elsewhere).

---

## Proposed Next Steps (following methodology)
1. Update backend `STOCK_PRICES_PREMIUM.KINGKONG_420GSM` from `250` to `300` to match TXT.
2. Run premium example tests from TXT examples and compare to website; if differences > $0.50, inspect GST behavior and decide whether to implement double GST.
3. If user confirms, apply the KingKong price change and re-run tests.

---

## Files Reviewed
- TXT: `UI/modules_external/quote-calculator/ARCHIVE_CONSOLIDATED/CALCULATOR_JSONS/SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt` (premium block lines ~12918-13360; economical block lines ~13440-13780)
- Backend: `UI/modules_external/quote-calculator/backend/shopify_calculators/business_card_calculator_shopify.py`

---

If you want, I'll implement the King Kong price update now and run the example tests (premium and economical) and validate against the expected ranges in the TXT examples. Otherwise confirm and I'll proceed.