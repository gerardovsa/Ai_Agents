"""
Structural Analysis Module
Beam deflection, stress analysis, and safety factor calculations
"""

import math
from typing import Dict, Tuple, List
from .material_database import get_profile_properties, get_material_properties


def calculate_beam_deflection(
    length_mm: float,
    load_kg: float,
    profile_id: str,
    support_type: str = 'simply_supported',
    load_position: str = 'center'
) -> Dict:
    """
    Calculate beam deflection, stress, and safety factor for T-slot beam.
    
    Args:
        length_mm: Beam span in millimeters
        load_kg: Applied load in kilograms
        profile_id: T-slot profile identifier
        support_type: 'simply_supported', 'cantilever', or 'fixed_both'
        load_position: 'center', 'uniform', or 'point' (for cantilever: 'end')
    
    Returns:
        Dictionary with deflection, stress, safety_factor, and pass/fail status
    """
    # Get profile and material properties
    profile = get_profile_properties(profile_id)
    if not profile:
        raise ValueError(f"Profile '{profile_id}' not found")
    
    material = get_material_properties(profile['material'])
    if not material:
        raise ValueError(f"Material '{profile['material']}' not found")
    
    # Convert units
    L_m = length_mm / 1000  # mm to m
    F_n = load_kg * 9.81    # kg to Newtons
    E_pa = material['properties']['elastic_modulus_mpa'] * 1e6  # MPa to Pa
    I_m4 = profile['section_properties']['moment_inertia_x_mm4'] * 1e-12  # mm⁴ to m⁴
    c_m = profile['dimensions']['height_mm'] / 2000  # Distance to neutral axis (m)
    
    # Calculate deflection based on support and load type
    if support_type == 'simply_supported':
        if load_position == 'center':
            # Simply supported beam, center point load
            delta_m = (F_n * L_m**3) / (48 * E_pa * I_m4)
            M_max = (F_n * L_m) / 4  # Maximum moment at center
        elif load_position == 'uniform':
            # Simply supported beam, uniform distributed load
            w_n_m = F_n / L_m  # Load per meter
            delta_m = (5 * w_n_m * L_m**4) / (384 * E_pa * I_m4)
            M_max = (w_n_m * L_m**2) / 8
        else:
            # Default to center load
            delta_m = (F_n * L_m**3) / (48 * E_pa * I_m4)
            M_max = (F_n * L_m) / 4
            
    elif support_type == 'cantilever':
        if load_position == 'end':
            # Cantilever beam, end point load
            delta_m = (F_n * L_m**3) / (3 * E_pa * I_m4)
            M_max = F_n * L_m  # Maximum moment at fixed end
        elif load_position == 'uniform':
            # Cantilever beam, uniform distributed load
            w_n_m = F_n / L_m
            delta_m = (w_n_m * L_m**4) / (8 * E_pa * I_m4)
            M_max = (w_n_m * L_m**2) / 2
        else:
            # Default to end load
            delta_m = (F_n * L_m**3) / (3 * E_pa * I_m4)
            M_max = F_n * L_m
            
    elif support_type == 'fixed_both':
        if load_position == 'center':
            # Fixed-fixed beam, center point load
            delta_m = (F_n * L_m**3) / (192 * E_pa * I_m4)
            M_max = (F_n * L_m) / 8
        elif load_position == 'uniform':
            # Fixed-fixed beam, uniform distributed load
            w_n_m = F_n / L_m
            delta_m = (w_n_m * L_m**4) / (384 * E_pa * I_m4)
            M_max = (w_n_m * L_m**2) / 12
        else:
            delta_m = (F_n * L_m**3) / (192 * E_pa * I_m4)
            M_max = (F_n * L_m) / 8
    else:
        raise ValueError(f"Unknown support_type: {support_type}")
    
    # Convert deflection to mm
    delta_mm = delta_m * 1000
    
    # Calculate maximum stress (bending stress)
    stress_pa = (M_max * c_m) / I_m4
    stress_mpa = stress_pa / 1e6
    
    # Calculate safety factor
    yield_strength_mpa = material['properties']['yield_strength_mpa']
    safety_factor = yield_strength_mpa / stress_mpa if stress_mpa > 0 else float('inf')
    
    # Deflection limit check (L/360 for general structures)
    max_deflection_ratio = profile['mechanical'].get('max_deflection_ratio', 360)
    max_allowed_deflection_mm = length_mm / max_deflection_ratio
    deflection_passes = delta_mm <= max_allowed_deflection_mm
    
    # Safety factor check (minimum 2.0)
    safety_passes = safety_factor >= 2.0
    
    overall_passes = deflection_passes and safety_passes
    
    return {
        'profile_id': profile_id,
        'profile_name': profile['name'],
        'material': profile['material'],
        'support_type': support_type,
        'load_position': load_position,
        'span_mm': length_mm,
        'load_kg': load_kg,
        'deflection_mm': round(delta_mm, 3),
        'max_allowed_deflection_mm': round(max_allowed_deflection_mm, 3),
        'deflection_ratio': f"L/{int(length_mm / delta_mm)}" if delta_mm > 0 else "L/∞",
        'max_stress_mpa': round(stress_mpa, 2),
        'yield_strength_mpa': yield_strength_mpa,
        'safety_factor': round(safety_factor, 2),
        'checks': {
            'deflection_ok': deflection_passes,
            'safety_ok': safety_passes,
            'overall_pass': overall_passes
        },
        'recommendation': 'PASS - Design is adequate' if overall_passes else 'FAIL - Increase profile size or reduce load/span'
    }


def analyze_multiple_profiles(
    length_mm: float,
    load_kg: float,
    support_type: str = 'simply_supported',
    profile_ids: List[str] = None
) -> List[Dict]:
    """
    Analyze multiple profiles for comparison.
    
    Args:
        length_mm: Beam span in mm
        load_kg: Load in kg
        support_type: Support condition
        profile_ids: List of profile IDs to compare (None = all profiles)
    
    Returns:
        List of analysis results sorted by cost
    """
    from .material_database import TSLOT_PROFILES
    
    if profile_ids is None:
        profile_ids = list(TSLOT_PROFILES.keys())
    
    results = []
    
    for profile_id in profile_ids:
        try:
            analysis = calculate_beam_deflection(length_mm, load_kg, profile_id, support_type)
            profile = TSLOT_PROFILES[profile_id]
            
            # Add cost information
            analysis['cost_aud_per_meter'] = profile['cost_aud_per_meter']
            analysis['total_cost_aud'] = profile['cost_aud_per_meter'] * (length_mm / 1000)
            
            results.append(analysis)
        except Exception as e:
            # Skip profiles that cause errors
            continue
    
    # Sort by cost (cheapest first)
    return sorted(results, key=lambda x: x.get('cost_aud_per_meter', float('inf')))


def calculate_distributed_load_capacity(
    length_mm: float,
    profile_id: str,
    support_type: str = 'simply_supported',
    safety_factor_target: float = 2.0
) -> Dict:
    """
    Calculate maximum uniformly distributed load capacity for a beam.
    
    Args:
        length_mm: Beam span in mm
        profile_id: T-slot profile ID
        support_type: Support condition
        safety_factor_target: Target safety factor
    
    Returns:
        Maximum load capacity and details
    """
    # Binary search for max load
    min_load = 1
    max_load = 5000
    tolerance = 0.1
    
    while max_load - min_load > tolerance:
        mid_load = (min_load + max_load) / 2
        
        result = calculate_beam_deflection(
            length_mm=length_mm,
            load_kg=mid_load,
            profile_id=profile_id,
            support_type=support_type,
            load_position='uniform'
        )
        
        if result['checks']['overall_pass'] and result['safety_factor'] >= safety_factor_target:
            min_load = mid_load
        else:
            max_load = mid_load
    
    # Get final result at max safe load
    final_result = calculate_beam_deflection(
        length_mm=length_mm,
        load_kg=min_load,
        profile_id=profile_id,
        support_type=support_type,
        load_position='uniform'
    )
    
    return {
        'max_load_kg': round(min_load, 1),
        'max_load_per_meter_kg': round(min_load / (length_mm / 1000), 1),
        'profile': final_result['profile_name'],
        'deflection_at_max_mm': final_result['deflection_mm'],
        'safety_factor_at_max': final_result['safety_factor'],
        'details': final_result
    }


def calculate_column_buckling(
    height_mm: float,
    profile_id: str,
    load_kg: float,
    end_conditions: str = 'pinned_pinned'
) -> Dict:
    """
    Calculate column buckling safety for vertical T-slot member.
    
    Args:
        height_mm: Column height in mm
        profile_id: T-slot profile ID
        load_kg: Axial load in kg
        end_conditions: 'pinned_pinned' (K=1.0), 'fixed_free' (K=2.0), 
                       'fixed_pinned' (K=0.7), 'fixed_fixed' (K=0.5)
    
    Returns:
        Buckling analysis results
    """
    profile = get_profile_properties(profile_id)
    material = get_material_properties(profile['material'])
    
    # Effective length factors
    K_factors = {
        'pinned_pinned': 1.0,
        'fixed_free': 2.0,
        'fixed_pinned': 0.7,
        'fixed_fixed': 0.5
    }
    K = K_factors.get(end_conditions, 1.0)
    
    # Convert units
    L_m = height_mm / 1000
    L_eff = K * L_m
    F_n = load_kg * 9.81
    E_pa = material['properties']['elastic_modulus_mpa'] * 1e6
    I_m4 = profile['section_properties']['moment_inertia_x_mm4'] * 1e-12
    A_m2 = profile['section_properties']['area_mm2'] * 1e-6
    
    # Euler buckling load
    P_critical_n = (math.pi**2 * E_pa * I_m4) / (L_eff**2)
    P_critical_kg = P_critical_n / 9.81
    
    # Safety factor against buckling
    safety_factor = P_critical_kg / load_kg if load_kg > 0 else float('inf')
    
    # Compressive stress
    stress_pa = F_n / A_m2
    stress_mpa = stress_pa / 1e6
    
    passes = safety_factor >= 2.0
    
    return {
        'profile': profile['name'],
        'height_mm': height_mm,
        'end_conditions': end_conditions,
        'effective_length_mm': L_eff * 1000,
        'applied_load_kg': load_kg,
        'critical_buckling_load_kg': round(P_critical_kg, 1),
        'safety_factor': round(safety_factor, 2),
        'compressive_stress_mpa': round(stress_mpa, 2),
        'passes': passes,
        'recommendation': 'PASS - Column is stable' if passes else 'FAIL - Risk of buckling, reduce height or increase profile size'
    }


if __name__ == '__main__':
    # Test the module
    print("Testing Structural Analysis Module\n")
    
    print("1. Beam Analysis (1900mm span, 200kg center load):")
    result = calculate_beam_deflection(1900, 200, '40x40_standard')
    print(f"   Profile: {result['profile_name']}")
    print(f"   Deflection: {result['deflection_mm']:.2f}mm ({result['deflection_ratio']})")
    print(f"   Stress: {result['max_stress_mpa']:.1f}MPa")
    print(f"   Safety Factor: {result['safety_factor']:.1f}")
    print(f"   Result: {result['recommendation']}")
    
    print("\n2. Compare Multiple Profiles:")
    comparisons = analyze_multiple_profiles(1900, 200, profile_ids=['40x40_light', '40x40_standard', '40x40_heavy'])
    for comp in comparisons:
        status = "✓" if comp['checks']['overall_pass'] else "✗"
        print(f"   {status} {comp['profile_name']}: SF={comp['safety_factor']:.1f}, ${comp['cost_aud_per_meter']:.2f}/m")
    
    print("\n3. Distributed Load Capacity (1900mm beam):")
    capacity = calculate_distributed_load_capacity(1900, '40x40_standard')
    print(f"   Max total load: {capacity['max_load_kg']:.1f}kg")
    print(f"   Max load/meter: {capacity['max_load_per_meter_kg']:.1f}kg/m")
    
    print("\n4. Column Buckling (2000mm height, 500kg):")
    column = calculate_column_buckling(2000, '40x40_standard', 500)
    print(f"   Critical load: {column['critical_buckling_load_kg']:.1f}kg")
    print(f"   Safety Factor: {column['safety_factor']:.1f}")
    print(f"   Result: {column['recommendation']}")
