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
    
    try:
        # Import credentials manager
        import sys
        import json
        
        # From: UI/modules_external/quote-calculator/implementations/calculator_wrapper.py
        # To: AI_infrastructure/auth (need to go up 5 levels to project root)
        # Levels: implementations -> quote-calculator -> modules_external -> UI -> AI_agents (root)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        credentials_path = project_root / 'AI_infrastructure' / 'auth'
        
        if str(credentials_path) not in sys.path:
            sys.path.insert(0, str(credentials_path))
        
        from supabase_credentials import get_database_config
        
        # Get config (auto-detects Render vs Local)
        config = get_database_config()
        
        # Write config to fixed location in project root
        config_dir = project_root / 'config'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'database-config-runtime.json'
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Import InHousePrintDB to create db_connector
        # ComprehensiveQuoteCalculator expects a db_connector, NOT a config_path
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        
        from inhouse_modules.db_connector import InHousePrintDB
        
        # Create database connector
        db_connector = InHousePrintDB(str(config_file))
        
        # Initialize calculator with db_connector
        return ComprehensiveQuoteCalculator(db_connector)
        
    except Exception as e:
        print(f"⚠️  [Calculator] Failed to initialize: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise RuntimeError(f"Calculator initialization failed: {e}")


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
        # Convert size to dimensions (mm)
        size_map = {
            "A6": (105, 148),
            "DL": (99, 210),
            "A5": (148, 210),
            "A4": (210, 297)
        }
        width, height = size_map.get(size.upper(), (210, 297))
        
        # Extract GSM from stock string (e.g. "150GSM Gloss" -> 150)
        import re
        gsm_match = re.search(r'(\d+)GSM', stock, re.IGNORECASE)
        gsm = int(gsm_match.group(1)) if gsm_match else 150
        
        # Convert sides to print_side parameters
        print_side1 = 1  # Always print side 1
        print_side2 = 1 if sides == 2 else 0
        
        calculator = _get_calculator()
        result = calculator.calculate_flyers(
            quantity=quantity,
            width=width,
            height=height,
            gsm=gsm,
            print_side1=print_side1,
            print_side2=print_side2
        )
        
        return {
            "success": True,
            "product": f"{size} Flyers",
            "quantity": quantity,
            "size": size,
            "stock": stock,
            "sides": sides,
            "total_cost_ex_gst": float(result.cost_to_business),
            "total_cost_inc_gst": float(result.total_cost_inc_gst),
            "per_unit_price": float(result.total_cost_inc_gst / quantity),
            "stock_details": f"{width}x{height}mm, {gsm}GSM"
        }
        
    except Exception as e:
        return _handle_calculator_error(e, "flyers")


def calculate_booklets(
    quantity: int,
    pages: int,
    cover_stock: str,
    inner_stock: str,
    size: str,
    binding_type: str = "saddle_stitch",
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate quote for booklets using Shopify calculators (database-independent)
    
    Args:
        quantity: Number of booklets
        pages: Total pages (must be divisible by 4)
        cover_stock: Cover paper stock (e.g., "350GSM Gloss", "300GSM Satin")
        inner_stock: Inner pages paper stock (e.g., "150GSM Gloss", "Uncoated Bond 100GSM")
        size: "A5" or "A4" (Portrait/Landscape)
        binding_type: "saddle_stitch", "wire_bound", "spiral_bound" (default: saddle_stitch)
        **kwargs: Additional parameters
    
    Returns:
        Dict with success, total_price, per_booklet_price, binding_cost
    """
    try:
        # Use Shopify calculators (no database dependency)
        if not SHOPIFY_CALCULATORS_AVAILABLE:
            raise RuntimeError("Shopify calculators not available")
        
        # Map stock names to Shopify format
        cover_stock_mapped = cover_stock.replace("GSM", "GSM")  # Normalize GSM
        inner_stock_mapped = inner_stock.replace("GSM", "GSM")
        
        # Map size to finish_size format
        if size.upper() == "A5":
            finish_size = "A5 Portrait"
        elif size.upper() == "A4":
            finish_size = "A4 Portrait"
        else:
            finish_size = f"{size} Portrait"
        
        # Determine cover print type based on stock
        if "350" in cover_stock or "300" in cover_stock:
            cover_print = "2pp Colour"  # Assume full color for heavier stocks
        else:
            cover_print = "1pp Colour"
        
        # Determine internal print type
        if "Uncoated" in inner_stock or "Bond" in inner_stock:
            internal_print = "Black & White"
        else:
            internal_print = "Full Colour"
        
        # Choose calculator based on binding type
        if binding_type == "wire_bound" or "wire" in binding_type.lower():
            calculator = WireBoundShopifyCalculator()
            result = calculator.calculate(
                quantity=quantity,
                artworks=1,  # Single artwork
                finish_size=finish_size,
                printed_front_cover=cover_stock_mapped,
                front_cover_print=cover_print,
                printed_back_cover=cover_stock_mapped,
                back_cover_print=cover_print,
                internal_pages=pages - 4,  # Subtract cover pages
                internal_stock=inner_stock_mapped,
                internal_print=internal_print
            )
        elif binding_type == "spiral_bound" or "spiral" in binding_type.lower():
            calculator = SpiralBoundShopifyCalculator()
            result = calculator.calculate(
                quantity=quantity,
                artworks=1,
                finish_size=finish_size,
                printed_front_cover=cover_stock_mapped,
                front_cover_print=cover_print,
                printed_back_cover=cover_stock_mapped,
                back_cover_print=cover_print,
                internal_pages=pages - 4,
                internal_stock=inner_stock_mapped,
                internal_print=internal_print
            )
        else:
            # Default: Use wire bound for saddle stitch approximation
            calculator = WireBoundShopifyCalculator()
            result = calculator.calculate(
                quantity=quantity,
                artworks=1,
                finish_size=finish_size,
                printed_front_cover=cover_stock_mapped,
                front_cover_print=cover_print,
                printed_back_cover=cover_stock_mapped,
                back_cover_print=cover_print,
                internal_pages=pages - 4,
                internal_stock=inner_stock_mapped,
                internal_print=internal_print
            )
        
        return {
            "success": True,
            "product": f"{size} Booklet ({pages} pages, {binding_type})",
            "quantity": quantity,
            "pages": pages,
            "cover_stock": cover_stock,
            "inner_stock": inner_stock,
            "size": size,
            "binding_type": binding_type,
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
        from inhouse_modules.db_connector import InHousePrintDB
        from decimal import Decimal
        
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
        from inhouse_modules.shopify_calculators import CorfluteInsertAFrameShopifyCalculator
        CorfluteInsertAFrameShopifyCalculator = getattr(__import__('inhouse_modules.shopify_calculators.CorfluteInsertA-Frame_Shopify_Calculator', fromlist=['CorfluteInsertAFrameShopifyCalculator']), 'CorfluteInsertAFrameShopifyCalculator')
        calculator = CorfluteInsertAFrameShopifyCalculator()
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
        MetalFaceAFrameShopifyCalculator = getattr(__import__('inhouse_modules.shopify_calculators.MetalFaceA-Frame_Shopify_Calculator', fromlist=['MetalFaceAFrameShopifyCalculator']), 'MetalFaceAFrameShopifyCalculator')
        calculator = MetalFaceAFrameShopifyCalculator()
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
        calculator = SpiralBoundShopifyCalculator()
        result = calculator.calculate(**kwargs)
        return {
            "success": True,
            "product_type": "Spiral Bound Books",
            "quantity": result.quantity,
            "total_price": float(result.total_price),
            "unit_price": float(result.unit_price),
            "cost_per_item": float(result.cost_per_item),
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
