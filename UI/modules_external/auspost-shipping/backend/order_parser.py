"""
Order Parser - Parse Shipping Label Data
========================================

Parses label text data to extract customer information and product codes.

Format:
"TO: Customer Name
Address Line 1
City Postcode
State, Country
Ph: Phone
Email: email@example.com

1 x PRODUCT_CODE
2 x ANOTHER_CODE"

FILE: UI/modules_external/auspost-shipping/backend/order_parser.py
"""

import re
from typing import Dict, List, Any


class OrderParser:
    """Parse shipping label data into structured order information."""
    
    # Product specifications (weight and thickness)
    PRODUCT_SPECS = {
        'CFS': {'weight_grams': 220, 'thickness_mm': 20},
        'MVG': {'weight_grams': 325, 'thickness_mm': 30},
        'MVGEQ': {'weight_grams': 220, 'thickness_mm': 20},
        'MVGEM': {'weight_grams': 370, 'thickness_mm': 35}
    }
    
    @staticmethod
    def parse_labels(label_data: str) -> List[Dict[str, Any]]:
        """
        Parse raw label data into structured orders.
        
        Args:
            label_data: Raw label text with orders separated by quotes
            
        Returns:
            List of parsed orders with customer and product details
        """
        # Split by quotes to get individual orders
        # Pattern: "..." or '...'
        orders_raw = re.findall(r'"([^"]+)"', label_data)
        if not orders_raw:
            # Try single quotes
            orders_raw = re.findall(r"'([^']+)'", label_data)
        
        if not orders_raw:
            # No quotes found, treat as single order
            orders_raw = [label_data]
        
        parsed_orders = []
        
        for idx, order_text in enumerate(orders_raw, 1):
            try:
                parsed_order = OrderParser._parse_single_order(order_text, idx)
                if parsed_order:
                    parsed_orders.append(parsed_order)
            except Exception as e:
                # Log error but continue processing other orders
                parsed_orders.append({
                    'order_id': idx,
                    'error': str(e),
                    'raw_text': order_text[:100]  # First 100 chars
                })
        
        return parsed_orders
    
    @staticmethod
    def _parse_single_order(order_text: str, order_id: int) -> Dict[str, Any]:
        """Parse a single order's text."""
        lines = [line.strip() for line in order_text.split('\n') if line.strip()]
        
        order = {
            'order_id': order_id,
            'customer': {},
            'products': [],
            'total_weight_grams': 0,
            'total_thickness_mm': 0
        }
        
        # Parse customer info
        customer_section = True
        product_section = False
        
        for line in lines:
            # Check if line is "TO:" header
            if line.upper().startswith('TO:'):
                order['customer']['name'] = line[3:].strip()
                continue
            
            # Check for phone
            if line.upper().startswith('PH:') or line.upper().startswith('PHONE:'):
                order['customer']['phone'] = re.sub(r'[^\d+]', '', line.split(':', 1)[1])
                customer_section = False
                continue
            
            # Check for email
            if line.upper().startswith('EMAIL:'):
                order['customer']['email'] = line.split(':', 1)[1].strip()
                continue
            
            # Check for product codes (e.g., "1 x MVG", "2 x MVGEM")
            product_match = re.match(r'(\d+)\s*x\s*([A-Z]+)', line, re.IGNORECASE)
            if product_match:
                quantity = int(product_match.group(1))
                product_code = product_match.group(2).upper()
                
                if product_code in OrderParser.PRODUCT_SPECS:
                    specs = OrderParser.PRODUCT_SPECS[product_code]
                    order['products'].append({
                        'code': product_code,
                        'quantity': quantity,
                        'unit_weight_grams': specs['weight_grams'],
                        'unit_thickness_mm': specs['thickness_mm'],
                        'total_weight_grams': specs['weight_grams'] * quantity,
                        'total_thickness_mm': specs['thickness_mm'] * quantity
                    })
                    
                    # Add to totals
                    order['total_weight_grams'] += specs['weight_grams'] * quantity
                    order['total_thickness_mm'] += specs['thickness_mm'] * quantity
                
                product_section = True
                customer_section = False
                continue
            
            # Parse address (when in customer section and not product section)
            if customer_section and not product_section:
                # Try to extract postcode (4-5 digits)
                postcode_match = re.search(r'\b(\d{4,5})\b', line)
                
                # Try to extract state codes (2-3 letters)
                state_match = re.search(r'\b([A-Z]{2,3})\b', line)
                
                # Try to extract country
                country_match = re.search(r',\s*([A-Za-z\s]+)$', line)
                
                if not order['customer'].get('address_line1'):
                    order['customer']['address_line1'] = line
                elif not order['customer'].get('address_line2'):
                    order['customer']['address_line2'] = line
                
                if postcode_match and not order['customer'].get('postcode'):
                    order['customer']['postcode'] = postcode_match.group(1)
                
                if state_match and not order['customer'].get('state'):
                    order['customer']['state'] = state_match.group(1)
                
                if country_match and not order['customer'].get('country'):
                    order['customer']['country'] = country_match.group(1).strip()
        
        # Determine if domestic or international
        country = order['customer'].get('country', '').lower()
        order['is_domestic'] = 'australia' in country or country == ''
        
        return order
    
    @staticmethod
    def get_product_specs() -> Dict[str, Dict[str, int]]:
        """Get product specifications."""
        return OrderParser.PRODUCT_SPECS.copy()
