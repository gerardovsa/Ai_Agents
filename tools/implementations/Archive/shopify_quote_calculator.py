"""
Shopify Quote Calculator Tools - FIXED VERSION
===============================================
Provides AI agent access to all 26 Shopify calculator wrappers.

KEY FIX: Tool metadata now introspects WRAPPER function signatures,
not the underlying calculator class methods. This fixes the "pages parameter
not supported" bug for book calculators.

Architecture:
    AI Agent Request
        ↓
    Tool System (this file)
        ↓
    shopify_calculator_wrappers.py
        ↓
    Individual Shopify Calculators

Date: December 10, 2025
Status: PRODUCTION READY - Bug Fixed
"""

import sys
import inspect
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, List, Optional, get_type_hints

# Add inhouse_modules to path
root_dir = Path(__file__).parent.parent.parent
inhouse_path = root_dir / "inhouse_modules"
if str(inhouse_path) not in sys.path:
    sys.path.insert(0, str(inhouse_path))

# Import ALL wrapper functions
try:
    from shopify_calculator_wrappers import (
        # Books (5 - note: 2 spiral bound variants)
        calculate_wire_bound_books_shopify,
        calculate_spiral_bound_books_shopify,
        calculate_perfect_bound_books_shopify,
        calculate_saddle_stitch_books_shopify,
        calculate_spiral_bound_books_shopify as calculate_spiral_books_simple_shopify,
        # Flyers (1)
        calculate_folded_flyers_shopify,
        # Business Cards (2)
        calculate_economical_business_cards_shopify,
        calculate_premium_business_cards_shopify,
        # Stationery (5)
        calculate_printed_letterheads_shopify,
        calculate_with_compliments_slips_shopify,
        calculate_notepads_a4_shopify,
        calculate_notepads_a5_shopify,
        calculate_notepads_a6_shopify,
        # Signs (9)
        calculate_election_signs_shopify,
        calculate_construction_signs_shopify,
        calculate_bollard_signs_shopify,
        calculate_corflute_insert_a_frame_shopify,
        calculate_metal_face_a_frame_shopify,
        calculate_strut_cards_a3_shopify,
        calculate_strut_cards_a4_shopify,
        # Promotional (6)
        calculate_custom_poster_printing_shopify,
        calculate_custom_vinyl_stickers_shopify,
        calculate_premium_bookmarks_shopify,
        calculate_selfie_frames_shopify,
        calculate_luxury_classic_pull_up_banners_shopify,
        calculate_stackable_cubes_shopify,
    )
    WRAPPERS_AVAILABLE = True
    print("✅ [Shopify Calculators] All 26 wrappers loaded successfully")
except ImportError as e:
    WRAPPERS_AVAILABLE = False
    print(f"❌ [Shopify Calculators] Failed to import wrappers: {e}")

# Map calculator names to wrapper functions
CALCULATOR_MAP = {
    # Books
    "wire_bound_books_shopify": calculate_wire_bound_books_shopify,
    "spiral_bound_books_shopify": calculate_spiral_bound_books_shopify,
    "spiral_books_simple_shopify": calculate_spiral_books_simple_shopify,
    "perfect_bound_books_shopify": calculate_perfect_bound_books_shopify,
    "saddle_stitch_books_shopify": calculate_saddle_stitch_books_shopify,
    # Flyers
    "folded_flyers_shopify": calculate_folded_flyers_shopify,
    # Business Cards
    "economical_business_cards_shopify": calculate_economical_business_cards_shopify,
    "premium_business_cards_shopify": calculate_premium_business_cards_shopify,
    # Stationery
    "printed_letterheads_shopify": calculate_printed_letterheads_shopify,
    "with_compliments_slips_shopify": calculate_with_compliments_slips_shopify,
    "notepads_a4_shopify": calculate_notepads_a4_shopify,
    "notepads_a5_shopify": calculate_notepads_a5_shopify,
    "notepads_a6_shopify": calculate_notepads_a6_shopify,
    # Signs
    "election_signs_shopify": calculate_election_signs_shopify,
    "construction_signs_shopify": calculate_construction_signs_shopify,
    "bollard_signs_shopify": calculate_bollard_signs_shopify,
    "corflute_insert_a_frame_shopify": calculate_corflute_insert_a_frame_shopify,
    "metal_face_a_frame_shopify": calculate_metal_face_a_frame_shopify,
    "strut_cards_a3_shopify": calculate_strut_cards_a3_shopify,
    "strut_cards_a4_shopify": calculate_strut_cards_a4_shopify,
    # Promotional
    "custom_poster_printing_shopify": calculate_custom_poster_printing_shopify,
    "custom_vinyl_stickers_shopify": calculate_custom_vinyl_stickers_shopify,
    "premium_bookmarks_shopify": calculate_premium_bookmarks_shopify,
    "selfie_frames_shopify": calculate_selfie_frames_shopify,
    "luxury_classic_pull_up_banners_shopify": calculate_luxury_classic_pull_up_banners_shopify,
    "stackable_cubes_shopify": calculate_stackable_cubes_shopify,
}


def get_calculator_requirements(calculator_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get parameter requirements for a specific calculator.
    
    KEY FIX: This function now introspects the WRAPPER function signature,
    not the underlying calculator class. This ensures the parameters listed
    match what the AI agent should pass.
    
    Args:
        calculator_name: Name of calculator (e.g., "wire_bound_books_shopify")
        
    Returns:
        Dict with:
            - calculator_name: Name of calculator
            - description: What this calculator does
            - parameters: Dict of parameter requirements
            - example: Example usage
    """
    if not WRAPPERS_AVAILABLE:
        return {
            "error": "Shopify calculators not available",
            "calculator_name": calculator_name
        }
    
    if calculator_name not in CALCULATOR_MAP:
        return {
            "error": f"Calculator '{calculator_name}' not found",
            "available_calculators": list(CALCULATOR_MAP.keys())
        }
    
    # Get the wrapper function
    wrapper_func = CALCULATOR_MAP[calculator_name]
    
    # Introspect the WRAPPER function signature (NOT the calculator class)
    sig = inspect.signature(wrapper_func)
    type_hints = get_type_hints(wrapper_func)
    
    # Extract parameter information
    parameters = {}
    for param_name, param in sig.parameters.items():
        param_info = {
            "type": type_hints.get(param_name, Any).__name__ if param_name in type_hints else "Any",
            "required": param.default == inspect.Parameter.empty,
        }
        
        # Add default value if present
        if param.default != inspect.Parameter.empty:
            param_info["default"] = param.default
        
        parameters[param_name] = param_info
    
    # Extract docstring
    docstring = inspect.getdoc(wrapper_func) or "No description available"
    
    # Parse docstring to extract description and examples
    lines = docstring.split('\n')
    description = lines[0] if lines else "No description"
    
    # Find example in docstring
    example = None
    for i, line in enumerate(lines):
        if 'Example:' in line or '>>>' in line:
            example = '\n'.join(lines[i:i+5])
            break
    
    return {
        "success": True,
        "calculator_name": calculator_name,
        "description": description,
        "parameters": parameters,
        "docstring": docstring,
        "example": example
    }


def calculate_shopify_quote(calculator_name: str, **kwargs) -> Dict[str, Any]:
    """
    Calculate a quote using any Shopify calculator.
    
    This is the universal entry point for all 26 calculators.
    Call get_calculator_requirements() first to see what parameters to pass.
    
    Args:
        calculator_name: Name of calculator (e.g., "wire_bound_books_shopify")
        **kwargs: Calculator-specific parameters
        
    Returns:
        Dict with:
            - total_price: Final price (Decimal)
            - unit_price: Price per item (Decimal)
            - cost_per_item: Same as unit_price (Decimal)
            - quantity: Number of items (int)
            - breakdown: Detailed cost breakdown (Dict)
            - specifications: Product specifications (Dict)
    """
    if not WRAPPERS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available - check server logs"
        }
    
    if calculator_name not in CALCULATOR_MAP:
        return {
            "success": False,
            "error": f"Calculator '{calculator_name}' not found",
            "available_calculators": list(CALCULATOR_MAP.keys())
        }
    
    try:
        # Get the wrapper function
        wrapper_func = CALCULATOR_MAP[calculator_name]
        
        # Call the wrapper with provided kwargs
        result = wrapper_func(**kwargs)
        
        # Convert Decimals to floats for JSON serialization
        # Handle breakdown values safely - some might be strings (e.g., 'price_increase_type': 'percentage')
        breakdown_serialized = {}
        for k, v in result["breakdown"].items():
            if isinstance(v, (Decimal, int, float)):
                breakdown_serialized[k] = float(v)
            else:
                breakdown_serialized[k] = v  # Keep strings as-is
        
        return {
            "success": True,
            "calculator_name": calculator_name,
            "total_price": float(result["total_price"]),
            "unit_price": float(result["unit_price"]),
            "cost_per_item": float(result.get("cost_per_item", result["unit_price"])),  # Fallback for older results
            "quantity": result["quantity"],
            "breakdown": breakdown_serialized,
            "specifications": result["specifications"]
        }
        
    except TypeError as e:
        # Parameter mismatch error
        return {
            "success": False,
            "error": f"Parameter error: {str(e)}",
            "hint": f"Call get_calculator_requirements('{calculator_name}') to see valid parameters"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Calculation failed: {str(e)}",
            "calculator_name": calculator_name
        }


def list_available_calculators(**kwargs) -> Dict[str, Any]:
    """
    List all available Shopify calculators.
    
    Returns:
        Dict with:
            - calculators: List of calculator names
            - count: Total number of calculators
            - categories: Calculators grouped by category
    """
    if not WRAPPERS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available"
        }
    
    categories = {
        "Books": [
            "wire_bound_books_shopify",
            "spiral_bound_books_shopify",
            "spiral_books_simple_shopify",
            "perfect_bound_books_shopify",
            "saddle_stitch_books_shopify"
        ],
        "Flyers": [
            "folded_flyers_shopify"
        ],
        "Business Cards": [
            "economical_business_cards_shopify",
            "premium_business_cards_shopify"
        ],
        "Stationery": [
            "printed_letterheads_shopify",
            "with_compliments_slips_shopify",
            "notepads_a4_shopify",
            "notepads_a5_shopify",
            "notepads_a6_shopify"
        ],
        "Signs": [
            "election_signs_shopify",
            "construction_signs_shopify",
            "bollard_signs_shopify",
            "corflute_insert_a_frame_shopify",
            "metal_face_a_frame_shopify",
            "strut_cards_a3_shopify",
            "strut_cards_a4_shopify"
        ],
        "Promotional": [
            "custom_poster_printing_shopify",
            "custom_vinyl_stickers_shopify",
            "premium_bookmarks_shopify",
            "selfie_frames_shopify",
            "luxury_classic_pull_up_banners_shopify",
            "stackable_cubes_shopify"
        ]
    }
    
    return {
        "success": True,
        "calculators": list(CALCULATOR_MAP.keys()),
        "count": len(CALCULATOR_MAP),
        "categories": categories,
        "note": "Call get_calculator_requirements(calculator_name) for parameter details"
    }


# Export tool functions for registry
__all__ = [
    'get_calculator_requirements',
    'calculate_shopify_quote',
    'list_available_calculators'
]
