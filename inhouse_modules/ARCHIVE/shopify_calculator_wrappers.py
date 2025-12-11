"""
Shopify Calculator Wrappers
============================

Simple wrapper functions that provide AI-friendly interfaces to the complex
F1-F14 Shopify calculator implementations.

These wrappers map common, natural parameters to the internal F1-F14 structure
used by WooCommerce DPO calculators.
"""

from decimal import Decimal
from typing import Dict, Any
from shopify_calculators.WireBound_Shopify_Calculator import (
    WireBoundShopifyCalculator,
    WireBoundQuoteResult
)
from shopify_calculators.SpiralBound_Shopify_Calculator import (
    SpiralBoundShopifyCalculator
)
from shopify_calculators.PerfectBound_Shopify_Calculator import (
    PerfectBoundShopifyCalculator
)
from shopify_calculators.SaddleStitchBooks_Shopify_Calculator import (
    SaddleStitchBooksShopifyCalculator
)
from shopify_calculators.FoldedFlyers_Shopify_Calculator import (
    FoldedFlyersShopifyCalculator, PrintSides, PrintType,
    FinishSize, PaperStock, FoldType, Celloglaze
)
from shopify_calculators.EconomicalBusinessCards_Shopify_Calculator import (
    EconomicalBusinessCardsShopifyCalculator
)
from shopify_calculators.PremiumBusinessCards_Shopify_Calculator import (
    PremiumBusinessCardsShopifyCalculator
)
from shopify_calculators.PrintedLetterheads_Shopify_Calculator import (
    PrintedLetterheadsShopifyCalculator
)
from shopify_calculators.WithComplimentsSlips_Shopify_Calculator import (
    WithComplimentsSlipsShopifyCalculator
)
from shopify_calculators.NotepadsA4_Shopify_Calculator import (
    NotepadsA4ShopifyCalculator
)
from shopify_calculators.NotepadsA5_Shopify_Calculator import (
    NotepadsA5ShopifyCalculator
)
from shopify_calculators.NotepadsA6_Shopify_Calculator import (
    NotepadsA6ShopifyCalculator
)
from shopify_calculators.ElectionSigns_Shopify_Calculator import (
    ElectionSignsShopifyCalculator
)
from shopify_calculators.ConstructionSigns_Shopify_Calculator import (
    ConstructionSignsShopifyCalculator
)
from shopify_calculators.BollardSigns_Shopify_Calculator import (
    BollardSignsShopifyCalculator
)
from shopify_calculators.CorfluteInsertA_Frame_Shopify_Calculator import (
    CorfluteInsertA_FrameShopifyCalculator
)
from shopify_calculators.MetalFaceA_Frame_Shopify_Calculator import (
    MetalFaceA_FrameShopifyCalculator
)
from shopify_calculators.StrutCardsA3_Shopify_Calculator import (
    StrutCardsA3ShopifyCalculator
)
from shopify_calculators.StrutCardsA4_Shopify_Calculator import (
    StrutCardsA4ShopifyCalculator
)
from shopify_calculators.CustomPosterPrinting_Shopify_Calculator import (
    CustomPosterPrintingShopifyCalculator
)
from shopify_calculators.CustomVinylStickers_Shopify_Calculator import (
    CustomVinylStickersShopifyCalculator
)
from shopify_calculators.PremiumBookmarks_Shopify_Calculator import (
    PremiumBookmarksShopifyCalculator
)
from shopify_calculators.SelfieFrames_Shopify_Calculator import (
    SelfieFramesShopifyCalculator
)
from shopify_calculators.LuxuryClassicPullUpBanners_Shopify_Calculator import (
    LuxuryClassicPullUpBannersShopifyCalculator
)
from shopify_calculators.StackableCubes_Shopify_Calculator import (
    StackableCubesShopifyCalculator
)
from shopify_calculators.SpiralBoundBooks_Shopify_Calculator import (
    SpiralBoundBooksShopifyCalculator
)


def calculate_wire_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A4",
    cover_stock: str = "350GSM Satin",
    inner_stock: str = "100GSM Uncoated",
    cover_cellophane: str = "No Cellophane",
    front_cover_pvc: bool = True
) -> Dict[str, Any]:
    """
    Calculate Wire Bound Books quote using simplified parameters.
    
    This wrapper provides a simple interface that maps to the complex F1-F14
    parameters used by WireBoundShopifyCalculator.
    
    Args:
        quantity: Number of books
        pages: Total page count (internal pages only, not including covers)
        size: Book size ("A4", "A5", "A6", "DL")
        cover_stock: Cover paper stock (e.g., "350GSM Satin", "300GSM Satin", "250GSM Satin")
        inner_stock: Internal pages paper (e.g., "100GSM Uncoated", "100GSM Satin", "80GSM Uncoated")
        cover_cellophane: Cellophane finish ("No Cellophane", "Gloss Cellophane", "Matt Cellophane")
        front_cover_pvc: Whether to add Clear PVC overlay on front (default True)
    
    Returns:
        Dictionary with:
            - total_price: Total quote price (Decimal)
            - unit_price: Price per book (Decimal)
            - quantity: Number of books
            - breakdown: Cost breakdown dictionary
            - specifications: Full spec dictionary
    
    Example:
        >>> result = calculate_wire_bound_books_shopify(
        ...     quantity=3,
        ...     pages=316,
        ...     size="A4",
        ...     cover_stock="350GSM Satin",
        ...     inner_stock="100GSM Uncoated"
        ... )
        >>> print(f"Total: ${result['total_price']}")
    """
    
    # Map simplified size to Shopify finish_size format
    size_map = {
        "A4": "A4 Portrait",
        "A5": "A5 Portrait",
        "A6": "A6 Portrait",
        "DL": "DL Landscape"
    }
    finish_size = size_map.get(size, "A4 Portrait")
    
    # Map cover_stock to printed_front_cover / printed_back_cover (F4, F8)
    # Examples: "350GSM Satin", "300GSM Satin", "250GSM Satin"
    printed_cover = cover_stock
    
    # Map inner_stock to internal_stock (F12)
    # Need to match exact Shopify options
    inner_stock_map = {
        "100GSM Uncoated": "Uncoated Bond 100GSM",
        "100GSM Satin": "Satin 100GSM",
        "80GSM Uncoated": "Uncoated Bond 80GSM",
        "80GSM Satin": "Satin 80GSM"
    }
    internal_stock = inner_stock_map.get(inner_stock, "Uncoated Bond 100GSM")
    
    # Map cellophane to front_celloglaze and back_celloglaze (F6, F10)
    cello_map = {
        "No Cellophane": "None",
        "Gloss Cellophane": "2 Sided Gloss",
        "Matt Cellophane": "2 Sided Matt",
        "Gloss Cellophane Front Only": "1 Side Gloss",
        "Matt Cellophane Front Only": "1 Side Matt"
    }
    celloglaze = cello_map.get(cover_cellophane, "None")
    
    # Front cover PVC overlay (F3)
    outer_front = "Clear PVC 250mic" if front_cover_pvc else "Not Required"
    
    # Initialize calculator
    calc = WireBoundShopifyCalculator()
    
    # Call the F1-F14 calculator with mapped parameters
    result = calc.calculate(
        quantity=quantity,                          # F1
        artworks=1,                                 # F2 (single artwork)
        finish_size=finish_size,                    # F14
        outer_front_cover=outer_front,              # F3
        printed_front_cover=printed_cover,          # F4
        front_cover_print="2pp Colour",             # F5 (assume full color)
        front_celloglaze=celloglaze,                # F6
        outer_back_cover="None",                    # F7 (no PVC on back)
        printed_back_cover=printed_cover,           # F8 (same as front)
        back_cover_print="2pp Colour",              # F9 (assume full color)
        back_celloglaze=celloglaze,                 # F10
        internal_pages=pages,                       # F11
        internal_stock=internal_stock,              # F12
        internal_print="Full Colour"                # F13 (assume color)
    )
    
    # Convert WireBoundQuoteResult dataclass to dictionary
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_spiral_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A4",
    cover_stock: str = "350GSM Satin",
    inner_stock: str = "100GSM Uncoated",
    cover_cellophane: str = "No Cellophane",
    front_cover_pvc: bool = True
) -> Dict[str, Any]:
    """
    Calculate Spiral Bound Books quote using simplified parameters.
    
    Same interface as wire_bound but uses plastic spiral binding instead of wire.
    Spiral binding typically has different material costs and 17 thickness tiers
    instead of wire's 14 tiers.
    
    Args:
        quantity: Number of books
        pages: Total page count (internal pages only)
        size: Book size ("A4", "A5", "A6", "DL")
        cover_stock: Cover paper stock
        inner_stock: Internal pages paper
        cover_cellophane: Cellophane finish
        front_cover_pvc: Whether to add Clear PVC overlay on front
    
    Returns:
        Dictionary with total_price, unit_price, quantity, breakdown, specifications
    """
    
    # Map simplified parameters (same logic as wire_bound)
    size_map = {
        "A4": "A4 Portrait",
        "A5": "A5 Portrait",
        "A6": "A6 Portrait",
        "DL": "DL Landscape"
    }
    finish_size = size_map.get(size, "A4 Portrait")
    
    printed_cover = cover_stock
    
    inner_stock_map = {
        "100GSM Uncoated": "Uncoated Bond 100GSM",
        "100GSM Satin": "Satin 100GSM",
        "80GSM Uncoated": "Uncoated Bond 80GSM",
        "80GSM Satin": "Satin 80GSM"
    }
    internal_stock = inner_stock_map.get(inner_stock, "Uncoated Bond 100GSM")
    
    cello_map = {
        "No Cellophane": "None",
        "Gloss Cellophane": "2 Sided Gloss",
        "Matt Cellophane": "2 Sided Matt"
    }
    celloglaze = cello_map.get(cover_cellophane, "None")
    
    outer_front = "Clear PVC 250mic" if front_cover_pvc else "Not Required"
    
    # Initialize Spiral Bound calculator
    calc = SpiralBoundShopifyCalculator()
    
    # Call with F1-F14 parameters
    result = calc.calculate(
        quantity=quantity,
        artworks=1,
        finish_size=finish_size,
        outer_front_cover=outer_front,
        printed_front_cover=printed_cover,
        front_cover_print="2pp Colour",
        front_celloglaze=celloglaze,
        outer_back_cover="None",
        printed_back_cover=printed_cover,
        back_cover_print="2pp Colour",
        back_celloglaze=celloglaze,
        internal_pages=pages,
        internal_stock=internal_stock,
        internal_print="Full Colour"
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


# ============================================================================
# PHASE 2: BOOK & BINDING CALCULATORS (3 calculators)
# ============================================================================

def calculate_perfect_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A5",
    cover_stock: str = "Satin 300GSM",
    inner_stock: str = "Uncoated Bond 100GSM",
    inner_print: str = "Black & White",
    cover_cellophane: str = "None"
) -> Dict[str, Any]:
    """
    Calculate Perfect Bound Books quote - glued spine binding for professional books.
    
    Perfect binding creates soft-cover books with glued spine. Best for books, catalogs,
    reports with 60+ pages. Professional appearance, cost-effective for medium runs.
    
    Args:
        quantity: Number of books (1-20,000)
        pages: Internal page count (40-800, must be divisible by 4)
        size: Book size - "A5" (most common), "A4", "US Trade"
        cover_stock: Cover paper - "Satin 300GSM" (default), "Satin 250GSM", "Satin 350GSM"
        inner_stock: Internal paper - "Uncoated Bond 100GSM" (default), "Satin 128GSM", "Satin 150GSM"
        inner_print: Internal printing - "Black & White" or "Full Colour"
        cover_cellophane: Cover finish - "None" (default), "Gloss", "Matt"
    
    Returns:
        Dict with total_price, unit_price, quantity, breakdown, specifications
    
    Example:
        >>> # 100-copy book, 200 pages, A5 size, B&W internals
        >>> result = calculate_perfect_bound_books_shopify(
        ...     quantity=100,
        ...     pages=200,
        ...     size="A5",
        ...     inner_print="Black & White"
        ... )
        >>> print(f"Total: ${result['total_price']:.2f}")
    """
    # Map simplified size to Shopify format
    size_map = {
        "A5": "A5 Portrait",
        "A4": "A4 Portrait",
        "US Trade": "US Trade",
        "A4 Landscape": "A4 Landscape"
    }
    finish_size = size_map.get(size, "A5 Portrait")
    
    # Map print type
    content_print = "Full Colour" if "Colour" in inner_print or "Color" in inner_print else "Black & White"
    
    # Map cellophane
    cello_map = {
        "None": "None",
        "Gloss": "Gloss outside only",
        "Matt": "Matt outside only"
    }
    celloglaze = cello_map.get(cover_cellophane, "None")
    
    # Call underlying calculator
    calc = PerfectBoundShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        printed_pages=pages,
        proof_requirements="Digital Emailed Proof",
        cover_stock=cover_stock,
        cover_print_type="2 side colour (4pp)",  # Assume full color covers
        celloglaze=celloglaze,
        finish_size=finish_size,
        content_print_type=content_print,
        content_stock_type=inner_stock
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_saddle_stitch_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A4",
    cover_stock: str = "Satin 200GSM",
    inner_stock: str = "Uncoated Bond 80GSM",
    inner_print: str = "Colour",
    cover_cellophane: str = "None"
) -> Dict[str, Any]:
    """
    Calculate Saddle Stitch Books quote - stapled spine binding for magazines/booklets.
    
    Saddle stitch uses staples through center fold. Best for magazines, programs,
    booklets with 8-48 pages. Cost-effective for short documents, lays flat when open.
    
    Args:
        quantity: Number of books - must be: 25, 50, 75, 100, 150, 200, 250, 500, 1000
        pages: Total page count including covers (8-48, must be divisible by 4)
        size: Book size - "A4" (most common), "A5", "A6"
        cover_stock: Cover paper - "Satin 200GSM" (default), other weights available
        inner_stock: Internal paper - "Uncoated Bond 80GSM" (default), "100GSM", etc.
        inner_print: Internal printing - "Colour" or "Black & White"
        cover_cellophane: Cover finish - "None" (default), "Gloss", "Matt"
    
    Returns:
        Dict with total_price, unit_price, quantity, breakdown, specifications
    
    Example:
        >>> # 100 magazines, 16 pages, A4 size, color printing
        >>> result = calculate_saddle_stitch_books_shopify(
        ...     quantity=100,
        ...     pages=16,
        ...     size="A4",
        ...     inner_print="Colour"
        ... )
    """
    # Map size
    size_map = {
        "A4": "A4 Portrait",
        "A5": "A5 Portrait",
        "A6": "A6 Portrait"
    }
    finish_size = size_map.get(size, "A4 Portrait")
    
    # Map cellophane
    cello_map = {
        "None": "None",
        "Gloss": "Gloss outside only",
        "Matt": "Matt outside only"
    }
    celloglaze = cello_map.get(cover_cellophane, "None")
    
    # Call calculator
    calc = SaddleStitchBooksShopifyCalculator()
    result = calc.calculate(
        quantity=str(quantity),  # Shopify expects string
        artworks=1,
        cover_option="Hard Cover",
        cover_stock=cover_stock,
        cover_print_type="2 side colour (4pp)",
        celloglaze=celloglaze,
        printed_pages=f"{pages}pp",
        finish_size=finish_size,
        content_print_type=inner_print,
        content_stock_type=inner_stock
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_folded_flyers_shopify(
    quantity: int,
    size: str = "A4",
    stock: str = "Satin 150GSM",
    double_sided: bool = True,
    colour: bool = True,
    fold_type: str = "Double Fold",
    cellophane: str = "None"
) -> Dict[str, Any]:
    """
    Calculate Folded Flyers quote - single sheet folded into brochure/leaflet.
    
    Folded flyers are single sheet printed and folded into panels. Best for brochures,
    leaflets, direct mail pieces. Cost-effective for marketing materials.
    
    Args:
        quantity: Number of flyers (minimum 100)
        size: Flat size before folding - "A5", "A4" (most common), "A3", "6pp A4"
        stock: Paper stock - "Satin 150GSM" (default), "Satin 300GSM", "Uncoated Bond 80GSM"
        double_sided: True for printing both sides (default), False for one side
        colour: True for colour printing (default), False for black & white
        fold_type: "Single Fold", "Double Fold" (default), "Triple Fold"
        cellophane: Lamination - "None" (default), "Gloss", "Matt" (Satin stocks only)
    
    Returns:
        Dict with total_price, unit_price, quantity, breakdown, specifications
    
    Example:
        >>> # 5,000 A4 brochures, double-sided color, double fold
        >>> result = calculate_folded_flyers_shopify(
        ...     quantity=5000,
        ...     size="A4",
        ...     stock="Satin 300GSM",
        ...     fold_type="Double Fold"
        ... )
    """
    # Map parameters to enums
    print_sides = PrintSides.DOUBLE_SIDE if double_sided else PrintSides.SINGLE_SIDE
    print_type = PrintType.COLOUR if colour else PrintType.BLACK_WHITE
    
    size_map = {
        "A5": FinishSize.A5,
        "A4": FinishSize.A4,
        "A3": FinishSize.A3,
        "6pp A4": FinishSize.A4_6PP
    }
    finish_size = size_map.get(size, FinishSize.A4)
    
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
    paper_stock = stock_map.get(stock, PaperStock.SATIN_150GSM)
    
    fold_map = {
        "Single Fold": FoldType.SINGLE_FOLD,
        "Double Fold": FoldType.DOUBLE_FOLD,
        "Triple Fold": FoldType.TRIPLE_FOLD
    }
    fold = fold_map.get(fold_type, FoldType.DOUBLE_FOLD)
    
    cello_map = {
        "None": Celloglaze.NONE,
        "Gloss": Celloglaze.TWO_SIDE_GLOSS,
        "Matt": Celloglaze.TWO_SIDE_MATT
    }
    cello = cello_map.get(cellophane, Celloglaze.NONE)
    
    # Call calculator
    calc = FoldedFlyersShopifyCalculator()
    result = calc.calculate_quote(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        finish_size=finish_size,
        paper_stock=paper_stock,
        artworks=1,
        fold_type=fold,
        celloglaze=cello
    )
    
    return {
        "total_price": result.final_price,
        "unit_price": result.final_price / quantity,
        "quantity": quantity,
        "breakdown": {
            "setup": result.setup_total,
            "stock": result.stock_cost,
            "printing": result.click_cost,
            "cutting": result.cutting_cost,
            "folding": result.folding_cost,
            "celloglaze": result.cello_cost,
            "profit": result.profit,
            "subtotal": result.subtotal,
            "gst": result.gst
        },
        "specifications": result.specifications
    }


# ============================================================================
# PHASE 3: BUSINESS STATIONERY CALCULATORS (6 calculators)
# ============================================================================

def calculate_economical_business_cards_shopify(
    quantity: int,
    double_sided: bool = True,
    colour: bool = True,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Economical Business Cards quote - standard 90mm x 55mm business cards.
    
    Economical range offers cost-effective business cards with standard options.
    Most popular configuration: 350GSM Satin, double-sided color, 500-1000 quantity.
    
    Historical data shows:
    - 72.5% choose Satin 350GSM stock
    - 88% print double-sided
    - 55.5% select no cellophane (economical)
    - Most common quantities: 1000 (34.5%), 500 (26%), 250 (24%)
    
    Args:
        quantity: Number of cards - 250, 500, 1000 (most common), 2000, 5000, 10000
        double_sided: True for printing both sides (default, 88% of orders)
        colour: True for color printing (default, most common)
        stock: Paper stock - "Satin 300GSM" (standard economical option)
        artworks: Number of different designs (1-50, default 1, extra designs cost $15 each)
    
    Returns:
        Dict with total_price, unit_price, cost_per_card, quantity, breakdown, specifications
    
    Example:
        >>> # 1000 business cards, double-sided color, standard stock
        >>> result = calculate_economical_business_cards_shopify(
        ...     quantity=1000,
        ...     double_sided=True,
        ...     colour=True
        ... )
        >>> print(f"Total: ${result['total_price']:.2f}")
        >>> print(f"Per card: ${result['cost_per_card']:.3f}")
    """
    # Map parameters
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    finish_size = "90mm x 55mm"  # Standard business card size
    
    # Call calculator
    calc = EconomicalBusinessCardsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        finish_size=finish_size,
        paper_stock="Satin 300GSM",  # Only stock option for economical
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_card": result.cost_per_card,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_premium_business_cards_shopify(
    quantity: int,
    double_sided: bool = True,
    colour: bool = True,
    stock: str = "Satin 350GSM",
    celloglaze: str = "1 Side Gloss",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Premium Business Cards quote - high-end 90mm x 55mm business cards.
    
    Premium range offers thicker stock and luxury finishes. Most popular: 350GSM-400GSM Satin
    with Matt or Gloss celloglaze, double-sided. Provides premium feel and appearance.
    
    Historical data shows:
    - 18% choose 400GSM stock (premium upgrade)
    - 21.5% select Matt Cellophane both sides (premium look)
    - 21% select Gloss Cellophane (premium glossy)
    - Silk Feel Matt is ultra-premium option
    
    Args:
        quantity: Number of cards - 250, 500, 1000, 2000, 5000, 10000
        double_sided: True for printing both sides (default)
        colour: True for color printing (default)
        stock: Paper stock - "Satin 350GSM" (default), "King Kong High Bulk", "EcoStar 350GSM Uncoated"
        celloglaze: Finish - "1 Side Gloss" (default), "2 Side Gloss", "1 Side Matt", "2 Side Matt",
                    "1 Side SILK FEEL Matt", "2 Side SILK FEEL Matt", "None"
        artworks: Number of different designs (1-50, default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_card, quantity, breakdown, specifications
    
    Example:
        >>> # 500 premium cards, double-sided, matt cellophane both sides
        >>> result = calculate_premium_business_cards_shopify(
        ...     quantity=500,
        ...     stock="Satin 350GSM",
        ...     celloglaze="2 Side Matt"
        ... )
        >>> print(f"Total: ${result['total_price']:.2f}")
        >>> print(f"Per card: ${result['cost_per_card']:.3f}")
    """
    # Map parameters
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    finish_size = "90mm x 55mm"  # Standard business card size
    
    # Call calculator
    calc = PremiumBusinessCardsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        finish_size=finish_size,
        paper_stock=stock,
        artworks=artworks,
        celloglaze=celloglaze
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_card": result.cost_per_card,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


# ============================================================================
# STATIONERY WRAPPERS
# ============================================================================

def calculate_printed_letterheads_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Printed Letterheads quote.
    
    Args:
        quantity: Number of letterheads
        double_sided: Print both sides (default False)
        colour: Full colour printing (default True)
        paper_stock: Paper type (default "Standard")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    
    calc = PrintedLetterheadsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        paper_stock=paper_stock,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_with_compliments_slips_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate With Compliments Slips quote.
    
    Args:
        quantity: Number of slips
        double_sided: Print both sides (default False)
        colour: Full colour printing (default True)
        paper_stock: Paper type (default "Standard")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    
    calc = WithComplimentsSlipsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        paper_stock=paper_stock,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_notepads_a4_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Notepads A4 quote.
    
    Args:
        quantity: Number of notepads
        double_sided: Print both sides (default False)
        colour: Full colour printing (default True)
        paper_stock: Paper type (default "Standard")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    
    calc = NotepadsA4ShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        paper_stock=paper_stock,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_notepads_a5_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Notepads A5 quote.
    
    Args:
        quantity: Number of notepads
        double_sided: Print both sides (default False)
        colour: Full colour printing (default True)
        paper_stock: Paper type (default "Standard")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    
    calc = NotepadsA5ShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        paper_stock=paper_stock,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_notepads_a6_shopify(
    quantity: int,
    double_sided: bool = False,
    colour: bool = True,
    paper_stock: str = "Standard",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Notepads A6 quote.
    
    Args:
        quantity: Number of notepads
        double_sided: Print both sides (default False)
        colour: Full colour printing (default True)
        paper_stock: Paper type (default "Standard")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    print_sides = "Double side print" if double_sided else "Single side print"
    print_type = "Colour" if colour else "Black & White"
    
    calc = NotepadsA6ShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        print_sides=print_sides,
        print_type=print_type,
        paper_stock=paper_stock,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


# ============================================================================
# SIGNS WRAPPERS
# ============================================================================

def calculate_election_signs_shopify(
    quantity: int,
    size: str = "600x450",
    material: str = "Corflute",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Election Signs quote.
    
    Args:
        quantity: Number of signs
        size: Sign size in mm, format "WIDTHxHEIGHT" (e.g., "600x450")
        material: Material type ("Corflute", "Metal", "Aluminium")
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = ElectionSignsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        material=material,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_construction_signs_shopify(
    quantity: int,
    size: str = "600x450",
    material: str = "Corflute",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Construction Signs quote.
    
    Args:
        quantity: Number of signs
        size: Sign size in mm, format "WIDTHxHEIGHT" (e.g., "600x450")
        material: Material type ("Corflute", "Metal")
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = ConstructionSignsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        material=material,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_bollard_signs_shopify(
    quantity: int,
    size: str = "300x300",
    material: str = "Aluminium",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Bollard Signs quote.
    
    Args:
        quantity: Number of signs
        size: Sign size in mm, format "WIDTHxHEIGHT" (e.g., "300x300")
        material: Material type ("Aluminium", "Metal")
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = BollardSignsShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        material=material,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_corflute_insert_a_frame_shopify(
    quantity: int,
    size: str = "600x450",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Corflute Insert A-Frame quote.
    
    Args:
        quantity: Number of A-frames
        size: Sign size in mm, format "WIDTHxHEIGHT" (e.g., "600x450")
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = CorfluteInsertA_FrameShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_metal_face_a_frame_shopify(
    quantity: int,
    size: str = "600x450",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Metal Face A-Frame quote.
    
    Args:
        quantity: Number of A-frames
        size: Sign size in mm, format "WIDTHxHEIGHT" (e.g., "600x450")
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = MetalFaceA_FrameShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_strut_cards_a3_shopify(
    quantity: int,
    size: str = "297x420",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Strut Cards A3 quote.
    
    Args:
        quantity: Number of strut cards
        size: Card size in mm, format "WIDTHxHEIGHT" (default "297x420" for A3)
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = StrutCardsA3ShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_strut_cards_a4_shopify(
    quantity: int,
    size: str = "210x297",
    double_sided: bool = False,
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Strut Cards A4 quote.
    
    Args:
        quantity: Number of strut cards
        size: Card size in mm, format "WIDTHxHEIGHT" (default "210x297" for A4)
        double_sided: Print both sides (default False)
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    sides = "Double" if double_sided else "Single"
    
    calc = StrutCardsA4ShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        sides=sides,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


# ============================================================================
# PROMOTIONAL WRAPPERS
# ============================================================================

def calculate_custom_poster_printing_shopify(
    quantity: int,
    width_mm: int = 420,
    height_mm: int = 594,
    paper_stock: str = "150gsm"
) -> Dict[str, Any]:
    """
    Calculate Custom Poster Printing quote.
    
    Args:
        quantity: Number of posters
        width_mm: Poster width in mm (default 420 for A3)
        height_mm: Poster height in mm (default 594 for A3)
        paper_stock: Paper weight/type (default "150gsm")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = CustomPosterPrintingShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        width_mm=width_mm,
        height_mm=height_mm,
        paper_stock=paper_stock
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_custom_vinyl_stickers_shopify(
    quantity: int,
    width_mm: int = 100,
    height_mm: int = 100,
    finish: str = "Gloss"
) -> Dict[str, Any]:
    """
    Calculate Custom Vinyl Stickers quote.
    
    Args:
        quantity: Number of stickers
        width_mm: Sticker width in mm (default 100)
        height_mm: Sticker height in mm (default 100)
        finish: Surface finish ("Gloss" or "Matte", default "Gloss")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = CustomVinylStickersShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        width_mm=width_mm,
        height_mm=height_mm,
        finish=finish
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_premium_bookmarks_shopify(
    quantity: int,
    width_mm: int = 55,
    height_mm: int = 200,
    paper_stock: str = "350gsm",
    lamination: str = "Matte"
) -> Dict[str, Any]:
    """
    Calculate Premium Bookmarks quote.
    
    Args:
        quantity: Number of bookmarks
        width_mm: Bookmark width in mm (default 55)
        height_mm: Bookmark height in mm (default 200)
        paper_stock: Paper weight/type (default "350gsm")
        lamination: Lamination type ("Matte", "Gloss", or "" for none, default "Matte")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = PremiumBookmarksShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        width_mm=width_mm,
        height_mm=height_mm,
        paper_stock=paper_stock,
        lamination=lamination
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_selfie_frames_shopify(
    quantity: int,
    width_mm: int = 600,
    height_mm: int = 600,
    material: str = "Foam Core",
    artworks: int = 1
) -> Dict[str, Any]:
    """
    Calculate Selfie Frames quote.
    
    Args:
        quantity: Number of selfie frames
        width_mm: Frame width in mm (default 600)
        height_mm: Frame height in mm (default 600)
        material: Material type ("Foam Core", "Card", default "Foam Core")
        artworks: Number of different designs (default 1)
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = SelfieFramesShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        width_mm=width_mm,
        height_mm=height_mm,
        material=material,
        artworks=artworks
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_luxury_classic_pull_up_banners_shopify(
    quantity: int,
    width_mm: int = 850,
    height_mm: int = 2000,
    material: str = "Premium Vinyl"
) -> Dict[str, Any]:
    """
    Calculate Luxury Classic Pull Up Banners quote.
    
    Args:
        quantity: Number of banners
        width_mm: Banner width in mm (default 850)
        height_mm: Banner height in mm (default 2000)
        material: Material type ("Premium Vinyl", "Standard Vinyl", default "Premium Vinyl")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = LuxuryClassicPullUpBannersShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        width_mm=width_mm,
        height_mm=height_mm,
        material=material
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_stackable_cubes_shopify(
    quantity: int,
    size: str = "300",
    material: str = "Corrugated"
) -> Dict[str, Any]:
    """
    Calculate Stackable Cubes quote.
    
    Args:
        quantity: Number of cubes
        size: Cube edge size in mm (default "300")
        material: Material type ("Corrugated", "Card", default "Corrugated")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = StackableCubesShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        size=size,
        material=material
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }


def calculate_spiral_bound_books_shopify(
    quantity: int,
    pages: int,
    size: str = "A4",
    paper_stock: str = "80gsm"
) -> Dict[str, Any]:
    """
    Calculate Spiral Bound Books quote.
    
    Args:
        quantity: Number of books
        pages: Number of pages per book
        size: Book size ("A4", "A5", default "A4")
        paper_stock: Paper weight/type (default "80gsm")
    
    Returns:
        Dict with total_price, unit_price, cost_per_item, quantity, breakdown, specifications
    """
    calc = SpiralBoundBooksShopifyCalculator()
    result = calc.calculate(
        quantity=quantity,
        pages=pages,
        size=size,
        paper_stock=paper_stock
    )
    
    return {
        "total_price": result.total_price,
        "unit_price": result.unit_price,
        "cost_per_item": result.cost_per_item,
        "quantity": result.quantity,
        "breakdown": result.breakdown,
        "specifications": result.specifications
    }






