# WooCommerce Shipping Integration - Testing Guide
**Date:** January 26, 2026

---

## Quick Start

### 1. Add Australia Post API Key

```bash
# Add to your .env file (or Render environment variables)
AUSPOST_API_KEY=your-api-key-here
```

**Get API Key:** https://developers.auspost.com.au/

### 2. Restart Flask Server

```powershell
# Stop current server (Ctrl+C)
cd AI_infrastructure
python flask_app.py
```

### 3. Open WooCommerce Orders

Navigate to: `http://localhost:5001` → WooCommerce → Orders

---

## What You Should See

### Before (Old Table):
```
┌────┬──────┬──────┬────────┬──────────┬────────┬───────────┬────────┐
│ ID │ Date │ Time │ Status │ Customer │ Items  │ Print Lab │ Total  │
└────┴──────┴──────┴────────┴──────────┴────────┴───────────┴────────┘
```

### After (New Table with Shipping Column):
```
┌────┬──────┬──────┬────────┬──────────┬────────┬───────────┬──────────┬────────┐
│ ID │ Date │ Time │ Status │ Customer │ Items  │ Print Lab │ Shipping │ Total  │
│    │      │      │        │          │        │           │ 📦 small │        │
│    │      │      │        │          │        │           │ ⚖️ 595g  │        │
│    │      │      │        │          │        │           │ 💰 $10.50│        │
└────┴──────┴──────┴────────┴──────────┴────────┴───────────┴──────────┴────────┘
```

---

## Test Scenarios

### Test 1: Small Box (Single Product Type)
**Order:** 10x CFS (Cards Full Size)
**Expected:**
- Box: small
- Weight: 2200g + 50g = 2250g
- Thickness: 10 × 20mm = 200mm
- **ERROR:** Thickness exceeds 85mm → custom handling

**Correct Order:** 3x CFS
- Box: small
- Weight: 660g + 50g = 710g
- Thickness: 3 × 20mm = 60mm ✅

### Test 2: Large Box (Thick Products)
**Order:** 2x MVGEM (Magnets Vinyl Gloss Extra Magnet)
**Expected:**
- Box: large
- Weight: 740g + 60g = 800g
- Thickness: 2 × 35mm = 70mm ✅

### Test 3: Mixed Products
**Order:** 2x CFS + 1x MVG
**Expected:**
- Box: large
- Weight: (440g + 325g) + 60g = 825g
- Thickness: (40mm + 30mm) = 70mm ✅

### Test 4: International Shipping
**Order:** 1x CFS to USA
**Expected:**
- Box: small
- Weight: 220g + 50g = 270g
- Country: USA
- Service: International Standard
- Cost: ~$25-30 (varies)

### Test 5: Missing Postcode
**Order:** No shipping address or invalid format
**Expected:**
- Display: "❌ No postcode"

### Test 6: Invalid SKU
**Order:** Products with SKUs not matching CFS/MVG/MVGEQ/MVGEM
**Expected:**
- Display: "❌ No recognized products"

---

## Manual Testing Steps

### 1. Check Column Appears
- [ ] Open WooCommerce orders page
- [ ] Verify "Shipping" column exists after "Print Label"
- [ ] Check column width is ~220px

### 2. Check Loading State
- [ ] Refresh page with orders
- [ ] Verify spinner appears: "🔄 Calculating..."
- [ ] Loading should last 1-3 seconds per row

### 3. Check Success State
- [ ] After loading, verify formatted display:
  ```
  📦 Box: small
  ⚖️ Wt: 595g
  💰 $10.50
  ```
- [ ] Check box type is correct (small/large)
- [ ] Check weight calculation includes box weight
- [ ] Check postage cost is realistic ($8-15 domestic)

### 4. Check Error States
- [ ] Order with no postcode → "❌ No postcode"
- [ ] Order with invalid SKU → "❌ No recognized products"
- [ ] Network failure → "❌ Network Error"
- [ ] API failure → "❌ API Error"

### 5. Check Caching
- [ ] Sort table by different columns
- [ ] Verify shipping data persists (no recalculation)
- [ ] Filter orders by status
- [ ] Verify shipping data still cached

### 6. Check Multiple Orders
- [ ] Load page with 10+ orders
- [ ] Verify all rows calculate independently
- [ ] Check console for errors (F12 → Console tab)
- [ ] Verify no rate limit errors from API

---

## Browser Console Testing

### Check API Requests
```javascript
// Open DevTools (F12) → Network tab
// Filter: /api/auspost/calculate-order-shipping
// Should see POST requests for each order row
```

### Check Response Data
```javascript
// Click on a request in Network tab
// Preview/Response should show:
{
  "success": true,
  "box_type": "small",
  "box_count": 1,
  "weight_grams": 595,
  "postage_cost": 10.50,
  "service": "Parcel Post"
}
```

### Check Cached Data
```javascript
// In Console tab, run:
window.wooOrdersTable.getData()[0]._shippingData
// Should show cached shipping result
```

---

## Flask API Testing

### Test Endpoint Directly

```bash
# Test health check
curl http://localhost:5001/api/auspost/health
```

**Expected Response:**
```json
{
  "success": true,
  "module": "auspost-shipping",
  "status": "available"
}
```

### Test Calculate Endpoint

```bash
curl -X POST http://localhost:5001/api/auspost/calculate-order-shipping \
  -H "Content-Type: application/json" \
  -d '{
    "line_items": [
      {"sku": "CFS", "quantity": 3, "name": "Cards Full Size"}
    ],
    "shipping_address": {
      "postcode": "2000",
      "state": "NSW",
      "country": "AU"
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "box_type": "small",
  "box_count": 1,
  "weight_grams": 710,
  "postage_cost": 10.50,
  "service": "Parcel Post"
}
```

---

## Troubleshooting

### Column Not Showing

**Problem:** "Shipping" column doesn't appear
**Solutions:**
1. Check Flask logs: `AI_infrastructure/flask_app.log`
2. Verify route registered: Search logs for "auspost_bp"
3. Restart Flask server
4. Hard refresh browser (Ctrl+Shift+R)

### "Calculating..." Never Finishes

**Problem:** Spinner shows forever
**Solutions:**
1. Check Flask server is running: `http://localhost:5001`
2. Check API endpoint works: `/api/auspost/health`
3. Check browser console for errors (F12 → Console)
4. Check Network tab for failed requests (F12 → Network)
5. Verify AUSPOST_API_KEY is set in .env

### "❌ No Recognized Products"

**Problem:** SKU doesn't match expected format
**Solutions:**
1. Check order line_items have SKU field
2. Verify SKU contains: CFS, MVG, MVGEQ, or MVGEM
3. Check SKU mapping logic in `auspost_routes.py` (lines 75-92)
4. Test with known SKU: "CFS-001"

### "❌ No Postcode"

**Problem:** Can't extract postcode from address
**Solutions:**
1. Check shipping_address contains 4-digit number
2. Verify address format: "123 Main St, Sydney NSW 2000"
3. Test regex: `"Sydney NSW 2000".match(/\b(\d{4})\b/)`
4. Check order has shipping_address field

### "❌ API Error"

**Problem:** Australia Post API call failed
**Solutions:**
1. Verify AUSPOST_API_KEY is correct
2. Check API key has not expired
3. Test API directly: `curl -H "AUTH-KEY: your-key" https://digitalapi.auspost.com.au/postage/parcel/domestic/service.json?from_postcode=3977&to_postcode=2000&length=10&width=10&height=10&weight=1`
4. Check rate limits not exceeded (100 requests/day free tier)
5. Review Flask logs for detailed error message

### Incorrect Postage Cost

**Problem:** Cost doesn't match expected value
**Solutions:**
1. Verify weight calculation includes box weight
2. Check box type is correct (small vs large)
3. Verify from_postcode is set correctly (default: 3977)
4. Test with Australia Post rate calculator: https://auspost.com.au/parcels-mail/calculate-postage-delivery-times
5. Check API response in Flask logs

---

## Performance Testing

### Load Test
```javascript
// In browser console, measure calculation time:
console.time('shipping');
// Refresh page with 20 orders
// Wait for all calculations to complete
console.timeEnd('shipping');
// Should be <10 seconds for 20 orders
```

### API Rate Limit Test
```bash
# Test 100 requests (free tier daily limit)
for i in {1..100}; do
  curl -X POST http://localhost:5001/api/auspost/calculate-order-shipping \
    -H "Content-Type: application/json" \
    -d '{"line_items":[{"sku":"CFS","quantity":3}],"shipping_address":{"postcode":"2000","state":"NSW","country":"AU"}}' &
done
wait
# Check if any requests failed due to rate limit
```

---

## Production Deployment Checklist

### Pre-Deployment
- [ ] Add AUSPOST_API_KEY to Render environment variables
- [ ] Test locally with real API key
- [ ] Verify all test scenarios pass
- [ ] Check Flask logs for errors
- [ ] Review browser console for JavaScript errors

### Deployment
- [ ] Commit changes to v11 branch
- [ ] Push to gerardo remote: `git push gerardo v11:v11`
- [ ] Monitor Render deployment logs
- [ ] Wait for auto-deploy to complete (~2-3 minutes)

### Post-Deployment
- [ ] Open production URL
- [ ] Verify "Shipping" column appears
- [ ] Test with real WooCommerce orders
- [ ] Check production logs for errors
- [ ] Monitor API usage (avoid rate limit)
- [ ] Verify postage costs are accurate

---

## Monitoring

### Flask Logs
```powershell
# View real-time logs
Get-Content AI_infrastructure/flask_app.log -Tail 50 -Wait

# Search for auspost errors
Select-String -Path AI_infrastructure/flask_app.log -Pattern "AUSPOST"
```

### Render Logs
```bash
# View production logs
# Go to: https://dashboard.render.com → Your Service → Logs
# Filter: "AUSPOST_ROUTES"
```

### API Usage Tracking
```python
# Add to auspost_routes.py for usage tracking
import time

@auspost_bp.before_request
def log_request():
    request._start_time = time.time()

@auspost_bp.after_request
def log_response(response):
    duration = time.time() - request._start_time
    logger.info(f"[AUSPOST_ROUTES] Request: {request.path} | Duration: {duration:.2f}s | Status: {response.status_code}")
    return response
```

---

## Success Criteria

✅ **Column Appears:** "Shipping" column visible after "Print Label"
✅ **Calculations Complete:** All orders show box/weight/cost within 10 seconds
✅ **Correct Results:** Box type, weight, and cost match manual calculations
✅ **Error Handling:** Invalid data shows meaningful error messages
✅ **Caching Works:** Sorting/filtering doesn't recalculate
✅ **No Console Errors:** Browser DevTools shows no JavaScript errors
✅ **No Flask Errors:** Flask logs show no exceptions
✅ **Production Ready:** Works on Render with real API key

---

## Next Steps After Testing

1. **Configure Sender Postcode:** Update default "3977" to your warehouse location
2. **Add Service Selection:** Allow choosing Parcel Post vs Express Post
3. **Enable Batch Calculation:** Add button to calculate all visible rows at once
4. **Cost Tracking:** Store shipping costs in database for analytics
5. **Export Integration:** Include shipping costs in CSV/PDF exports

---

**Status:** Ready for testing
**Documentation:** See `WOOCOMMERCE_SHIPPING_INTEGRATION_JAN26_2026.md` for complete details
