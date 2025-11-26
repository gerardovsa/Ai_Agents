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
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add root directory to Python path to import inhouse_modules
root_dir = Path(__file__).parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator
    
    CALCULATOR_AVAILABLE = True
    print("✅ [Quote Calculator Wrapper] Initialized successfully")
    
except ImportError as e:
    CALCULATOR_AVAILABLE = False
    print(f"⚠️  [Quote Calculator Wrapper] Failed to import calculator: {e}")
    print("   Quote calculator tools will not be available")

# Import GOD calculators
GOD_CALCULATORS_AVAILABLE = False
try:
    backend_dir = Path(__file__).parent.parent / 'backend'
    god_calc_dir = backend_dir / 'god_calculators'
    shopify_calc_dir = backend_dir / 'shopify_calculators'
    
    # Add backend to path for relative imports
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    from god_calculators.GOD_flyer_calculator import FlyerCalculatorGOD
    from god_calculators.GOD_letterhead_calculator import LetterheadCalculatorGOD
    from god_calculators.GOD_perfect_bound_books_calculator import PerfectBoundBooksCalculator
    from god_calculators.corflute_calculator import CorflutePricingCalculator
    
    GOD_CALCULATORS_AVAILABLE = True
    print("✅ [GOD Calculators] Loaded successfully")
except ImportError as e:
    print(f"⚠️  [GOD Calculators] Failed to import: {e}")
    print("   GOD calculator tools will not be available")

# Import Shopify calculators
SHOPIFY_CALCULATORS_AVAILABLE = False
try:
    from shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
    from shopify_calculators.PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
    from shopify_calculators.FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
    from shopify_calculators.WireBound_Shopify_Calculator import WireBoundShopifyCalculator
    from shopify_calculators.SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
    
    SHOPIFY_CALCULATORS_AVAILABLE = True
    print("✅ [Shopify Calculators] Loaded successfully")
except ImportError as e:
    print(f"⚠️  [Shopify Calculators] Failed to import: {e}")
    print("   Shopify calculator tools will not be available")


# ==================== HELPER FUNCTIONS ====================

def _ensure_calculator():
    """Ensure calculator is available, raise error if not"""
    if not CALCULATOR_AVAILABLE:
        raise RuntimeError(
            "Quote calculator not available. "
            "Ensure inhouse_modules/calculators is properly configured."
        )


def _get_calculator():
    """Get calculator instance"""
    _ensure_calculator()
    
    # Get database config path - works both locally and on Render.com
    # Detect Render by checking for SUPABASE_DB_URL (exists on Render, not locally)
    is_render = (
        os.environ.get('RENDER') == 'true' or
        'SUPABASE_DB_URL' in os.environ or
        not sys.platform.startswith('win')
    )
    
    if is_render:
        # Render deployment: Use /app root
        config_path = Path('/app/config/database-config.json')
    else:
        # Local development: Use root_dir
        config_path = root_dir / "config" / "database-config.json"
    
    if not config_path.exists():
        # Fallback to default G_Folder path
        config_path = None
    
    return ComprehensiveQuoteCalculator(config_path=str(config_path) if config_path else None)


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
    sides: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for business cards
    
    Args:
        quantity: Number of cards (50-10000)
        stock_type: "standard" (350GSM Satin) or "premium" (400GSM Satin)
        sides: 1 or 2 (single/double-sided)
        **kwargs: Additional parameters (ignored, for compatibility)
    
    Returns:
        Dict with success, total_price, per_unit_price, stock_details, turnaround_days
    """
    try:
        calculator = _get_calculator()
        result = calculator.calculate_business_cards(
            quantity=quantity,
            stock_type=stock_type,
            sides=sides
        )
        
        return {
            "success": True,
            "product": "Business Cards",
            "quantity": quantity,
            "stock_type": stock_type,
            "sides": sides,
            "total_price": result.get("total_price"),
            "per_unit_price": result.get("per_unit_price"),
            "stock_details": result.get("stock_details"),
            "turnaround_days": result.get("turnaround_days", 3),
            "size": "90x55mm (standard)"
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "business cards")


def calculate_flyers(
    quantity: int,
    size: str,
    stock: str,
    sides: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for flyers/leaflets
    
    Args:
        quantity: Number of flyers
        size: "A6", "DL", "A5", or "A4"
        stock: Paper stock (e.g. "150GSM Gloss")
        sides: 1 or 2
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_unit_price, stock_details
    """
    try:
        calculator = _get_calculator()
        result = calculator.calculate_flyers(
            quantity=quantity,
            size=size,
            stock=stock,
            sides=sides
        )
        
        return {
            "success": True,
            "product": f"{size} Flyers",
            "quantity": quantity,
            "size": size,
            "stock": stock,
            "sides": sides,
            "total_price": result.get("total_price"),
            "per_unit_price": result.get("per_unit_price"),
            "stock_details": result.get("stock_details")
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "flyers")


def calculate_booklets(
    quantity: int,
    pages: int,
    cover_stock: str,
    inner_stock: str,
    size: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for saddle-stitched booklets
    
    Args:
        quantity: Number of booklets
        pages: Total pages (must be divisible by 4)
        cover_stock: Cover paper stock
        inner_stock: Inner pages paper stock
        size: "A5" or "A4"
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_booklet_price, binding_cost
    """
    try:
        calculator = _get_calculator()
        result = calculator.calculate_booklets(
            quantity=quantity,
            pages=pages,
            cover_stock=cover_stock,
            inner_stock=inner_stock,
            size=size
        )
        
        return {
            "success": True,
            "product": f"{size} Booklet ({pages} pages)",
            "quantity": quantity,
            "pages": pages,
            "cover_stock": cover_stock,
            "inner_stock": inner_stock,
            "size": size,
            "total_price": result.get("total_price"),
            "per_booklet_price": result.get("per_booklet_price"),
            "binding_cost": result.get("binding_cost")
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "booklets")


def calculate_perfect_bound_books(
    quantity: int,
    pages: int,
    cover_stock: str,
    inner_stock: str,
    size: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for perfect bound books (glued spine)
    
    Args:
        quantity: Number of books
        pages: Total pages (minimum 24)
        cover_stock: Cover paper stock (typically heavier)
        inner_stock: Inner pages paper stock
        size: "A5" or "A4"
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_book_price, binding_cost
    """
    try:
        calculator = _get_calculator()
        result = calculator.calculate_perfect_bound_books(
            quantity=quantity,
            pages=pages,
            cover_stock=cover_stock,
            inner_stock=inner_stock,
            size=size
        )
        
        return {
            "success": True,
            "product": f"{size} Perfect Bound Book ({pages} pages)",
            "quantity": quantity,
            "pages": pages,
            "cover_stock": cover_stock,
            "inner_stock": inner_stock,
            "size": size,
            "binding_type": "Perfect Bound (glued spine)",
            "total_price": result.get("total_price"),
            "per_book_price": result.get("per_book_price"),
            "binding_cost": result.get("binding_cost")
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
        calculator = _get_calculator()
        result = calculator.calculate_letterheads(
            quantity=quantity,
            stock=stock,
            colors=colors
        )
        
        return {
            "success": True,
            "product": "Letterheads",
            "quantity": quantity,
            "stock": stock,
            "colors": colors,
            "size": "A4",
            "total_price": result.get("total_price"),
            "per_sheet_price": result.get("per_sheet_price")
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "letterheads")


def calculate_corflute_signs(
    quantity: int,
    size: str,
    thickness: str,
    sides: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for corflute signs (rigid plastic signage)
    
    Args:
        quantity: Number of signs
        size: Size in "WIDTHxHEIGHT" format (e.g. "600x900")
        thickness: "3mm" or "5mm"
        sides: 1 or 2
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_sign_price, material_cost
    """
    try:
        calculator = _get_calculator()
        result = calculator.calculate_corflute_signs(
            quantity=quantity,
            size=size,
            thickness=thickness,
            sides=sides
        )
        
        return {
            "success": True,
            "product": f"Corflute Sign ({size})",
            "quantity": quantity,
            "size": size,
            "thickness": thickness,
            "sides": sides,
            "total_price": result.get("total_price"),
            "per_sign_price": result.get("per_sign_price"),
            "material_cost": result.get("material_cost")
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "corflute signs")


def get_stock_list(category: str = "all", **kwargs) -> List[Dict[str, Any]]:
    """
    Get list of available paper stocks with specifications
    
    Args:
        category: Filter by category ("all", "gloss", "satin", "uncoated", "specialty")
        **kwargs: Additional parameters (ignored)
    
    Returns:
        List of stock objects with name, gsm, finish, suitable_for, price_multiplier
    """
    try:
        calculator = _get_calculator()
        stocks = calculator.get_stock_list()
        
        # Filter by category if specified
        if category and category != "all":
            category_lower = category.lower()
            stocks = [
                stock for stock in stocks
                if category_lower in stock.get("finish", "").lower()
            ]
        
        # Format for AI consumption
        return [{
            "name": stock.get("name"),
            "gsm": stock.get("gsm"),
            "finish": stock.get("finish"),
            "suitable_for": stock.get("suitable_for", []),
            "price_multiplier": stock.get("price_multiplier", 1.0),
            "description": f"{stock.get('gsm')}GSM {stock.get('finish')}"
        } for stock in stocks]
        
    except Exception as e:
        print(f"❌ [Stock List] Error: {e}")
        return []


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
        from inhouse_modules.db_connector import InHousePrintDB
        from decimal import Decimal
        
        db = InHousePrintDB()
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
    cello_required: bool = False,
    cello_side1: int = 0,
    discount: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) letterhead calculator - Database-accurate pricing
    
    Args:
        quantity: Number of letterheads
        width: Finished width in mm (typically 210 for A4)
        height: Finished height in mm (typically 297 for A4)
        gsm: Paper weight (e.g., 100, 120)
        print_side1: Print mode for side 1 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        print_side2: Print mode for side 2 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
        cello_required: Whether cellophane lamination required
        cello_side1: Cello type for side 1 (0=none, 1=gloss, 2=matt)
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
        from inhouse_modules.db_connector import InHousePrintDB
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
            cello_required=cello_required,
            cello_side1=cello_side1,
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
    cover_width: int,
    cover_height: int,
    cover_gsm: int,
    inner_gsm: int,
    print_cover_outside: int = 1,
    print_cover_inside: int = 0,
    print_inner: int = 2,
    cello_required: bool = False,
    discount: float = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) perfect bound books calculator
    
    Args:
        quantity: Number of books
        pages: Total number of pages (minimum 24)
        cover_width: Cover width in mm (210 for A4, 148 for A5)
        cover_height: Cover height in mm (297 for A4, 210 for A5)
        cover_gsm: Cover paper weight (e.g., 250, 300)
        inner_gsm: Inner pages paper weight (e.g., 100, 115, 120)
        print_cover_outside: Print mode for cover outside (0=none, 1=colour, 2=b&w)
        print_cover_inside: Print mode for cover inside (0=none, 1=colour, 2=b&w)
        print_inner: Print mode for inner pages (0=none, 1=colour, 2=b&w)
        cello_required: Cover cellophane lamination
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
        from inhouse_modules.db_connector import InHousePrintDB
        from decimal import Decimal
        
        db = InHousePrintDB()
        calculator = PerfectBoundBooksCalculator(db)
        
        result = calculator.calculate(
            quantity=quantity,
            pages=pages,
            cover_width=cover_width,
            cover_height=cover_height,
            cover_gsm=cover_gsm,
            inner_gsm=inner_gsm,
            print_cover_outside=print_cover_outside,
            print_cover_inside=print_cover_inside,
            print_inner=print_inner,
            cello_required=cello_required,
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
        print(f"❌ [GOD Perfect Bound Books Calculator] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def calculate_corflute_signs_god(
    quantity: int,
    width: int,
    height: int,
    thickness: int = 3,
    print_sides: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    GOD (database-driven) corflute signs calculator
    
    Args:
        quantity: Number of signs
        width: Sign width in mm (e.g., 600, 900, 1200)
        height: Sign height in mm (e.g., 600, 900, 1200)
        thickness: Corflute thickness in mm (3 or 5)
        print_sides: Number of printed sides (1 or 2)
    
    Returns:
        Dict with success, quote result, or error
    """
    if not GOD_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "GOD calculators not available. Check database connection."
        }
    
    try:
        from inhouse_modules.db_connector import InHousePrintDB
        from decimal import Decimal
        
        db = InHousePrintDB()
        calculator = CorflutePricingCalculator(db)
        
        result = calculator.calculate_quote(
            quantity=quantity,
            width_mm=width,
            height_mm=height,
            thickness_mm=thickness,
            sides=print_sides
        )
        
        return {
            "success": True,
            "product_type": "Corflute Signs",
            "quantity": result.quantity,
            "cost_to_business": float(result.cost_to_business),
            "profit_margin": float(result.profit_margin_percent),
            "total_cost_ex_gst": float(result.total_ex_gst),
            "total_cost_inc_gst": float(result.total_inc_gst),
            "breakdown": {
                "material_cost": float(result.material_cost),
                "printing_cost": float(result.printing_cost),
                "setup_cost": float(result.setup_cost),
                "unit_price_ex_gst": float(result.unit_price_ex_gst),
                "unit_price_inc_gst": float(result.unit_price_inc_gst)
            },
            "specifications": {
                "size": f"{width}x{height}mm",
                "thickness": f"{thickness}mm",
                "sides": print_sides,
                "area_sqm": float(result.area_sqm)
            }
        }
        
    except Exception as e:
        print(f"❌ [GOD Corflute Signs Calculator] Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ==================== SHOPIFY CALCULATOR WRAPPERS ====================

def calculate_economical_business_cards_shopify(
    quantity: int,
    print_sides: str,
    print_type: str = "Colour",
    artworks: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Economical Business Cards
    
    Args:
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single side print" or "Double side print"
        print_type: "Colour" or "Black & White"
        artworks: Number of different designs (1-50, first free, $15 per extra)
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
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
    print_sides: str,
    print_type: str = "Colour",
    cellophane: str = "No Cellophane",
    artworks: int = 1,
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Premium Business Cards
    
    Args:
        quantity: Number of cards (250, 500, 1000, 2000, 5000, 10000)
        print_sides: "Single side print" or "Double side print"
        print_type: "Colour" or "Black & White"
        cellophane: "No Cellophane", "Gloss Cellophane", or "Matt Cellophane"
        artworks: Number of different designs (1-50)
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        calculator = PremiumBusinessCardsShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            print_sides=print_sides,
            print_type=print_type,
            cellophane=cellophane,
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
    paper_stock: str,
    print_sides: str,
    folding: str = "No Folding",
    **kwargs
) -> Dict[str, Any]:
    """
    Shopify calculator for Folded Flyers
    
    Args:
        quantity: Number of flyers
        size: "A4", "A5", or "DL"
        paper_stock: Paper stock (e.g., "150GSM Gloss Art", "300GSM Gloss Art")
        print_sides: "Single side print" or "Double side print"
        folding: "No Folding", "Half Fold", "Z Fold", or "Gate Fold"
    
    Returns:
        Dict with success, quote result, or error
    """
    if not SHOPIFY_CALCULATORS_AVAILABLE:
        return {
            "success": False,
            "error": "Shopify calculators not available."
        }
    
    try:
        calculator = FoldedFlyersShopifyCalculator()
        result = calculator.calculate(
            quantity=quantity,
            size=size,
            paper_stock=paper_stock,
            print_sides=print_sides,
            folding=folding
        )
        
        return {
            "success": True,
            "product_type": "Folded Flyers",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
            "specifications": result.specifications
        }
        
    except Exception as e:
        print(f"❌ [Shopify Folded Flyers] Error: {e}")
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
            pages=pages,
            size=size,
            cover_stock=cover_stock,
            inner_stock=inner_stock,
            cover_cellophane=cover_cellophane
        )
        
        return {
            "success": True,
            "product_type": "Wire Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "breakdown": {k: float(v) for k, v in result.breakdown.items()},
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
            pages=pages,
            size=size,
            cover_stock=cover_stock,
            inner_stock=inner_stock,
            cover_cellophane=cover_cellophane
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
