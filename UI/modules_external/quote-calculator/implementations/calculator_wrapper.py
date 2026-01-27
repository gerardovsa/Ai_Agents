"""
Quote Calculator Wrapper - Connects Registry V3 to inhouse_modules calculators

This wrapper provides AI tool access to InHouse Print quote calculators.
It wraps the existing calculator code in inhouse_modules/ without duplication.

Architecture:
    AI Agent Request
        ↓
    Registry V3
        ↓
    calculator_wrapper.py (THIS FILE) ← WITH TYPE ENFORCEMENT
        ↓
    inhouse_modules/complete_calculator_implementation.py
        ↓
    G_Folder database

TYPE SAFETY:
All wrapper functions use @enforce_schema_types decorator to automatically
convert parameter types (e.g., "500" string → 500 integer). This prevents
type mismatch errors between AI agents and backend calculators.

FILE: UI/external/modules/quote-calculator/implementations/calculator_wrapper.py
PURPOSE: Wrapper functions for quote calculator tools
DEPENDENCIES:
- inhouse_modules.complete_calculator_implementation
- schema_validator (type enforcement)

EXPORTS:
- calculate_business_cards(quantity, stock_type, sides)
- calculate_flyers(quantity, size, stock, sides)
- calculate_booklets(quantity, pages, cover_stock, inner_stock, size)
- calculate_perfect_bound_books(quantity, pages, cover_stock, inner_stock, size)
- calculate_letterheads(quantity, stock, colors)
- calculate_corflute_signs(quantity, size, thickness, sides)
- get_stock_list(category="all")

LAST MODIFIED: 2025-12-14 - Added comprehensive type enforcement system
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from decimal import Decimal

# Import type enforcement system
from schema_validator import enforce_schema_types, calculator_wrapper

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
# DEACTIVATED: GOD calculators removed from AI access (Jan 13, 2026)
# Using Shopify calculators as primary system
GOD_CALCULATORS_AVAILABLE = False
# try:
#     from GOD_flyer_calculator import FlyerCalculatorGOD
#     from GOD_letterhead_calculator import LetterheadCalculatorGOD
#     from GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator
#     from corflute_calculator import CorflutePricingCalculator
#     
#     GOD_CALCULATORS_AVAILABLE = True
#     print("✅ [GOD Calculators] Loaded successfully")
# except ImportError as e:
#     print(f"⚠️  [GOD Calculators] Failed to import: {e}")
#     print("   GOD calculator tools will not be available")

# Import Shopify calculators from In_House_SQL (source of truth)
SHOPIFY_CALCULATORS_AVAILABLE = False
try:
    from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
    from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
    from PrintedFlyers_Shopify_Calculator import PrintedFlyersShopifyCalculator
    from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
    from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
    from SpiralBound_Shopify_Calculator import SpiralBoundBooksShopifyCalculator
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

@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000])
def calculate_business_cards(
    quantity: int,
    stock_type: str,
    print_type: str,
    finish_size: str = "90x55mm",
    celloglaze: str = "none",
    **kwargs
) -> Dict[str, Any]:
    """
    DEPRECATED: This GOD calculator should NOT be used for business card quotes.
    
    ⚠️ WARNING: This calculator produces incorrect pricing (30-56% under-quoted).
    
    For business cards, ALWAYS use the specialized Shopify calculators:
    - calculate_premium_business_cards_shopify (Satin 350GSM, King Kong, EcoStar)
    - calculate_economical_business_cards_shopify (Standard 350GSM)
    
    This function is maintained for backward compatibility with flyer products only.
    
    TYPE SAFE: @calculator_wrapper decorator ensures all types are correct
    
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
        # CRITICAL VALIDATION: Reject business card requests
        if finish_size in ["90x55mm", "90x50mm", "85x55mm"] and (
            "business_card" in str(kwargs).lower() or 
            (width := kwargs.get("width")) and (height := kwargs.get("height")) and 
            (width in [85, 90] and height in [50, 55])
        ):
            return {
                "success": False,
                "error": "DEPRECATED: calculate_business_cards() should NOT be used for business card quotes. "
                        "This calculator produces incorrect pricing (30-56% under-quoted). "
                        "Use calculate_premium_business_cards_shopify or calculate_economical_business_cards_shopify instead.",
                "error_type": "deprecated_calculator",
                "recommended_tools": [
                    "calculate_premium_business_cards_shopify",
                    "calculate_economical_business_cards_shopify"
                ]
            }
        
        # Use Shopify calculator directly (like GOD calculators)
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        # NOTE: No need for int(quantity) - decorator already converted it!
        
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


@enforce_schema_types
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


# ORPHANED WRAPPER REMOVED (No schema exists for calculate_corflute_signs)
# Use calculate_corflute_signs_shopify instead (line ~990)


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

@enforce_schema_types
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
    
    TYPE SAFE: @enforce_schema_types decorator ensures all numeric types are correct
    
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


@enforce_schema_types
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
    
    TYPE SAFE: @enforce_schema_types decorator ensures all numeric types are correct
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


@enforce_schema_types
def calculate_perfect_bound_books_god(
    quantity: int = 100,
    pages: int = 100,
    book_width: int = 210,
    book_height: int = 297,
    cover_gsm: int = 300,
    inner_gsm: int = 80,
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


@calculator_wrapper(
    quantity_enum=[1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 1500, 2000, 3000, 5000, 10000],
    validate_params=True
)
def calculate_corflute_signs_shopify(
    quantity: int,
    size_preset: str = "600x900",
    custom_width_mm: int = 0,
    custom_height_mm: int = 0,
    thickness: str = "5mm",
    double_sided: bool = False,
    eyelet_option: str = "none",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate quote for Corflute Signs (Shopify)
    
    ✅ CURRENT PARAMETERS:
        quantity: Number of signs (1-10000)
        size_preset: "450x600", "600x900", "900x1200", "1200x2400", "custom"
        custom_width_mm: Custom width in mm (only if size_preset='custom')
        custom_height_mm: Custom height in mm (only if size_preset='custom')
        thickness: "3mm" or "5mm" (default: "5mm")
        double_sided: Print both sides - adds $6/sqm (default: False)
        eyelet_option: "none", "four_corners", "two_top", "two_center_lr", 
                       "two_center_tb", "six_top_bottom", "six_left_right"
        artworks: Number of artworks (first 5 free, then $5 each, default: 1)
    
    Returns:
        Dict with success, tier pricing breakdown, costs, discounts, final total
    """
    # Validate parameter values (AI learns valid options from errors)
    valid_size_presets = ["450x600", "600x900", "900x1200", "1200x2400", "custom"]
    if size_preset not in valid_size_presets:
        return {
            "success": False,
            "error": f"Invalid size_preset: '{size_preset}'. Must be one of: {', '.join(valid_size_presets)}"
        }
    
    if size_preset == "custom":
        if custom_width_mm < 100 or custom_width_mm > 3000:
            return {
                "success": False,
                "error": f"Invalid custom_width_mm: {custom_width_mm}. Must be between 100 and 3000 millimeters"
            }
        if custom_height_mm < 100 or custom_height_mm > 3000:
            return {
                "success": False,
                "error": f"Invalid custom_height_mm: {custom_height_mm}. Must be between 100 and 3000 millimeters"
            }
    
    valid_thicknesses = ["3mm", "5mm"]
    if thickness not in valid_thicknesses:
        return {
            "success": False,
            "error": f"Invalid thickness: '{thickness}'. Must be one of: {', '.join(valid_thicknesses)}"
        }
    
    valid_eyelet_options = ["none", "four_corners", "two_top", "two_center_lr", "two_center_tb", "six_top_bottom", "six_left_right"]
    if eyelet_option not in valid_eyelet_options:
        return {
            "success": False,
            "error": f"Invalid eyelet_option: '{eyelet_option}'. Must be one of: {', '.join(valid_eyelet_options)}"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        from corflute_calculator_shopify import (
            CorflutePricingCalculatorShopify,
            CorfluteSizePreset,
            CorfiuteThickness,
            EyeletOption
        )
        
        # Convert string parameters to int (fix type errors from JSON)
        quantity = int(quantity) if isinstance(quantity, str) else quantity
        custom_width_mm = int(custom_width_mm) if isinstance(custom_width_mm, str) else custom_width_mm
        custom_height_mm = int(custom_height_mm) if isinstance(custom_height_mm, str) else custom_height_mm
        artworks = int(artworks) if isinstance(artworks, str) else artworks
        
        # Map size preset string to enum
        size_map = {
            "450x600": CorfluteSizePreset.SIZE_450x600,
            "600x900": CorfluteSizePreset.SIZE_600x900,
            "900x1200": CorfluteSizePreset.SIZE_900x1200,
            "1200x2400": CorfluteSizePreset.SIZE_1200x2400,
            "custom": CorfluteSizePreset.CUSTOM
        }
        
        # Map thickness string to enum
        thickness_map = {
            "3mm": CorfiuteThickness.MM_3,
            "5mm": CorfiuteThickness.MM_5
        }
        
        # Map eyelet option string to enum
        eyelet_map = {
            "none": EyeletOption.NONE,
            "four_corners": EyeletOption.FOUR_CORNERS,
            "two_top": EyeletOption.TWO_TOP,
            "two_center_lr": EyeletOption.TWO_CENTER_LR,
            "two_center_tb": EyeletOption.TWO_CENTER_TB,
            "six_top_bottom": EyeletOption.SIX_TOP_BOTTOM,
            "six_left_right": EyeletOption.SIX_LEFT_RIGHT
        }
        
        calculator = CorflutePricingCalculatorShopify()
        result = calculator.calculate_quote(
            size_preset=size_map.get(size_preset, CorfluteSizePreset.SIZE_600x900),
            custom_width_mm=custom_width_mm,
            custom_height_mm=custom_height_mm,
            thickness=thickness_map.get(thickness, CorfiuteThickness.MM_5),
            quantity=quantity,
            double_sided=double_sided,
            eyelet_option=eyelet_map.get(eyelet_option, EyeletOption.NONE),
            artworks=artworks
        )
        
        return {
            "success": True,
            "product_type": "Corflute Signs (Shopify)",
            "quantity": result['quantity'],
            "total_price": result['total'],
            "per_unit_price": result['per_unit'],
            "breakdown": {
                "dimensions": f"{result['width_mm']}mm x {result['height_mm']}mm",
                "thickness": result['thickness'],
                "sqm_per_unit": result['sqm_per_unit'],
                "total_sqm": result['total_sqm'],
                "tier_price_per_sqm": result['tier_price_per_sqm'],
                "base_cost": result['base_cost'],
                "double_sided_cost": result['double_sided_cost'],
                "custom_premium": result['custom_premium'],
                "eyelet_cost": result['eyelet_cost'],
                "artwork_cost": result['artwork_cost'],
                "subtotal_before_discount": result['subtotal_before_discount'],
                "discount_5_percent": result['discount_amount'],
                "subtotal_after_discount": result['subtotal_after_discount'],
                "minimum_order_applied": result.get('minimum_applied', False)
            },
            "specifications": {
                "is_custom_size": result['is_custom_size'],
                "double_sided": result['double_sided'],
                "eyelets": result['eyelets'],
                "artworks": result['artworks']
            }
        }
        
    except Exception as e:
        print(f"❌ [Shopify Corflute Signs Calculator] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# ==================== SHOPIFY CALCULATOR WRAPPERS ====================

@calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_economical_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    print_sides: str = None,
    celloglaze: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Economical Business Cards - MATCHES SHOPIFY JSON EXACTLY
    
    TYPE SAFE: @calculator_wrapper decorator ensures:
    - quantity is converted from string to int if needed
    - quantity is validated against [250, 500, 1000, 2000, 5000, 10000]
    
    ✅ PARAMETERS (EXACT match to Shopify JSON config):
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single side print" or "Double side print" (default: "Double side print")
        print_type: "Colour" or "Black & White" (default: "Colour")
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt" (default: "None")
        artworks: Number of different designs (1-50, default: 1, first free, $15 per extra)
    
    ❌ NO TRANSLATION - AI must send exact strings from Shopify JSON
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # ========================================================================
        # STRICT VALIDATION: No defaults, no translation - AI must provide correct values
        # ========================================================================
        # NOTE: quantity is validated by @calculator_wrapper decorator
        
        # Apply Shopify JSON defaults for optional parameters
        if print_type is None:
            print_type = "Colour"  # Shopify JSON default
        
        if print_sides is None:
            print_sides = "Double side print"  # Shopify JSON default
        
        if celloglaze is None:
            celloglaze = "None"  # Shopify JSON default
        
        if artworks is None:
            artworks = 1  # Shopify JSON default
        
        # Validate parameter values are in allowed ranges/enums
        if print_type not in ["Colour", "Black & White"]:
            return {
                "success": False,
                "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
            }
        
        if celloglaze not in ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"]:
            return {
                "success": False,
                "error": f"Invalid celloglaze: '{celloglaze}'. Must be one of: None, 1 Side Gloss, 2 Side Gloss, 1 Side Matt, 2 Side Matt"
            }
        
        if artworks < 1 or artworks > 50:
            return {
                "success": False,
                "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
            }
        
        # STRICT VALIDATION: No translation - AI must send exact format from Shopify JSON
        if print_sides not in ["Single side print", "Double side print"]:
            return {
                "success": False,
                "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print' (exact match to Shopify JSON)",
                "valid_options": ["Single side print", "Double side print"]
            }
        
        calculator = EconomicalBusinessCardsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            artworks=artworks
        )
        
        response = {
            "success": True,
            "product_type": "Economical Business Cards",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_card": float(result.cost_per_card),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Economical Business Cards] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_premium_business_cards_shopify(
    quantity: int,
    print_type: str = None,
    paper_stock: str = None,
    print_sides: str = None,
    finish_size: str = None,
    celloglaze: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Premium Business Cards - MATCHES SHOPIFY JSON EXACTLY
    
    TYPE SAFE: @calculator_wrapper decorator ensures all types are correct
    
    ✅ PARAMETERS (EXACT match to Shopify JSON config):
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single side print" or "Double side print" (default: "Single side print")
        print_type: "Colour" or "Black & White" (default: "Colour")
        finish_size: "90mm x 55mm" (standard) or "90mm x 45mm" (slim) (default: "90mm x 55mm")
        paper_stock: "Satin 350GSM", "King Kong High Bulk", "EcoStar 350GSM Uncoated" (default: "Satin 350GSM")
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt", 
                    "1 Side SILK FEEL Matt", "2 Side SILK FEEL Matt" (default: "1 Side Gloss")
        artworks: Number of different designs (1-50, default: 1)
    
    ❌ NO TRANSLATION - AI must send exact strings from Shopify JSON
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # ========================================================================
        # STRICT VALIDATION: No translation - AI must provide correct values from Shopify JSON
        # ========================================================================
        # Apply Shopify JSON defaults for optional parameters
        if print_type is None:
            print_type = "Colour"  # Shopify JSON default
        
        if paper_stock is None:
            paper_stock = "Satin 350GSM"  # Shopify JSON default
        
        if print_sides is None:
            print_sides = "Single side print"  # Shopify JSON default
        
        if finish_size is None:
            finish_size = "90mm x 55mm"  # Shopify JSON default
        
        if celloglaze is None:
            celloglaze = "1 Side Gloss"  # Shopify JSON default
        
        if artworks is None:
            artworks = 1  # Shopify JSON default
        
        # Validate parameter values match Shopify JSON exactly
        if print_type not in ["Colour", "Black & White"]:
            return {
                "success": False,
                "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
            }
        
        if paper_stock not in ["Satin 350GSM", "King Kong High Bulk", "EcoStar 350GSM Uncoated"]:
            return {
                "success": False,
                "error": f"Invalid paper_stock: '{paper_stock}'. Must be one of: Satin 350GSM, King Kong High Bulk, EcoStar 350GSM Uncoated"
            }
        
        if print_sides not in ["Single side print", "Double side print"]:
            return {
                "success": False,
                "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print' (exact match to Shopify JSON)",
                "valid_options": ["Single side print", "Double side print"]
            }
        
        if celloglaze not in ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt", "1 Side SILK FEEL Matt", "2 Side SILK FEEL Matt"]:
            return {
                "success": False,
                "error": f"Invalid celloglaze: '{celloglaze}'. Must be one of: None, 1 Side Gloss, 2 Side Gloss, 1 Side Matt, 2 Side Matt, 1 Side SILK FEEL Matt, 2 Side SILK FEEL Matt"
            }
        
        if artworks < 1 or artworks > 50:
            return {
                "success": False,
                "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
            }
        
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
        
        response = {
            "success": True,
            "product_type": "Premium Business Cards",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_card": float(result.cost_per_card),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        # Add deprecation warnings if legacy parameters were used
        if warnings:
            response["deprecation_warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Premium Business Cards] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@calculator_wrapper(quantity_enum=[100, 250, 500, 1000, 2000, 5000, 10000], validate_params=True)
def calculate_folded_flyers_shopify(
    quantity: int,
    finish_size: str = None,       # ✅ CORRECTED: Use finish_size (not 'size')
    paper_stock: str = None,       # ✅ CORRECTED: Use paper_stock (not 'stock')
    print_type: str = None,
    print_sides: str = None,
    fold_type: str = None,         # ✅ CORRECTED: Use fold_type (actual website names)
    artworks: int = None,
    celloglaze: str = None,
    # DEPRECATED PARAMETERS (backwards compatibility - generates warnings)
    size: str = None,              # OLD: kept for backwards compat
    stock: str = None,             # OLD: kept for backwards compat
    folding: str = None,           # OLD: kept for backwards compat
    double_sided: bool = None,
    colour: bool = None,
    cellophane: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Folded Flyers - DEFENSIVE TRANSLATION PATTERN
    
    TYPE SAFE: @calculator_wrapper decorator ensures all types are correct
    VALIDATED: validate_params=True catches unknown parameters
    
    ✅ CORRECT PARAMETERS (match Python calculator):
        quantity: Number of flyers (100-10000)
        finish_size: Full format like "A5 - 148mm x 210mm" (REQUIRED format)
        paper_stock: Paper stock (e.g., "Satin 150GSM", "Uncoated Bond 100GSM")
        print_sides: "Single" or "Double" (simplified, not "Single side print")
        print_type: "Colour" or "Black & White"
        fold_type: ACTUAL website fold names like "Half fold to A5", "Tri Roll fold to DL", etc.
        artworks: Number of artwork designs (1-50, default: 1)
        celloglaze: "None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"
    
    ⚠️ DEPRECATED PARAMETERS (backwards compatibility - generates warnings):
        size (str) → use finish_size instead
        stock (str) → use paper_stock instead
        folding (str) → use fold_type with actual fold names
        double_sided (bool) → use print_sides instead
        colour (bool) → use print_type instead
        cellophane (str) → use celloglaze instead
    
    Returns:
        Dict with success, quote result, specifications, and warnings (if any)
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # LEGACY PARAMETER TRANSLATION (backwards compatibility)
        warnings = []
        
        # Translate OLD parameter names to NEW
        if size is not None and finish_size is None:
            finish_size = size
            warnings.append({
                "deprecated_parameter": "size",
                "use_instead": "finish_size",
                "message": f"⚠️ Parameter 'size' is deprecated. Use 'finish_size' instead."
            })
        
        if stock is not None and paper_stock is None:
            paper_stock = stock
            warnings.append({
                "deprecated_parameter": "stock",
                "use_instead": "paper_stock",
                "message": f"⚠️ Parameter 'stock' is deprecated. Use 'paper_stock' instead."
            })
        
        if folding is not None and fold_type is None:
            fold_type = folding
            warnings.append({
                "deprecated_parameter": "folding",
                "use_instead": "fold_type",
                "message": f"⚠️ Parameter 'folding' is deprecated. Use 'fold_type' with actual fold names instead."
            })
        
        if colour is not None:
            print_type = "Colour" if colour else "Black & White"
            warnings.append({
                "deprecated_parameter": "colour",
                "use_instead": "print_type",
                "message": f"⚠️ Parameter 'colour' is deprecated. Use 'print_type' instead."
            })
        
        if double_sided is not None and print_sides is None:
            print_sides = "Double" if double_sided else "Single"
            warnings.append({
                "deprecated_parameter": "double_sided",
                "use_instead": "print_sides",
                "message": f"⚠️ Parameter 'double_sided' is deprecated. Use 'print_sides' instead."
            })
        
        if cellophane is not None:
            # Map old cellophane values to new celloglaze format
            cellophane_map = {
                "None": "None",
                "Gloss": "2 Side Gloss",  # Default to 2-sided for old "Gloss"
                "Matt": "2 Side Matt"      # Default to 2-sided for old "Matt"
            }
            celloglaze = cellophane_map.get(cellophane, "None")
            warnings.append({
                "deprecated_parameter": "cellophane",
                "use_instead": "celloglaze",
                "message": f"⚠️ Parameter 'cellophane' is deprecated. Use 'celloglaze' instead."
            })
        
        # Log warnings to console (visible in Flask logs)
        if warnings:
            print(f"\n{'='*80}")
            print(f"⚠️  DEPRECATED PARAMETERS DETECTED in calculate_folded_flyers_shopify")
            print(f"{'='*80}")
            for w in warnings:
                print(f"  • {w['message']}")
            print(f"{'='*80}\n")
        
        # ========================================================================
        # APPLY DEFAULTS
        # ========================================================================
        
        if finish_size is None:
            finish_size = "A4 - 210mm x 297mm"
        
        if paper_stock is None:
            paper_stock = "Satin 150GSM"
        
        if print_type is None:
            print_type = "Colour"
        
        if print_sides is None:
            print_sides = "Double"
        
        if fold_type is None:
            fold_type = "Half fold to A5"  # Default for A4
        
        if artworks is None:
            artworks = 1
        
        if celloglaze is None:
            celloglaze = "None"
        
        # ========================================================================
        # VALIDATION
        # ========================================================================
        
        # Validate print_sides (accept "Single" or "Double")
        if print_sides not in ["Single", "Double"]:
            return {
                "success": False,
                "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single' or 'Double'.",
                "valid_options": ["Single", "Double"]
            }
        
        # Validate print_type
        if print_type not in ["Colour", "Black & White"]:
            return {
                "success": False,
                "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'."
            }
        
        # Validate finish_size (full format required)
        valid_sizes = [
            "A5 - 148mm x 210mm",
            "A4 - 210mm x 297mm",
            "A3 - 297mm x 420mm",
            "6pp A4 - 630mm x 297mm"
        ]
        if finish_size not in valid_sizes:
            return {
                "success": False,
                "error": f"Invalid finish_size: '{finish_size}'. Must use full format.",
                "valid_options": valid_sizes
            }
        
        # Validate paper_stock
        valid_stocks = ["Satin 128GSM", "Satin 150GSM", "Satin 250GSM", "Satin 300GSM", "Satin 350GSM", 
                        "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
        if paper_stock not in valid_stocks:
            return {
                "success": False,
                "error": f"Invalid paper_stock: '{paper_stock}'.",
                "valid_options": valid_stocks
            }
        
        # Validate fold_type (actual website fold names)
        valid_folds = [
            "Half fold to A6",
            "Half fold to A5",
            "Half fold to A4",
            "Tri Roll fold to DL",
            "Tri Z fold to DL",
            "Tri Roll fold to A4",
            "Crash fold to A5(Half then half)",
            "Crash fold to DL(Half then roll)"
        ]
        if fold_type not in valid_folds:
            return {
                "success": False,
                "error": f"Invalid fold_type: '{fold_type}'. Must use actual website fold name.",
                "valid_options": valid_folds,
                "hint": "Use exact fold names like 'Half fold to A5', not generic 'Single Fold'"
            }
        
        # Validate celloglaze
        if celloglaze not in ["None", "1 Side Gloss", "2 Side Gloss", "1 Side Matt", "2 Side Matt"]:
            return {
                "success": False,
                "error": f"Invalid celloglaze: '{celloglaze}'."
            }
        
        # Validate artworks range
        if artworks < 1 or artworks > 50:
            return {
                "success": False,
                "error": f"Invalid artworks: {artworks}. Must be between 1 and 50."
            }
        
        # ========================================================================
        # ENUM MAPPING: Convert strings to backend enums
        # ========================================================================
        
        # Import backend enums
        from shopify_calculators.FoldedFlyers_Shopify_Calculator import (
            PrintSides, PrintType, FinishSize, PaperStock, FoldType, Celloglaze
        )
        
        size_map = {
            "A5 - 148mm x 210mm": FinishSize.A5,
            "A4 - 210mm x 297mm": FinishSize.A4,
            "A3 - 297mm x 420mm": FinishSize.A3,
            "6pp A4 - 630mm x 297mm": FinishSize.A4_6PP
        }
        
        sides_map = {
            "Single": PrintSides.SINGLE_SIDE,
            "Double": PrintSides.DOUBLE_SIDE
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
            "Half fold to A6": FoldType.HALF_FOLD_TO_A6,
            "Half fold to A5": FoldType.HALF_FOLD_TO_A5,
            "Half fold to A4": FoldType.HALF_FOLD_TO_A4,
            "Tri Roll fold to DL": FoldType.TRI_ROLL_FOLD_TO_DL,
            "Tri Z fold to DL": FoldType.TRI_Z_FOLD_TO_DL,
            "Tri Roll fold to A4": FoldType.TRI_ROLL_FOLD_TO_A4,
            "Crash fold to A5(Half then half)": FoldType.CRASH_FOLD_TO_A5_HALF,
            "Crash fold to DL(Half then roll)": FoldType.CRASH_FOLD_TO_DL_HALF
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
            print_sides=sides_map[print_sides],
            print_type=type_map[print_type],
            finish_size=size_map[finish_size],
            paper_stock=stock_map[paper_stock],
            artworks=artworks,
            fold_type=fold_map[fold_type],
            celloglaze=cello_map[celloglaze]
        )
        
        response = {
            "success": True,
            "product_type": "Folded Flyers",
            "quantity": result.quantity,
            "total_price": float(result.final_price),
            "unit_price": float(result.final_price / result.quantity),
            "specifications": result.specifications
        }
        
        # Add deprecation warnings if legacy parameters were used
        if warnings:
            response["deprecation_warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Folded Flyers] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@calculator_wrapper(validate_params=True)
def calculate_printed_flyers_shopify(
    quantity: int,
    print_sides: str = "Double",
    print_type: str = "Colour",
    finish_size: str = "A5 - 148mm x 210mm",
    paper_stock: str = "Satin 150GSM",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Shopify calculator for Printed Flyers (flat/unfolded)
    
    Args:
        quantity: Number of flyers (100, 250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single" or "Double" (default: "Double")
        print_type: "Colour" or "Black & White" (default: "Colour")
        finish_size: Size option - DL (6/sheet), A6 (8/sheet), A5 (4/sheet), A4 (2/sheet), A3 (1/sheet)
        paper_stock: Paper stock type (9 options: Satin 128-350GSM, Uncoated 80-100GSM)
        artworks: Number of different designs (1-50, first FREE then $15 each)
    
    Returns:
        Dict with success, quote result, or error
        
    Features:
        - 11-tier profit margin system (170% → 25% based on cost)
        - Automatic 10% discount for quantities ≥ 1000
        - Items per sheet calculation (DL=6, A6=8, A5=4, A4=2, A3=1)
        - 5% stock waste factor
        - Setup: $15 imposition + $12 guillotine + artwork extras
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        # Initialize calculator
        calculator = PrintedFlyersShopifyCalculator()
        
        # Calculate quote
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            finish_size=finish_size,
            paper_stock=paper_stock,
            artworks=artworks
        )
        
        # Return result dict
        return result.to_dict()
        
    except Exception as e:
        print(f"❌ [Shopify Printed Flyers] Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "product_type": "Printed Flyers"
        }


@calculator_wrapper(validate_params=True)
def calculate_wire_bound_books_shopify(
    quantity: int,
    internal_pages: int = 100,
    finish_size: str = "A5 Portrait",
    printed_front_cover: str = "300GSM Satin",
    front_cover_print: str = "2pp Colour",
    front_celloglaze: str = "None",
    outer_front_cover: str = "Not Required",
    printed_back_cover: str = "300GSM Satin",
    back_cover_print: str = "2pp Colour",
    back_celloglaze: str = "None",
    outer_back_cover: str = "None",
    internal_stock: str = "Uncoated Bond 100GSM",
    internal_print: str = "Black & White",
    artworks: int = 1,
    # Legacy parameter support (DEPRECATED - will be removed)
    pages: int = None,
    size: str = None,
    cover_stock: str = None,
    inner_stock: str = None,
    cover_cellophane: str = None,
    front_cover_pvc: bool = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Wire Bound Books
    
    Args:
        quantity: Number of books (1-10000)
        internal_pages: Total page count for internal pages (1-500)
        finish_size: Book size with orientation (e.g., "A5 Portrait", "A4 Landscape")
        printed_front_cover: Front printed cover stock (250/300/350GSM Satin)
        front_cover_print: Front cover print type (1pp/2pp Colour/Black & White)
        front_celloglaze: Front cover celloglaze (None/1 Side/2 Sided Gloss/Matt)
        outer_front_cover: Clear PVC overlay on front (Not Required/Clear PVC)
        printed_back_cover: Back printed cover stock
        back_cover_print: Back cover print type
        back_celloglaze: Back cover celloglaze
        outer_back_cover: Back cover outer layer (None/Clear PVC/Black Leather/Blank)
        internal_stock: Internal pages paper stock
        internal_print: Internal print type (Full Colour/Black & White)
        artworks: Number of different artworks (1-50, first free, $15 each)
        
        DEPRECATED PARAMETERS (legacy support, will warn):
        pages: Use 'internal_pages' instead
        size: Use 'finish_size' instead
        cover_stock: Use 'printed_front_cover' instead
        inner_stock: Use 'internal_stock' instead (note: spelling)
        cover_cellophane: Use 'front_celloglaze' instead
        front_cover_pvc: Use 'outer_front_cover' instead
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    # ========================================================================
    # LEGACY PARAMETER TRANSLATION (with warnings)
    # ========================================================================
    warnings = []
    
    # Translate 'pages' → 'internal_pages'
    if pages is not None:
        internal_pages = pages
        warnings.append({
            "deprecated": "pages",
            "use_instead": "internal_pages",
            "value_sent": pages,
            "translated_to": internal_pages
        })
    
    # Translate 'size' → 'finish_size' (add orientation if missing)
    if size is not None:
        if "Portrait" not in size and "Landscape" not in size:
            finish_size = f"{size} Portrait"  # Default to Portrait
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size,
                "note": "Added 'Portrait' orientation (default)"
            })
        else:
            finish_size = size
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size
            })
    
    # Translate 'cover_stock' → 'printed_front_cover'
    if cover_stock is not None:
        printed_front_cover = cover_stock
        warnings.append({
            "deprecated": "cover_stock",
            "use_instead": "printed_front_cover",
            "value_sent": cover_stock,
            "translated_to": printed_front_cover
        })
    
    # Translate 'inner_stock' → 'internal_stock' (fix spelling + format)
    if inner_stock is not None:
        # Fix format: "100GSM Uncoated" → "Uncoated Bond 100GSM"
        if "Uncoated" in inner_stock:
            gsm = inner_stock.split("GSM")[0] + "GSM"
            internal_stock = f"Uncoated Bond {gsm}"
        elif "Satin" in inner_stock:
            gsm = inner_stock.split("GSM")[0] + "GSM"
            internal_stock = f"Satin {gsm}"
        else:
            internal_stock = inner_stock
        warnings.append({
            "deprecated": "inner_stock",
            "use_instead": "internal_stock",
            "value_sent": inner_stock,
            "translated_to": internal_stock
        })
    
    # Translate 'cover_cellophane' → 'front_celloglaze'
    if cover_cellophane is not None:
        # Map values: "No Cellophane" → "None", "Gloss Cellophane" → "2 Sided Gloss"
        cello_map = {
            "No Cellophane": "None",
            "Gloss Cellophane": "2 Sided Gloss",
            "Matt Cellophane": "2 Sided Matt"
        }
        front_celloglaze = cello_map.get(cover_cellophane, cover_cellophane)
        warnings.append({
            "deprecated": "cover_cellophane",
            "use_instead": "front_celloglaze",
            "value_sent": cover_cellophane,
            "translated_to": front_celloglaze
        })
    
    # Translate 'front_cover_pvc' → 'outer_front_cover'
    if front_cover_pvc is not None:
        outer_front_cover = "Clear PVC" if front_cover_pvc else "Not Required"
        warnings.append({
            "deprecated": "front_cover_pvc",
            "use_instead": "outer_front_cover",
            "value_sent": front_cover_pvc,
            "translated_to": outer_front_cover
        })
    
    # Print warnings if any legacy parameters were used
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_wire_bound_books_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
            if 'note' in w:
                log_msg += f"      Note: {w['note']}\n"
        print(log_msg)
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    if internal_pages < 1 or internal_pages > 500:
        return {
            "success": False,
            "error": f"Invalid internal_pages: {internal_pages}. Must be between 1 and 500"
        }
    
    valid_sizes = ["A6 Portrait", "A6 Landscape", "DL Portrait", "DL Landscape", "A5 Portrait", "A5 Landscape", "A4 Portrait", "A4 Landscape"]
    if finish_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_cover_stock = ["250GSM Satin", "300GSM Satin", "350GSM Satin"]
    if printed_front_cover not in valid_cover_stock:
        return {
            "success": False,
            "error": f"Invalid printed_front_cover: '{printed_front_cover}'. Must be one of: {', '.join(valid_cover_stock)}"
        }
    
    if printed_back_cover not in valid_cover_stock:
        return {
            "success": False,
            "error": f"Invalid printed_back_cover: '{printed_back_cover}'. Must be one of: {', '.join(valid_cover_stock)}"
        }
    
    valid_print = ["1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"]
    if front_cover_print not in valid_print:
        return {
            "success": False,
            "error": f"Invalid front_cover_print: '{front_cover_print}'. Must be one of: {', '.join(valid_print)}"
        }
    
    if back_cover_print not in valid_print:
        return {
            "success": False,
            "error": f"Invalid back_cover_print: '{back_cover_print}'. Must be one of: {', '.join(valid_print)}"
        }
    
    valid_celloglaze = ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"]
    if front_celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid front_celloglaze: '{front_celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    if back_celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid back_celloglaze: '{back_celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    valid_outer_front = ["Not Required", "Clear PVC"]
    if outer_front_cover not in valid_outer_front:
        return {
            "success": False,
            "error": f"Invalid outer_front_cover: '{outer_front_cover}'. Must be one of: {', '.join(valid_outer_front)}"
        }
    
    valid_outer_back = ["None", "Clear PVC", "Black Leather", "Blank"]
    if outer_back_cover not in valid_outer_back:
        return {
            "success": False,
            "error": f"Invalid outer_back_cover: '{outer_back_cover}'. Must be one of: {', '.join(valid_outer_back)}"
        }
    
    valid_internal_stock = ["Satin 128GSM", "Satin 150GSM", "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
    if internal_stock not in valid_internal_stock:
        return {
            "success": False,
            "error": f"Invalid internal_stock: '{internal_stock}'. Must be one of: {', '.join(valid_internal_stock)}"
        }
    
    valid_internal_print = ["Full Colour", "Black & White"]
    if internal_print not in valid_internal_print:
        return {
            "success": False,
            "error": f"Invalid internal_print: '{internal_print}'. Must be one of: {', '.join(valid_internal_print)}"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    # ========================================================================
    # BACKEND CALCULATION
    # ========================================================================
    try:
        calculator = WireBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks,
            finish_size=finish_size,
            outer_front_cover=outer_front_cover,
            printed_front_cover=printed_front_cover,
            front_cover_print=front_cover_print,
            front_celloglaze=front_celloglaze,
            outer_back_cover=outer_back_cover,
            printed_back_cover=printed_back_cover,
            back_cover_print=back_cover_print,
            back_celloglaze=back_celloglaze,
            internal_pages=internal_pages,
            internal_stock=internal_stock,
            internal_print=internal_print
        )
        
        # Convert breakdown values safely (handle strings like "percentage")
        breakdown_converted = {}
        for k, v in result.breakdown.items():
            try:
                breakdown_converted[k] = float(v)
            except (ValueError, TypeError):
                breakdown_converted[k] = str(v)  # Keep as string if not numeric
        
        response = {
            "success": True,
            "product_type": "Wire Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": breakdown_converted,
            "specifications": result.specifications
        }
        
        # Include warnings in response if any
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        import traceback
        print(f"❌ [Shopify Wire Bound Books] Error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@calculator_wrapper(validate_params=True)
def calculate_spiral_bound_books_shopify(
    quantity: int,
    internal_pages: int = None,
    finish_size: str = None,
    printed_front_cover: str = "300GSM Satin",
    front_cover_print: str = "2pp Colour",
    front_celloglaze: str = "None",
    outer_front_cover: str = "Not Required",
    printed_back_cover: str = "300GSM Satin",
    back_cover_print: str = "2pp Colour",
    back_celloglaze: str = "None",
    outer_back_cover: str = "None",
    internal_stock: str = "Uncoated Bond 100GSM",
    internal_print: str = "Black & White",
    artworks: int = 1,
    # Legacy parameter support (DEPRECATED - will be removed)
    pages: int = None,
    size: str = None,
    cover_stock: str = None,
    inner_stock: str = None,
    cover_cellophane: str = None,
    front_cover_pvc: bool = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Spiral Bound Books (identical structure to Wire Bound)
    
    Args:
        quantity: Number of books (1-10000)
        internal_pages: Total page count for internal pages (1-500)
        finish_size: Book size with orientation (e.g., "A5 Portrait", "A4 Landscape")
        printed_front_cover: Front printed cover stock (250/300/350GSM Satin)
        front_cover_print: Front cover print type (1pp/2pp Colour/Black & White)
        front_celloglaze: Front cover celloglaze (None/1 Side/2 Sided Gloss/Matt)
        outer_front_cover: Clear PVC overlay on front (Not Required/Clear PVC)
        printed_back_cover: Back printed cover stock
        back_cover_print: Back cover print type
        back_celloglaze: Back cover celloglaze
        outer_back_cover: Back cover outer layer (None/Clear PVC/Black Leather/Blank)
        internal_stock: Internal pages paper stock
        internal_print: Internal print type (Full Colour/Black & White)
        artworks: Number of different artworks (1-50, first free, $15 each)
        
        DEPRECATED PARAMETERS (legacy support, will warn):
        pages: Use 'internal_pages' instead
        size: Use 'finish_size' instead
        cover_stock: Use 'printed_front_cover' instead
        inner_stock: Use 'internal_stock' instead (note: spelling)
        cover_cellophane: Use 'front_celloglaze' instead
        front_cover_pvc: Use 'outer_front_cover' instead
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    # ========================================================================
    # LEGACY PARAMETER TRANSLATION (with warnings)
    # ========================================================================
    warnings = []
    
    if pages is not None:
        internal_pages = pages
        warnings.append({
            "deprecated": "pages",
            "use_instead": "internal_pages",
            "value_sent": pages,
            "translated_to": internal_pages
        })
    
    if size is not None:
        if "Portrait" not in size and "Landscape" not in size:
            finish_size = f"{size} Portrait"
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size,
                "note": "Added 'Portrait' orientation (default)"
            })
        else:
            finish_size = size
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size
            })
    
    if cover_stock is not None:
        printed_front_cover = cover_stock
        warnings.append({
            "deprecated": "cover_stock",
            "use_instead": "printed_front_cover",
            "value_sent": cover_stock,
            "translated_to": printed_front_cover
        })
    
    if inner_stock is not None:
        if "Uncoated" in inner_stock:
            gsm = inner_stock.split("GSM")[0] + "GSM"
            internal_stock = f"Uncoated Bond {gsm}"
        elif "Satin" in inner_stock:
            gsm = inner_stock.split("GSM")[0] + "GSM"
            internal_stock = f"Satin {gsm}"
        else:
            internal_stock = inner_stock
        warnings.append({
            "deprecated": "inner_stock",
            "use_instead": "internal_stock",
            "value_sent": inner_stock,
            "translated_to": internal_stock
        })
    
    if cover_cellophane is not None:
        cello_map = {
            "No Cellophane": "None",
            "Gloss Cellophane": "2 Sided Gloss",
            "Matt Cellophane": "2 Sided Matt"
        }
        front_celloglaze = cello_map.get(cover_cellophane, cover_cellophane)
        warnings.append({
            "deprecated": "cover_cellophane",
            "use_instead": "front_celloglaze",
            "value_sent": cover_cellophane,
            "translated_to": front_celloglaze
        })
    
    if front_cover_pvc is not None:
        outer_front_cover = "Clear PVC" if front_cover_pvc else "Not Required"
        warnings.append({
            "deprecated": "front_cover_pvc",
            "use_instead": "outer_front_cover",
            "value_sent": front_cover_pvc,
            "translated_to": outer_front_cover
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_spiral_bound_books_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
            if 'note' in w:
                log_msg += f"      Note: {w['note']}\n"
        print(log_msg)
    
    # ========================================================================
    # APPLY BACKEND DEFAULTS (if None after legacy translation)
    # ========================================================================
    if internal_pages is None:
        internal_pages = 100  # Backend default
    
    if finish_size is None:
        finish_size = "A5 Portrait"  # Backend default
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    if internal_pages < 1 or internal_pages > 500:
        return {
            "success": False,
            "error": f"Invalid internal_pages: {internal_pages}. Must be between 1 and 500"
        }
    
    valid_sizes = ["A6 Portrait", "A6 Landscape", "DL Portrait", "DL Landscape", "A5 Portrait", "A5 Landscape", "A4 Portrait", "A4 Landscape"]
    if finish_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_cover_stock = ["250GSM Satin", "300GSM Satin", "350GSM Satin"]
    if printed_front_cover not in valid_cover_stock:
        return {
            "success": False,
            "error": f"Invalid printed_front_cover: '{printed_front_cover}'. Must be one of: {', '.join(valid_cover_stock)}"
        }
    
    if printed_back_cover not in valid_cover_stock:
        return {
            "success": False,
            "error": f"Invalid printed_back_cover: '{printed_back_cover}'. Must be one of: {', '.join(valid_cover_stock)}"
        }
    
    valid_print = ["1pp Colour", "2pp Colour", "1pp Black & White", "2pp Black & White"]
    if front_cover_print not in valid_print:
        return {
            "success": False,
            "error": f"Invalid front_cover_print: '{front_cover_print}'. Must be one of: {', '.join(valid_print)}"
        }
    
    if back_cover_print not in valid_print:
        return {
            "success": False,
            "error": f"Invalid back_cover_print: '{back_cover_print}'. Must be one of: {', '.join(valid_print)}"
        }
    
    valid_celloglaze = ["None", "1 Side Gloss", "2 Sided Gloss", "1 Side Matt", "2 Sided Matt"]
    if front_celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid front_celloglaze: '{front_celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    if back_celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid back_celloglaze: '{back_celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    valid_outer_front = ["Not Required", "Clear PVC"]
    if outer_front_cover not in valid_outer_front:
        return {
            "success": False,
            "error": f"Invalid outer_front_cover: '{outer_front_cover}'. Must be one of: {', '.join(valid_outer_front)}"
        }
    
    valid_outer_back = ["None", "Clear PVC", "Black Leather", "Blank"]
    if outer_back_cover not in valid_outer_back:
        return {
            "success": False,
            "error": f"Invalid outer_back_cover: '{outer_back_cover}'. Must be one of: {', '.join(valid_outer_back)}"
        }
    
    valid_internal_stock = ["Satin 128GSM", "Satin 150GSM", "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
    if internal_stock not in valid_internal_stock:
        return {
            "success": False,
            "error": f"Invalid internal_stock: '{internal_stock}'. Must be one of: {', '.join(valid_internal_stock)}"
        }
    
    valid_internal_print = ["Full Colour", "Black & White"]
    if internal_print not in valid_internal_print:
        return {
            "success": False,
            "error": f"Invalid internal_print: '{internal_print}'. Must be one of: {', '.join(valid_internal_print)}"
        }
    
    # ========================================================================
    # BACKEND CALCULATION
    # ========================================================================
    try:
        calculator = SpiralBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks,
            finish_size=finish_size,
            outer_front_cover=outer_front_cover,
            printed_front_cover=printed_front_cover,
            front_cover_print=front_cover_print,
            front_celloglaze=front_celloglaze,
            outer_back_cover=outer_back_cover,
            printed_back_cover=printed_back_cover,
            back_cover_print=back_cover_print,
            back_celloglaze=back_celloglaze,
            internal_pages=internal_pages,
            internal_stock=internal_stock,
            internal_print=internal_print
        )
        
        # Convert breakdown safely
        breakdown_converted = {}
        for k, v in result.breakdown.items():
            try:
                breakdown_converted[k] = float(v)
            except (ValueError, TypeError):
                breakdown_converted[k] = str(v)
        
        response = {
            "success": True,
            "product_type": "Spiral Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": breakdown_converted,
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        import traceback
        print(f"❌ [Shopify Spiral Bound Books] Error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@calculator_wrapper(validate_params=True)
def calculate_perfect_bound_books_shopify(
    quantity: int,
    printed_pages: int = None,
    finish_size: str = None,
    cover_stock: str = None,
    cover_print_type: str = None,
    celloglaze: str = None,
    content_print_type: str = None,
    content_stock_type: str = None,
    proof_requirements: str = None,
    # Legacy parameter support (DEPRECATED)
    pages: int = None,
    size: str = None,
    inner_stock: str = None,
    inner_print: str = None,
    cover_cellophane: str = None,
    proof_required: bool = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Perfect Bound Books (glued spine binding)
    
    Args:
        quantity: Number of books (1-20,000)
        printed_pages: Number of internal pages (40-800, must be divisible by 4)
        finish_size: Book size (A5 Portrait/A4 Portrait/A4 Landscape/US Trade)
        cover_stock: Cover paper stock (Satin 300GSM default)
        cover_print_type: Cover printing (1 side/2 side colour/B&W)
        celloglaze: Cover finish (None/Gloss outside only/Matt outside only)
        content_print_type: Internal printing (Full Colour/Black & White)
        content_stock_type: Internal paper stock (Satin 128/150GSM, Uncoated Bond 80/90/100GSM)
        proof_requirements: Proof type (Digital Emailed Proof/$0 or Physical Proof/$40)
        
        DEPRECATED PARAMETERS (legacy support, will warn):
        pages: Use 'printed_pages' instead
        size: Use 'finish_size' instead
        inner_stock: Use 'content_stock_type' instead
        inner_print: Use 'content_print_type' instead
        cover_cellophane: Use 'celloglaze' instead
        proof_required: Use 'proof_requirements' instead
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    # ========================================================================
    # LEGACY PARAMETER TRANSLATION (with warnings)
    # ========================================================================
    warnings = []
    
    if pages is not None:
        printed_pages = pages
        warnings.append({
            "deprecated": "pages",
            "use_instead": "printed_pages",
            "value_sent": pages,
            "translated_to": printed_pages
        })
    
    if size is not None:
        if "Portrait" not in size and "Landscape" not in size:
            finish_size = f"{size} Portrait"
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size,
                "note": "Added 'Portrait' orientation (default)"
            })
        else:
            finish_size = size
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size
            })
    
    if inner_stock is not None:
        content_stock_type = inner_stock
        warnings.append({
            "deprecated": "inner_stock",
            "use_instead": "content_stock_type",
            "value_sent": inner_stock,
            "translated_to": content_stock_type
        })
    
    if inner_print is not None:
        content_print_type = "Full Colour" if "Colour" in inner_print or "Color" in inner_print else "Black & White"
        warnings.append({
            "deprecated": "inner_print",
            "use_instead": "content_print_type",
            "value_sent": inner_print,
            "translated_to": content_print_type
        })
    
    if cover_cellophane is not None:
        cello_map = {
            "None": "None",
            "Gloss": "Gloss outside only",
            "Matt": "Matt outside only"
        }
        celloglaze = cello_map.get(cover_cellophane, cover_cellophane)
        warnings.append({
            "deprecated": "cover_cellophane",
            "use_instead": "celloglaze",
            "value_sent": cover_cellophane,
            "translated_to": celloglaze
        })
    
    if proof_required is not None:
        proof_requirements = "Physical Proof" if proof_required else "Digital Emailed Proof"
        warnings.append({
            "deprecated": "proof_required",
            "use_instead": "proof_requirements",
            "value_sent": proof_required,
            "translated_to": proof_requirements
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_perfect_bound_books_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
            if 'note' in w:
                log_msg += f"      Note: {w['note']}\n"
        print(log_msg)
    
    # ========================================================================
    # APPLY BACKEND DEFAULTS (if None after legacy translation)
    # ========================================================================
    if printed_pages is None:
        printed_pages = 100  # Backend default
    
    if finish_size is None:
        finish_size = "A5 Portrait"  # Backend default
    
    if cover_stock is None:
        cover_stock = "Satin 300GSM"  # Backend default
    
    if cover_print_type is None:
        cover_print_type = "2 side colour (4pp)"  # Backend default
    
    if celloglaze is None:
        celloglaze = "None"  # Backend default
    
    if content_print_type is None:
        content_print_type = "Black & White"  # Backend default
    
    if content_stock_type is None:
        content_stock_type = "Uncoated Bond 100GSM"  # Backend default
    
    if proof_requirements is None:
        proof_requirements = "Digital Emailed Proof"  # Backend default
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    if printed_pages < 40 or printed_pages > 800:
        return {
            "success": False,
            "error": f"Invalid printed_pages: {printed_pages}. Must be between 40 and 800"
        }
    
    if printed_pages % 4 != 0:
        return {
            "success": False,
            "error": f"Invalid printed_pages: {printed_pages}. Must be divisible by 4"
        }
    
    valid_sizes = ["A5 Portrait", "A4 Portrait", "A4 Landscape", "US Trade - 152mm x 229mm"]
    if finish_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_cover_print = ["1 side colour (2pp)", "2 side colour (4pp)", "1 side Black & White (2pp)", "2 side Black & White (4pp)"]
    if cover_print_type not in valid_cover_print:
        return {
            "success": False,
            "error": f"Invalid cover_print_type: '{cover_print_type}'. Must be one of: {', '.join(valid_cover_print)}"
        }
    
    valid_celloglaze = ["None", "Gloss outside only", "Matt outside only"]
    if celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid celloglaze: '{celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    valid_content_print = ["Full Colour", "Black & White"]
    if content_print_type not in valid_content_print:
        return {
            "success": False,
            "error": f"Invalid content_print_type: '{content_print_type}'. Must be one of: {', '.join(valid_content_print)}"
        }
    
    valid_content_stock = ["Satin 128GSM", "Satin 150GSM", "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
    if content_stock_type not in valid_content_stock:
        return {
            "success": False,
            "error": f"Invalid content_stock_type: '{content_stock_type}'. Must be one of: {', '.join(valid_content_stock)}"
        }
    
    valid_proof = ["Digital Emailed Proof", "Physical Proof"]
    if proof_requirements not in valid_proof:
        return {
            "success": False,
            "error": f"Invalid proof_requirements: '{proof_requirements}'. Must be one of: {', '.join(valid_proof)}"
        }
    
    # ========================================================================
    # BACKEND CALCULATION
    # ========================================================================
    try:
        calculator = PerfectBoundShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            printed_pages=printed_pages,
            proof_requirements=proof_requirements,
            cover_stock=cover_stock,
            cover_print_type=cover_print_type,
            celloglaze=celloglaze,
            finish_size=finish_size,
            content_print_type=content_print_type,
            content_stock_type=content_stock_type
        )
        
        # Convert breakdown safely
        breakdown_converted = {}
        for k, v in result.breakdown.items():
            try:
                breakdown_converted[k] = float(v)
            except (ValueError, TypeError):
                breakdown_converted[k] = str(v)
        
        response = {
            "success": True,
            "product_type": "Perfect Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": breakdown_converted,
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        import traceback
        print(f"❌ [Shopify Perfect Bound Books] Error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@calculator_wrapper(quantity_enum=[25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000], validate_params=True)
def calculate_saddle_stitch_books_shopify(
    quantity: int,
    printed_pages: str = None,
    finish_size: str = None,
    cover_stock: str = None,
    cover_print_type: str = None,
    celloglaze: str = None,
    content_print_type: str = None,
    content_stock_type: str = None,
    cover_option: str = None,
    artworks: int = None,
    # Legacy parameters
    pages: int = None,
    size: str = None,
    cover_cellophane: str = None,
    inner_stock: str = None,
    inner_print: str = None,
    hard_cover: bool = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Saddle Stitch Books (stapled spine binding)
    
    Args:
        quantity: Number of books (25, 50, 75, 100, etc.)
        printed_pages: Total page count as string (e.g., "16pp", "20pp")
        finish_size: Book size (A4 Portrait/A5 Portrait/A6 Portrait)
        cover_stock: Cover paper stock (Satin 200GSM default)
        cover_print_type: Cover printing (1 side/2 side colour/B&W)
        celloglaze: Cover finish (None/Gloss outside only/Matt outside only)
        content_print_type: Internal printing (Colour/Black & White)
        content_stock_type: Internal paper stock
        cover_option: Hard Cover or Self Cover
        artworks: Number of different artworks (default 1)
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    warnings = []
    
    if pages is not None:
        printed_pages = f"{pages}pp"
        warnings.append({
            "deprecated": "pages",
            "use_instead": "printed_pages",
            "value_sent": pages,
            "translated_to": printed_pages
        })
    
    if size is not None:
        if "Portrait" not in size:
            finish_size = f"{size} Portrait"
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size,
                "note": "Added 'Portrait' orientation"
            })
        else:
            finish_size = size
            warnings.append({
                "deprecated": "size",
                "use_instead": "finish_size",
                "value_sent": size,
                "translated_to": finish_size
            })
    
    if cover_cellophane is not None:
        cello_map = {
            "None": "None",
            "Gloss": "Gloss outside only",
            "Matt": "Matt outside only"
        }
        celloglaze = cello_map.get(cover_cellophane, cover_cellophane)
        warnings.append({
            "deprecated": "cover_cellophane",
            "use_instead": "celloglaze",
            "value_sent": cover_cellophane,
            "translated_to": celloglaze
        })
    
    if inner_stock is not None:
        content_stock_type = inner_stock
        warnings.append({
            "deprecated": "inner_stock",
            "use_instead": "content_stock_type",
            "value_sent": inner_stock,
            "translated_to": content_stock_type
        })
    
    if inner_print is not None:
        content_print_type = inner_print
        warnings.append({
            "deprecated": "inner_print",
            "use_instead": "content_print_type",
            "value_sent": inner_print,
            "translated_to": content_print_type
        })
    
    if hard_cover is not None:
        cover_option = "Hard Cover" if hard_cover else "Self Cover"
        warnings.append({
            "deprecated": "hard_cover",
            "use_instead": "cover_option",
            "value_sent": hard_cover,
            "translated_to": cover_option
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_saddle_stitch_books_shopify:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
            if 'note' in w:
                log_msg += f"      Note: {w['note']}\n"
        print(log_msg)
    
    # Apply backend defaults for None values
    if printed_pages is None:
        printed_pages = "16pp"  # Backend default
    
    if finish_size is None:
        finish_size = "A4 Portrait"  # Backend default
    
    if cover_stock is None:
        cover_stock = "Satin 200GSM"  # Backend default
    
    if cover_print_type is None:
        cover_print_type = "2 side colour (4pp)"  # Backend default
    
    if celloglaze is None:
        celloglaze = "None"  # Backend default
    
    if content_print_type is None:
        content_print_type = "Colour"  # Backend default
    
    if content_stock_type is None:
        content_stock_type = "Uncoated Bond 80GSM"  # Backend default
    
    if cover_option is None:
        cover_option = "Hard Cover"  # Backend default
    
    if artworks is None:
        artworks = 1  # Backend default
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    valid_pages = ["8pp", "12pp", "16pp", "20pp", "24pp", "28pp", "32pp", "36pp", "40pp", "44pp", "48pp"]
    if printed_pages not in valid_pages:
        return {
            "success": False,
            "error": f"Invalid printed_pages: '{printed_pages}'. Must be one of: {', '.join(valid_pages)}"
        }
    
    valid_sizes = ["A4 Portrait", "A5 Portrait", "A4 Landscape"]
    if finish_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_cover_stock = ["Satin 200GSM", "Satin 250GSM", "Satin 300GSM"]
    if cover_stock not in valid_cover_stock:
        return {
            "success": False,
            "error": f"Invalid cover_stock: '{cover_stock}'. Must be one of: {', '.join(valid_cover_stock)}"
        }
    
    valid_cover_print = ["1 side colour (2pp)", "2 side colour (4pp)", "1 side Black & White (2pp)", "2 side Black & White (4pp)"]
    if cover_print_type not in valid_cover_print:
        return {
            "success": False,
            "error": f"Invalid cover_print_type: '{cover_print_type}'. Must be one of: {', '.join(valid_cover_print)}"
        }
    
    valid_celloglaze = ["None", "Gloss outside only", "Matt outside only"]
    if celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid celloglaze: '{celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    valid_content_print = ["Colour", "Black & White"]
    if content_print_type not in valid_content_print:
        return {
            "success": False,
            "error": f"Invalid content_print_type: '{content_print_type}'. Must be one of: {', '.join(valid_content_print)}"
        }
    
    valid_content_stock = ["Uncoated Bond 80GSM", "Uncoated Bond 100GSM", "Satin 128GSM", "Satin 150GSM"]
    if content_stock_type not in valid_content_stock:
        return {
            "success": False,
            "error": f"Invalid content_stock_type: '{content_stock_type}'. Must be one of: {', '.join(valid_content_stock)}"
        }
    
    valid_cover_option = ["Hard Cover", "Self Cover"]
    if cover_option not in valid_cover_option:
        return {
            "success": False,
            "error": f"Invalid cover_option: '{cover_option}'. Must be one of: {', '.join(valid_cover_option)}"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    try:
        from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator
        
        calculator = SaddleStitchBooksShopifyCalculator()
        result = calculator.calculate(
            quantity=str(quantity),
            artworks=artworks,
            cover_option=cover_option,
            cover_stock=cover_stock,
            cover_print_type=cover_print_type,
            celloglaze=celloglaze,
            printed_pages=printed_pages if "pp" in str(printed_pages) else f"{printed_pages}pp",
            finish_size=finish_size,
            content_print_type=content_print_type,
            content_stock_type=content_stock_type
        )
        
        breakdown_converted = {}
        for k, v in result.breakdown.items():
            try:
                breakdown_converted[k] = float(v)
            except (ValueError, TypeError):
                breakdown_converted[k] = str(v)
        
        response = {
            "success": True,
            "product_type": "Saddle Stitch Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": breakdown_converted,
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        import traceback
        print(f"❌ [Shopify Saddle Stitch Books] Error: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@calculator_wrapper(validate_params=True)
def calculate_spiral_books_simple_shopify(
    quantity: int,
    internal_pages: int = None,
    finish_size: str = None,
    printed_front_cover: str = None,
    front_cover_print: str = None,
    front_celloglaze: str = None,
    outer_front_cover: str = None,
    printed_back_cover: str = None,
    back_cover_print: str = None,
    back_celloglaze: str = None,
    outer_back_cover: str = None,
    internal_stock: str = None,
    internal_print: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Alias for Spiral Bound Books (simple version uses same calculator)
    This is identical to calculate_spiral_bound_books_shopify
    """
    # Apply backend defaults for None values
    if internal_pages is None:
        internal_pages = 100  # Backend default
    
    if finish_size is None:
        finish_size = "A5 Portrait"  # Backend default
    
    if printed_front_cover is None:
        printed_front_cover = "300GSM Satin"  # Backend default
    
    if front_cover_print is None:
        front_cover_print = "2pp Colour"  # Backend default
    
    if front_celloglaze is None:
        front_celloglaze = "None"  # Backend default
    
    if outer_front_cover is None:
        outer_front_cover = "Not Required"  # Backend default
    
    if printed_back_cover is None:
        printed_back_cover = "300GSM Satin"  # Backend default
    
    if back_cover_print is None:
        back_cover_print = "2pp Colour"  # Backend default
    
    if back_celloglaze is None:
        back_celloglaze = "None"  # Backend default
    
    if outer_back_cover is None:
        outer_back_cover = "None"  # Backend default
    
    if internal_stock is None:
        internal_stock = "Uncoated Bond 100GSM"  # Backend default
    
    if internal_print is None:
        internal_print = "Black & White"  # Backend default
    
    if artworks is None:
        artworks = 1  # Backend default
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    if internal_pages < 1 or internal_pages > 500:
        return {
            "success": False,
            "error": f"Invalid internal_pages: {internal_pages}. Must be between 1 and 500"
        }
    
    valid_sizes = ["A5 Portrait", "A5 Landscape", "A4 Portrait", "A4 Landscape"]
    if finish_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    return calculate_spiral_bound_books_shopify(
        quantity=quantity,
        internal_pages=internal_pages,
        finish_size=finish_size,
        printed_front_cover=printed_front_cover,
        front_cover_print=front_cover_print,
        front_celloglaze=front_celloglaze,
        outer_front_cover=outer_front_cover,
        printed_back_cover=printed_back_cover,
        back_cover_print=back_cover_print,
        back_celloglaze=back_celloglaze,
        outer_back_cover=outer_back_cover,
        internal_stock=internal_stock,
        internal_print=internal_print,
        artworks=artworks
    )


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
        from SaddleStitchBooks_Shopify_Calculator import SaddleStitchBooksShopifyCalculator
        
        calculator = SaddleStitchBooksShopifyCalculator()
        result = calculator.calculate(
            quantity=str(quantity),  # Convert int to str for calculator
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


@calculator_wrapper(validate_params=True)
@calculator_wrapper(validate_params=True)
def calculate_bollard_signs(
    quantity: int,
    size: str = None,
    material: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Bollard Signs
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of signs (1-1000, required)
        material: "3mm Corflute" or "5mm Corflute" (from JSON)
        size: "270mm W x 1000mm H - Three Sided" format (from JSON, 12 options)
        artworks: Number of artwork designs (1-20)
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults (from Shopify specification)
    if size is None:
        size = "270mm W x 1000mm H - Three Sided"  # JSON default
    if material is None:
        material = "5mm Corflute"  # JSON default
    if artworks is None:
        artworks = 1
    
    # ✅ Validate quantity range (JSON specifies 1-1000)
    if quantity < 1 or quantity > 1000:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 1000"
        }
    
    # ✅ Validate against JSON enum values (exact match required)
    valid_materials = ["3mm Corflute", "5mm Corflute"]
    if material not in valid_materials:
        return {
            "success": False,
            "error": f"Invalid material: '{material}'. Must be one of: {', '.join(valid_materials)}"
        }
    
    valid_sizes = [
        "270mm W x 1000mm H - Three Sided",
        "270mm W x 1200mm H - Three Sided",
        "270mm W x 1800mm H - Three Sided",
        "300mm W x 1000mm H - Three Sided",
        "300mm W x 1200mm H - Three Sided",
        "300mm W x 1800mm H - Three Sided",
        "155mm W x 1000mm H - Four Sided",
        "155mm W x 1200mm H - Four Sided",
        "155mm W x 1800mm H - Four Sided",
        "175mm W x 1000mm H - Four Sided",
        "175mm W x 1200mm H - Four Sided",
        "175mm W x 1800mm H - Four Sided"
    ]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {valid_sizes[0]}, {valid_sizes[1]}, ... (12 options total)"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend (no translation needed)
    try:
        from BollardSigns_Shopify_Calculator import BollardSignsShopifyCalculator
        calculator = BollardSignsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # ✅ JSON format passed directly
            material=material,  # ✅ JSON format passed directly
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_construction_signs(
    quantity: int,
    size: str = None,
    thickness: str = None,
    sides: str = None,
    eyelets: str = None,
    cutting: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Construction Signs
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of signs (1-10000, required)
        size: "450mm x 600mm" format with spaces (JSON, 5 options)
        thickness: "3mm" or "5mm" (JSON)
        sides: "Single Sided" or "Double Sided" with suffix (JSON)
        eyelets: Eyelet configuration (JSON, 7 options)
        cutting: "Standard square edge" or "Custom Shape" (JSON)
        artworks: Number of artwork designs (1-20)
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults
    if size is None:
        size = "600mm x 900mm"  # JSON default
    if thickness is None:
        thickness = "5mm"  # JSON default
    if sides is None:
        sides = "Single Sided"  # JSON default
    if eyelets is None:
        eyelets = "No Eyelets"  # JSON default
    if cutting is None:
        cutting = "Standard square edge"  # JSON default
    if artworks is None:
        artworks = 1
    
    # ✅ Validate against JSON enum values
    valid_sizes = [
        "450mm x 600mm",
        "600mm x 900mm",
        "900mm x 1200mm",
        "1200mm x 2400mm",
        "Custom"
    ]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_thickness = ["3mm", "5mm"]
    if thickness not in valid_thickness:
        return {
            "success": False,
            "error": f"Invalid thickness: '{thickness}'. Must be one of: {', '.join(valid_thickness)}"
        }
    
    valid_sides = ["Single Sided", "Double Sided"]
    if sides not in valid_sides:
        return {
            "success": False,
            "error": f"Invalid sides: '{sides}'. Must be one of: {', '.join(valid_sides)}"
        }
    
    valid_eyelets = [
        "No Eyelets",
        "4 x Eyelets (1 In Each Corner)",
        "2 x Eyelets (top left & right corners)",
        "2 x Eyelets (center left & right)",
        "2 x Eyelets (center top & bottom)",
        "6 x Eyelets (3 each top & bottom)",
        "6 x Eyelets (3 each left & right)"
    ]
    if eyelets not in valid_eyelets:
        return {
            "success": False,
            "error": f"Invalid eyelets: '{eyelets}'. Must be one of the 7 eyelet options"
        }
    
    valid_cutting = ["Standard square edge", "Custom Shape"]
    if cutting not in valid_cutting:
        return {
            "success": False,
            "error": f"Invalid cutting: '{cutting}'. Must be one of: {', '.join(valid_cutting)}"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend
    try:
        from ConstructionSigns_Shopify_Calculator import ConstructionSignsShopifyCalculator
        calculator = ConstructionSignsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # ✅ JSON format
            thickness=thickness,  # ✅ JSON format
            sides=sides,  # ✅ JSON format
            eyelets=eyelets,  # ✅ JSON format
            cutting=cutting,  # ✅ JSON format
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
@calculator_wrapper(validate_params=True)
def calculate_election_signs(
    quantity: int,
    size: str = None,
    thickness: str = None,
    sides: str = None,
    eyelets: str = None,
    cutting: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Election Signs
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of election signs (1-10000, required)
        size: "450mm x 600mm" format with spaces (JSON, 5 options)
        thickness: "3mm" or "5mm" (JSON)
        sides: "Single Sided" or "Double Sided" with suffix (JSON)
        eyelets: Eyelet configuration (JSON, 7 options)
        cutting: "Standard square edge" or "Custom Shape" (JSON)
        artworks: Number of artwork designs (1-20)
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults
    if size is None:
        size = "600mm x 900mm"  # JSON default
    if thickness is None:
        thickness = "5mm"  # JSON default
    if sides is None:
        sides = "Single Sided"  # JSON default
    if eyelets is None:
        eyelets = "No Eyelets"  # JSON default
    if cutting is None:
        cutting = "Standard square edge"  # JSON default
    if artworks is None:
        artworks = 1
    
    # ✅ Validate against JSON enum values
    valid_sizes = [
        "450mm x 600mm",
        "600mm x 900mm",
        "900mm x 1200mm",
        "1200mm x 2400mm",
        "Custom"
    ]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_thickness = ["3mm", "5mm"]
    if thickness not in valid_thickness:
        return {
            "success": False,
            "error": f"Invalid thickness: '{thickness}'. Must be one of: {', '.join(valid_thickness)}"
        }
    
    valid_sides = ["Single Sided", "Double Sided"]
    if sides not in valid_sides:
        return {
            "success": False,
            "error": f"Invalid sides: '{sides}'. Must be one of: {', '.join(valid_sides)}"
        }
    
    valid_eyelets = [
        "No Eyelets",
        "4 x Eyelets (1 In Each Corner)",
        "2 x Eyelets (top left and right corners)",
        "2 x Eyelets (center left and right)",
        "2 x Eyelets (center top and bottom)",
        "6 x Eyelets (3 each top and bottom)",
        "6 x Eyelets (3 each left and right)"
    ]
    if eyelets not in valid_eyelets:
        return {
            "success": False,
            "error": f"Invalid eyelets: '{eyelets}'. Must be one of the 7 eyelet options"
        }
    
    valid_cutting = ["Standard square edge", "Custom Shape"]
    if cutting not in valid_cutting:
        return {
            "success": False,
            "error": f"Invalid cutting: '{cutting}'. Must be one of: {', '.join(valid_cutting)}"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend
    try:
        from ElectionSigns_Shopify_Calculator import ElectionSignsShopifyCalculator
        calculator = ElectionSignsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # ✅ JSON format
            thickness=thickness,  # ✅ JSON format
            sides=sides,  # ✅ JSON format
            eyelets=eyelets,  # ✅ JSON format
            cutting=cutting,  # ✅ JSON format
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_corflute_insert_a_frame(
    quantity: int,
    size: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Corflute Insert A-Frame
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of frames (1-10000, required)
        size: "600mm(W) x 900mm(H)" format (JSON, only 1 option)
        artworks: Number of artwork designs (1-20)
    
    Note: This product only has ONE size option in Shopify JSON
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults
    if size is None:
        size = "600mm(W) x 900mm(H)"  # JSON default (only option)
    if artworks is None:
        artworks = 1
    
    # ✅ Validate against JSON enum values
    valid_sizes = ["600mm(W) x 900mm(H)"]  # Only 1 option in JSON
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be: {valid_sizes[0]}"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend
    try:
        from CorfluteInsertA_Frame_Shopify_Calculator import CorfluteInsertA_FrameShopifyCalculator
        calculator = CorfluteInsertA_FrameShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # ✅ JSON format
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_metal_face_a_frame(
    quantity: int,
    size: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Metal Face A-Frame
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of frames (1-100, required)
        size: "600mm W x 900mm H" format (JSON, only 1 option)
        artworks: Number of artwork designs (1-20)
    
    Note: This product only has ONE size option and is single-sided only
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults
    if size is None:
        size = "600mm W x 900mm H"  # JSON default (only option)
    if artworks is None:
        artworks = 1
    
    # ✅ Validate against JSON enum values
    valid_sizes = ["600mm W x 900mm H"]  # Only 1 option in JSON
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be: {valid_sizes[0]}"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend
    try:
        from MetalFaceA_Frame_Shopify_Calculator import MetalFaceA_FrameShopifyCalculator
        calculator = MetalFaceA_FrameShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # ✅ JSON format
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
@calculator_wrapper(validate_params=True)
def calculate_luxury_classic_pull_up_banners(
    quantity: int,
    size: str = "850mm W x 2000mm H",  # JSON default
    base_colour: str = "Silver",  # JSON default  
    artworks: int = 1  # JSON default
) -> Dict[str, Any]:
    """
    Shopify calculator for Luxury Classic Pull Up Banners
    
    Args:
        quantity: Number of banners 1-100 (required)
        size: Banner size - "850mm W x 2000mm H", "850mm W x 1500mm H", or "850mm W x 1400mm H Shopping Center" (default: "850mm W x 2000mm H")
        base_colour: Base finish color - "Silver" or "Black" (default: "Silver")
        artworks: Number of different artwork designs 1-20 (default: 1, visible when quantity > 2)
    
    Returns:
        Dict with success, quote result, or error
    """
    # ========================================================================
    # VALIDATION: Validate JSON format parameters
    # ========================================================================
    valid_sizes = ["850mm W x 2000mm H", "850mm W x 1500mm H", "850mm W x 1400mm H Shopping Center"]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_base_colours = ["Silver", "Black"]
    if base_colour not in valid_base_colours:
        return {
            "success": False,
            "error": f"Invalid base_colour: '{base_colour}'. Must be one of: {', '.join(valid_base_colours)}"
        }
    
    if quantity < 1 or quantity > 100:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 100"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from LuxuryClassicPullUpBanners_Shopify_Calculator import LuxuryClassicPullUpBannersShopifyCalculator
        calculator = LuxuryClassicPullUpBannersShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # JSON format like "850mm W x 2000mm H"
            base_colour=base_colour,  # JSON field name
            artworks=artworks
        )
        response = {
            "success": True,
            "product_type": "Luxury Classic Pull Up Banners",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        return response
    except Exception as e:
        print(f"❌ [Shopify Luxury Classic Pull Up Banners] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_premium_pull_up_banners(
    quantity: int,
    size: str = "850mm W x 2000mm H",  # JSON default
    base_colour: str = "Silver",  # JSON default  
    artworks: int = 1  # JSON default
) -> Dict[str, Any]:
    """
    Shopify calculator for Premium Pull Up Banners
    
    Args:
        quantity: Number of banners 1-100 (required)
        size: Banner size - "850mm W x 2000mm H", "850mm W x 1500mm H", or "850mm W x 1400mm H Shopping Center" (default: "850mm W x 2000mm H")
        base_colour: Base finish color - "Silver" or "Black" (default: "Silver")
        artworks: Number of different artwork designs 1-20 (default: 1, visible when quantity > 2)
    
    Returns:
        Dict with success, quote result, or error
    """
    # ========================================================================
    # VALIDATION: Validate JSON format parameters
    # ========================================================================
    valid_sizes = ["850mm W x 2000mm H", "850mm W x 1500mm H", "850mm W x 1400mm H Shopping Center"]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    valid_base_colours = ["Silver", "Black"]
    if base_colour not in valid_base_colours:
        return {
            "success": False,
            "error": f"Invalid base_colour: '{base_colour}'. Must be one of: {', '.join(valid_base_colours)}"
        }
    
    if quantity < 1 or quantity > 100:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 100"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from PremiumPullUpBanners_Shopify_Calculator import PremiumPullUpBannersShopifyCalculator
        calculator = PremiumPullUpBannersShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # JSON format like "850mm W x 2000mm H"
            base_colour=base_colour,  # JSON field name
            artworks=artworks
        )
        response = {
            "success": True,
            "product_type": "Premium Pull Up Banners",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        return response
    except Exception as e:
        print(f"❌ [Shopify Premium Pull Up Banners] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_metal_face_a_frame(
    quantity: int,
    artworks: int = 1,
    size: str = "600mm W x 900mm H"
) -> Dict[str, Any]:
    """
    Shopify calculator for Metal Face A-Frame
    
    Args:
        quantity: Number of A-frames (1-100, required)
        artworks: Number of artwork designs (1-20, default 1)
        size: A-frame size (fixed: "600mm W x 900mm H")
    
    Returns:
        Dict with success, quote result, or error
    
    Formula: qty-based tiers (10 tiers) + artworks COUNT + ×1.1 ×1.1
    Note: Adds artwork count directly, not cost calculation
    """
    # Validate parameters
    if quantity < 1 or quantity > 100:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 100"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from MetalFaceAFrame_Shopify_Calculator import MetalFaceAFrameShopifyCalculator
        calculator = MetalFaceAFrameShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks,
            size=size
        )
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


@calculator_wrapper(validate_params=True)
def calculate_selfie_frames(
    quantity: int,
    size: str = "Small 600mm x 900mm",  # JSON default
    number_of_artworks: int = 1  # JSON field name
) -> Dict[str, Any]:
    """
    Shopify calculator for Selfie Frames
    
    Args:
        quantity: Number of frames 1-200 (required)
        size: Frame size - "Small 600mm x 900mm" or "Large 900mm x 1200mm" (default: "Small 600mm x 900mm")
        number_of_artworks: Number of artwork designs 1-20 (default: 1)
    
    Returns:
        Dict with success, quote result, or error
    """
    # ========================================================================
    # VALIDATION: Validate JSON format parameters
    # ========================================================================
    valid_sizes = ["Small 600mm x 900mm", "Large 900mm x 1200mm"]
    if size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid size: '{size}'. Must be one of: {', '.join(valid_sizes)}"
        }
    
    if quantity < 1 or quantity > 200:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 200"
        }
    
    if number_of_artworks < 1 or number_of_artworks > 20:
        return {
            "success": False,
            "error": f"Invalid number_of_artworks: {number_of_artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from SelfieFrames_Shopify_Calculator import SelfieFramesShopifyCalculator
        calculator = SelfieFramesShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,  # JSON format like "Small 600mm x 900mm"
            number_of_artworks=number_of_artworks  # JSON field name
        )
        response = {
            "success": True,
            "product_type": "Selfie Frames",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        return response
    except Exception as e:
        print(f"❌ [Shopify Selfie Frames] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(validate_params=True)
def calculate_stackable_cubes(
    quantity: int,
    material: str = None,
    cube_size: str = None,
    artworks: int = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Stackable Cubes
    
    ✅ ALIGNED JAN 23, 2026: Backend, Wrapper, Schema all use JSON format
    
    Parameters (Shopify JSON format):
        quantity: Number of cubes (1-1000, required)
        material: "3mm Corflute" or "5mm Corflute" (JSON)
        cube_size: "Small 300mm x 300mm", "Medium 400mm x 400mm", "Large 500mm x 500mm", "X-Large 580mm x 580mm" (JSON)
        artworks: Number of artwork designs (1-20)
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    # ✅ Apply JSON defaults
    if material is None:
        material = "5mm Corflute"  # JSON default
    if cube_size is None:
        cube_size = "Medium 400mm x 400mm"  # JSON default
    if artworks is None:
        artworks = 1
    
    # ✅ Validate against JSON enum values
    valid_materials = ["3mm Corflute", "5mm Corflute"]
    if material not in valid_materials:
        return {
            "success": False,
            "error": f"Invalid material: '{material}'. Must be one of: {', '.join(valid_materials)}"
        }
    
    valid_cube_sizes = [
        "Small 300mm x 300mm",
        "Medium 400mm x 400mm",
        "Large 500mm x 500mm",
        "X-Large 580mm x 580mm"
    ]
    if cube_size not in valid_cube_sizes:
        return {
            "success": False,
            "error": f"Invalid cube_size: '{cube_size}'. Must be one of: {', '.join(valid_cube_sizes)}"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    # ✅ Pass JSON format directly to backend
    try:
        from StackableCubes_Shopify_Calculator import StackableCubesShopifyCalculator
        calculator = StackableCubesShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            material=material,  # ✅ JSON format
            cube_size=cube_size,  # ✅ JSON format
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_strut_cards_a3(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Strut Cards A3 - Exact TXT Formula
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A3 - 297mm x 420mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Formula: 25-tier quantity pricing + artwork cost + $79 minimum + double markup (×1.1 ×1.1)
    """
    # Validate parameters
    if quantity < 1 or quantity > 10000:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 10000"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA3_Shopify_Calculator import StrutCardsA3ShopifyCalculator
        calculator = StrutCardsA3ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_strut_cards_a4(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Strut Cards A4 - Exact TXT Formula
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A4 - 210mm x 297mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Formula: 25-tier quantity pricing + artwork cost + $79 minimum + double markup (×1.1 ×1.1)
    """
    # Validate parameters
    if quantity < 1 or quantity > 10000:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 10000"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA4_Shopify_Calculator import StrutCardsA4ShopifyCalculator
        calculator = StrutCardsA4ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
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


@calculator_wrapper(validate_params=True)
def calculate_strut_cards_a5(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Strut Cards A5 - Exact TXT Formula
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A5 - 148mm x 210mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Formula: 25-tier quantity pricing + artwork cost + $79 minimum + double markup (×1.1 ×1.2)
    """
    # Validate parameters
    if quantity < 1 or quantity > 10000:
        return {
            "success": False,
            "error": f"Invalid quantity: {quantity}. Must be between 1 and 10000"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA5_Shopify_Calculator import StrutCardsA5ShopifyCalculator
        calculator = StrutCardsA5ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
        return {
            "success": True,
            "product_type": "Strut Cards A5",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Strut Cards A5] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_counter_strut_cards_a3(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Counter Strut Cards A3 (alias of Strut Cards A3)
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A3 - 297mm x 420mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Note: Same formula as Strut Cards A3, just different product_type labeling
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA3_Shopify_Calculator import StrutCardsA3ShopifyCalculator
        calculator = StrutCardsA3ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
        return {
            "success": True,
            "product_type": "Counter Strut Cards A3",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Counter Strut Cards A3] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_counter_strut_cards_a4(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Counter Strut Cards A4 (alias of Strut Cards A4)
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A4 - 210mm x 297mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Note: Same formula as Strut Cards A4, just different product_type labeling
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA4_Shopify_Calculator import StrutCardsA4ShopifyCalculator
        calculator = StrutCardsA4ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
        return {
            "success": True,
            "product_type": "Counter Strut Cards A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Counter Strut Cards A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_counter_strut_cards_a5(
    quantity: int,
    artworks: int = 1,
    stock: str = None,
    size: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for Counter Strut Cards A5 (alias of Strut Cards A5)
    
    Args:
        quantity: Number of cards (1-10000, required)
        artworks: Number of artwork designs (1-20, default 1, first $5 included then $5 each)
        stock: Material stock (fixed: "2mm Screenboard")
        size: Card size (fixed: "A5 - 148mm x 210mm")
    
    Returns:
        Dict with success, quote result, or error
    
    Note: Same formula as Strut Cards A5, just different product_type labeling
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from StrutCardsA5_Shopify_Calculator import StrutCardsA5ShopifyCalculator
        calculator = StrutCardsA5ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            artworks=artworks
        )
        return {
            "success": True,
            "product_type": "Counter Strut Cards A5",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
    except Exception as e:
        print(f"❌ [Shopify Counter Strut Cards A5] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(validate_params=True)
def calculate_custom_poster_printing(
    quantity: int,
    width_mm: int = None,
    height_mm: int = None,
    paper_stock: str = None,
    # Legacy aliases for backwards compatibility
    width: int = None,
    height: int = None
) -> Dict[str, Any]:
    """
    Calculate quote for Custom Poster Printing (Shopify)
    
    Args:
        quantity: Number of posters (1-10000, required)
        width_mm: Width in millimeters (100-2000mm, default backend: 420 for A3)
        height_mm: Height in millimeters (100-3000mm, default backend: 594 for A3)
        paper_stock: Paper type - "150gsm", "200gsm", "250gsm" (default backend: "150gsm")
        
        DEPRECATED:
        width: Legacy alias for width_mm (use width_mm instead)
        height: Legacy alias for height_mm (use height_mm instead)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    warnings = []
    
    # ========================================================================
    # LEGACY TRANSLATION (with warnings)
    # ========================================================================
    if width is not None:
        width_mm = width
        warnings.append({
            "deprecated": "width",
            "use_instead": "width_mm",
            "value_sent": width,
            "translated_to": width_mm
        })
    if height is not None:
        height_mm = height
        warnings.append({
            "deprecated": "height",
            "use_instead": "height_mm",
            "value_sent": height,
            "translated_to": height_mm
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_custom_poster_printing:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}={w['translated_to']}\n"
        print(log_msg)
    
    # ========================================================================
    # VALIDATION (after legacy translation - THE CRITICAL MISSING PIECE!)
    # ========================================================================
    # Apply backend defaults for None values
    if width_mm is None:
        width_mm = 420  # Backend default (A3 width)
    
    if height_mm is None:
        height_mm = 594  # Backend default (A3 height)
    
    if paper_stock is None:
        paper_stock = "150gsm"  # Backend default
    
    # ========================================================================
    # VALIDATION: Validate parameter values (AI learns valid options from errors)
    # ========================================================================
    if width_mm < 100 or width_mm > 2000:
        return {
            "success": False,
            "error": f"Invalid width_mm: {width_mm}. Must be between 100 and 2000 millimeters"
        }
    
    if height_mm < 100 or height_mm > 3000:
        return {
            "success": False,
            "error": f"Invalid height_mm: {height_mm}. Must be between 100 and 3000 millimeters"
        }
    
    valid_paper_stocks = ["150gsm", "200gsm", "250gsm"]
    if paper_stock not in valid_paper_stocks:
        return {
            "success": False,
            "error": f"Invalid paper_stock: '{paper_stock}'. Must be one of: {', '.join(valid_paper_stocks)}"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from CustomPosterPrinting_Shopify_Calculator import CustomPosterPrintingShopifyCalculator
        calculator = CustomPosterPrintingShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            width_mm=width_mm,
            height_mm=height_mm,
            paper_stock=paper_stock
        )
        response = {
            "success": True,
            "product_type": "Custom Poster Printing",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        if warnings:
            response["warnings"] = warnings
        return response
    except Exception as e:
        print(f"❌ [Shopify Custom Poster Printing] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(validate_params=True)
def calculate_custom_vinyl_stickers(
    quantity: int,
    size: str = "75mm Circle",
    width: int = None,
    height: int = None,
    vinyl_family: str = "Standard (Monomeric)",
    adhesive: str = "Permanent",
    laminate: str = "No Lamination",
    cutting_method: str = "Kiss-Cut (Individual)",
    artworks: int = 1,
    labour_rate: str = "Trade ($70/hr)",
    # Legacy parameters for backward compatibility
    width_mm: int = None,
    height_mm: int = None,
    finish: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Custom Vinyl Stickers (Shopify)
    ⚠️ NO WEBSITE CALCULATOR - Backend implementation only.
    
    Args:
        quantity: Number of stickers (1-10000)
        size: Preset size or "Custom Size" - 50mm/75mm/100mm Circle/Square, rectangles
        width: Custom width in mm (25-500, only if size="Custom Size")
        height: Custom height in mm (25-500, only if size="Custom Size")
        vinyl_family: "Standard (Monomeric)" or "Premium (Polymeric)" (×1.25 multiplier)
        adhesive: "Permanent" or "Removable" (×1.15 multiplier)
        laminate: "No Lamination", "Gloss Laminate", or "Matte Laminate"
        cutting_method: "Kiss-Cut (Individual)", "Die-Cut", "Contour-Cut", "Sheet"
        artworks: Number of designs (1-20, first included free, $5 each additional)
        labour_rate: "Trade ($70/hr)" or "Non-Trade ($90/hr)"
        
        DEPRECATED:
        width_mm: Legacy alias for width (use width instead)
        height_mm: Legacy alias for height (use height instead)
        finish: Legacy alias for laminate (use laminate instead)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    warnings = []
    
    # ========================================================================
    # LEGACY TRANSLATION
    # ========================================================================
    if width_mm is not None and width is None:
        width = width_mm
        size = "Custom Size"
        warnings.append({
            "deprecated": "width_mm",
            "use_instead": "width (with size='Custom Size')",
            "value_sent": width_mm,
            "translated_to": width
        })
    
    if height_mm is not None and height is None:
        height = height_mm
        size = "Custom Size"
        warnings.append({
            "deprecated": "height_mm",
            "use_instead": "height (with size='Custom Size')",
            "value_sent": height_mm,
            "translated_to": height
        })
    
    if finish is not None and laminate == "No Lamination":
        if finish.lower() == "gloss":
            laminate = "Gloss Laminate"
        elif finish.lower() == "matte":
            laminate = "Matte Laminate"
        warnings.append({
            "deprecated": "finish",
            "use_instead": "laminate",
            "value_sent": finish,
            "translated_to": laminate
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_custom_vinyl_stickers:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}={w['translated_to']}\n"
        print(log_msg)
    
    # ========================================================================
    # SIZE PRESET TRANSLATION
    # ========================================================================
    size_presets = {
        "50mm Circle": (50, 50),
        "75mm Circle": (75, 75),
        "100mm Circle": (100, 100),
        "50mm Square": (50, 50),
        "75mm Square": (75, 75),
        "100mm Square": (100, 100),
        "100x50mm Rectangle": (100, 50),
        "150x75mm Rectangle": (150, 75),
        "200x100mm Rectangle": (200, 100)
    }
    
    if size != "Custom Size":
        if size in size_presets:
            width, height = size_presets[size]
        else:
            return {"success": False, "error": f"Invalid size preset: {size}. Valid options: {list(size_presets.keys())} or 'Custom Size'"}
    else:
        if width is None or height is None:
            return {"success": False, "error": "Custom Size requires width and height parameters"}
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    if width is not None and not (25 <= width <= 500):
        return {"success": False, "error": f"width must be between 25 and 500mm, got {width}"}
    
    if height is not None and not (25 <= height <= 500):
        return {"success": False, "error": f"height must be between 25 and 500mm, got {height}"}
    
    if not (1 <= artworks <= 20):
        return {"success": False, "error": f"artworks must be between 1 and 20, got {artworks}"}
    
    valid_vinyl_families = ["Standard (Monomeric)", "Premium (Polymeric)"]
    if vinyl_family not in valid_vinyl_families:
        return {"success": False, "error": f"vinyl_family must be one of {valid_vinyl_families}, got '{vinyl_family}'"}
    
    valid_adhesives = ["Permanent", "Removable"]
    if adhesive not in valid_adhesives:
        return {"success": False, "error": f"adhesive must be one of {valid_adhesives}, got '{adhesive}'"}
    
    valid_laminates = ["No Lamination", "Gloss Laminate", "Matte Laminate"]
    if laminate not in valid_laminates:
        return {"success": False, "error": f"laminate must be one of {valid_laminates}, got '{laminate}'"}
    
    valid_cutting_methods = ["Kiss-Cut (Individual)", "Die-Cut", "Contour-Cut", "Sheet"]
    if cutting_method not in valid_cutting_methods:
        return {"success": False, "error": f"cutting_method must be one of {valid_cutting_methods}, got '{cutting_method}'"}
    
    valid_labour_rates = ["Trade ($70/hr)", "Non-Trade ($90/hr)"]
    if labour_rate not in valid_labour_rates:
        return {"success": False, "error": f"labour_rate must be one of {valid_labour_rates}, got '{labour_rate}'"}
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from CustomVinylStickers_Shopify_Calculator import CustomVinylStickersShopifyCalculator
        calculator = CustomVinylStickersShopifyCalculator()
        
        # Call backend with ALL 10 parameters (no translation needed - backend handles them all)
        result = calculator.calculate(
            quantity=quantity,
            size=size,
            width=width,
            height=height,
            vinyl_family=vinyl_family,
            adhesive=adhesive,
            laminate=laminate,
            cutting_method=cutting_method,
            artworks=artworks,
            labour_rate=labour_rate
        )
        
        response = {
            "success": True,
            "product_type": "Custom Vinyl Stickers",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        if warnings:
            response["warnings"] = warnings
        return response
    except Exception as e:
        print(f"❌ [Shopify Custom Vinyl Stickers] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(
    quantity_enum=[25, 50, 100, 250, 500, 750, 1000, 1250, 1500, 2000],
    validate_params=True
)
def calculate_premium_bookmarks(
    quantity: int,
    finish_size: str = "50x150mm",
    paper_stock: str = "satin_350gsm",
    print_type: str = "colour_1_sided",
    celloglaze: str = "None",
    artworks: int = 1,
    # Legacy parameters for backwards compatibility
    width_mm: int = None,
    height_mm: int = None,
    width: int = None,
    height: int = None,
    lamination: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Premium Bookmarks (Shopify) - REWRITTEN Jan 24, 2026
    
    ✅ CURRENT PARAMETERS (Exact TXT Formula):
        quantity: Number of bookmarks (25-2000)
        finish_size: Bookmark size - "50x150mm", "50x185mm", "50x230mm", "65x215mm"
        paper_stock: Paper type - "satin_350gsm" or "uncoated_300gsm"
        print_type: Print option - "colour_1_sided" or "colour_2_sided"
        celloglaze: Celloglaze option - "None", "1_side_gloss", "1_side_matt", "2_side_gloss", "2_side_matt"
        artworks: Number of artworks (first artwork free, $15 per additional)
    
    ⚠️ DEPRECATED PARAMETERS (automatically translated):
        width_mm, height_mm, width, height → use finish_size
        lamination → use celloglaze
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
        
    Backend: PremiumBookmarks_Shopify_Calculator.py (Exact TXT lines 1644-1950)
    Validated: Jan 24, 2026 - 4/4 tests = 100% website match
    """
    warnings = []
    
    # Legacy translation: dimensions to finish_size
    if width_mm is not None or height_mm is not None or width is not None or height is not None:
        w = width_mm or width or 50
        h = height_mm or height or 150
        finish_size = f"{w}x{h}mm"
        warnings.append({
            "deprecated": "width_mm/height_mm",
            "use_instead": "finish_size",
            "translated_to": finish_size
        })
    
    # Legacy translation: lamination to celloglaze
    if lamination is not None:
        lamination_map = {
            "None": "None",
            "Gloss": "2_side_gloss",
            "Matte": "2_side_matt",
            "Gloss 1 Sided": "1_side_gloss",
            "Gloss 2 Sided": "2_side_gloss",
            "Matt 1 Sided": "1_side_matt",
            "Matt 2 Sided": "2_side_matt"
        }
        celloglaze = lamination_map.get(lamination, celloglaze)
        warnings.append({
            "deprecated": "lamination",
            "use_instead": "celloglaze",
            "value": lamination,
            "translated_to": celloglaze
        })
    
    # Validate parameter values (AI learns valid options from errors)
    valid_finish_sizes = ["50x150mm", "50x185mm", "50x230mm", "65x215mm"]
    if finish_size not in valid_finish_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be one of: {', '.join(valid_finish_sizes)}"
        }
    
    valid_paper_stocks = ["satin_350gsm", "uncoated_300gsm"]
    if paper_stock not in valid_paper_stocks:
        return {
            "success": False,
            "error": f"Invalid paper_stock: '{paper_stock}'. Must be one of: {', '.join(valid_paper_stocks)}"
        }
    
    valid_print_types = ["colour_1_sided", "colour_2_sided"]
    if print_type not in valid_print_types:
        return {
            "success": False,
            "error": f"Invalid print_type: '{print_type}'. Must be one of: {', '.join(valid_print_types)}"
        }
    
    valid_celloglaze = ["None", "1_side_gloss", "1_side_matt", "2_side_gloss", "2_side_matt"]
    if celloglaze not in valid_celloglaze:
        return {
            "success": False,
            "error": f"Invalid celloglaze: '{celloglaze}'. Must be one of: {', '.join(valid_celloglaze)}"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from PremiumBookmarks_Shopify_Calculator import PremiumBookmarksShopifyCalculator
        calculator = PremiumBookmarksShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            finish_size=finish_size,
            paper_stock=paper_stock,
            print_type=print_type,
            celloglaze=celloglaze,
            artworks=artworks
        )
        
        response = {
            "success": True,
            "product_type": "Premium Bookmarks",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        if warnings:
            response["warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Premium Bookmarks] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}



@calculator_wrapper(quantity_enum=[50, 100, 250, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000, 5000], validate_params=True)
def calculate_printed_letterheads(
    quantity: int,
    print_sides: str = "Single side print",
    print_type: str = "Colour",
    finish_size: str = "A4 - 210mm x 297mm",
    paper_stock: str = "Uncoated Bond 80GSM",
    artworks: int = 1,
    # LEGACY PARAMETER (backwards compatibility)
    paper_stock_type: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Printed Letterheads (Shopify) - REWRITTEN Jan 24, 2026
    
    ✅ CURRENT PARAMETERS (Exact TXT Formula):
        quantity: Number of letterheads (50-5000)
        print_sides: "Single side print" or "Double side print"
        print_type: "Colour" or "Black & White"
        finish_size: "A4 - 210mm x 297mm" (only option)
        paper_stock: "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", or "Uncoated Bond 100GSM"
        artworks: Number of designs (first free, $15 per additional)
    
    ⚠️ DEPRECATED: paper_stock_type → use paper_stock instead
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
        
    Backend: PrintedLetterheads_Shopify_Calculator.py (Exact TXT lines 2115-2450)
    Validated: Jan 24, 2026 - 4/4 tests = 100% website match
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        # LEGACY PARAMETER TRANSLATION
        warnings = []
        if paper_stock_type is not None:
            paper_stock = paper_stock_type
            warnings.append({
                "deprecated_parameter": "paper_stock_type",
                "use_instead": "paper_stock",
                "value_sent": paper_stock_type,
                "translated_to": paper_stock,
                "message": f"⚠️ Parameter 'paper_stock_type' is deprecated. Use 'paper_stock' instead."
            })
        
        # Validate parameter values (AI learns valid options from errors)
        if print_type not in ["Colour", "Black & White"]:
            return {
                "success": False,
                "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
            }
        
        if print_sides not in ["Single side print", "Double side print"]:
            return {
                "success": False,
                "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'"
            }
        
        valid_paper_stocks = ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
        if paper_stock not in valid_paper_stocks:
            return {
                "success": False,
                "error": f"Invalid paper_stock: '{paper_stock}'. Must be one of: {', '.join(valid_paper_stocks)}"
            }
        
        if artworks < 1 or artworks > 50:
            return {
                "success": False,
                "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
            }
        
        from PrintedLetterheads_Shopify_Calculator import PrintedLetterheadsShopifyCalculator
        calculator = PrintedLetterheadsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            finish_size=finish_size,
            paper_stock=paper_stock,
            artworks=artworks
        )
        
        response = {
            "success": True,
            "product_type": "Printed Letterheads",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        if warnings:
            response["deprecation_warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify Printed Letterheads] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(quantity_enum=[50, 100, 250, 500, 750, 1000, 1250, 1500, 2000, 2500, 3000, 3500, 4000, 5000], validate_params=True)
def calculate_with_compliments_slips(
    quantity: int,
    print_type: str = "Colour",
    paper_stock: str = "Uncoated Bond 80GSM",
    print_sides: str = "Single side print",
    finish_size: str = "DL - 99mm x 210mm",
    artworks: int = 1,
    # LEGACY PARAMETER (backwards compatibility)
    paper_stock_type: str = None
) -> Dict[str, Any]:
    """
    Shopify calculator for With Compliments Slips
    REWRITTEN Jan 24, 2026 - Exact TXT formula (lines 2581-2930)
    ✅ VALIDATED: 4/4 tests = 100% website match (Jan 25, 2026)
    
    Backend: WithComplimentsSlips_Shopify_Calculator.py
    Test Results:
    - TEST 1 (250 qty, Single, Colour, 80GSM, 1 art): $101.41 ✅
    - TEST 2 (5000 qty, Double, B&W, 100GSM, 2 arts): $347.44 ✅
    - TEST 3 (1000 qty, Double, Colour, 90GSM, 1 art): $158.64 ✅
    - TEST 4 (50 qty, Single, B&W, 80GSM, 1 art): $90.16 ✅
    
    Args:
        quantity: Number of compliments slips (50-5000)
        print_sides: 'Single side print' (1×) or 'Double side print' (2×)
        print_type: 'Colour' ($0.044/sheet) or 'Black & White' ($0.02/sheet)
        finish_size: 'DL - 99mm x 210mm' (6 slips per sheet)
        paper_stock: 'Uncoated Bond 80GSM' ($26.34), '90GSM' ($29.51), or '100GSM' ($32.68) per 1000
        artworks: Number of designs (first FREE, $15 per additional)
    
    ⚠️ DEPRECATED: paper_stock_type → use paper_stock instead
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        # LEGACY PARAMETER TRANSLATION
        warnings = []
        if paper_stock_type is not None:
            paper_stock = paper_stock_type
            warnings.append({
                "deprecated_parameter": "paper_stock_type",
                "use_instead": "paper_stock",
                "value_sent": paper_stock_type,
                "translated_to": paper_stock,
                "message": f"⚠️ Parameter 'paper_stock_type' is deprecated. Use 'paper_stock' instead."
            })
            print(f"\n{'='*80}")
            print(f"⚠️  DEPRECATED PARAMETER in calculate_with_compliments_slips")
            print(f"  • {warnings[0]['message']}")
            print(f"{'='*80}\n")
        
        # ========================================================================
        # VALIDATION: Parameters now have defaults in function signature
        # ========================================================================
        
        # Validate parameter values (AI learns valid options from errors)
        if print_type not in ["Colour", "Black & White"]:
            return {
                "success": False,
                "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
            }
        
        if print_sides not in ["Single side print", "Double side print"]:
            return {
                "success": False,
                "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'"
            }
        
        valid_paper_stocks = ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM"]
        if paper_stock not in valid_paper_stocks:
            return {
                "success": False,
                "error": f"Invalid paper_stock: '{paper_stock}'. Must be one of: {', '.join(valid_paper_stocks)}"
            }
        
        if artworks < 1 or artworks > 50:
            return {
                "success": False,
                "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
            }
        
        from WithComplimentsSlips_Shopify_Calculator import WithComplimentsSlipsShopifyCalculator
        calculator = WithComplimentsSlipsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            finish_size=finish_size,
            paper_stock=paper_stock,
            artworks=artworks
        )
        
        response = {
            "success": True,
            "product_type": "With Compliments Slips",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
        if warnings:
            response["deprecation_warnings"] = warnings
        
        return response
        
    except Exception as e:
        print(f"❌ [Shopify With Compliments Slips] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_notepads_a4(
    quantity: str,  # JSON uses string quantities
    print_type: str = "Black & White 1 sided",  # JSON default
    stock_type: str = "Uncoated Bond 80GSM",  # JSON default
    leaves_per_pad: str = "50",  # JSON default
    finish_size: str = "A4 Portrait",  # JSON only has 1 option
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate quote for Notepads A4 (Shopify)
    
    Args:
        quantity: Number of notepads as string - "25", "50", "75", "100", "150", "200", "250", "300", "400", "500", "750", "1000", "2000"
        print_type: Print type with sides - "Colour 1 sided", "Colour 2 sided", "Black & White 1 sided", "Black & White 2 sided" (default: "Black & White 1 sided")
        stock_type: Paper stock - "Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM", "Revive 100% Recycled 80GSM Bond" (default: "Uncoated Bond 80GSM")
        leaves_per_pad: Leaves per pad as string - "25", "50", "100" (default: "50")
        finish_size: Finish size - "A4 Portrait" (only option)
        artworks: Number of unique designs 1-20 (default: 1)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    # ========================================================================
    # VALIDATION: Validate JSON format parameters
    # ========================================================================
    valid_quantities = ["25", "50", "75", "100", "150", "200", "250", "300", "400", "500", "750", "1000", "2000"]
    if quantity not in valid_quantities:
        return {
            "success": False,
            "error": f"Invalid quantity: '{quantity}'. Must be one of: {', '.join(valid_quantities)}"
        }
    
    valid_print_types = ["Colour 1 sided", "Colour 2 sided", "Black & White 1 sided", "Black & White 2 sided"]
    if print_type not in valid_print_types:
        return {
            "success": False,
            "error": f"Invalid print_type: '{print_type}'. Must be one of: {', '.join(valid_print_types)}"
        }
    
    valid_stock_types = ["Uncoated Bond 80GSM", "Uncoated Bond 90GSM", "Uncoated Bond 100GSM", "Revive 100% Recycled 80GSM Bond"]
    if stock_type not in valid_stock_types:
        return {
            "success": False,
            "error": f"Invalid stock_type: '{stock_type}'. Must be one of: {', '.join(valid_stock_types)}"
        }
    
    valid_leaves_per_pad = ["25", "50", "100"]
    if leaves_per_pad not in valid_leaves_per_pad:
        return {
            "success": False,
            "error": f"Invalid leaves_per_pad: '{leaves_per_pad}'. Must be one of: {', '.join(valid_leaves_per_pad)}"
        }
    
    valid_finish_sizes = ["A4 Portrait"]
    if finish_size not in valid_finish_sizes:
        return {
            "success": False,
            "error": f"Invalid finish_size: '{finish_size}'. Must be: A4 Portrait"
        }
    
    if artworks < 1 or artworks > 20:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 20"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    
    try:
        from NotepadsA4_Shopify_Calculator import NotepadsA4ShopifyCalculator
        calculator = NotepadsA4ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,  # Pass as string
            print_type=print_type,  # Pass combined format like "Colour 1 sided"
            stock_type=stock_type,  # JSON field name
            leaves_per_pad=leaves_per_pad,  # JSON field name
            artworks=artworks
        )
        response = {
            "success": True,
            "product_type": "Notepads A4",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        return response
    except Exception as e:
        print(f"❌ [Shopify Notepads A4] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(quantity_enum=[25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000], validate_params=True)
def calculate_notepads_a5(
    quantity: int,
    print_type: str = None,
    print_sides: str = None,
    paper_stock: str = None,
    artworks: int = None,
    # Legacy parameter
    stock_type: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Notepads A5 (Shopify)
    
    Args:
        quantity: Number of notepads (25-2000, required)
        print_type: "Colour" or "Black & White" (default backend: "Colour")
        print_sides: "Single side print" or "Double side print" (default backend: "Single side print")
        paper_stock: Paper type - "Standard", "Uncoated Bond 80GSM", etc. (default backend: "Standard")
        artworks: Number of unique designs (default backend: 1)
        
        DEPRECATED:
        stock_type: Legacy alias for paper_stock (use paper_stock instead)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    warnings = []
    
    # ========================================================================
    # LEGACY TRANSLATION (with warnings)
    # ========================================================================
    if stock_type is not None:
        paper_stock = stock_type
        warnings.append({
            "deprecated": "stock_type",
            "use_instead": "paper_stock",
            "value_sent": stock_type,
            "translated_to": paper_stock
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_notepads_a5:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
        print(log_msg)
    
    # ========================================================================
    # VALIDATION (after legacy translation - THE CRITICAL MISSING PIECE!)
    # ========================================================================
    # Apply backend defaults for None values
    if print_type is None:
        print_type = "Colour"  # Backend default
    
    if print_sides is None:
        print_sides = "Single side print"  # Backend default
    
    if paper_stock is None:
        paper_stock = "Standard"  # Backend default
    
    if artworks is None:
        artworks = 1  # Backend default
    
    # Validate parameter values (AI learns valid options from errors)
    if print_type not in ["Colour", "Black & White"]:
        return {
            "success": False,
            "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
        }
    
    if print_sides not in ["Single side print", "Double side print"]:
        return {
            "success": False,
            "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator
        calculator = NotepadsA5ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_type=print_type,
            print_sides=print_sides,
            paper_stock=paper_stock,
            artworks=artworks
        )
        response = {
            "success": True,
            "product_type": "Notepads A5",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        if warnings:
            response["warnings"] = warnings
        return response
    except Exception as e:
        print(f"❌ [Shopify Notepads A5] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


@calculator_wrapper(quantity_enum=[25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000], validate_params=True)
def calculate_notepads_a6(
    quantity: int,
    print_type: str = None,
    print_sides: str = None,
    paper_stock: str = None,
    artworks: int = None,
    # Legacy parameter
    stock_type: str = None
) -> Dict[str, Any]:
    """
    Calculate quote for Notepads A6 (Shopify)
    
    Args:
        quantity: Number of notepads (25-2000, required)
        print_type: "Colour" or "Black & White" (default backend: "Colour")
        print_sides: "Single side print" or "Double side print" (default backend: "Single side print")
        paper_stock: Paper type - "Standard", "Uncoated Bond 80GSM", etc. (default backend: "Standard")
        artworks: Number of unique designs (default backend: 1)
        
        DEPRECATED:
        stock_type: Legacy alias for paper_stock (use paper_stock instead)
    
    Returns:
        Dict with success, total_price, unit_price, cost_per_item, breakdown, specifications
    """
    warnings = []
    
    # ========================================================================
    # LEGACY TRANSLATION (with warnings)
    # ========================================================================
    if stock_type is not None:
        paper_stock = stock_type
        warnings.append({
            "deprecated": "stock_type",
            "use_instead": "paper_stock",
            "value_sent": stock_type,
            "translated_to": paper_stock
        })
    
    if warnings:
        log_msg = f"\n⚠️  DEPRECATED PARAMETERS in calculate_notepads_a6:\n"
        for w in warnings:
            log_msg += f"   {w['deprecated']}={w['value_sent']} → {w['use_instead']}='{w['translated_to']}'\n"
        print(log_msg)
    
    # ========================================================================
    # VALIDATION (after legacy translation - THE CRITICAL MISSING PIECE!)
    # ========================================================================
    # Apply backend defaults for None values
    if print_type is None:
        print_type = "Colour"  # Backend default
    
    if print_sides is None:
        print_sides = "Single side print"  # Backend default
    
    if paper_stock is None:
        paper_stock = "Standard"  # Backend default
    
    if artworks is None:
        artworks = 1  # Backend default
    
    # Validate parameter values (AI learns valid options from errors)
    if print_type not in ["Colour", "Black & White"]:
        return {
            "success": False,
            "error": f"Invalid print_type: '{print_type}'. Must be 'Colour' or 'Black & White'"
        }
    
    if print_sides not in ["Single side print", "Double side print"]:
        return {
            "success": False,
            "error": f"Invalid print_sides: '{print_sides}'. Must be 'Single side print' or 'Double side print'"
        }
    
    if artworks < 1 or artworks > 50:
        return {
            "success": False,
            "error": f"Invalid artworks: {artworks}. Must be between 1 and 50"
        }
    
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from NotepadsA6_Shopify_Calculator import NotepadsA6ShopifyCalculator
        calculator = NotepadsA6ShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_type=print_type,
            print_sides=print_sides,
            paper_stock=paper_stock,
            artworks=artworks
        )
        response = {
            "success": True,
            "product_type": "Notepads A6",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
            "breakdown": {k: float(v) if isinstance(v, Decimal) else v for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        if warnings:
            response["warnings"] = warnings
        return response
    except Exception as e:
        print(f"❌ [Shopify Notepads A6] Error: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}


def calculate_spiral_bound_books(**kwargs) -> Dict[str, Any]:
    """Shopify calculator for Spiral Bound Books"""
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {"success": False, "error": "Shopify calculators not available."}
    try:
        from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
        
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
