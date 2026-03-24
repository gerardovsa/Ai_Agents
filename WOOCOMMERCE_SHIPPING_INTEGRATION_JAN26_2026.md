# WooCommerce Shipping Column Integration - Complete Implementation
**Date:** January 26, 2026
**Feature:** Australia Post shipping calculation integrated into WooCommerce orders UI

---

## Overview

Integrated the Australia Post shipping module directly into the WooCommerce orders table as a new "Shipping" column that displays:
- **Box type**: small/large based on product thickness
- **Total weight**: in grams
- **Postage cost**: in AUD ($)

All calculations happen automatically when orders are loaded, with async API calls per row.

---

## Architecture

```
WooCommerce UI (woocommerce.js)
    ↓
    Tabulator column formatter calls calculateShipping()
    ↓
    Flask API: /api/auspost/calculate-order-shipping
    ↓
    auspost_routes.py extracts SKUs → maps to product codes
    ↓
    auspost-shipping backend:
        - OrderParser: validates product codes
        - BoxCalculator: determines box size/weight
        - AusPostClient: calls Australia Post PAC API
    ↓
    Returns: {box_type, weight_grams, postage_cost}
    ↓
    UI updates cell with formatted result
```

---

## Files Modified

### 1. **Flask Backend - New Route**
**File:** `AI_infrastructure/routes/auspost_routes.py` (NEW)
- **Lines:** 183 lines
- **Endpoints:**
  - `POST /api/auspost/calculate-order-shipping` - Calculate shipping for order
  - `GET /api/auspost/health` - Health check endpoint

**Key Functions:**
- SKU mapping: CFS, MVG, MVGEQ, MVGEM → product codes
- Domestic vs international detection (country code)
- Box calculation using BoxCalculator
- API call to Australia Post PAC API
- Error handling with detailed messages

### 2. **Flask App - Route Registration**
**File:** `AI_infrastructure/flask_app.py`
- **Line 195:** Import auspost_routes
- **Line 507:** Register auspost_bp blueprint

### 3. **WooCommerce UI - Shipping Column**
**File:** `UI/modules_internal/woocommerce/woocommerce.js`
- **Lines 118-196:** Added 3 helper functions:
  - `calculateShipping(order)` - Async API call to calculate shipping
  - `extractPostcode(address)` - Extract 4-digit Australian postcode
  - `extractState(address)` - Extract state code (NSW, VIC, etc.)

- **Lines 370-415:** New Tabulator column definition:
  - **Title:** "Shipping"
  - **Width:** 220px
  - **Position:** After "Print Label" column
  - **Formatter:** Shows loading spinner → calculates → displays result
  - **Caching:** Results cached in `row._shippingData` to avoid recalculation

---

## Column Display Format

### Success State:
```
📦 Box: small
⚖️ Wt: 595g
💰 $10.50
```

### Loading State:
```
🔄 Calculating...
```

### Error State:
```
❌ No postcode
❌ Calc Error
❌ Network Error
```

---

## API Request/Response

### Request to Flask:
```json
POST /api/auspost/calculate-order-shipping
{
  "line_items": [
    {"sku": "CFS", "quantity": 10, "name": "Cards Full Size"},
    {"sku": "MVG", "quantity": 5, "name": "Magnets Vinyl Gloss"}
  ],
  "shipping_address": {
    "postcode": "2000",
    "state": "NSW",
    "country": "AU"
  }
}
```

### Response from Flask:
```json
{
  "success": true,
  "box_type": "small",
  "box_count": 1,
  "weight_grams": 595,
  "postage_cost": 10.50,
  "service": "Parcel Post"
}
```

---

## Product Code Mapping

| SKU Pattern | Product Code | Weight | Thickness |
|-------------|--------------|--------|-----------|
| Contains "CFS" | CFS | 220g | 20mm |
| Contains "MVGEM" | MVGEM | 370g | 35mm |
| Contains "MVGEQ" | MVGEQ | 220g | 20mm |
| Contains "MVG" | MVG | 325g | 30mm |

**Note:** Order matters - MVGEM/MVGEQ must be checked before MVG to avoid incorrect matches.

---

## Box Selection Logic

```javascript
// From BoxCalculator backend
if (total_thickness <= 60mm) {
    box = "small" (50g box, max 60mm)
} else if (total_thickness <= 85mm) {
    box = "large" (60g box, max 85mm)
} else {
    box = "custom" (manual handling required)
}

total_weight = product_weight + box_weight
```

---

## Error Handling

### Backend Errors:
- **No line items:** Returns 400 error with message
- **No recognized products:** SKU doesn't match CFS/MVG/MVGEQ/MVGEM
- **Box calculation fails:** Thickness exceeds 85mm (custom required)
- **No postcode:** Missing shipping address data
- **API failure:** Australia Post API unreachable or rate limited

### Frontend Errors:
- **Network Error:** Fetch failed or timeout
- **API Error:** Non-200 response from Flask
- **No postcode:** Can't extract from shipping address
- **Calc Error:** Generic fallback for any error

---

## Performance Optimizations

1. **Caching:** Results stored in `row._shippingData` to avoid recalculation on table refresh
2. **Async Loading:** Spinner shown immediately, calculation happens in background
3. **Batch Prevention:** Each row calculates independently (no batch API to avoid rate limits)
4. **Error Recovery:** Failed calculations don't block other rows

---

## Testing Checklist

- [ ] Test with CFS products (small box expected)
- [ ] Test with MVG products (small/large box depending on quantity)
- [ ] Test with MVGEM products (large box expected)
- [ ] Test with mixed products (box calculator logic)
- [ ] Test with international shipping (country != AU)
- [ ] Test with missing postcode (should show "No postcode")
- [ ] Test with invalid SKU (should show "No recognized products")
- [ ] Test with thick products >85mm (should show custom box error)
- [ ] Test table refresh (should use cached data)
- [ ] Test network failure (should show "Network Error")

---

## Dependencies

### Python Packages (already in requirements.txt):
- `requests` - HTTP client for Australia Post API
- `python-dotenv` - Environment variable loading
- `Flask` - Web framework

### Frontend Libraries (already loaded):
- `Tabulator.js` - Table framework
- `Font Awesome` - Icons (📦 ⚖️ 💰)

### Environment Variables Required:
```bash
AUSPOST_API_KEY=your-api-key-here
```

**Note:** API key must be added to `.env` file for production deployment.

---

## Future Enhancements

1. **Bulk Calculation:** Add button to calculate all visible rows at once
2. **Service Selection:** Allow user to choose Parcel Post vs Express Post
3. **Rate Comparison:** Show multiple service options with prices
4. **Weight Override:** Manual weight adjustment for custom scenarios
5. **Export Integration:** Include shipping costs in CSV/PDF exports
6. **Cost Tracking:** Store shipping costs in database for analytics
7. **Auto-refresh:** Recalculate when order items change
8. **International Rates:** Improve international shipping accuracy

---

## Known Limitations

1. **Postcode Extraction:** Regex-based, may fail with non-standard address formats
2. **State Detection:** Only works for Australian addresses (NSW, VIC, etc.)
3. **No Insurance:** Doesn't include shipping insurance costs
4. **Fixed Origin:** Uses hardcoded "3977" postcode as sender (should be configurable)
5. **Rate Limits:** Australia Post API has rate limits (not currently handled)
6. **No Caching:** API calls made every time (could use Redis for 24h cache)

---

## Configuration

### Change Default Sender Postcode:
**File:** `AI_infrastructure/routes/auspost_routes.py`
**Line 118:**
```python
from_postcode='3977',  # Change this to your warehouse postcode
```

### Change Default Service:
**File:** `AI_infrastructure/routes/auspost_routes.py`
**Line 121:**
```python
service_code='AUS_PARCEL_REGULAR'  # Options: AUS_PARCEL_REGULAR, AUS_PARCEL_EXPRESS
```

---

## Troubleshooting

### Column Not Showing:
- Check Flask logs: `AI_infrastructure/flask_app.log`
- Verify route registered: Should see "auspost_bp" in startup logs
- Check browser console for JavaScript errors

### "Calculating..." Forever:
- Check Flask API is running on correct port
- Verify `/api/auspost/calculate-order-shipping` endpoint returns 200
- Check network tab in browser DevTools for request/response

### "No Recognized Products":
- Verify SKU contains CFS, MVG, MVGEQ, or MVGEM
- Check line_items array has correct structure
- Check SKU mapping logic in auspost_routes.py (lines 75-92)

### "API Error":
- Check AUSPOST_API_KEY in .env file
- Verify Australia Post API is accessible
- Check rate limits not exceeded
- Review Flask logs for detailed error

---

## Deployment Notes

### Local Development:
1. Add `AUSPOST_API_KEY` to `.env`
2. Restart Flask server: `cd AI_infrastructure && python flask_app.py`
3. Refresh WooCommerce page

### Production (Render):
1. Add `AUSPOST_API_KEY` to Render environment variables
2. Push to v11 branch: `git push gerardo v11:v11`
3. Wait for auto-deploy (~2-3 minutes)
4. Verify column appears in production WooCommerce UI

---

## Related Documentation

- **Module README:** `UI/modules_external/auspost-shipping/README.md`
- **Quick Start:** `UI/modules_external/auspost-shipping/QUICK_START.md`
- **API Examples:** `UI/modules_external/auspost-shipping/EXAMPLES.md`
- **Implementation Notes:** `UI/modules_external/auspost-shipping/IMPLEMENTATION_COMPLETE.md`

---

## Commit Message

```
feat(woocommerce): integrate Australia Post shipping column

- Add shipping calculation column to WooCommerce orders table
- Display box type, weight, and postage cost per order
- Create Flask API endpoint /api/auspost/calculate-order-shipping
- Async loading with spinner → formatted result display
- SKU mapping: CFS/MVG/MVGEQ/MVGEM → product codes
- Box calculation: small (≤60mm) or large (≤85mm)
- Error handling: no postcode, network errors, calc failures
- Caching: store results in row data to avoid recalculation

Files:
- AI_infrastructure/routes/auspost_routes.py (NEW - 183 lines)
- AI_infrastructure/flask_app.py (added route registration)
- UI/modules_internal/woocommerce/woocommerce.js (added column + helpers)

Related: auspost-shipping module (UI/modules_external/)
```

---

**Status:** ✅ Complete - Ready for testing
**Next Steps:** Add `AUSPOST_API_KEY` to .env and test with real orders
