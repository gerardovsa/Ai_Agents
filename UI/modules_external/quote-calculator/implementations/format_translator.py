"""
Shopify JSON Format to Backend Format Translator

This module translates between human-readable Shopify JSON formats
and machine-friendly backend calculator formats.

Created: January 23, 2026
Purpose: Fix multi-layer format mismatch between JSON specs and backend calculators

Example Translations:
    Material: "3mm Corflute" → "Corflute"
    Size: "270mm W x 1000mm H - Three Sided" → "270x1000"
    Size: "A3 - 297mm x 420mm" → "297x420"
"""

import re
from typing import Any, Dict, Optional


# ============================================================================
# MATERIAL TRANSLATIONS
# ============================================================================

MATERIAL_TRANSLATIONS: Dict[str, str] = {
    # Corflute variations (JSON → Backend)
    '3mm Corflute': 'Corflute',
    '5mm Corflute': 'Corflute',
    '3mm': 'Corflute',
    '5mm': 'Corflute',
    
    # Metal variations
    'Aluminium': 'Aluminium',
    'Metal': 'Metal',
    
    # Vinyl variations (for Custom Vinyl Stickers)
    'Standard (Monomeric)': 'mono',
    'Premium (Polymeric)': 'poly',
    
    # Screenboard variations (for Strut Cards)
    '2mm Screenboard': '2mm_screenboard',
    
    # Add more as needed
}


# ============================================================================
# SIZE FORMAT TRANSLATIONS
# ============================================================================

def translate_size_format(shopify_size: str) -> str:
    """
    Translate Shopify descriptive size to backend WxH format
    
    Handles multiple Shopify format patterns:
    - "270mm W x 1000mm H - Three Sided" → "270x1000"
    - "A3 - 297mm x 420mm" → "297x420"
    - "450mm x 600mm" → "450x600"
    - "600mm(W) x 900mm(H)" → "600x900"
    - "300x300" → "300x300" (already backend format)
    
    Args:
        shopify_size: Size string from Shopify JSON
        
    Returns:
        Backend-compatible "WxH" format string
        
    Raises:
        ValueError: If size format cannot be parsed
        
    Examples:
        >>> translate_size_format("270mm W x 1000mm H - Three Sided")
        "270x1000"
        >>> translate_size_format("A3 - 297mm x 420mm")
        "297x420"
        >>> translate_size_format("450mm x 600mm")
        "450x600"
        >>> translate_size_format("300x300")
        "300x300"
    """
    # Pattern 1: "270mm W x 1000mm H - Three Sided" (most complex)
    match = re.search(r'(\d+)mm\s*W\s*x\s*(\d+)mm\s*H', shopify_size, re.IGNORECASE)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    # Pattern 2: "600mm(W) x 900mm(H)" (with parentheses)
    match = re.search(r'(\d+)mm\s*\(W\)\s*x\s*(\d+)mm\s*\(H\)', shopify_size, re.IGNORECASE)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    # Pattern 3: "450mm x 600mm" (simple with units)
    match = re.search(r'(\d+)mm\s*x\s*(\d+)mm', shopify_size, re.IGNORECASE)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    # Pattern 4: "300x300" (already backend format)
    if re.match(r'^\d+x\d+$', shopify_size):
        return shopify_size
    
    # Pattern 5: "A3 - 297mm x 420mm" (with label prefix)
    match = re.search(r'(\d+)mm\s*x\s*(\d+)mm', shopify_size)
    if match:
        return f"{match.group(1)}x{match.group(2)}"
    
    # If no patterns match, raise error
    raise ValueError(
        f"Cannot parse size format: '{shopify_size}'. "
        f"Expected formats: '270mm W x 1000mm H', '450mm x 600mm', '300x300', etc."
    )


# ============================================================================
# SIDES FORMAT TRANSLATIONS
# ============================================================================

SIDES_TRANSLATIONS: Dict[str, str] = {
    # Shopify full format → Backend short format
    'Single Sided': 'Single',
    'Double Sided': 'Double',
    'Single': 'Single',  # Already backend format
    'Double': 'Double',  # Already backend format
}


# ============================================================================
# PRINT TYPE TRANSLATIONS
# ============================================================================

PRINT_TYPE_TRANSLATIONS: Dict[str, str] = {
    # Shopify detailed format → Backend simplified format
    'Colour 1 sided': 'Colour',
    'Colour 2 sided': 'Colour',
    'Black & White 1 sided': 'Black & White',
    'Black & White 2 sided': 'Black & White',
    'Colour': 'Colour',  # Already backend format
    'Black & White': 'Black & White',  # Already backend format
}


# ============================================================================
# MAIN TRANSLATION DISPATCHER
# ============================================================================

def translate_field(field_name: str, shopify_value: Any, calculator_name: Optional[str] = None) -> Any:
    """
    Translate a Shopify JSON field value to backend-compatible format
    
    Args:
        field_name: Name of the field being translated (e.g., 'material', 'size')
        shopify_value: Value from Shopify JSON or schema
        calculator_name: Optional calculator name for context-specific translations
        
    Returns:
        Backend-compatible value (same type as input)
        
    Examples:
        >>> translate_field('material', '3mm Corflute')
        'Corflute'
        >>> translate_field('size', '270mm W x 1000mm H - Three Sided')
        '270x1000'
        >>> translate_field('sides', 'Single Sided')
        'Single'
    """
    # Handle None/empty values
    if shopify_value is None or shopify_value == '':
        return shopify_value
    
    # Material translations
    if field_name == 'material' and isinstance(shopify_value, str):
        if shopify_value in MATERIAL_TRANSLATIONS:
            return MATERIAL_TRANSLATIONS[shopify_value]
    
    # Size translations
    if field_name == 'size' and isinstance(shopify_value, str):
        try:
            return translate_size_format(shopify_value)
        except ValueError:
            # If translation fails, return original (may be already in backend format)
            return shopify_value
    
    # Sides translations
    if field_name in ['sides', 'sides?'] and isinstance(shopify_value, str):
        if shopify_value in SIDES_TRANSLATIONS:
            return SIDES_TRANSLATIONS[shopify_value]
    
    # Print type translations
    if field_name == 'print_type' and isinstance(shopify_value, str):
        if shopify_value in PRINT_TYPE_TRANSLATIONS:
            return PRINT_TYPE_TRANSLATIONS[shopify_value]
    
    # No translation needed - return original
    return shopify_value


def translate_params(params: Dict[str, Any], calculator_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Translate all parameters in a dictionary from Shopify to backend format
    
    Args:
        params: Dictionary of parameter name → value from Shopify JSON
        calculator_name: Optional calculator name for context
        
    Returns:
        New dictionary with translated values
        
    Example:
        >>> params = {
        ...     'quantity': 10,
        ...     'material': '3mm Corflute',
        ...     'size': '270mm W x 1000mm H - Three Sided',
        ...     'sides': 'Single Sided'
        ... }
        >>> translate_params(params)
        {
            'quantity': 10,
            'material': 'Corflute',
            'size': '270x1000',
            'sides': 'Single'
        }
    """
    translated = {}
    for key, value in params.items():
        translated[key] = translate_field(key, value, calculator_name)
    return translated


# ============================================================================
# REVERSE TRANSLATIONS (Backend → Shopify JSON)
# ============================================================================

def reverse_translate_material(backend_value: str) -> Optional[str]:
    """
    Translate backend material format back to Shopify JSON format
    Used for displaying results/specifications
    
    Args:
        backend_value: Material value in backend format
        
    Returns:
        Shopify JSON format, or None if no mapping found
        
    Example:
        >>> reverse_translate_material('Corflute')
        '3mm Corflute'  # Returns first matching JSON format
    """
    # Reverse lookup in translations
    for shopify_format, backend_format in MATERIAL_TRANSLATIONS.items():
        if backend_format == backend_value:
            return shopify_format
    return None


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def is_shopify_format(field_name: str, value: str) -> bool:
    """
    Check if a value is in Shopify JSON format (vs backend format)
    
    Args:
        field_name: Field name (e.g., 'size', 'material')
        value: Value to check
        
    Returns:
        True if value appears to be Shopify JSON format
        
    Examples:
        >>> is_shopify_format('size', '270mm W x 1000mm H - Three Sided')
        True
        >>> is_shopify_format('size', '270x1000')
        False
        >>> is_shopify_format('material', '3mm Corflute')
        True
        >>> is_shopify_format('material', 'Corflute')
        False
    """
    if field_name == 'size':
        # Shopify format contains 'mm' and/or 'W'/'H' labels
        return 'mm' in value.lower() or 'W' in value or 'H' in value
    
    if field_name == 'material':
        # Shopify format has thickness prefix or descriptive suffix
        return bool(re.search(r'\d+mm', value) or r'\(' in value)
    
    if field_name in ['sides', 'sides?']:
        # Shopify format has 'Sided' suffix
        return 'Sided' in value
    
    if field_name == 'print_type':
        # Shopify format has 'sided' or digit
        return 'sided' in value.lower() or bool(re.search(r'\d', value))
    
    return False


# ============================================================================
# TESTING UTILITIES
# ============================================================================

def test_translations():
    """Run basic translation tests"""
    print("Testing format_translator.py...")
    
    # Test size translations
    test_cases = [
        ('size', '270mm W x 1000mm H - Three Sided', '270x1000'),
        ('size', 'A3 - 297mm x 420mm', '297x420'),
        ('size', '450mm x 600mm', '450x600'),
        ('size', '600mm(W) x 900mm(H)', '600x900'),
        ('size', '300x300', '300x300'),
        ('material', '3mm Corflute', 'Corflute'),
        ('material', '5mm Corflute', 'Corflute'),
        ('sides', 'Single Sided', 'Single'),
        ('sides', 'Double Sided', 'Double'),
        ('print_type', 'Colour 1 sided', 'Colour'),
    ]
    
    passed = 0
    failed = 0
    
    for field, shopify_val, expected in test_cases:
        result = translate_field(field, shopify_val)
        if result == expected:
            print(f"✅ {field}: '{shopify_val}' → '{result}'")
            passed += 1
        else:
            print(f"❌ {field}: '{shopify_val}' → '{result}' (expected '{expected}')")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    # Run tests when executed directly
    test_translations()
