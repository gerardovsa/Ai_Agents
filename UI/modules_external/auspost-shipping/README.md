# Australia Post Shipping Calculator Module

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Created:** January 29, 2026  
**Module Type:** External Module - Shipping Cost Calculation

---

## 📋 Overview

Integrates with **Australia Post Postage Assessment Calculator (PAC) API** to calculate accurate shipping costs for orders. Automatically parses label data, determines optimal box sizes, and retrieves real-time postage rates for both domestic and international shipments.

### Key Features

✅ **Label Data Parsing** - Extracts customer details and product codes from label text  
✅ **Product Weight Calculation** - Tracks weight and dimensions for CFS, MVG, MVGEQ, MVGEM products  
✅ **Box Size Optimization** - Automatically selects small/large box based on product thickness  
✅ **Australia Post API Integration** - Real-time postage rates from official API  
✅ **Domestic & International** - Supports Australian and overseas destinations  
✅ **Batch Processing** - Calculate postage for multiple orders at once  
✅ **Service Comparison** - Compare Express Post, Parcel Post, and Satchel options

---

## 🚀 Quick Start

### 1. Get Australia Post API Key

**Option A: Production API Key (Recommended)**

1. Register at: https://developers.auspost.com.au/apis/pacpcs-registration
2. Check email for your API key
3. Add to `.env` file:

```bash
AUSPOST_API_KEY=your_api_key_here
```

**Option B: Test Environment (Development)**

Uses public test key automatically. No registration needed for testing.

```python
# In backend/auspost_client.py
client = AusPostClient(use_test_env=True)
```

### 2. Install Dependencies

```bash
pip install requests python-dotenv
```

### 3. Test the Module

```bash
cd UI/modules_external/auspost-shipping/implementations
python auspost_wrapper.py
```

---

## 📦 Product Specifications

| Product Code | Weight (grams) | Thickness (mm) | Description |
|--------------|----------------|----------------|-------------|
| **CFS** | 220g | 20mm | Compact Flat Sheet |
| **MVG** | 325g | 30mm | Medium Volume Guide |
| **MVGEQ** | 220g | 20mm | Medium Volume Guide EQ |
| **MVGEM** | 370g | 35mm | Medium Volume Guide EM |

### Box Specifications

| Box Type | Weight | Depth | Max Depth | Dimensions (cm) |
|----------|--------|-------|-----------|-----------------|
| **Small** | 50g | 45mm | 60mm | 22 × 16 × 7.7 |
| **Large** | 60g | 70mm | 85mm | 31 × 22.5 × 10.2 |

**Auto-Selection Logic:**
- Total thickness ≤ 60mm → **Small box**
- Total thickness ≤ 85mm → **Large box**
- Total thickness > 85mm → **Custom box** (manual handling required)

---

## 🛠️ AI Tool Usage

### Tool 1: Parse Order Labels

**Tool Name:** `auspost_parse_order_labels`

**Description:** Parse label data and calculate order dimensions/weight.

**Parameters:**
- `label_data` (string, required) - Raw label text with customer details and product codes

**Example:**

```json
{
  "label_data": "\"TO: John Smith\n123 Main St\nMelbourne 3000\nVIC, Australia\nPh: 0400123456\nEmail: john@example.com\n\n1 x MVG\n1 x CFS\""
}
```

**Returns:**

```json
{
  "success": true,
  "total_orders": 1,
  "successful_orders": 1,
  "total_weight_kg": 0.595,
  "orders": [
    {
      "order_id": 1,
      "customer": {
        "name": "John Smith",
        "address_line1": "123 Main St",
        "postcode": "3000",
        "state": "VIC",
        "country": "Australia"
      },
      "products": [
        {"code": "MVG", "quantity": 1, "total_weight_grams": 325},
        {"code": "CFS", "quantity": 1, "total_weight_grams": 220}
      ],
      "total_weight_grams": 545,
      "total_thickness_mm": 50,
      "box_details": {
        "box_type": "small",
        "total_weight_kg": 0.595,
        "dimensions_cm": {"length": 22, "width": 16, "height": 7.7}
      }
    }
  ]
}
```

---

### Tool 2: Calculate Single Order Postage

**Tool Name:** `auspost_calculate_single_postage`

**Description:** Calculate postage cost for one order with Australia Post API.

**Parameters:**
- `from_postcode` (string, required) - Origin Australian postcode
- `to_address` (object, required) - Destination address details
  - `postcode` (string) - Destination postcode
  - `country` (string) - Country name (e.g., "Australia", "United States")
- `weight_kg` (number, required) - Package weight in kilograms
- `length_cm` (number, required) - Package length in cm
- `width_cm` (number, required) - Package width in cm
- `height_cm` (number, required) - Package height in cm
- `service_code` (string, optional) - Specific service code (e.g., "AUS_PARCEL_REGULAR")

**Example:**

```json
{
  "from_postcode": "3020",
  "to_address": {
    "postcode": "3000",
    "country": "Australia"
  },
  "weight_kg": 0.595,
  "length_cm": 22,
  "width_cm": 16,
  "height_cm": 7.7
}
```

**Returns:**

```json
{
  "success": true,
  "is_domestic": true,
  "services": [
    {
      "code": "AUS_PARCEL_REGULAR",
      "name": "Parcel Post",
      "price": "10.50",
      "delivery_time": "Delivered in 3-5 business days"
    },
    {
      "code": "AUS_PARCEL_EXPRESS",
      "name": "Express Post",
      "price": "15.75",
      "delivery_time": "Delivered next business day"
    }
  ],
  "cheapest_service": {
    "code": "AUS_PARCEL_REGULAR",
    "price": "10.50"
  },
  "fastest_service": {
    "code": "AUS_PARCEL_EXPRESS",
    "price": "15.75"
  }
}
```

---

### Tool 3: Batch Calculate Postage

**Tool Name:** `auspost_batch_calculate_postage`

**Description:** Process multiple orders and calculate postage for each.

**Parameters:**
- `label_data` (string, required) - Raw label text with multiple orders
- `from_postcode` (string, required) - Origin postcode
- `service_preference` (string, optional) - Service selection strategy:
  - `"cheapest"` (default) - Lowest cost option
  - `"fastest"` - Fastest delivery (Express Post)
  - `"regular"` - Standard Parcel Post
  - `"express"` - Express Post only

**Example:**

```json
{
  "label_data": "\"TO: Customer 1...\" \"TO: Customer 2...\"",
  "from_postcode": "3020",
  "service_preference": "cheapest"
}
```

**Returns:**

```json
{
  "success": true,
  "total_orders": 12,
  "successful_calculations": 12,
  "total_postage_cost": 145.80,
  "service_preference": "cheapest",
  "summary": {
    "domestic_orders": 9,
    "international_orders": 3,
    "total_weight_kg": 5.2
  },
  "orders": [
    {
      "order_id": 1,
      "customer": {...},
      "postage_cost": 10.50,
      "selected_service": {
        "code": "AUS_PARCEL_REGULAR",
        "name": "Parcel Post",
        "price": "10.50"
      }
    }
  ]
}
```

---

### Tool 4: Get Service Options

**Tool Name:** `auspost_get_service_options`

**Description:** List available Australia Post service codes and descriptions.

**Parameters:**
- `service_type` (string, optional) - Filter: `"domestic"`, `"international"`, or `"all"` (default)

**Returns:**

```json
{
  "success": true,
  "domestic_services": [
    {"code": "AUS_PARCEL_REGULAR", "name": "Parcel Post (Standard)", "type": "domestic"},
    {"code": "AUS_PARCEL_EXPRESS", "name": "Express Post", "type": "domestic"}
  ],
  "international_services": [
    {"code": "INT_PARCEL_STD_OWN_PACKAGING", "name": "International Standard Parcel"}
  ]
}
```

---

## 📊 Example Use Cases

### Use Case 1: Daily Order Batch Processing

**Scenario:** Process all orders for the day and get total shipping costs.

```
AI: Please calculate postage for today's orders.

User provides label data from label printer.

AI uses: auspost_batch_calculate_postage(label_data, from_postcode="3020", service_preference="cheapest")

Result:
- 15 orders processed
- 12 domestic (Australia)
- 3 international (US, UK, NZ)
- Total postage cost: $187.50
- Estimated total weight: 6.8kg
```

---

### Use Case 2: Cost Comparison for Customer Quote

**Scenario:** Customer wants shipping options for their order.

```
AI: I need shipping quotes for an order going to Sydney.

AI uses: auspost_calculate_single_postage(
  from_postcode="3020",
  to_address={"postcode": "2000", "country": "Australia"},
  weight_kg=0.8,
  length_cm=22, width_cm=16, height_cm=7.7
)

Result shows:
- Parcel Post: $11.20 (3-5 days)
- Express Post: $16.85 (next day)
- Express Satchel: $14.50 (next day, fixed price)
```

---

### Use Case 3: International Shipping Estimate

**Scenario:** Determine shipping cost to USA.

```
Order: 2x MVG + 1x MVGEM (total 1.02kg in large box)

AI uses: auspost_calculate_single_postage(
  from_postcode="3020",
  to_address={"postcode": "90210", "country": "United States"},
  weight_kg=1.08,
  length_cm=31, width_cm=22.5, height_cm=10.2
)

Result:
- International Standard Parcel: $45.80 (7-14 days)
- International Express: $78.50 (3-5 days)
```

---

## 🔧 Technical Architecture

### Module Structure

```
auspost-shipping/
├── manifest.json                     # Module configuration
├── tools/
│   └── auspost_tools.json            # Tool definitions for Registry V3
├── implementations/
│   └── auspost_wrapper.py            # AI tool wrappers (@tool_executor)
├── backend/
│   ├── order_parser.py               # Parse label data
│   ├── box_calculator.py             # Determine box size
│   └── auspost_client.py             # Australia Post API client
└── README.md                         # This file
```

### Data Flow

```
1. Label Data (raw text)
   ↓
2. OrderParser.parse_labels()
   → Extract customer info, product codes
   ↓
3. BoxCalculator.calculate_box_requirements()
   → Determine small/large box, calculate total weight
   ↓
4. AusPostClient.get_domestic_services() or calculate_international_postage()
   → Call Australia Post API
   ↓
5. Return postage costs with service options
```

### API Integration

**Base URL (Production):** `https://digitalapi.auspost.com.au`  
**Test URL:** `https://test.npe.auspost.com.au`

**Authentication:** HTTP Header `AUTH-KEY: your_api_key`

**Key Endpoints:**
- `GET /postage/parcel/domestic/service.json` - List domestic services
- `GET /postage/parcel/domestic/calculate.json` - Calculate domestic cost
- `GET /postage/parcel/international/service.json` - List international services
- `GET /postage/parcel/international/calculate.json` - Calculate international cost

**Rate Limits:** Check Australia Post documentation for current limits.

---

## ⚙️ Configuration

### Environment Variables

Add to `.env` file in project root:

```bash
# Australia Post API Key (get from https://developers.auspost.com.au)
AUSPOST_API_KEY=your_production_api_key_here
```

### Module Configuration

Edit `manifest.json` to update product specs or box dimensions:

```json
{
  "supported_products": {
    "CFS": {"weight_grams": 220, "thickness_mm": 20},
    "MVG": {"weight_grams": 325, "thickness_mm": 30}
  },
  "supported_boxes": {
    "small": {"weight_grams": 50, "depth_mm": 45, "max_depth_mm": 60},
    "large": {"weight_grams": 60, "depth_mm": 70, "max_depth_mm": 85}
  }
}
```

---

## 🧪 Testing

### Manual Test

```bash
cd UI/modules_external/auspost-shipping/implementations
python auspost_wrapper.py
```

### Test with Sample Data

```python
from auspost_wrapper import auspost_parse_order_labels

sample_labels = '''
"TO: Test Customer
123 Main St
Melbourne 3000
VIC, Australia
Ph: 0400123456
Email: test@example.com

1 x MVG
1 x CFS"
'''

result = auspost_parse_order_labels(sample_labels)
print(f"Orders: {result['total_orders']}")
print(f"Weight: {result['total_weight_kg']} kg")
```

### Test Postage Calculation

```python
from auspost_wrapper import auspost_calculate_single_postage

result = auspost_calculate_single_postage(
    from_postcode='3020',
    to_address={'postcode': '3000', 'country': 'Australia'},
    weight_kg=0.595,
    length_cm=22, width_cm=16, height_cm=7.7
)

if result['success']:
    cheapest = result['cheapest_service']
    print(f"Cheapest: {cheapest['name']} - ${cheapest['price']}")
```

---

## 🐛 Troubleshooting

### Issue: "API key required" error

**Solution:**
1. Check `.env` file has `AUSPOST_API_KEY=...`
2. Verify API key is correct from Australia Post
3. For testing, use `use_test_env=True` parameter

```python
client = AusPostClient(use_test_env=True)  # Uses public test key
```

### Issue: "Country code not found" for international

**Solution:**
Add country mapping to `auspost_client.py` in `country_name_to_code()` method.

```python
country_map = {
    'your_country': 'ISO_CODE',  # Add missing country
    ...
}
```

### Issue: Parsing fails for label data

**Solution:**
Ensure label data format matches expected structure:
- Orders separated by quotes: `"..."` `"..."`
- Product codes: `1 x MVG`, `2 x CFS`
- Address includes postcode (4-5 digits)

### Issue: Box calculation incorrect

**Solution:**
Check product specs in `backend/order_parser.py`:

```python
PRODUCT_SPECS = {
    'YOUR_CODE': {'weight_grams': 220, 'thickness_mm': 20}
}
```

---

## 📚 API Documentation References

- **Australia Post Developer Portal:** https://developers.auspost.com.au/
- **PAC API Getting Started:** https://developers.auspost.com.au/apis/pac/getting-started
- **Domestic Parcel Tutorial:** https://developers.auspost.com.au/apis/pac/tutorial/domestic-parcel
- **API Reference:** https://developers.auspost.com.au/apis/pac/reference
- **Register for API Key:** https://developers.auspost.com.au/apis/pacpcs-registration

---

## 🔄 Future Enhancements

- [ ] Add signature on delivery option pricing
- [ ] Integrate extra cover (insurance) calculations
- [ ] Support for letter-sized items
- [ ] Historical postage cost tracking
- [ ] Bulk discount calculations for high-volume shippers
- [ ] Auto-select optimal box based on cost vs. dimension trade-offs
- [ ] Integration with label printing system
- [ ] Real-time tracking integration
- [ ] Automated postage reconciliation

---

## 📝 Change Log

### Version 1.0.0 (January 29, 2026)
- ✅ Initial release
- ✅ Order parsing with product codes (CFS, MVG, MVGEQ, MVGEM)
- ✅ Box size calculation (small/large)
- ✅ Australia Post API integration
- ✅ Domestic and international postage calculation
- ✅ Batch processing support
- ✅ AI tool registration with Registry V3

---

## 📞 Support

**Module Maintainer:** InHouse Print Development Team  
**Created:** January 29, 2026  
**Module Path:** `UI/modules_external/auspost-shipping/`

For issues or feature requests, see project documentation or contact the development team.

---

## 📄 License

Part of InHouse Print AI Agents system. Internal use only.
