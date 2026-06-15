"""
Parameter Translator for GOD Calculator Integration

This module provides translation functions to convert high-level calculator parameters
(like size="A5") into low-level parameters (like width=148, height=210) required by
GOD (database-driven) calculators.

PURPOSE:
    The wrapper layer (calculator_wrapper.py, inhouse_wrapper.py) accepts high-level
    parameters for user convenience, but GOD calculators expect low-level parameters
    that match their database schema.

USAGE:
    from parameter_translator import translate_parameters
    
    high_level = {
        "size": "A5",
        "colour": "Full Colour",
        "finish": "Gloss Celloglaze",
        "quantity": 500
    }
    
    low_level = translate_parameters(high_level, calculator_type="flyers")
    # Returns: {
    #     "width": 148,
    #     "height": 210,
    #     "colour": "4/0",
    #     "finish": "Gloss Celloglaze",
    #     "quantity": 500
    # }

ARCHITECTURE:
    1. Size translation: A4, A5, DL, etc. → width × height in mm
    2. Colour translation: "Full Colour" → "4/0", "4/4"
    3. Finish translation: User-friendly names → database values
    4. Material translation: "Standard", "Premium" → specific stock types
    5. Binding translation: "Saddle Stitch" → binding IDs

LAST MODIFIED: 2026-01-03 - Initial creation
"""

from typing import Dict, Any, Optional
from decimal import Decimal

# ============================================================================
# SIZE TRANSLATIONS
# ============================================================================

SIZE_TO_DIMENSIONS = {
    # Standard paper sizes (mm)
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "A3": (297, 420),
    "DL": (99, 210),
    
    # Common business sizes
    "Business Card": (90, 55),
    "Postcard": (148, 105),
    
    # Sign sizes (mm)
    "600x900": (600, 900),
    "900x1200": (900, 1200),
    "1200x1800": (1200, 1800),
    
    # US Letter sizes (mm)
    "Letter": (216, 279),
    "Legal": (216, 356),
}


def translate_size(size: str) -> Dict[str, int]:
    """
    Translate size code to width and height
    
    Args:
        size: Size code like "A4", "A5", "DL", "600x900"
    
    Returns:
        dict: {"width": int, "height": int}
    
    Raises:
        ValueError: If size code is not recognized
    """
    if size in SIZE_TO_DIMENSIONS:
        width, height = SIZE_TO_DIMENSIONS[size]
        return {"width": width, "height": height}
    
    # Try parsing "WIDTHxHEIGHT" format
    if "x" in size.lower():
        try:
            parts = size.lower().split("x")
            width = int(parts[0])
            height = int(parts[1])
            return {"width": width, "height": height}
        except (ValueError, IndexError):
            pass
    
    raise ValueError(f"Unknown size code: {size}")


# ============================================================================
# COLOUR TRANSLATIONS
# ============================================================================

COLOUR_TO_CODE = {
    # Flyers, posters, leaflets
    "Full Colour": "4/0",
    "Full Colour Both Sides": "4/4",
    "Black and White": "1/0",
    "Black and White Both Sides": "1/1",
    
    # Business cards (special cases)
    "4 Colour Front Only": "4/0",
    "4 Colour Both Sides": "4/4",
    "Single Colour": "1/0",
}


def translate_colour(colour: str, product_type: Optional[str] = None) -> str:
    """
    Translate user-friendly colour name to database code
    
    Args:
        colour: User-friendly name like "Full Colour"
        product_type: Optional product type for context
    
    Returns:
        str: Database code like "4/0" or "4/4"
    """
    if colour in COLOUR_TO_CODE:
        return COLOUR_TO_CODE[colour]
    
    # Already in correct format
    if "/" in colour:
        return colour
    
    # Default to full colour if unknown
    return "4/0"


# ============================================================================
# FINISH TRANSLATIONS
# ============================================================================

FINISH_ALIASES = {
    # Celloglaze variants
    "Gloss Celloglaze": "Gloss Celloglaze",
    "Gloss": "Gloss Celloglaze",
    "Matt Celloglaze": "Matt Celloglaze",
    "Matt": "Matt Celloglaze",
    "Uncoated": "Uncoated",
    "None": "Uncoated",
    
    # Lamination
    "Gloss Lamination": "Gloss Lamination",
    "Matt Lamination": "Matt Lamination",
    "Velvet Lamination": "Velvet Lamination",
}


def translate_finish(finish: str) -> str:
    """
    Translate finish alias to standard database value
    
    Args:
        finish: User input like "Gloss" or "Matt"
    
    Returns:
        str: Standard database value
    """
    return FINISH_ALIASES.get(finish, finish)


# ============================================================================
# MATERIAL/STOCK TRANSLATIONS
# ============================================================================

MATERIAL_TO_STOCK = {
    # Paper weights for flyers/leaflets
    "Standard": "130gsm Gloss",
    "Premium": "170gsm Gloss",
    "Heavy": "250gsm Gloss",
    
    # Business card stock
    "Standard Card": "350gsm Silk",
    "Premium Card": "400gsm Silk",
    "Luxury Card": "540gsm Uncoated",
}


def translate_material(material: str, product_type: Optional[str] = None) -> str:
    """
    Translate material name to specific stock type
    
    Args:
        material: User-friendly material name
        product_type: Optional product type for context
    
    Returns:
        str: Specific stock type for database
    """
    return MATERIAL_TO_STOCK.get(material, material)


# ============================================================================
# BINDING TRANSLATIONS
# ============================================================================

BINDING_TO_ID = {
    "Saddle Stitch": 1,
    "Perfect Bound": 2,
    "Wire-O": 3,
    "Spiral": 4,
    "Comb": 5,
}


def translate_binding(binding: str) -> int:
    """
    Translate binding type to database ID
    
    Args:
        binding: User-friendly binding name
    
    Returns:
        int: Database binding ID
    """
    return BINDING_TO_ID.get(binding, 1)  # Default to Saddle Stitch


# ============================================================================
# MAIN TRANSLATION FUNCTION
# ============================================================================

def translate_parameters(
    params: Dict[str, Any],
    calculator_type: str
) -> Dict[str, Any]:
    """
    Translate high-level parameters to low-level GOD calculator parameters
    
    This is the main entry point for parameter translation. It applies all
    relevant translations based on the calculator type.
    
    Args:
        params: High-level parameters from wrapper
        calculator_type: Type of calculator ("flyers", "booklets", "letterheads", etc.)
    
    Returns:
        dict: Low-level parameters for GOD calculator
    
    Example:
        >>> params = {"size": "A5", "colour": "Full Colour", "quantity": 500}
        >>> translate_parameters(params, "flyers")
        {"width": 148, "height": 210, "colour": "4/0", "quantity": 500}
    """
    translated = params.copy()
    
    # 1. Translate size → width, height
    if "size" in translated:
        try:
            dimensions = translate_size(translated["size"])
            translated["width"] = dimensions["width"]
            translated["height"] = dimensions["height"]
            del translated["size"]  # Remove high-level param
        except ValueError as e:
            # Keep original if translation fails
            pass
    
    # 2. Translate colour
    if "colour" in translated:
        translated["colour"] = translate_colour(
            translated["colour"],
            product_type=calculator_type
        )
    
    # 3. Translate finish/celloglaze
    if "finish" in translated:
        translated["finish"] = translate_finish(translated["finish"])
    
    if "celloglaze" in translated:
        translated["celloglaze"] = translate_finish(translated["celloglaze"])
    
    # 4. Translate material/stock
    if "material" in translated:
        translated["stock"] = translate_material(
            translated["material"],
            product_type=calculator_type
        )
        del translated["material"]
    
    # 5. Translate binding
    if "binding" in translated and calculator_type in ["booklets", "books"]:
        translated["binding_id"] = translate_binding(translated["binding"])
        del translated["binding"]
    
    # 6. Convert numeric values to Decimal for precise calculations
    for key in ["quantity", "pages", "width", "height"]:
        if key in translated and not isinstance(translated[key], Decimal):
            try:
                translated[key] = Decimal(str(translated[key]))
            except (ValueError, TypeError):
                pass
    
    return translated


def get_required_parameters(calculator_type: str) -> list:
    """
    Get list of required low-level parameters for a calculator type
    
    Args:
        calculator_type: Type of calculator
    
    Returns:
        list: Required parameter names
    """
    REQUIRED_PARAMS = {
        "flyers": ["width", "height", "colour", "quantity"],
        "booklets": ["width", "height", "pages", "quantity"],
        "letterheads": ["width", "height", "colour", "quantity"],
        "perfect_bound": ["width", "height", "pages", "quantity"],
        "business_cards": ["width", "height", "celloglaze", "quantity"],
    }
    
    return REQUIRED_PARAMS.get(calculator_type, [])


def validate_parameters(
    params: Dict[str, Any],
    calculator_type: str
) -> tuple[bool, list]:
    """
    Validate that all required parameters are present
    
    Args:
        params: Parameters to validate
        calculator_type: Type of calculator
    
    Returns:
        tuple: (is_valid, list_of_missing_parameters)
    """
    required = get_required_parameters(calculator_type)
    missing = [param for param in required if param not in params]
    
    return (len(missing) == 0, missing)


# ============================================================================
# REVERSE TRANSLATION (for UI display)
# ============================================================================

def reverse_translate_size(width: int, height: int) -> str:
    """
    Convert width/height back to size code for UI display
    
    Args:
        width: Width in mm
        height: Height in mm
    
    Returns:
        str: Size code like "A4" or "600x900"
    """
    # Check standard sizes
    for size_code, (w, h) in SIZE_TO_DIMENSIONS.items():
        if w == width and h == height:
            return size_code
    
    # Return custom format
    return f"{width}x{height}"


def reverse_translate_colour(colour_code: str) -> str:
    """
    Convert colour code back to user-friendly name
    
    Args:
        colour_code: Database code like "4/0"
    
    Returns:
        str: User-friendly name
    """
    REVERSE_COLOUR = {
        "4/0": "Full Colour",
        "4/4": "Full Colour Both Sides",
        "1/0": "Black and White",
        "1/1": "Black and White Both Sides",
    }
    
    return REVERSE_COLOUR.get(colour_code, colour_code)


# ============================================================================
# TESTING UTILITIES
# ============================================================================

if __name__ == "__main__":
    # Test size translation
    print("Testing size translation:")
    test_sizes = ["A4", "A5", "DL", "600x900"]
    for size in test_sizes:
        result = translate_size(size)
        print(f"  {size} → {result}")
    
    print("\nTesting full parameter translation:")
    test_params = {
        "size": "A5",
        "colour": "Full Colour",
        "finish": "Gloss",
        "quantity": 500
    }
    result = translate_parameters(test_params, "flyers")
    print(f"  Input: {test_params}")
    print(f"  Output: {result}")
    
    print("\nTesting validation:")
    is_valid, missing = validate_parameters(result, "flyers")
    print(f"  Valid: {is_valid}")
    print(f"  Missing: {missing}")
