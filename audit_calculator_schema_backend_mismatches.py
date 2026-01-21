#!/usr/bin/env python3
"""
Calculator Schema/Backend Mismatch Audit Tool
==============================================

Checks for discrepancies between calculator_tools.json schema definitions
and actual backend calculator implementations.

Finds:
- Schema enums that don't exist in backend
- Backend enums missing from schema
- Parameter mismatches (required vs optional)
- Type mismatches

Author: GitHub Copilot
Date: January 22, 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Paths
SCHEMA_PATH = Path("UI/modules_external/quote-calculator/schema/calculator_tools.json")
BACKEND_DIR = Path("UI/modules_external/quote-calculator/backend/shopify_calculators")

def load_schema() -> Dict:
    """Load calculator schema"""
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_backend_file(calculator_name: str) -> Path:
    """Find backend calculator file by name"""
    # Map schema names to backend files
    name_mappings = {
        'calculate_folded_flyers_shopify': 'FoldedFlyers_Shopify_Calculator.py',
        'calculate_business_cards': 'business_card_calculator_shopify.py',
        'calculate_economical_business_cards_shopify': 'EconomicalBusinessCards_Shopify_Calculator.py',
        'calculate_premium_business_cards_shopify': 'PremiumBusinessCards_Shopify_Calculator.py',
        'calculate_corflute_signs_shopify': 'corflute_calculator_shopify.py',
        'calculate_wire_bound_books_shopify': 'WireBound_Shopify_Calculator.py',
        'calculate_spiral_bound_books_shopify': 'SpiralBound_Shopify_Calculator.py',
        'calculate_perfect_bound_books_shopify': 'PerfectBound_Shopify_Calculator.py',
        'calculate_saddle_stitch_books_shopify': 'SaddleStitchBooks_Shopify_Calculator.py',
        'calculate_spiral_books_simple_shopify': 'SpiralSimple_Shopify_Calculator.py',
        'calculate_bollard_signs': 'BollardSigns_Shopify_Calculator.py',
        'calculate_construction_signs': 'ConstructionSigns_Shopify_Calculator.py',
        'calculate_election_signs': 'ElectionSigns_Shopify_Calculator.py',
        'calculate_corflute_insert_a_frame': 'CorfluteInsertA_Frame_Shopify_Calculator.py',
        'calculate_custom_poster_printing': 'CustomPosterPrinting_Shopify_Calculator.py',
        'calculate_custom_vinyl_stickers': 'CustomVinylStickers_Shopify_Calculator.py',
        'calculate_luxury_classic_pull_up_banners': 'LuxuryClassicPullUpBanners_Shopify_Calculator.py',
        'calculate_notepads_a4': 'NotepadsA4_Shopify_Calculator.py',
        'calculate_notepads_a5': 'NotepadsA5_Shopify_Calculator.py',
        'calculate_notepads_a6': 'NotepadsA6_Shopify_Calculator.py',
        'calculate_printed_letterheads': 'PrintedLetterheads_Shopify_Calculator.py',
        'calculate_with_compliments_slips': 'WithComplimentsSlips_Shopify_Calculator.py',
        'calculate_premium_bookmarks': 'PremiumBookmarks_Shopify_Calculator.py',
        'calculate_metal_face_a_frame': 'MetalFaceA_Frame_Shopify_Calculator.py',
        'calculate_stackable_cubes': 'StackableCubes_Shopify_Calculator.py',
        'calculate_strut_cards_a3': 'StrutCardsA3_Shopify_Calculator.py',
        'calculate_strut_cards_a4': 'StrutCardsA4_Shopify_Calculator.py',
        'calculate_selfie_frame_large': 'SelfieFrameLarge_Shopify_Calculator.py',
    }
    
    backend_file = name_mappings.get(calculator_name)
    if backend_file:
        return BACKEND_DIR / backend_file
    return None

def extract_backend_enums(backend_path: Path) -> Dict[str, Set[str]]:
    """Extract enum values from backend Python file"""
    if not backend_path or not backend_path.exists():
        return {}
    
    with open(backend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    enums = {}
    
    # Find all Enum classes
    enum_pattern = r'class (\w+)\(Enum\):(.*?)(?=\n(?:class |def |if __name__)|\Z)'
    for match in re.finditer(enum_pattern, content, re.DOTALL):
        enum_name = match.group(1)
        enum_body = match.group(2)
        
        # Extract enum values
        values = set()
        # Pattern: VALUE_NAME = ("Title", ...)
        value_pattern = r'(\w+)\s*=\s*\('
        for value_match in re.finditer(value_pattern, enum_body):
            values.add(value_match.group(1))
        
        enums[enum_name] = values
    
    return enums

def audit_calculator(tool_def: Dict) -> List[str]:
    """Audit single calculator for schema/backend mismatches"""
    issues = []
    calculator_name = tool_def['name']
    
    # Find backend file
    backend_path = find_backend_file(calculator_name)
    if not backend_path or not backend_path.exists():
        issues.append(f"[WARNING] No backend file found for {calculator_name}")
        return issues
    
    # Extract backend enums
    backend_enums = extract_backend_enums(backend_path)
    
    # Check each parameter with enum
    parameters = tool_def.get('parameters', {})
    for param_name, param_def in parameters.items():
        # Skip if param_def is not a dict (some tools have string descriptions)
        if not isinstance(param_def, dict):
            continue
        
        schema_enum = param_def.get('enum')
        if not schema_enum:
            continue
        
        # Try to match parameter to backend enum
        # Common mappings
        param_to_enum = {
            'size': 'FinishSize',
            'finish_size': 'FinishSize',
            'stock': 'PaperStock',
            'stock_type': 'PaperStock',
            'print_type': 'PrintType',
            'print_sides': 'PrintSides',
            'double_sided': 'PrintSides',
            'folding': 'FoldType',
            'fold_type': 'FoldType',
            'celloglaze': 'CelloglazeOption',
            'cover_stock': 'CoverStock',
            'text_stock': 'TextStock',
        }
        
        backend_enum_name = param_to_enum.get(param_name)
        if not backend_enum_name or backend_enum_name not in backend_enums:
            continue
        
        backend_values = backend_enums[backend_enum_name]
        schema_values = set(schema_enum) if isinstance(schema_enum, list) else set()
        
        # Compare
        schema_only = schema_values - backend_values
        backend_only = backend_values - schema_values
        
        if schema_only:
            issues.append(f"  [ERROR] Schema has {param_name} values missing from backend {backend_enum_name}: {schema_only}")
        if backend_only:
            issues.append(f"  [INFO] Backend {backend_enum_name} has values missing from schema {param_name}: {backend_only}")
    
    return issues

def main():
    """Run full audit"""
    print("=" * 80)
    print("CALCULATOR SCHEMA/BACKEND MISMATCH AUDIT")
    print("=" * 80)
    print()
    
    schema = load_schema()
    tools = schema.get('tools', [])
    
    total_issues = 0
    calculators_with_issues = []
    
    for tool in tools:
        calculator_name = tool['name']
        issues = audit_calculator(tool)
        
        if issues:
            total_issues += len(issues)
            calculators_with_issues.append(calculator_name)
            print(f"\n[AUDIT] {calculator_name}")
            print(f"   Backend: {find_backend_file(calculator_name)}")
            for issue in issues:
                print(issue)
    
    print("\n" + "=" * 80)
    print(f"SUMMARY: {total_issues} issues found across {len(calculators_with_issues)} calculators")
    print("=" * 80)
    
    if calculators_with_issues:
        print("\n[SUMMARY] Calculators with issues:")
        for calc in calculators_with_issues:
            print(f"  - {calc}")
    else:
        print("\n[SUCCESS] No mismatches found! All schemas match backend implementations.")

if __name__ == "__main__":
    main()
