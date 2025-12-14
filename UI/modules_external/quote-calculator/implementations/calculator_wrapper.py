"""
Quote Calculator Wrapper - Connects Registry V3 to inhouse_modules calculators

This wrapper provides AI tool access to InHouse Print quote calculators.
It wraps the existing calculator code in inhouse_modules/ without duplication.

Architecture:
    AI Agent Request
        ↓
    Registry V3
        ↓
    calculator_wrapper.py (THIS FILE)
        ↓
    inhouse_modules/complete_calculator_implementation.py
        ↓
    G_Folder database

FILE: UI/external/modules/quote-calculator/implementations/calculator_wrapper.py
PURPOSE: Wrapper functions for quote calculator tools
DEPENDENCIES:
- inhouse_modules.complete_calculator_implementation

EXPORTS:
- calculate_business_cards(quantity, stock_type, sides)
- calculate_flyers(quantity, size, stock, sides)
- calculate_booklets(quantity, pages, cover_stock, inner_stock, size)
- calculate_perfect_bound_books(quantity, pages, cover_stock, inner_stock, size)
- calculate_letterheads(quantity, stock, colors)
- calculate_corflute_signs(quantity, size, thickness, sides)
- get_stock_list(category="all")

LAST MODIFIED: 2025-11-04 - Initial creation
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '..', 'backend'))
god_calc_dir = os.path.join(backend_dir, 'god_calculators')
shopify_calc_dir = os.path.join(backend_dir, 'shopify_calculators')  # NEW: Correct path
inhouse_print_module = os.path.abspath(os.path.join(current_dir, '..', '..', 'inhouse-print'))

# Add necessary paths
for path in [current_dir, backend_dir, god_calc_dir, shopify_calc_dir, inhouse_print_module]:
    abs_path = os.path.abspath(path)
    if abs_path not in sys.path:
        sys.path.insert(0, abs_path)
# Import GOD calculators from backend/god_calculators
GOD_CALCULATORS_AVAILABLE = False
try:
    from GOD_flyer_calculator import FlyerCalculatorGOD
    from GOD_letterhead_calculator import LetterheadCalculatorGOD
    from GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator
    from corflute_calculator import CorflutePricingCalculator
    
    GOD_CALCULATORS_AVAILABLE = True
    print("✅ [GOD Calculators] Loaded successfully")
except ImportError as e:
    print(f"⚠️  [GOD Calculators] Failed to import: {e}")
    print("   GOD calculator tools will not be available")

# Import Shopify calculators from In_House_SQL (source of truth)
SHOPIFY_CALCULATORS_AVAILABLE = False
try:
    from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
    from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
    from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
    from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
    from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
    from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
    
    SHOPIFY_CALCULATORS_AVAILABLE = True
    print("✅ [Shopify Calculators] Loaded successfully")
except ImportError as e:
    print(f"⚠️  [Shopify Calculators] Failed to import: {e}")
    print("   Shopify calculator tools will not be available")


# ==================== HELPER FUNCTIONS ====================

def _handle_calculator_error(e: Exception, product_type: str) -> Dict[str, Any]:
    """Format calculator errors consistently"""
    return {
        "success": False,
        "error": f"Failed to calculate {product_type} quote",
        "message": str(e),
        "details": "Check parameters and database connection"
    }


# ==================== CALCULATOR TOOL FUNCTIONS ====================

def calculate_business_cards(
    quantity: int,
    stock_type: str,
    print_type: str,
    finish_size: str = "90x55mm",
    celloglaze: str = "none",
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for business cards - MATCHES SCHEMA
    
    Args:
        quantity: Number of cards (100, 250, 500, 1000, 2000, 5000, 10000)
        stock_type: "standard", "premium", "satin", "uncoated"
        print_type: "single_sided" or "double_sided"
        finish_size: "90x55mm" (standard), "90x50mm", "85x55mm" (default: "90x55mm")
        celloglaze: "none", "gloss", "matt", "1_side_gloss", "2_side_gloss", "1_side_matt", "2_side_matt" (default: "none")
        **kwargs: Additional parameters (ignored, for compatibility)
    
    Returns:
        Dict with success, total_price, per_unit_price, stock_details, turnaround_days
    """
    try:
        # Use Shopify calculator directly (like GOD calculators)
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        # Ensure quantity is integer (may come as string from schema)
        quantity = int(quantity)
        
        # Convert print_type to Shopify format
        print_sides = "Double side print" if print_type == "double_sided" else "Single side print"
        
        # Convert finish_size format: 90x55mm -> 90mm x 55mm
        size_parts = finish_size.replace('mm', '').split('x')
        shopify_size = f"{size_parts[0]}mm x {size_parts[1]}mm"
        
        # Choose calculator based on stock_type
        if stock_type == "premium":
            calculator = PremiumBusinessCardsShopifyCalculator()
            # Premium uses Satin 350GSM by default
            result = calculator.calculate(
                quantity=quantity,
                print_sides=print_sides,
                print_type="Colour",
                finish_size=shopify_size,
                paper_stock="Satin 350GSM",
                celloglaze=celloglaze.replace("_", " ").title() if celloglaze != "none" else "1 Side Gloss",
                artworks=1
            )
        else:
            calculator = EconomicalBusinessCardsShopifyCalculator()
            # Economical uses Satin 300GSM by default (NO celloglaze parameter)
            # Note: Stock format is "Satin 300GSM" not "300GSM Satin"
            result = calculator.calculate(
                quantity=quantity,
                print_sides=print_sides,
                print_type="Colour",
                finish_size=shopify_size,
                paper_stock="Satin 300GSM",
                artworks=1
            )
        
        return {
            "success": True,
            "product": "Business Cards",
            "quantity": quantity,
            "stock_type": stock_type,
            "print_type": print_type,
            "finish_size": finish_size,
            "celloglaze": celloglaze,
            "total_price": float(result.total_price),
            "per_unit_price": float(result.unit_price),
            "stock_details": f"{finish_size}, {stock_type}",
            "turnaround_days": 3,
            "breakdown": {k: float(v) if hasattr(v, '__float__') else v 
                         for k, v in result.breakdown.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "business cards")


def calculate_flyers(
    quantity: int,
    width: int,
    height: int,
    stock_gsm: int,
    print_mode: str = "single_sided",
    cello_type: str = "none",
    folded: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for flyers/leaflets - MATCHES SCHEMA
    
    Args:
        quantity: Number of items to print (100-10000)
        width: Width in millimeters (e.g., 210 for A4)
        height: Height in millimeters (e.g., 297 for A4)
        stock_gsm: Stock weight in GSM (128, 150, 170, 200, 250, 300, 350, 400)
        print_mode: 'single_sided', 'double_sided', 'no_print' (default: 'single_sided')
        cello_type: 'none', 'gloss_both_sides', 'matt_both_sides', 'gloss_front_only', 'matt_front_only' (default: 'none')
        folded: Whether the flyer is folded (default: False)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_unit_price, stock_details
    """
    try:
        # Ensure types are correct (schema may pass strings)
        quantity = int(quantity)
        width = int(width)
        height = int(height)
        stock_gsm = int(stock_gsm)
        
        # Use GOD calculator directly (like calculate_flyers_god)
        if not GOD_CALCULATORS_AVAILABLE:
            raise RuntimeError("GOD calculators not available")
        
        # Get database connector
        from db_connector import InHousePrintDB
        from decimal import Decimal
        
        try:
            db = InHousePrintDB()
        except (FileNotFoundError, ConnectionError) as db_error:
            return {
                "success": False,
                "error": f"Database unavailable: {str(db_error)}",
                "error_type": "database_connection"
            }
        
        # Convert print_mode to print_side parameters
        if print_mode == "double_sided":
            print_side1 = 1
            print_side2 = 1
        elif print_mode == "no_print":
            print_side1 = 0
            print_side2 = 0
        else:  # single_sided
            print_side1 = 1
            print_side2 = 0
        
        # Use GOD calculator directly (needs db connector)
        calculator = FlyerCalculatorGOD(db)
        result = calculator.calculate(
            quantity=quantity,
            width=width,
            height=height,
            gsm=stock_gsm,
            print_side1=print_side1,
            print_side2=print_side2,
            folding_required=folded,
            folding_passes=1 if folded else 0,
            cello_required=(cello_type != "none"),
            cello_side1=1 if "gloss" in cello_type else (2 if "matt" in cello_type else 0),
            cello_side2=1 if "both" in cello_type or "2" in cello_type else 0,
            discount=Decimal("0")
        )
        
        return {
            "success": True,
            "product": "Flyers",
            "quantity": quantity,
            "width": width,
            "height": height,
            "stock_gsm": stock_gsm,
            "print_mode": print_mode,
            "cello_type": cello_type,
            "folded": folded,
            "total_price": float(result.total_cost_inc_gst),
            "cost_to_business": float(result.cost_to_business),
            "total_cost_ex_gst": float(result.total_cost_ex_gst),
            "total_cost_inc_gst": float(result.total_cost_inc_gst),
            "per_unit_price": float(result.total_cost_inc_gst / quantity),
            "stock_details": f"{width}x{height}mm, {stock_gsm}GSM",
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v 
                         for k, v in result.breakdown.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "flyers")


def calculate_booklets(
    quantity: int,
    total_pages: int,
    cover_stock_gsm: int,
    internal_stock_gsm: int,
    cover_print_mode: str = "double_sided",
    internal_print_mode: str = "double_sided",
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for saddle-stitched booklets - MATCHES SCHEMA
    
    Args:
        quantity: Number of booklets (100-10000)
        total_pages: Total page count (must be divisible by 4, minimum 8)
        cover_stock_gsm: Cover stock weight (250, 300, 350, 400)
        internal_stock_gsm: Internal pages stock weight (80, 100, 128, 150, 170)
        cover_print_mode: 'single_sided', 'double_sided' (default: 'double_sided')
        internal_print_mode: 'single_sided', 'double_sided', 'black_white', 'mixed' (default: 'double_sided')
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_booklet_price, binding_cost
    """
    try:
        # Ensure types are correct (schema may pass strings)
        quantity = int(quantity)
        total_pages = int(total_pages)
        cover_stock_gsm = int(cover_stock_gsm)
        internal_stock_gsm = int(internal_stock_gsm)
        
        # Use Shopify Spiral Bound calculator directly (booklets = spiral bound)
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        # Convert print modes to Shopify format
        if cover_print_mode == "double_sided":
            front_cover_print = "2pp Colour"
        else:
            front_cover_print = "1pp Colour"
        
        if internal_print_mode == "double_sided":
            internal_print = "Full Colour"
        elif internal_print_mode == "black_white":
            internal_print = "Black & White"
        else:
            internal_print = "Full Colour"  # Default to color
        
        calculator = SpiralBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=1,
            finish_size="A5 Portrait",
            outer_front_cover="Not Required",
            printed_front_cover=f"{cover_stock_gsm}GSM Satin",
            front_cover_print=front_cover_print,
            front_celloglaze="None",
            outer_back_cover="None",
            printed_back_cover=f"{cover_stock_gsm}GSM Satin",
            back_cover_print=front_cover_print,
            back_celloglaze="None",
            internal_pages=total_pages - 4,  # Shopify counts internal only
            internal_stock=f"Uncoated Bond {internal_stock_gsm}GSM",
            internal_print=internal_print
        )
        
        return {
            "success": True,
            "product": f"Booklet ({total_pages} pages)",
            "quantity": quantity,
            "total_pages": total_pages,
            "cover_stock_gsm": cover_stock_gsm,
            "internal_stock_gsm": internal_stock_gsm,
            "cover_print_mode": cover_print_mode,
            "internal_print_mode": internal_print_mode,
            "binding_type": "Spiral Bound",
            "total_price": float(result.total_price),
            "per_booklet_price": float(result.unit_price),
            "unit_price": float(result.unit_price),
            "breakdown": {k: float(v) if hasattr(v, '__float__') else v 
                         for k, v in result.breakdown.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "booklets")


def calculate_perfect_bound_books(
    quantity: int,
    total_pages: int,
    cover_stock_gsm: int,
    internal_stock_gsm: int,
    cover_print_mode: str = "double_sided",
    internal_print_mode: str = "double_sided",
    cover_lamination: str = "none",
    spot_uv: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for perfect bound books (glued spine) - MATCHES SCHEMA
    
    Args:
        quantity: Number of books (100-10000)
        total_pages: Total page count (minimum 40, divisible by 4)
        cover_stock_gsm: Cover stock weight (250, 300, 350, 400)
        internal_stock_gsm: Internal stock weight (80, 100, 128, 150, 170)
        cover_print_mode: 'single_sided', 'double_sided' (default: 'double_sided')
        internal_print_mode: 'single_sided', 'double_sided', 'black_white', 'mixed' (default: 'double_sided')
        cover_lamination: 'none', 'gloss', 'matt' (default: 'none')
        spot_uv: Add spot UV finish to cover (default: False)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_book_price, binding_cost
    """
    try:
        # Ensure types are correct (schema may pass strings)
        quantity = int(quantity)
        total_pages = int(total_pages)
        cover_stock_gsm = int(cover_stock_gsm)
        internal_stock_gsm = int(internal_stock_gsm)
        
        # Use Shopify Perfect Bound calculator directly
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        # Convert print modes to Shopify format
        if cover_print_mode == "double_sided":
            cover_print_type = "2 side colour (4pp)"
        else:
            cover_print_type = "1 side colour (2pp)"
        
        if internal_print_mode == "double_sided" or internal_print_mode == "mixed":
            content_print_type = "Full Colour"
        elif internal_print_mode == "black_white":
            content_print_type = "Black & White"
        else:
            content_print_type = "Full Colour"
        
        # Convert celloglaze
        cello_map = {
            "none": "None",
            "gloss": "Gloss outside only",
            "matt": "Matt outside only"
        }
        celloglaze = cello_map.get(cover_lamination, "None")
        
        calculator = PerfectBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            printed_pages=total_pages,
            proof_requirements="Digital Emailed Proof",
            cover_stock=f"Satin {cover_stock_gsm}GSM",
            cover_print_type=cover_print_type,
            celloglaze=celloglaze,
            finish_size="A5 Portrait",
            content_print_type=content_print_type,
            content_stock_type=f"Uncoated Bond {internal_stock_gsm}GSM"
        )
        
        return {
            "success": True,
            "product": f"Perfect Bound Book ({total_pages} pages)",
            "quantity": quantity,
            "total_pages": total_pages,
            "cover_stock_gsm": cover_stock_gsm,
            "internal_stock_gsm": internal_stock_gsm,
            "cover_print_mode": cover_print_mode,
            "internal_print_mode": internal_print_mode,
            "cover_lamination": cover_lamination,
            "spot_uv": spot_uv,
            "binding_type": "Perfect Bound (glued spine)",
            "total_price": float(result.total_price),
            "per_book_price": float(result.unit_price),
            "binding_cost": float(result.breakdown.get('binding_cost', 0)),
            "breakdown": {k: float(v) if hasattr(v, '__float__') else v 
                         for k, v in result.breakdown.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "perfect bound books")


def calculate_letterheads(
    quantity: int,
    stock: str,
    colors: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for letterheads (company stationery)
    
    Args:
        quantity: Number of letterheads
        stock: Paper stock (e.g. "100GSM Uncoated")
        colors: Number of ink colors (1 or 4)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_sheet_price
    """
    try:
        # Ensure quantity and colors are integers
        quantity = int(quantity)
        colors = int(colors)
        
        # Use GOD Letterhead calculator directly
        if not GOD_CALCULATORS_AVAILABLE:
            raise RuntimeError("GOD calculators not available")
        
        # Get database connector
        from db_connector import InHousePrintDB
        from decimal import Decimal
        
        try:
            db = InHousePrintDB()
        except (FileNotFoundError, ConnectionError) as db_error:
            return {
                "success": False,
                "error": f"Database unavailable: {str(db_error)}",
                "error_type": "database_connection"
            }
        
        # Parse stock to get GSM (handle both string "100GSM Uncoated" and int 100)
        if isinstance(stock, str):
            stock_gsm = int(''.join(filter(str.isdigit, stock)))
        else:
            stock_gsm = int(stock)
        
        # Convert colors to print sides (1=B&W, 4=Color)
        # A4 letterheads are typically 210x297mm
        if colors == 4:
            print_side1 = 1  # 1 = Colour
            print_side2 = 0  # No printing on back
        else:
            print_side1 = 2  # 2 = B&W
            print_side2 = 0
        
        calculator = LetterheadCalculatorGOD(db)
        result = calculator.calculate(
            quantity=quantity,
            width=210,  # A4 width
            height=297,  # A4 height
            gsm=stock_gsm,
            print_side1=print_side1,
            print_side2=print_side2,
            discount=Decimal("0")
        )
        
        return {
            "success": True,
            "product": "Letterheads",
            "quantity": quantity,
            "stock": stock,
            "colors": colors,
            "size": "A4",
            "total_cost_ex_gst": float(result.total_cost_ex_gst),
            "total_cost_inc_gst": float(result.total_cost_inc_gst),
            "total_price": float(result.total_cost_inc_gst),
            "per_sheet_price": float(result.total_cost_inc_gst / quantity),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v 
                         for k, v in result.breakdown.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "letterheads")


def calculate_corflute_signs(
    quantity: int,
    width: int,
    height: int,
    thickness: str = "5mm",
    double_sided: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for corflute signs (rigid plastic signage) - MATCHES SCHEMA
    
    Args:
        quantity: Number of signs (100-10000)
        width: Width in millimeters (e.g., 600, 900, 1200)
        height: Height in millimeters (e.g., 600, 900, 1200)
        thickness: '3mm' or '5mm' (default: '5mm')
        double_sided: Print on both sides (default: False)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_sign_price, material_cost
    """
    try:
        # Use GOD Corflute calculator directly (no database needed)
        if not GOD_CALCULATORS_AVAILABLE:
            raise RuntimeError("GOD calculators not available")
        
        # Convert all parameters to correct types (ensure no string/int mismatch)
        quantity = int(quantity)
        width = int(width)
        height = int(height)
        
        # Convert thickness to integer (remove "mm" if present)
        if isinstance(thickness, str):
            thickness_mm = int(thickness.replace('mm', ''))
        else:
            thickness_mm = int(thickness)
        
        # Convert double_sided to print_sides
        print_sides = "double" if double_sided else "single"
        
        calculator = CorflutePricingCalculator()
        result = calculator.calculate_base_quote(
            width_mm=width,
            height_mm=height,
            thickness_mm=thickness_mm,
            quantity=quantity,
            print_sides=print_sides,
            print_mode="color",
            artworks=1
        )
        
        # Extract prices from calculator result
        total_inc_gst = result.get('total_inc_gst', 0)
        material_cost = result.get('material_cost_per_unit', 0) * quantity
        
        return {
            "success": True,
            "product": f"Corflute Sign ({width}x{height}mm)",
            "quantity": quantity,
            "width": width,
            "height": height,
            "thickness": thickness,
            "double_sided": double_sided,
            "sides": 2 if double_sided else 1,
            "total_price": float(total_inc_gst),
            "per_sign_price": float(total_inc_gst / quantity if quantity > 0 else 0),
            "material_cost": float(material_cost),
            "breakdown": {k: float(v) if isinstance(v, (int, float)) else v 
                         for k, v in result.items()}
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "corflute signs")


def get_stock_list(category: str = "all", **kwargs) -> Dict[str, Any]:
    """
    Get list of available paper stocks with specifications (hardcoded - no database)
    
    Args:
        category: Filter by category ("all", "gloss", "satin", "uncoated", "specialty")
        **kwargs: Additional parameters (ignored)
    
    Returns:
        Dict with success status and list of stock objects
    """
    try:
        # Hardcoded stock list based on Shopify calculator standards
        all_stocks = [
            # Gloss Stocks
            {"name": "150GSM Gloss", "gsm": 150, "finish": "Gloss", "suitable_for": ["flyers", "leaflets"], "price_multiplier": 1.0},
            {"name": "170GSM Gloss", "gsm": 170, "finish": "Gloss", "suitable_for": ["flyers", "booklets"], "price_multiplier": 1.1},
            {"name": "250GSM Gloss", "gsm": 250, "finish": "Gloss", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.3},
            {"name": "300GSM Gloss", "gsm": 300, "finish": "Gloss", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.5},
            {"name": "350GSM Gloss", "gsm": 350, "finish": "Gloss", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.7},
            
            # Satin Stocks
            {"name": "170GSM Satin", "gsm": 170, "finish": "Satin", "suitable_for": ["flyers", "booklets"], "price_multiplier": 1.1},
            {"name": "250GSM Satin", "gsm": 250, "finish": "Satin", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.3},
            {"name": "300GSM Satin", "gsm": 300, "finish": "Satin", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.5},
            {"name": "350GSM Satin", "gsm": 350, "finish": "Satin", "suitable_for": ["business cards", "covers"], "price_multiplier": 1.7},
            {"name": "400GSM Satin", "gsm": 400, "finish": "Satin", "suitable_for": ["premium business cards"], "price_multiplier": 2.0},
            
            # Uncoated Bond Stocks
            {"name": "Uncoated Bond 80GSM", "gsm": 80, "finish": "Uncoated", "suitable_for": ["letterheads", "internal pages"], "price_multiplier": 0.7},
            {"name": "Uncoated Bond 90GSM", "gsm": 90, "finish": "Uncoated", "suitable_for": ["letterheads", "internal pages"], "price_multiplier": 0.8},
            {"name": "Uncoated Bond 100GSM", "gsm": 100, "finish": "Uncoated", "suitable_for": ["letterheads", "booklet internals"], "price_multiplier": 0.9},
            {"name": "Uncoated Bond 120GSM", "gsm": 120, "finish": "Uncoated", "suitable_for": ["letterheads", "booklet internals"], "price_multiplier": 1.0},
            
            # Specialty Stocks
            {"name": "Revive 100% Recycled 80GSM Bond", "gsm": 80, "finish": "Recycled Uncoated", "suitable_for": ["eco-friendly letterheads"], "price_multiplier": 0.85},
            {"name": "310GSM Enviro Uncoated", "gsm": 310, "finish": "Recycled Uncoated", "suitable_for": ["eco-friendly business cards"], "price_multiplier": 1.6},
        ]
        
        # Filter by category if specified
        if category and category != "all":
            category_lower = category.lower()
            filtered_stocks = [
                stock for stock in all_stocks
                if category_lower in stock["finish"].lower()
            ]
        else:
            filtered_stocks = all_stocks
        
        # Format for AI consumption
        return {
            "success": True,
            "data": [{
                "name": stock["name"],
                "gsm": stock["gsm"],
                "finish": stock["finish"],
                "suitable_for": stock["suitable_for"],
                "price_multiplier": stock["price_multiplier"],
                "description": f"{stock['gsm']}GSM {stock['finish']}"
            } for stock in filtered_stocks]
        }
        
    except Exception as e:
        print(f"❌ [Stock List] Error: {e}")
        return {"success": False, "error": str(e), "data": []}


# ==================== GOD CALCULATOR WRAPPERS ====================

def calculate_flyers_god(
    quantity: int,
    width: int,
    height: int,
    gsm: int,
    print_side1: int = 1,
    print_side2: int = 0,
    folding_required: bool = False,
    folding_passes: int = 1,
    folding_extra_mins: int = 0,
    cello_required: bool = False,
    cello_side1: int = 0,
    cello_side2: int = 0,
    discount: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) flyer calculator - Most accurate pricing
    
    Args:
        quantity: Number of flyers
        width: Finished width in mm (e.g., 210 for A4)
        height: Finished height in mm (e.g., 297 for A4)
        gsm: Paper weight (e.g., 150, 250, 300)
        print_side1: Print mode for side 1 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        print_side2: Print mode for side 2 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        folding_required: Whether folding is required
        folding_passes: Number of folds (1=half, 2=z-fold, 3=gate)
        folding_extra_mins: Extra minutes for complex folding
        cello_required: Whether cellophane lamination required
        cello_side1: Cello type for side 1 (0=none, 1=gloss, 2=matt)
        cello_side2: Cello type for side 2 (0=none, 1=gloss, 2=matt)
        discount: Discount as decimal (0.1 = 10% off)
    
    Returns:
        Dict with success, quote result, or error
    """
    if not GOD_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "GOD calculators not available. Check database connection."
        }
    
    try:
        from db_connector import InHousePrintDB
        from decimal import Decimal
        
        # Convert string print modes to integers if needed
        print_mode_map = {'none': 0, 'colour': 1, 'color': 1, 'b&w': 2, 'bw': 2, 'black_white': 2, 'bw_on_colour': 3}
        if isinstance(print_side1, str):
            print_side1 = print_mode_map.get(print_side1.lower(), 1)
        if isinstance(print_side2, str):
            print_side2 = print_mode_map.get(print_side2.lower(), 0)
        
        # Convert cello string values to integers if needed
        cello_map = {'none': 0, 'gloss': 1, 'matt': 2, 'mat': 2, 'matte': 2}
        if isinstance(cello_side1, str):
            cello_side1 = cello_map.get(cello_side1.lower(), 0)
        if isinstance(cello_side2, str):
            cello_side2 = cello_map.get(cello_side2.lower(), 0)
        
        try:
            db = InHousePrintDB()
        except (FileNotFoundError, ConnectionError) as db_error:
            return {
                "success": False,
                "error": f"Database unavailable: {str(db_error)}",
                "error_type": "database_connection",
                "details": "InHousePrint SQL Server database is required for GOD calculators"
            }
        
        calculator = FlyerCalculatorGOD(db)
        
        result = calculator.calculate(
            quantity=quantity,
            width=width,
            height=height,
            gsm=gsm,
            print_side1=print_side1,
            print_side2=print_side2,
            folding_required=folding_required,
            folding_passes=folding_passes,
            folding_extra_mins=folding_extra_mins,
            cello_required=cello_required,
            cello_side1=cello_side1,
            cello_side2=cello_side2,
            discount=Decimal(str(discount))
        )
        
        return {
            "success": True,
            "product_type": result.product_type,
            "quantity": result.quantity,
            "cost_to_business": float(result.cost_to_business),
            "profit_margin": float(result.profit_margin),
            "total_cost_ex_gst": float(result.total_cost_ex_gst),
            "total_cost_inc_gst": float(result.total_cost_inc_gst),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [GOD Flyer Calculator] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_letterheads_god(
    quantity: int,
    width: int,
    height: int,
    gsm: int,
    print_side1: int = 1,
    print_side2: int = 0,
    discount: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) letterhead calculator - Database-accurate pricing
    Note: Letterheads are simplified - no cellophane lamination options
    
    Args:
        quantity: Number of letterheads
        width: Finished width in mm (typically 210 for A4)
        height: Finished height in mm (typically 297 for A4)
        gsm: Paper weight (e.g., 100, 120)
        print_side1: Print mode for side 1 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        print_side2: Print mode for side 2 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        discount: Discount as decimal
    
    Returns:
        Dict with success, quote result, or error
    """
    if not GOD_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "GOD calculators not available. Check database connection."
        }
    
    try:
        from db_connector import InHousePrintDB
        from decimal import Decimal
        
        db = InHousePrintDB()
        calculator = LetterheadCalculatorGOD(db)
        
        result = calculator.calculate(
            quantity=quantity,
            width=width,
            height=height,
            gsm=gsm,
            print_side1=print_side1,
            print_side2=print_side2,
            discount=Decimal(str(discount))
        )
        
        return {
            "success": True,
            "product_type": result.product_type,
            "quantity": result.quantity,
            "cost_to_business": float(result.cost_to_business),
            "profit_margin": float(result.profit_margin),
            "total_cost_ex_gst": float(result.total_cost_ex_gst),
            "total_cost_inc_gst": float(result.total_cost_inc_gst),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [GOD Letterhead Calculator] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_perfect_bound_books_god(
    quantity: int,
    pages: int,
    book_width: int,
    book_height: int,
    cover_gsm: int,
    inner_gsm: int,
    print_cover_mode: int = 1,
    print_inner_mode: int = 1,
    cello_type: int = 0,
    stock_type_id: int = 29,        # Type 29 (Bond) has common GSMs
    cover_stock_type_id: int = 20,  # Type 20 (Satin/Silk) has common cover GSMs
    discount: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) perfect bound books calculator
    
    Args:
        quantity: Number of books
        pages: Total number of internal pages (must be divisible by 4)
        book_width: Book width in mm (210 for A4, 148 for A5)
        book_height: Book height in mm (297 for A4, 210 for A5)
        cover_gsm: Cover paper weight (e.g., 250, 300)
        inner_gsm: Inner pages paper weight (e.g., 80, 100, 120)
        print_cover_mode: Cover print (0=2pp one side, 1=4pp both sides)
        print_inner_mode: Inner print (0=colour, 1=b&w, 2=both scattered)
        cello_type: Cellophane (0=none, 1=gloss, 2=matt)
        stock_type_id: Internal paper type (29=Bond, 20=Satin/Silk)
        cover_stock_type_id: Cover paper type (20=Satin/Silk, 29=Bond)
        discount: Discount as decimal
    
    Returns:
        Dict with success, quote result, or error
    """
    if not GOD_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "GOD calculators not available. Check database connection."
        }
    
    try:
        from decimal import Decimal
        
        # PerfectBoundBooksCalculator creates its own DB connection
        calculator = PerfectBoundBooksCalculator()
        
        result = calculator.calculate(
            quantity=quantity,
            book_width=book_width,
            book_height=book_height,
            pages=pages,
            stock_type_id=stock_type_id,
            internal_stock_gsm=inner_gsm,
            internal_print_mode=print_inner_mode,
            cover_stock_type_id=cover_stock_type_id,
            cover_stock_gsm=cover_gsm,
            cover_print_mode=print_cover_mode,
            cello_type=cello_type,
            discount=Decimal(str(discount))
        )
        
        return {
            "success": True,
            "product_type": "Perfect Bound Books (GOD)",
            "quantity": quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "total_cost_inc_gst": float(result.total_inc_gst),
            "breakdown": {
                "cover_cost": float(result.cover_cost),
                "internal_cost": float(result.internal_cost),
                "cello_cost": float(result.cello_cost),
                "binding_cost": float(result.binding_cost),
                "trimming_cost": float(result.trimming_cost),
                "cutting_cost": float(result.cutting_cost),
                "scoring_cost": float(result.scoring_cost),
                "imposition_setup": float(result.imposition_setup),
                "proof_cost": float(result.proof_cost),
                "extra_books": float(result.extra_books)
            },
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [GOD Perfect Bound Books Calculator] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def calculate_corflute_signs_god(
    quantity: int,
    width: int,
    height: int,
    thickness: int = 5,
    print_sides: str = "single",
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) corflute signs calculator
    
    Args:
        quantity: Number of signs
        width: Sign width in mm (e.g., 600, 900, 1200)
        height: Sign height in mm (e.g., 600, 900, 1200)
        thickness: Corflute thickness in mm (3, 5, or 10)
        print_sides: "single" or "double"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not GOD_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "GOD calculators not available. Check database connection."
        }
    
    try:
        from decimal import Decimal
        
        calculator = CorflutePricingCalculator()  # No args needed
        
        # Convert print_sides to string format if passed as int
        if isinstance(print_sides, int):
            print_sides_str = "double" if print_sides == 2 else "single"
        else:
            print_sides_str = print_sides.lower() if print_sides else "single"
        
        result = calculator.calculate_base_quote(
            width_mm=width,
            height_mm=height,
            thickness_mm=thickness,
            quantity=quantity,
            print_sides=print_sides_str
        )
        
        return {
            "success": True,
            "product_type": "Corflute Signs (GOD)",
            "quantity": result['quantity'],
            "cost_to_business": float(result['total_cost_ex_margin']),
            "profit_margin": float(result['margin_percent']),
            "total_cost_ex_gst": float(result['total_cost_inc_margin']),
            "total_cost_inc_gst": float(result['total_inc_gst']),
            "breakdown": {
                "material_cost_per_unit": result['material_cost_per_unit'],
                "print_cost_per_unit": result['print_cost_per_unit'],
                "cutting_cost_per_unit": result['cutting_cost_per_unit'],
                "margin_multiplier": result['margin_multiplier']
            },
            "specifications": {
                "dimensions": result['dimensions'],
                "area_sqm": result['area_sqm'],
                "thickness_mm": result['thickness_mm'],
                "print_specification": result['print_specification']
            }
        }
        
    except Exception as e:
        print(f"❌ [GOD Corflute Signs Calculator] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ==================== SHOPIFY CALCULATOR WRAPPERS ====================

def calculate_economical_business_cards_shopify(
    quantity: int,
    double_sided: bool = True,
    print_type: str = "Colour",
    artworks: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Economical Business Cards (WRAPPER - Translation Layer)
    
    Schema Parameters (User-facing):
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        double_sided: True for double-sided, False for single-sided (default: True)
        print_type: "Colour" or "Black & White" (default: "Colour")
        artworks: Number of different designs (1-50, default: 1, first free, $15 per extra)
    
    Backend Translation:
        double_sided (bool) → print_sides (str): "Single side print" or "Double side print"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # TRANSLATION LAYER: Schema → Backend
        print_sides = "Double side print" if double_sided else "Single side print"
        
        # Ensure quantity is integer (may come as string from schema)
        quantity = int(quantity)
        
        calculator = EconomicalBusinessCardsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            artworks=artworks
        )
        
        return {
            "success": True,
            "product_type": "Economical Business Cards",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_card": float(result.cost_per_card),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Economical Business Cards] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_premium_business_cards_shopify(
    quantity: int,
    double_sided: bool = True,
    print_type: str = "Colour",
    finish_size: str = "90mm x 55mm",
    paper_stock: str = "Satin 350GSM",
    celloglaze: str = "1 Side Gloss",
    artworks: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Premium Business Cards (WRAPPER - Translation Layer)
    
    Schema Parameters (User-facing):
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        double_sided: True for double-sided, False for single-sided (default: True)
        print_type: "Colour" or "Black & White" (default: "Colour")
        finish_size: "90mm x 55mm" (standard) or "90mm x 45mm" (slim) (default: "90mm x 55mm")
        paper_stock: "Satin 350GSM", "King Kong High Bulk", "EcoStar 350GSM Uncoated" (default: "Satin 350GSM")
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt", 
                    "1 Side SILK FEEL Matt", "2 Side SILK FEEL Matt" (default: "1 Side Gloss")
        artworks: Number of different designs (1-50, default: 1)
    
    Backend Translation:
        double_sided (bool) → print_sides (str): "Single side print" or "Double side print"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # TRANSLATION LAYER: Schema → Backend
        print_sides = "Double side print" if double_sided else "Single side print"
        
        # Ensure quantity is integer (may come as string from schema)
        quantity = int(quantity)
        
        calculator = PremiumBusinessCardsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            finish_size=finish_size,
            paper_stock=paper_stock,
            celloglaze=celloglaze,
            artworks=artworks
        )
        
        return {
            "success": True,
            "product_type": "Premium Business Cards",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_card": float(result.cost_per_card),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Premium Business Cards] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_folded_flyers_shopify(
    quantity: int,
    size: str,
    stock: str,
    double_sided: bool = True,
    folding: str = "Single Fold",
    print_type: str = "Colour",
    artworks: int = 1,
    celloglaze: str = "None",
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Folded Flyers (WRAPPER - Translation Layer)
    
    Schema Parameters (User-facing):
        quantity: Number of flyers
        size: "A5", "A4", "A3", or "6pp A4"
        stock: Paper stock string (e.g., "Satin 128GSM", "Satin 150GSM", "Uncoated Bond 100GSM")
        double_sided: True for double-sided, False for single-sided (default: True)
        folding: "Single Fold", "Double Fold", or "Triple Fold" (default: "Single Fold")
        print_type: "Colour" or "Black & White" (default: "Colour")
        artworks: Number of artwork designs (1-50, default: 1)
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt" (default: "None")
    
    Backend Translation:
        stock (str) → paper_stock (str): Same value
        double_sided (bool) → print_sides (str): "Single side print" or "Double side print"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # TRANSLATION LAYER: Schema → Backend
        paper_stock = stock  # Rename for backend
        print_sides = "Double side print" if double_sided else "Single side print"
        
        # Ensure quantity is integer (may come as string from schema)
        quantity = int(quantity)
        
        # Import backend enums
        from shopify_calculators.FoldedFlyers_Shopify_Calculator import (
            PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
        )
        
        # Translation: Map schema strings to backend enums
        size_map = {
            "A5": FinishSize.A5,
            "A4": FinishSize.A4,
            "A3": FinishSize.A3,
            "6pp A4": FinishSize.A4_6PP
        }
        
        sides_map = {
            "Single side print": PrintSides.SINGLE_SIDE,
            "Double side print": PrintSides.DOUBLE_SIDE
        }
        
        type_map = {
            "Colour": PrintType.COLOUR,
            "Black & White": PrintType.BLACK_WHITE
        }
        
        stock_map = {
            "Satin 128GSM": PaperStock.SATIN_128GSM,
            "Satin 150GSM": PaperStock.SATIN_150GSM,
            "Satin 250GSM": PaperStock.SATIN_250GSM,
            "Satin 300GSM": PaperStock.SATIN_300GSM,
            "Satin 350GSM": PaperStock.SATIN_350GSM,
            "Uncoated Bond 80GSM": PaperStock.UNCOATED_80GSM,
            "Uncoated Bond 90GSM": PaperStock.UNCOATED_90GSM,
            "Uncoated Bond 100GSM": PaperStock.UNCOATED_100GSM
        }
        
        fold_map = {
            "Single Fold": FoldType.SINGLE_FOLD,
            "Double Fold": FoldType.DOUBLE_FOLD,
            "Triple Fold": FoldType.TRIPLE_FOLD
        }
        
        cello_map = {
            "None": Celloglaze.NONE,
            "1 Side Gloss": Celloglaze.ONE_SIDE_GLOSS,
            "2 Side Gloss": Celloglaze.TWO_SIDE_GLOSS,
            "1 Side Matt": Celloglaze.ONE_SIDE_MATT,
            "2 Side Matt": Celloglaze.TWO_SIDE_MATT
        }
        
        calculator = FoldedFlyersShopifyCalculator()
        result = calculator.calculate_quote(
            quantity=quantity,
            print_sides=sides_map.get(print_sides, PrintSides.SINGLE_SIDE),
            print_type=type_map.get(print_type, PrintType.COLOUR),
            finish_size=size_map.get(size, FinishSize.A5),
            paper_stock=stock_map.get(paper_stock, PaperStock.SATIN_150GSM),
            artworks=artworks,
            fold_type=fold_map.get(folding, FoldType.SINGLE_FOLD),
            celloglaze=cello_map.get(celloglaze, Celloglaze.NONE)
        )
        
        return {
            "success": True,
            "product_type": "Folded Flyers",
            "quantity": result.quantity,
            "total_price": float(result.final_price),
            "unit_price": float(result.final_price / result.quantity),
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Folded Flyers] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def calculate_wire_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str,
    cover_stock: str,
    inner_stock: str,
    cover_cellophane: str = "No Cellophane",
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Wire Bound Books
    
    Args:
        quantity: Number of books
        pages: Total page count (must be divisible by 4)
        size: "A4" or "A5"
        cover_stock: Cover paper stock
        inner_stock: Inner pages paper stock
        cover_cellophane: "No Cellophane", "Gloss Cellophane", or "Matt Cellophane"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        calculator = WireBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            internal_pages=pages,
            finish_size=size,
            printed_front_cover=cover_stock,
            internal_stock=inner_stock,
            front_celloglaze=cover_cellophane
        )
        
        # Convert breakdown values safely (handle strings like "percentage")
        breakdown_converted = {}
        for k, v in result.breakdown.items():
            try:
                breakdown_converted[k] = float(v)
            except (ValueError, TypeError):
                breakdown_converted[k] = str(v)  # Keep as string if not numeric
        
        return {
            "success": True,
            "product_type": "Wire Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": breakdown_converted,
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Wire Bound Books] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_spiral_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str,
    cover_stock: str,
    inner_stock: str,
    cover_cellophane: str = "No Cellophane",
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Spiral Bound Books
    
    Args:
        quantity: Number of books
        pages: Total page count (must be divisible by 4)
        size: "A4" or "A5"
        cover_stock: Cover paper stock
        inner_stock: Inner pages paper stock
        cover_cellophane: "No Cellophane", "Gloss Cellophane", or "Matt Cellophane"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        calculator = SpiralBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            internal_pages=pages,
            finish_size=size,
            printed_front_cover=cover_stock,
            internal_stock=inner_stock,
            front_celloglaze=cover_cellophane
        )
        
        return {
            "success": True,
            "product_type": "Spiral Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Spiral Bound Books] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_saddle_stitch_books(
    quantity: int,
    artworks: int = 1,
    cover_option: str = "Hard Cover",
    cover_stock: str = "Satin 350GSM",
    cover_print_type: str = "2 side colour (4pp)",
    celloglaze: str = "None",
    printed_pages: str = "20pp",
    finish_size: str = "A5 Portrait",
    content_print_type: str = "Colour",
    content_stock_type: str = "Satin 150GSM",
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Saddle Stitch Books
    
    Args:
        quantity: Number of books
        artworks: Number of different artworks (1 = included, >1 = extra charge)
        cover_option: "Hard Cover" or other options
        cover_stock: Cover paper stock (e.g., "Satin 350GSM")
        cover_print_type: Cover printing type (e.g., "2 side colour (4pp)")
        celloglaze: Celloglaze finish (e.g., "None", "Gloss outside only")
        printed_pages: Page count as string (e.g., "20pp", "24pp")
        finish_size: Book size (e.g., "A5 Portrait", "A4 Landscape")
        content_print_type: Interior printing (e.g., "Colour", "Black & White")
        content_stock_type: Interior paper stock (e.g., "Satin 150GSM")
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        from inhouse_modules.shopify_calculators.SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator
        
        calculator = SaddleStitchBooksShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks,
            cover_option=cover_option,
            cover_stock=cover_stock,
            cover_print_type=cover_print_type,
            celloglaze=celloglaze,
            printed_pages=printed_pages,
            finish_size=finish_size,
            content_print_type=content_print_type,
            content_stock_type=content_stock_type
        )
        
        return {
            "success": True,
            "product_type": "Saddle Stitch Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Saddle Stitch Books] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


def calculate_bollard_signs(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Bollard Signs"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator
        calculator = BollardSignsShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Bollard Signs",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Bollard Signs] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_construction_signs(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Construction Signs"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.ConstructionSigns_Shopify_Calculator import ConstructionSignsShopifyCalculator
        calculator = ConstructionSignsShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Construction Signs",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Construction Signs] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_election_signs(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Election Signs"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.ElectionSigns_Shopify_Calculator import ElectionSignsShopifyCalculator
        calculator = ElectionSignsShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Election Signs",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Election Signs] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_corflute_insert_a_frame(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Corflute Insert A-Frame"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.CorfluteInsertA_Frame_Shopify_Calculator import CorfluteInsertA_FrameShopifyCalculator
        calculator = CorfluteInsertA_FrameShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Corflute Insert A-Frame",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Corflute Insert A-Frame] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_metal_face_a_frame(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Metal Face A-Frame"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.MetalFaceA_Frame_Shopify_Calculator import MetalFaceA_FrameShopifyCalculator
        calculator = MetalFaceA_FrameShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Metal Face A-Frame",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Metal Face A-Frame] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_luxury_classic_pull_up_banners(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Luxury Classic Pull Up Banners"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.LuxuryClassicPullUpBanners_Shopify_Calculator import LuxuryClassicPullUpBannersShopifyCalculator
        calculator = LuxuryClassicPullUpBannersShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Luxury Classic Pull Up Banners",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Luxury Classic Pull Up Banners] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_selfie_frames(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Selfie Frames"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.SelfieFrames_Shopify_Calculator import SelfieFramesShopifyCalculator
        calculator = SelfieFramesShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Selfie Frames",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Selfie Frames] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_stackable_cubes(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Stackable Cubes"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.StackableCubes_Shopify_Calculator import StackableCubesShopifyCalculator
        calculator = StackableCubesShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Stackable Cubes",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Stackable Cubes] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_strut_cards_a3(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Strut Cards A3"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.StrutCardsA3_Shopify_Calculator import StrutCardsA3ShopifyCalculator
        calculator = StrutCardsA3ShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Strut Cards A3",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Strut Cards A3] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_strut_cards_a4(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Strut Cards A4"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.StrutCardsA4_Shopify_Calculator import StrutCardsA4ShopifyCalculator
        calculator = StrutCardsA4ShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Strut Cards A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Strut Cards A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_custom_poster_printing(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Custom Poster Printing"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator
        calculator = CustomPosterPrintingShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Custom Poster Printing",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Custom Poster Printing] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_custom_vinyl_stickers(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Custom Vinyl Stickers"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.CustomVinylStickers_Shopify_Calculator import CustomVinylStickersShopifyCalculator
        calculator = CustomVinylStickersShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Custom Vinyl Stickers",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Custom Vinyl Stickers] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_premium_bookmarks(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Premium Bookmarks"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator
        calculator = PremiumBookmarksShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Premium Bookmarks",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Premium Bookmarks] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_printed_letterheads(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Printed Letterheads"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.PrintedLetterheads_Shopify_Calculator import PrintedLetterheadsShopifyCalculator
        calculator = PrintedLetterheadsShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Printed Letterheads",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Printed Letterheads] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_with_compliments_slips(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for With Compliments Slips"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.WithComplimentsSlips_Shopify_Calculator import WithComplimentsSlipsShopifyCalculator
        calculator = WithComplimentsSlipsShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "With Compliments Slips",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify With Compliments Slips] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_notepads_a4(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Notepads A4"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator
        calculator = NotepadsA4ShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Notepads A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Notepads A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_notepads_a5(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Notepads A5"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator
        calculator = NotepadsA5ShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Notepads A5",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Notepads A5] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_notepads_a6(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Notepads A6"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.NotepadsA6_Shopify_Calculator import NotepadsA6ShopifyCalculator
        calculator = NotepadsA6ShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Notepads A6",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Notepads A6] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_spiral_bound_books(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Spiral Bound Books"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from inhouse_modules.shopify_calculators.SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
        
        # Map schema parameters to backend parameters
        # Handle pages parameter - convert "40pp" to 40
        pages_value = kwargs.get('number_of_content_pages', kwargs.get('pages', 100))
        if isinstance(pages_value, str):
            pages_value = int(pages_value.replace('pp', ''))
        
        # Map print types - "Colour" -> "Black & White" or "Colour"
        content_print = kwargs.get('content_print_type', 'Black & White')
        if content_print == 'Colour':
            content_print = '2pp Colour'  # Default to 2pp if just "Colour"
        
        mapped_kwargs = {
            'quantity': kwargs.get('quantity'),
            'artworks': kwargs.get('artworks', 1),
            'finish_size': kwargs.get('finish_size', 'A5 Portrait'),
            'outer_front_cover': kwargs.get('outer_front_cover', 'Not Required'),
            'printed_front_cover': kwargs.get('printed_front_cover', '300GSM Satin'),
            'front_cover_print': kwargs.get('cover_print_type', '2pp Colour'),  # Schema: cover_print_type -> Backend: front_cover_print
            'front_celloglaze': kwargs.get('celloglaze', 'None'),  # Schema: celloglaze -> Backend: front_celloglaze
            'outer_back_cover': kwargs.get('outer_back_cover', 'Not Required'),
            'printed_back_cover': kwargs.get('printed_back_cover', 'None'),
            'back_cover_print': kwargs.get('back_cover_print_type', '2pp Colour'),  # Schema: back_cover_print_type -> Backend: back_cover_print
            'back_celloglaze': kwargs.get('back_celloglaze', 'None'),
            'internal_pages': pages_value,  # Converted to int above
            'internal_stock': kwargs.get('content_paper_stock', kwargs.get('content_stock', 'Uncoated Bond 100GSM')),  # Schema: content_paper_stock or content_stock -> Backend: internal_stock
            'internal_print': content_print  # Converted above
        }
        
        calculator = SpiralBoundShopifyCalculator()
        result = calculator.calculate(**mapped_kwargs)
        return {
            "success": True,
            "product_type": "Spiral Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.unit_price),  # Spiral Bound doesn't have separate cost_per_item, use unit_price
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Spiral Bound Books] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


# ==================== MODULE INITIALIZATION ====================

if __name__ == "__main__":
    # Test the wrapper functions
    print("=" * 60)
    print("Testing Quote Calculator Wrapper")
    print("=" * 60)
    
    if CALCULATOR_AVAILABLE:
        print("\n✅ Calculator available")
        
        # Test stock list
        print("\n📋 Testing get_stock_list():")
        stocks = get_stock_list()
        print(f"   Found {len(stocks)} stocks")
        if stocks:
            print(f"   Example: {stocks[0]}")
        
        # Test business cards calculator
        print("\n💳 Testing calculate_business_cards():")
        try:
            result = calculate_business_cards(
                quantity=1000,
                stock_type="premium",
                sides=2
            )
            if result.get("success"):
                print(f"   ✅ Success: ${result.get('total_price'):.2f}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    else:
        print("\n❌ Calculator not available")
        print("   Ensure inhouse_modules is properly configured")
