# Australia Post Shipping Calculator - Quick Setup Guide

## ✅ What You Now Have

A complete Australia Post shipping cost calculator that:
- ✅ Parses your label printer data automatically
- ✅ Calculates product weights and dimensions
- ✅ Determines optimal box size (small/large)
- ✅ Gets real-time postage costs from Australia Post API
- ✅ Handles domestic (Australia) and international orders
- ✅ Processes multiple orders in one batch
- ✅ Integrates with your AI agent system

## 🚀 Quick Start (3 Steps)

### Step 1: Get Australia Post API Key

**Option A: Production (Recommended)**
1. Go to: https://developers.auspost.com.au/apis/pacpcs-registration
2. Fill out registration form
3. Check email for API key
4. Add to `.env` file:
   ```bash
   AUSPOST_API_KEY=your_api_key_here
   ```

**Option B: Testing (No Registration)**
- Uses public test API key automatically
- Just run the code - it works out of the box!

### Step 2: Install Dependencies

```bash
pip install requests python-dotenv
```

### Step 3: Restart Flask Server

```powershell
cd AI_infrastructure
python flask_app.py
```

The module will auto-register with your AI agent system!

## 📝 How to Use with AI Agent

### Example 1: Process Today's Orders

**You say:**
> "Calculate postage costs for these orders"

**Then paste your label printer output:**
```
"TO: Customer Name
Address
City Postcode
State, Country
Ph: Phone
Email: email@example.com

1 x MVG
1 x CFS"

"TO: Another Customer
..."
```

**AI will:**
1. Parse all orders automatically
2. Calculate weights and dimensions
3. Get postage costs from Australia Post
4. Show you total cost and breakdown per order

### Example 2: Compare Shipping Options

**You say:**
> "What are the shipping options for an order to Sydney? 1x MVG + 2x CFS"

**AI will:**
- Calculate total weight (325g + 440g + 50g box = 815g)
- Get quotes for all services:
  - Parcel Post: $11.20 (3-5 days)
  - Express Post: $16.85 (next day)
  - Satchel: $14.50 (next day, fixed price)

### Example 3: International Shipping

**You say:**
> "How much to ship 2x MVGEM to the United States?"

**AI will:**
- Calculate weight (740g + 60g box = 800g)
- Get international quotes:
  - Standard Parcel: $45.80 (7-14 days)
  - Express: $78.50 (3-5 days)

## 🛠️ Product Codes Currently Supported

| Code | Weight | Thickness | Description |
|------|--------|-----------|-------------|
| CFS | 220g | 20mm | Compact Flat Sheet |
| MVG | 325g | 30mm | Medium Volume Guide |
| MVGEQ | 220g | 20mm | Medium Volume Guide EQ |
| MVGEM | 370g | 35mm | Medium Volume Guide EM |

### Need to Add More Products?

Edit: `UI/modules_external/auspost-shipping/backend/order_parser.py`

```python
PRODUCT_SPECS = {
    'CFS': {'weight_grams': 220, 'thickness_mm': 20},
    'MVG': {'weight_grams': 325, 'thickness_mm': 30},
    'MVGEQ': {'weight_grams': 220, 'thickness_mm': 20},
    'MVGEM': {'weight_grams': 370, 'thickness_mm': 35},
    'YOURNEWCODE': {'weight_grams': 300, 'thickness_mm': 25}  # Add here
}
```

## 📦 Box Selection Logic

**Automatic:**
- Products ≤ 60mm thick → Small box (50g, 22×16×7.7cm)
- Products ≤ 85mm thick → Large box (60g, 31×22.5×10.2cm)
- Products > 85mm thick → Custom box (manual handling)

**Example:**
- 1x MVG (30mm) + 1x CFS (20mm) = 50mm → **Small box**
- 2x MVGEM (70mm total) → **Large box**
- 3x MVGEM (105mm total) → **Custom box** (alert you)

## 🎯 AI Tool Names (For Reference)

If you want to call tools directly in prompts:

1. **auspost_parse_order_labels** - Parse label data
2. **auspost_calculate_single_postage** - Get quote for one order
3. **auspost_batch_calculate_postage** - Process multiple orders
4. **auspost_get_service_options** - List available services

## 🧪 Testing the System

### Test 1: Parse Sample Order

```bash
cd UI/modules_external/auspost-shipping/implementations
python auspost_wrapper.py
```

Expected output:
```
✅ Success: true
📦 Total Orders: 1
⚖️  Total Weight: 0.595 kg
💰 Cheapest Service: Parcel Post - $10.50
```

### Test 2: Test with Your Real Labels

Copy your label printer output and paste into test:

```python
sample_labels = '''
[PASTE YOUR LABEL DATA HERE]
'''
```

## 🔧 Customization Options

### Change Default Warehouse Postcode

In AI conversations, you can specify:
```
"Calculate postage from postcode 3020"
```

Or set a default in your configuration.

### Prefer Express Shipping

When asking AI:
```
"Calculate postage for these orders, use Express Post"
```

AI will use `service_preference='express'`

### Get Detailed Breakdown

Ask AI:
```
"Show me all shipping options, not just the cheapest"
```

AI will return full service list with prices.

## 📊 Sample AI Conversation

**You:**
> Calculate shipping costs for today's orders. Here are the labels:
> [paste label data]

**AI Response:**
> I've processed 12 orders with the following results:
> 
> **Total Postage Cost:** $145.80
> - 9 domestic orders: $89.50
> - 3 international orders: $56.30
> 
> **Total Weight:** 5.2kg across all packages
> 
> **Breakdown by destination:**
> - 6 orders to Melbourne: $45.20 (Parcel Post)
> - 2 orders to Sydney: $28.40 (Express Post)
> - 1 order to Brisbane: $15.90 (Parcel Post)
> - 2 orders to USA: $89.60 (International Standard)
> - 1 order to UK: $66.70 (International Standard)
> 
> Would you like me to break down individual order costs or compare Express vs Standard for any destinations?

## 🐛 Common Issues & Fixes

### Issue: "API key required"
**Fix:** Add to `.env` file:
```bash
AUSPOST_API_KEY=your_key_here
```

Or for testing, it will use the public test API automatically.

### Issue: "Country code not found"
**Fix:** Country name might need mapping. Check `auspost_client.py` line 265 for country_map. Add your country if missing.

### Issue: Label parsing fails
**Fix:** Ensure labels have:
- Customer name after "TO:"
- Postcode (4-5 digits)
- Product codes like "1 x MVG"

### Issue: Box calculation wrong
**Fix:** Check product specs in `order_parser.py` - weight and thickness must be accurate.

## 📚 Documentation Files

- **README.md** - Full documentation with API details
- **EXAMPLES.md** - Code examples for customization
- **QUICK_START.md** - This file
- **manifest.json** - Module configuration

## 🔗 Useful Links

- **Australia Post Developer Portal:** https://developers.auspost.com.au/
- **Register for API Key:** https://developers.auspost.com.au/apis/pacpcs-registration
- **API Documentation:** https://developers.auspost.com.au/apis/pac/reference
- **Parcel Size Guidelines:** http://auspost.com.au/parcels-mail/size-and-weight-guidelines.html

## ✨ Next Steps

1. ✅ Get your Australia Post API key (5 minutes)
2. ✅ Add to `.env` file
3. ✅ Install dependencies (`pip install requests python-dotenv`)
4. ✅ Restart Flask server
5. ✅ Test with sample label data
6. ✅ Try with real label printer output
7. ✅ Start using with AI agent!

---

**Module Location:** `UI/modules_external/auspost-shipping/`  
**Created:** January 29, 2026  
**Status:** ✅ Production Ready
