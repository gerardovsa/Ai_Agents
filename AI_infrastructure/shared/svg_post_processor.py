"""
SVG Post-Processor
Handles browser rendering quirks and SVG optimization.

BOLD TEXT BASELINE BUG FIX:
Browsers incorrectly position bold text when using dominant-baseline="middle"
because they calculate the bounding box with regular font metrics but render
with bold font metrics, causing ~5-7px downward shift.

Solution: Convert dominant-baseline="middle" to manual baseline positioning
for all bold text elements.
"""

import re
import logging
from typing import Optional
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


def fix_svg_bold_baseline_bug(svg_code: str) -> str:
    """
    Fix the browser rendering bug where bold text with dominant-baseline="middle"
    renders 5-7px below the intended position.
    
    Strategy:
    1. Parse SVG and find all <text> elements
    2. Identify bold text with dominant-baseline="middle"
    3. Convert to manual baseline positioning
    4. Remove problematic dominant-baseline attribute
    
    Args:
        svg_code: Raw SVG XML string
        
    Returns:
        Fixed SVG XML string
        
    Example:
        Before: <text y="150" dominant-baseline="middle" font-weight="bold">Title</text>
        After:  <text y="155.6" font-weight="bold">Title</text>
                (y adjusted from center to baseline position)
    """
    if not svg_code or '<text' not in svg_code:
        return svg_code
    
    try:
        # Parse SVG
        # Handle namespace
        namespaces = {'svg': 'http://www.w3.org/2000/svg'}
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        
        root = ET.fromstring(svg_code)
        
        fixes_applied = 0
        
        # Find all text elements (with and without namespace)
        for text_elem in root.iter():
            # Check if it's a text element (handle both namespaced and non-namespaced)
            tag_name = text_elem.tag.split('}')[-1] if '}' in text_elem.tag else text_elem.tag
            if tag_name != 'text':
                continue
            
            # Check if this text element needs fixing
            is_bold = _is_bold_text(text_elem)
            uses_middle_baseline = _uses_middle_baseline(text_elem)
            
            if not (is_bold and uses_middle_baseline):
                continue
            
            # Extract font size
            font_size = _extract_font_size(text_elem)
            
            # Extract current Y position
            y_attr = text_elem.get('y')
            if not y_attr:
                continue
            
            try:
                y_center = float(y_attr)
            except ValueError:
                logger.warning(f"Could not parse Y value: {y_attr}")
                continue
            
            # Calculate correct baseline position
            # Formula: y_baseline = y_center - (font_size × 0.5)
            # This compensates for browser shifting bold text DOWN by ~0.5em
            y_baseline = y_center - (font_size * 0.5)
            
            # Apply fix
            text_elem.set('y', f"{y_baseline:.2f}")
            
            # Remove dominant-baseline attribute
            if 'dominant-baseline' in text_elem.attrib:
                del text_elem.attrib['dominant-baseline']
            
            fixes_applied += 1
            logger.debug(f"Fixed bold text: y={y_center} -> {y_baseline:.2f} (font-size={font_size})")
        
        if fixes_applied > 0:
            logger.info(f"[SVG_POST_PROCESSOR] Fixed {fixes_applied} bold text baseline issue(s)")
        
        # Convert back to string
        fixed_svg = ET.tostring(root, encoding='unicode')
        
        # Clean up XML declaration if present
        if fixed_svg.startswith('<?xml'):
            fixed_svg = re.sub(r'<\?xml[^>]+\?>\s*', '', fixed_svg)
        
        return fixed_svg
    
    except ET.ParseError as e:
        logger.error(f"[SVG_POST_PROCESSOR] XML parsing failed: {e}")
        return svg_code
    except Exception as e:
        logger.error(f"[SVG_POST_PROCESSOR] Unexpected error: {e}")
        return svg_code


def _is_bold_text(elem: ET.Element) -> bool:
    """Check if text element uses bold font-weight."""
    # Check font-weight attribute
    if elem.get('font-weight') == 'bold':
        return True
    
    # Check style attribute
    style = elem.get('style', '')
    if 'font-weight:bold' in style.replace(' ', ''):
        return True
    if re.search(r'font-weight:\s*bold', style):
        return True
    
    return False


def _uses_middle_baseline(elem: ET.Element) -> bool:
    """Check if element uses dominant-baseline='middle'."""
    return elem.get('dominant-baseline') == 'middle'


def _extract_font_size(elem: ET.Element) -> float:
    """Extract font size from element, return default if not found."""
    default_size = 14.0
    
    # Check font-size attribute
    font_size_attr = elem.get('font-size')
    if font_size_attr:
        try:
            # Remove 'px' suffix if present
            value = re.sub(r'[^\d.]', '', font_size_attr)
            return float(value)
        except ValueError:
            pass
    
    # Check style attribute
    style = elem.get('style', '')
    font_match = re.search(r'font-size:\s*(\d+(?:\.\d+)?)', style)
    if font_match:
        try:
            return float(font_match.group(1))
        except ValueError:
            pass
    
    return default_size


def optimize_svg(svg_code: str) -> str:
    """
    Apply all SVG optimizations and fixes.
    
    This is the main entry point for SVG post-processing.
    
    Args:
        svg_code: Raw SVG from AI agent
        
    Returns:
        Optimized and fixed SVG
    """
    # Apply bold baseline fix
    svg_code = fix_svg_bold_baseline_bug(svg_code)
    
    # Add additional optimizations here as needed
    # - Remove duplicate IDs
    # - Optimize path data
    # - Minify if requested
    
    return svg_code


def validate_svg(svg_code: str) -> tuple[bool, Optional[str]]:
    """
    Validate SVG syntax and structure.
    
    Returns:
        (is_valid, error_message)
    """
    try:
        ET.fromstring(svg_code)
        return True, None
    except ET.ParseError as e:
        return False, str(e)


if __name__ == "__main__":
    # Test the post-processor
    test_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
        <text x="300" y="200" text-anchor="middle" dominant-baseline="middle" 
              font-size="16" font-weight="bold">SPECIFICATIONS</text>
        <text x="300" y="250" text-anchor="middle" dominant-baseline="middle" 
              font-size="12">Regular Text</text>
    </svg>'''
    
    print("Original SVG:")
    print(test_svg)
    print("\n" + "="*60 + "\n")
    
    fixed_svg = optimize_svg(test_svg)
    print("Fixed SVG:")
    print(fixed_svg)
    
    # Validate
    is_valid, error = validate_svg(fixed_svg)
    print(f"\nValidation: {'✓ PASS' if is_valid else f'✗ FAIL - {error}'}")
