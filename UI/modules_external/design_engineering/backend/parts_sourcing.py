"""
Parts Sourcing Module
BOM generation with supplier catalogs and pricing
"""

import json
from typing import Dict, List, Optional
from .material_database import get_profile_properties, get_supplier_info, SUPPLIERS


def generate_bom(design_spec: Dict, preferred_supplier: str = 'makerbeam_australia') -> Dict:
    """
    Generate Bill of Materials from design specification.
    
    Args:
        design_spec: Dictionary with:
            - components: List of component dicts with type, profile_id, length_mm, quantity
            - connectors: List of connector dicts with type, quantity
        preferred_supplier: Supplier ID to use for pricing
    
    Returns:
        Complete BOM with part numbers, costs, and supplier links
    """
    supplier = get_supplier_info(preferred_supplier)
    if not supplier:
        return {'error': f'Supplier "{preferred_supplier}" not found'}
    
    bom_items = []
    total_cost = 0
    warnings = []
    
    # Process profile/beam components
    for component in design_spec.get('components', []):
        if component['type'] == 'beam':
            profile_id = component['profile_id']
            length_mm = component['length_mm']
            quantity = component.get('quantity', 1)
            
            profile = get_profile_properties(profile_id)
            if not profile:
                warnings.append(f"Profile '{profile_id}' not found")
                continue
            
            # Check if supplier stocks this profile
            supplier_profile = supplier['profiles'].get(profile_id)
            if not supplier_profile:
                warnings.append(f"Supplier does not stock {profile_id}")
                # Try to find alternative supplier
                alternative = find_alternative_supplier(profile_id)
                if alternative:
                    warnings.append(f"Available from {alternative['supplier']}")
                continue
            
            length_m = length_mm / 1000
            unit_cost = supplier_profile['price_aud_per_meter'] * length_m
            
            # Add cutting fee if applicable
            cut_fee = 0
            if supplier_profile.get('cut_to_length'):
                cut_fee = supplier_profile.get('cut_fee_aud', 0)
            
            item_total = (unit_cost + cut_fee) * quantity
            total_cost += item_total
            
            bom_items.append({
                'category': 'Structural Profile',
                'item': f"{profile['name']} - {length_mm}mm",
                'part_number': supplier_profile['part_number'],
                'supplier': supplier['name'],
                'quantity': quantity,
                'length_mm': length_mm,
                'unit_cost_aud': round(unit_cost + cut_fee, 2),
                'total_cost_aud': round(item_total, 2),
                'url': f"{supplier['website']}/products/{supplier_profile['part_number']}",
                'specifications': {
                    'profile': profile_id,
                    'weight_per_unit_kg': round(profile['mechanical']['weight_per_meter_kg'] * length_m, 2),
                    'material': profile['material']
                }
            })
    
    # Process connector components
    for connector in design_spec.get('connectors', []):
        connector_type = connector['type']
        quantity = connector.get('quantity', 1)
        
        # Check if supplier has this connector
        supplier_connector = supplier['connectors'].get(connector_type)
        if not supplier_connector:
            warnings.append(f"Supplier does not stock connector '{connector_type}'")
            continue
        
        item_total = supplier_connector['price_aud'] * quantity
        total_cost += item_total
        
        bom_items.append({
            'category': 'Hardware',
            'item': connector_type.replace('_', ' ').title(),
            'part_number': supplier_connector['part_number'],
            'supplier': supplier['name'],
            'quantity': quantity,
            'unit_cost_aud': supplier_connector['price_aud'],
            'total_cost_aud': round(item_total, 2),
            'url': f"{supplier['website']}/products/{supplier_connector['part_number']}",
            'specifications': {
                'material': supplier_connector.get('material', 'N/A'),
                'load_rating_kg': supplier_connector.get('load_rating_kg', 'N/A')
            }
        })
    
    # Calculate shipping
    shipping_cost = 0
    threshold = supplier['shipping'].get('free_shipping_threshold_aud', 0)
    if total_cost < threshold:
        shipping_cost = supplier['shipping'].get('australia_shipping_aud', 0)
    
    grand_total = total_cost + shipping_cost
    
    # Generate summary
    summary = {
        'supplier': supplier['name'],
        'contact': supplier['contact'],
        'total_items': len(bom_items),
        'subtotal_aud': round(total_cost, 2),
        'shipping_aud': round(shipping_cost, 2),
        'grand_total_aud': round(grand_total, 2),
        'estimated_delivery_days': supplier['shipping']['typical_delivery_days'],
        'free_shipping_threshold_aud': threshold,
        'notes': []
    }
    
    if total_cost < threshold:
        summary['notes'].append(f"Add ${threshold - total_cost:.2f} more for free shipping")
    else:
        summary['notes'].append("Free shipping applied!")
    
    return {
        'bom': bom_items,
        'summary': summary,
        'warnings': warnings,
        'generated_date': 'December 2025'
    }


def find_alternative_supplier(profile_id: str) -> Optional[Dict]:
    """Find alternative supplier that stocks a given profile"""
    for supplier_id, supplier_data in SUPPLIERS.items():
        if profile_id in supplier_data['profiles']:
            return {
                'supplier': supplier_data['name'],
                'supplier_id': supplier_id,
                'part_number': supplier_data['profiles'][profile_id]['part_number'],
                'price_aud_per_meter': supplier_data['profiles'][profile_id]['price_aud_per_meter']
            }
    return None


def generate_bed_frame_bom(
    width_mm: float = 1400,
    length_mm: float = 1900,
    profile_id: str = '40x40_standard',
    preferred_supplier: str = 'makerbeam_australia'
) -> Dict:
    """
    Generate complete BOM for campervan bed frame.
    
    Args:
        width_mm: Bed width
        length_mm: Bed length
        profile_id: T-slot profile to use
        preferred_supplier: Supplier ID
    
    Returns:
        Complete BOM with all components
    """
    design_spec = {
        'components': [
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': length_mm, 'quantity': 2, 'label': 'Side Rails'},
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': width_mm, 'quantity': 2, 'label': 'End Rails'},
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': length_mm, 'quantity': 1, 'label': 'Center Support'},
        ],
        'connectors': [
            {'type': 'corner_bracket_90deg', 'quantity': 8},
            {'type': 'anchor_fastener', 'quantity': 16},
            {'type': 'end_cap', 'quantity': 10}
        ]
    }
    
    return generate_bom(design_spec, preferred_supplier)


def generate_kitchen_module_bom(
    width_mm: float = 600,
    height_mm: float = 900,
    depth_mm: float = 600,
    profile_id: str = '30x30_standard',
    preferred_supplier: str = 'makerbeam_australia'
) -> Dict:
    """Generate BOM for kitchen module frame"""
    design_spec = {
        'components': [
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': height_mm, 'quantity': 4, 'label': 'Vertical Posts'},
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': width_mm, 'quantity': 4, 'label': 'Width Beams'},
            {'type': 'beam', 'profile_id': profile_id, 'length_mm': depth_mm, 'quantity': 4, 'label': 'Depth Beams'},
        ],
        'connectors': [
            {'type': 'corner_bracket_90deg', 'quantity': 8},
            {'type': 't_bracket', 'quantity': 4},
            {'type': 'anchor_fastener', 'quantity': 24},
            {'type': 'end_cap', 'quantity': 12}
        ]
    }
    
    return generate_bom(design_spec, preferred_supplier)


def compare_suppliers_for_design(design_spec: Dict) -> List[Dict]:
    """
    Compare prices across all suppliers for a design.
    
    Args:
        design_spec: Design specification with components
    
    Returns:
        List of supplier comparisons sorted by cost
    """
    comparisons = []
    
    for supplier_id in SUPPLIERS.keys():
        try:
            bom = generate_bom(design_spec, supplier_id)
            
            if 'error' not in bom:
                comparisons.append({
                    'supplier': bom['summary']['supplier'],
                    'supplier_id': supplier_id,
                    'grand_total_aud': bom['summary']['grand_total_aud'],
                    'delivery_days': bom['summary']['estimated_delivery_days'],
                    'items_count': bom['summary']['total_items'],
                    'warnings_count': len(bom.get('warnings', []))
                })
        except Exception as e:
            # Skip suppliers that cause errors
            continue
    
    return sorted(comparisons, key=lambda x: x['grand_total_aud'])


def export_bom_csv(bom_data: Dict) -> str:
    """Export BOM to CSV format"""
    lines = ['Category,Item,Part Number,Supplier,Quantity,Unit Cost (AUD),Total Cost (AUD),URL']
    
    for item in bom_data.get('bom', []):
        line = f"{item['category']},{item['item']},{item['part_number']},{item['supplier']},"
        line += f"{item['quantity']},{item['unit_cost_aud']},{item['total_cost_aud']},{item['url']}"
        lines.append(line)
    
    # Add summary
    summary = bom_data.get('summary', {})
    lines.append('')
    lines.append(f"Subtotal,,,,,,{summary.get('subtotal_aud', 0)},")
    lines.append(f"Shipping,,,,,,{summary.get('shipping_aud', 0)},")
    lines.append(f"Grand Total,,,,,,{summary.get('grand_total_aud', 0)},")
    
    return '\n'.join(lines)


def export_bom_markdown(bom_data: Dict) -> str:
    """Export BOM to Markdown table format"""
    lines = ['# Bill of Materials\n']
    lines.append(f"**Supplier:** {bom_data['summary']['supplier']}\n")
    lines.append(f"**Estimated Delivery:** {bom_data['summary']['estimated_delivery_days']} days\n")
    
    lines.append('## Components\n')
    lines.append('| Category | Item | Part # | Qty | Unit Cost | Total |')
    lines.append('|----------|------|--------|-----|-----------|-------|')
    
    for item in bom_data.get('bom', []):
        line = f"| {item['category']} | {item['item']} | {item['part_number']} | "
        line += f"{item['quantity']} | ${item['unit_cost_aud']:.2f} | ${item['total_cost_aud']:.2f} |"
        lines.append(line)
    
    lines.append('')
    lines.append('## Summary\n')
    summary = bom_data['summary']
    lines.append(f"- **Subtotal:** ${summary['subtotal_aud']:.2f}")
    lines.append(f"- **Shipping:** ${summary['shipping_aud']:.2f}")
    lines.append(f"- **Grand Total:** ${summary['grand_total_aud']:.2f}")
    
    if bom_data.get('warnings'):
        lines.append('\n## Warnings\n')
        for warning in bom_data['warnings']:
            lines.append(f"- {warning}")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    # Test the module
    print("Testing Parts Sourcing Module\n")
    
    print("1. Bed Frame BOM (1400x1900mm):")
    bed_bom = generate_bed_frame_bom(1400, 1900, '40x40_standard')
    print(f"   Items: {bed_bom['summary']['total_items']}")
    print(f"   Total: ${bed_bom['summary']['grand_total_aud']:.2f}")
    print(f"   Delivery: {bed_bom['summary']['estimated_delivery_days']} days")
    
    print("\n2. Kitchen Module BOM (600x900x600mm):")
    kitchen_bom = generate_kitchen_module_bom(600, 900, 600, '30x30_standard')
    print(f"   Items: {kitchen_bom['summary']['total_items']}")
    print(f"   Total: ${kitchen_bom['summary']['grand_total_aud']:.2f}")
    
    print("\n3. Export BOM as Markdown:")
    md = export_bom_markdown(bed_bom)
    print(md[:300] + "...")
