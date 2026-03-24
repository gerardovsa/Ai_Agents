# Example: Adding Custom Product Codes

If you need to add new product codes (e.g., "NEWPRODUCT"), update the PRODUCT_SPECS in order_parser.py:

```python
PRODUCT_SPECS = {
    'CFS': {'weight_grams': 220, 'thickness_mm': 20},
    'MVG': {'weight_grams': 325, 'thickness_mm': 30},
    'MVGEQ': {'weight_grams': 220, 'thickness_mm': 20},
    'MVGEM': {'weight_grams': 370, 'thickness_mm': 35},
    'NEWPRODUCT': {'weight_grams': 400, 'thickness_mm': 25}  # Add here
}
```

# Example: Testing with Real Label Data

Your label data from the printer should work directly:

```python
from implementations.auspost_wrapper import auspost_batch_calculate_postage

# Your actual label printer output
label_data = '''
"TO: Bethany Hopkinson
2858 W Belmont Ave
Apt 3W
Chicago 60618
IL, United States
Ph: 6386507894
Email: bethany.k.meyer@gmail.com

1 x MVG
1 x MVGEM"
"TO: Tayla Hawkins
41 Yallamurra St, The Gap
Brisbane 4061
QLD, Australia
Ph: 0400793034
Email: tayla276@bigpond.com

1 x MVG
1 x MVGEQ"
'''

result = auspost_batch_calculate_postage(
    label_data=label_data,
    from_postcode='3020',  # Your warehouse postcode
    service_preference='cheapest'
)

print(f"Total Orders: {result['total_orders']}")
print(f"Total Postage Cost: ${result['total_postage_cost']}")

for order in result['orders']:
    customer = order['customer']['name']
    cost = order.get('postage_cost', 0)
    print(f"  {customer}: ${cost}")
```

# Example: Get Shipping Quote for Specific Service

```python
from implementations.auspost_wrapper import auspost_calculate_single_postage

# Calculate Express Post cost only
result = auspost_calculate_single_postage(
    from_postcode='3020',
    to_address={'postcode': '2000', 'country': 'Australia'},
    weight_kg=0.8,
    length_cm=22, width_cm=16, height_cm=7.7,
    service_code='AUS_PARCEL_EXPRESS'  # Specific service
)

if result['success']:
    service = result['service']
    print(f"Service: {service['service']}")
    print(f"Cost: ${service['total_cost']}")
    print(f"Delivery: {service['delivery_time']}")
```

# Example: Country Code Mapping for International

If you get "country code not found" error, the system has mappings for common countries. But you can add more in auspost_client.py:

```python
@staticmethod
def country_name_to_code(country_name: str) -> Optional[str]:
    country_map = {
        'united states': 'US',
        'new zealand': 'NZ',
        # Add your country here:
        'your_country_name': 'ISO_CODE'
    }
    return country_map.get(country_name.lower().strip())
```

# Example: Box Size Override

If your custom products need different box logic, edit box_calculator.py:

```python
@staticmethod
def calculate_box_requirements(order: Dict[str, Any]) -> Dict[str, Any]:
    total_thickness = order.get('total_thickness_mm', 0)
    
    # Add custom logic here
    if total_thickness <= 50:  # Changed from 60mm
        box_type = 'small'
    elif total_thickness <= 80:  # Changed from 85mm
        box_type = 'large'
    else:
        box_type = 'custom'
    
    # Rest of function...
```

# Example: Service Preference in AI Conversation

When the AI agent processes orders, it can intelligently select services:

```
User: "Calculate shipping for today's orders, but use Express for anything going to Sydney."

AI can use custom logic:
1. Parse all orders
2. Check destination postcodes (2000-2999 = Sydney)
3. Use service_preference='express' for Sydney orders
4. Use service_preference='cheapest' for others
```

# Example: Error Handling

The wrapper returns detailed error information:

```python
result = auspost_batch_calculate_postage(...)

if not result['success']:
    print(f"Error: {result['error']}")
    print(f"Details: {result.get('details', 'N/A')}")
else:
    # Check individual order errors
    for order in result['orders']:
        if 'error' in order:
            print(f"Order {order['order_id']} failed: {order['error']}")
```
