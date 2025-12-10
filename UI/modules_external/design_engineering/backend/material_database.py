"""
Material Database Module
Provides access to aluminum alloy properties and T-slot profile specifications
"""

import json
import os
from typing import Dict, List, Optional

# Get the data directory path
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def load_json_data(filename: str) -> Dict:
    """Load JSON data from data directory"""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load data on module import
ALUMINUM_ALLOYS = load_json_data('aluminum_alloys.json')
TSLOT_PROFILES = load_json_data('tslot_profiles.json')
SUPPLIERS = load_json_data('suppliers.json')


def get_material_properties(material_id: str) -> Optional[Dict]:
    """
    Get material properties for a given material ID.
    
    Args:
        material_id: Material identifier (e.g., "6061-T6", "6063-T5")
    
    Returns:
        Dictionary with material properties or None if not found
    """
    return ALUMINUM_ALLOYS.get(material_id)


def get_profile_properties(profile_id: str) -> Optional[Dict]:
    """
    Get T-slot profile properties and dimensions.
    
    Args:
        profile_id: Profile identifier (e.g., "40x40_standard", "80x80_standard")
    
    Returns:
        Dictionary with profile properties or None if not found
    """
    return TSLOT_PROFILES.get(profile_id)


def get_supplier_info(supplier_id: str) -> Optional[Dict]:
    """
    Get supplier contact and catalog information.
    
    Args:
        supplier_id: Supplier identifier (e.g., "makerbeam_australia")
    
    Returns:
        Dictionary with supplier info or None if not found
    """
    return SUPPLIERS.get(supplier_id)


def list_available_profiles(min_size_mm: Optional[int] = None,
                            max_size_mm: Optional[int] = None) -> List[Dict]:
    """
    List available T-slot profiles with optional size filtering.
    
    Args:
        min_size_mm: Minimum width/height in mm
        max_size_mm: Maximum width/height in mm
    
    Returns:
        List of profile dictionaries with IDs and properties
    """
    profiles = []
    
    for profile_id, data in TSLOT_PROFILES.items():
        width = data['dimensions']['width_mm']
        height = data['dimensions']['height_mm']
        max_dim = max(width, height)
        
        if min_size_mm and max_dim < min_size_mm:
            continue
        if max_size_mm and max_dim > max_size_mm:
            continue
        
        profiles.append({
            'id': profile_id,
            'name': data['name'],
            'size': f"{width}x{height}mm",
            'weight_kg_m': data['mechanical']['weight_per_meter_kg'],
            'cost_aud_m': data['cost_aud_per_meter'],
            'material': data['material']
        })
    
    return sorted(profiles, key=lambda x: x['cost_aud_m'])


def list_available_materials() -> List[Dict]:
    """
    List all available aluminum alloys.
    
    Returns:
        List of material dictionaries with IDs and key properties
    """
    materials = []
    
    for material_id, data in ALUMINUM_ALLOYS.items():
        materials.append({
            'id': material_id,
            'name': data['name'],
            'yield_strength_mpa': data['properties']['yield_strength_mpa'],
            'elastic_modulus_mpa': data['properties']['elastic_modulus_mpa'],
            'density_kg_m3': data['properties']['density_kg_m3']
        })
    
    return materials


def recommend_profile_for_load(
    span_mm: float,
    load_kg: float,
    max_deflection_ratio: int = 360,
    safety_factor_target: float = 2.0
) -> Optional[Dict]:
    """
    Recommend the most economical T-slot profile for given load conditions.
    
    Args:
        span_mm: Beam span in millimeters
        load_kg: Total load in kilograms (center load assumed)
        max_deflection_ratio: Maximum span/deflection ratio (default 360 = L/360)
        safety_factor_target: Minimum safety factor (default 2.0)
    
    Returns:
        Dictionary with recommended profile or None if no suitable profile
    """
    from .structural_analysis import calculate_beam_deflection
    
    suitable_profiles = []
    
    for profile_id in TSLOT_PROFILES.keys():
        try:
            result = calculate_beam_deflection(
                length_mm=span_mm,
                load_kg=load_kg,
                profile_id=profile_id,
                support_type='simply_supported'
            )
            
            # Check if profile meets criteria
            deflection_ok = result['deflection_mm'] <= (span_mm / max_deflection_ratio)
            safety_ok = result['safety_factor'] >= safety_factor_target
            
            if deflection_ok and safety_ok:
                profile = TSLOT_PROFILES[profile_id]
                suitable_profiles.append({
                    'profile_id': profile_id,
                    'name': profile['name'],
                    'cost_aud_m': profile['cost_aud_per_meter'],
                    'deflection_mm': result['deflection_mm'],
                    'safety_factor': result['safety_factor'],
                    'weight_kg_m': profile['mechanical']['weight_per_meter_kg']
                })
        except Exception as e:
            # Skip profiles that cause calculation errors
            continue
    
    if not suitable_profiles:
        return None
    
    # Return cheapest suitable profile
    return sorted(suitable_profiles, key=lambda x: x['cost_aud_m'])[0]


def get_profile_for_application(application: str) -> List[str]:
    """
    Get recommended profile IDs for common applications.
    
    Args:
        application: Application name (e.g., "campervan_bed", "kitchen_frame")
    
    Returns:
        List of recommended profile IDs
    """
    recommendations = {
        'campervan_bed': ['40x40_standard', '40x40_heavy', '40x80_standard'],
        'campervan_kitchen': ['40x40_standard', '30x30_standard'],
        'workbench': ['40x40_standard', '60x60_standard'],
        'light_frame': ['20x20_light', '30x30_standard'],
        'heavy_machinery': ['60x60_standard', '80x80_standard'],
        'display_stand': ['20x20_light', '30x30_standard', '40x40_light'],
        'enclosure': ['30x30_standard', '40x40_standard'],
        'gantry': ['60x60_standard', '80x80_standard', '40x80_standard']
    }
    
    return recommendations.get(application, ['40x40_standard'])


def calculate_total_cost(
    profile_id: str,
    length_mm: float,
    quantity: int = 1,
    supplier_id: str = 'makerbeam_australia'
) -> Dict:
    """
    Calculate total cost for profile purchase including cuts.
    
    Args:
        profile_id: Profile identifier
        length_mm: Length per piece in mm
        quantity: Number of pieces
        supplier_id: Supplier to use
    
    Returns:
        Cost breakdown dictionary
    """
    profile = TSLOT_PROFILES.get(profile_id)
    supplier = SUPPLIERS.get(supplier_id)
    
    if not profile or not supplier:
        return {'error': 'Profile or supplier not found'}
    
    # Get supplier pricing for this profile
    supplier_profile = supplier['profiles'].get(profile_id)
    if not supplier_profile:
        return {'error': f'Supplier does not stock {profile_id}'}
    
    # Calculate costs
    length_m = length_mm / 1000
    material_cost = supplier_profile['price_aud_per_meter'] * length_m * quantity
    
    # Add cutting fee if applicable
    cut_cost = 0
    if supplier_profile.get('cut_to_length'):
        cut_cost = supplier_profile.get('cut_fee_aud', 0) * quantity
    
    total_cost = material_cost + cut_cost
    
    # Check shipping
    shipping_cost = 0
    threshold = supplier['shipping'].get('free_shipping_threshold_aud', 0)
    if total_cost < threshold:
        shipping_cost = supplier['shipping'].get('australia_shipping_aud', 0)
    
    grand_total = total_cost + shipping_cost
    
    return {
        'profile': profile['name'],
        'supplier': supplier['name'],
        'quantity': quantity,
        'length_mm_each': length_mm,
        'costs': {
            'material_aud': round(material_cost, 2),
            'cutting_aud': round(cut_cost, 2),
            'subtotal_aud': round(total_cost, 2),
            'shipping_aud': round(shipping_cost, 2),
            'total_aud': round(grand_total, 2)
        },
        'price_per_unit_aud': round(grand_total / quantity, 2),
        'supplier_part_number': supplier_profile['part_number'],
        'delivery_days': supplier['shipping']['typical_delivery_days']
    }


if __name__ == '__main__':
    # Test the module
    print("Testing Material Database Module\n")
    
    print("1. Available Materials:")
    for mat in list_available_materials():
        print(f"   - {mat['name']}: {mat['yield_strength_mpa']}MPa yield")
    
    print("\n2. Available Profiles (40-60mm):")
    for prof in list_available_profiles(min_size_mm=40, max_size_mm=60):
        print(f"   - {prof['name']}: ${prof['cost_aud_m']:.2f}/m")
    
    print("\n3. Recommend Profile for 1900mm span, 200kg load:")
    rec = recommend_profile_for_load(1900, 200)
    if rec:
        print(f"   - {rec['name']}: ${rec['cost_aud_m']:.2f}/m")
        print(f"     Deflection: {rec['deflection_mm']:.2f}mm, SF: {rec['safety_factor']:.1f}")
    
    print("\n4. Cost Calculation (4x 1900mm 40x40_standard):")
    cost = calculate_total_cost('40x40_standard', 1900, 4)
    print(f"   - Total: ${cost['costs']['total_aud']:.2f}")
    print(f"   - Per unit: ${cost['price_per_unit_aud']:.2f}")
