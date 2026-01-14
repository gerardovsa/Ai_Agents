"""
Spiral Bound Books Shopify Calculator
Exact implementation of Shopify DPO JavaScript formula for Spiral Bound Books

Based on: Wire_Spiral_Bound.json specification
Fields: F1-F14 (Quantity, Artworks, Finish Size, Layered Cover Structure, etc.)
NOTE: Uses different binding price tiers than Wire Bound (17 tiers vs 14 tiers)
"""

import json
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class SpiralBoundQuoteResult:
    """Result from Spiral Bound book calculation"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SpiralBoundShopifyCalculator:
    """
    Spiral Bound Books Calculator - Exact Shopify DPO Implementation
    
    Features:
    - F1-F14 Shopify field structure (same as Wire Bound)
    - Layered cover: Outer PVC + Printed Cover + Celloglaze
    - Separate front/back specifications
    - Thickness-based binding cost tiers (17 tiers - DIFFERENT from Wire)
    - Artworks parameter (F2: 1-50, first free, $15 each additional)
    - Configurable price increase, GST rate, and surcharge
    """
    
    # ============================================================================
    # CONFIGURABLE PRICING VARIABLES
    # ============================================================================
    PRICE_INCREASE_MULTIPLIER = Decimal('1.05')  # 5% price increase (HIDDEN markup)
    GST_RATE = Decimal('1.10')                   # 10% GST (standard Australian GST)
    SURCHARGE = Decimal('44.00')                 # Fixed $44 surcharge (Spiral Bound specific - SAME as Wire)
    
    def __init__(self, config_path: str = None):
        """
        Initialize Spiral Bound calculator
        
        Args:
            config_path: Optional path to Wire_Spiral_Bound.json config file
        """
        self.config = self._load_config(config_path) if config_path else None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data.get('shopify_spiral_bound_books', {})
    
    def calculate(self,
                  quantity: int,                    # F1
                  artworks: int = 1,                # F2
                  finish_size: str = "A5 Portrait", # F14
                  outer_front_cover: str = "Not Required",  # F3
                  printed_front_cover: str = "300GSM Satin",  # F4
                  front_cover_print: str = "2pp Colour",  # F5
                  front_celloglaze: str = "None",   # F6
                  outer_back_cover: str = "None",   # F7
                  printed_back_cover: str = "300GSM Satin",  # F8
                  back_cover_print: str = "2pp Colour",  # F9
                  back_celloglaze: str = "None",    # F10
                  internal_pages: int = 100,        # F11
                  internal_stock: str = "Uncoated Bond 100GSM",  # F12
                  internal_print: str = "Black & White"  # F13
                  ) -> SpiralBoundQuoteResult:
        """
        Calculate Spiral Bound book quote using exact Shopify DPO formula
        
        All parameters same as Wire Bound - see WireBound_Shopify_Calculator.py for details
        Main difference: Uses 17 spiral binding price tiers instead of 14 wire tiers
        """
        
        # Convert parameters to correct types if needed
        quantity = int(quantity) if isinstance(quantity, str) else quantity
        artworks = int(artworks) if isinstance(artworks, str) else artworks
        internal_pages = int(internal_pages) if isinstance(internal_pages, str) else internal_pages
        
        # ========================================================================
        # STEP 1: Calculate Artwork Costs (F2)
        # ========================================================================
        artwork_cost = Decimal(max(0, (artworks - 1) * 15))
        
        # ========================================================================
        # STEP 2: Determine Finish Size Parameters (F14)
        # ========================================================================
        size_params = self._get_finish_size_params(finish_size)
        imposition = size_params['imposition']
        book_width = size_params['width']
        book_height = size_params['height']
        
        # ========================================================================
        # STEP 3: Calculate Front Cover Costs (F3, F4, F5, F6)
        # ========================================================================
        outer_front_price = Decimal('0.12') if "Clear PVC" in outer_front_cover else Decimal('0')
        front_stock_price = self._get_stock_price(printed_front_cover)
        front_print_price = self._get_print_price(front_cover_print)
        front_cello_price = self._get_cello_price(front_celloglaze)
        
        cover_sheets = Decimal(quantity) * Decimal('1.05')  # 5% waste
        front_cover_cost = cover_sheets * (outer_front_price + front_stock_price + 
                                           front_print_price + front_cello_price)
        
        # ========================================================================
        # STEP 4: Calculate Back Cover Costs (F7, F8, F9, F10)
        # ========================================================================
        outer_back_price = self._get_outer_back_price(outer_back_cover)
        back_stock_price = self._get_stock_price(printed_back_cover)
        back_print_price = self._get_print_price(back_cover_print)
        back_cello_price = self._get_cello_price(back_celloglaze)
        
        back_cover_cost = cover_sheets * (outer_back_price + back_stock_price + 
                                          back_print_price + back_cello_price)
        
        # ========================================================================
        # STEP 5: Calculate Internal/Content Costs (F11, F12, F13)
        # ========================================================================
        internal_sheets = ((Decimal(quantity) * Decimal(internal_pages)) / Decimal(imposition)) * Decimal('1.05')
        internal_stock_price, internal_thickness = self._get_internal_stock_price(internal_stock)
        internal_print_price = self._get_internal_print_price(internal_print)
        content_cost = internal_sheets * (internal_stock_price + internal_print_price)
        
        # ========================================================================
        # STEP 6: Calculate Book Thickness and SPIRAL Binding Cost
        # ========================================================================
        cover_thickness = self._get_cover_thickness(printed_front_cover, printed_back_cover,
                                                    outer_front_cover, outer_back_cover)
        internal_total_thickness = Decimal(internal_pages) * internal_thickness
        total_thickness = cover_thickness + internal_total_thickness
        
        # Get SPIRAL binding price per book based on thickness (17 tiers - DIFFERENT from Wire)
        spiral_price_per_book = self._get_spiral_binding_price(total_thickness)
        
        # Adjust for small sizes (A6, DL Landscape, A5 Landscape use HALF spiral cost)
        if self._is_small_size(finish_size):
            spiral_price_per_book = spiral_price_per_book / Decimal('2')
        
        spiral_binding_cost = Decimal(quantity) * spiral_price_per_book
        
        # ========================================================================
        # STEP 7: Calculate Setup and Processing Costs
        # ========================================================================
        guilo_setup = Decimal('12')
        impos_setup = Decimal('15')
        punch_setup = Decimal('15')
        
        # Punch cost calculation
        bindery_labor_per_hour = Decimal('70')
        punch_sheets_per_hour = Decimal('15000')
        total_sheets_to_punch = internal_sheets + cover_sheets
        punch_hours = total_sheets_to_punch / punch_sheets_per_hour
        punch_cost = punch_hours * bindery_labor_per_hour
        
        # Cutting cost
        cutting_block = Decimal('500')
        cut_cost = Decimal('11')
        total_sheets = internal_sheets + cover_sheets
        cutting_cost = (total_sheets / cutting_block) * cut_cost
        
        # Cello setup cost
        has_cello = (front_celloglaze != "None" or back_celloglaze != "None")
        cello_setup = Decimal('25') if has_cello else Decimal('0')
        
        # Per-book labor cost
        wirebind_per_book = Decimal('1.16')  # Same constant name in Shopify for spiral too
        bindery_labor_cost = Decimal(quantity) * wirebind_per_book
        
        # ========================================================================
        # STEP 8: Calculate Business Cost (BizCost)
        # ========================================================================
        setup_costs = guilo_setup + impos_setup + punch_setup + cello_setup
        
        biz_cost = (setup_costs + 
                   artwork_cost +
                   front_cover_cost + 
                   back_cover_cost + 
                   content_cost + 
                   spiral_binding_cost +
                   punch_cost +
                   cutting_cost +
                   bindery_labor_cost)
        
        # ========================================================================
        # STEP 9: Apply Profit Margin (based on BizCost tiers)
        # ========================================================================
        profit_margin = self._get_profit_margin(biz_cost)
        subtotal = biz_cost + (biz_cost * profit_margin)
        
        # ========================================================================
        # STEP 10: Apply Price Increase
        # ========================================================================
        subtotal_with_increase = subtotal * self.PRICE_INCREASE_MULTIPLIER
        
        # ========================================================================
        # STEP 11: Apply GST and Surcharge (Spiral Bound Specific - SAME as Wire)
        # ========================================================================
        # Spiral Bound: 15% GST + $44 surcharge (SAME as Wire Bound)
        total_price = (subtotal_with_increase * self.GST_RATE) + self.SURCHARGE
        
        # ========================================================================
        # STEP 12: Calculate Unit Price
        # ========================================================================
        unit_price = total_price / Decimal(quantity)
        
        # ========================================================================
        # Build Detailed Breakdown
        # ========================================================================
        breakdown = {
            'artwork_cost': artwork_cost,
            'front_cover_cost': front_cover_cost,
            'back_cover_cost': back_cover_cost,
            'content_cost': content_cost,
            'spiral_binding_cost': spiral_binding_cost,
            'punch_cost': punch_cost,
            'cutting_cost': cutting_cost,
            'bindery_labor_cost': bindery_labor_cost,
            'setup_costs': setup_costs,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin,
            'profit_amount': biz_cost * profit_margin,
            'subtotal': subtotal,
            'price_increase_multiplier': self.PRICE_INCREASE_MULTIPLIER,
            'subtotal_with_increase': subtotal_with_increase,
            'gst_rate': self.GST_RATE,
            'gst_amount': subtotal_with_increase * (self.GST_RATE - Decimal('1')),
            'surcharge': self.SURCHARGE,
            'total_price': total_price,
            'unit_price': unit_price,
            'book_thickness_mm': total_thickness
        }
        
        specifications = {
            'quantity': quantity,
            'artworks': artworks,
            'finish_size': finish_size,
            'book_dimensions': f"{book_width}mm × {book_height}mm",
            'outer_front_cover': outer_front_cover,
            'printed_front_cover': printed_front_cover,
            'front_cover_print': front_cover_print,
            'front_celloglaze': front_celloglaze,
            'outer_back_cover': outer_back_cover,
            'printed_back_cover': printed_back_cover,
            'back_cover_print': back_cover_print,
            'back_celloglaze': back_celloglaze,
            'internal_pages': internal_pages,
            'internal_stock': internal_stock,
            'internal_print': internal_print,
            'total_thickness_mm': float(total_thickness),
            'spiral_price_per_book': float(spiral_price_per_book)
        }
        
        return SpiralBoundQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    # ============================================================================
    # HELPER METHODS (Same as Wire Bound except spiral binding tier)
    # ============================================================================
    
    def _get_finish_size_params(self, finish_size: str) -> Dict:
        """Get dimensions and imposition for finish size"""
        sizes = {
            "A6 Portrait": {'width': 105, 'height': 148, 'imposition': 8},
            "A6 Landscape": {'width': 148, 'height': 105, 'imposition': 8},
            "DL Portrait": {'width': 99, 'height': 210, 'imposition': 6},
            "DL Landscape": {'width': 210, 'height': 99, 'imposition': 6},
            "A5 Portrait": {'width': 148, 'height': 210, 'imposition': 4},
            "A5 Landscape": {'width': 210, 'height': 148, 'imposition': 4},
            "A4 Portrait": {'width': 210, 'height': 297, 'imposition': 2},
            "A4 Landscape": {'width': 297, 'height': 210, 'imposition': 2}
        }
        return sizes.get(finish_size, sizes["A5 Portrait"])
    
    def _is_small_size(self, finish_size: str) -> bool:
        """Check if size qualifies for half spiral cost"""
        small_sizes = ["A6 Portrait", "A6 Landscape", "DL Landscape", "A5 Landscape"]
        return finish_size in small_sizes
    
    def _get_stock_price(self, stock: str) -> Decimal:
        """Get price for printed cover stock"""
        if "250GSM" in stock:
            return Decimal('0.09')
        elif "300GSM" in stock:
            return Decimal('0.14')
        elif "350GSM" in stock:
            return Decimal('0.18')
        elif "None" in stock or stock.lower() == "none":
            return Decimal('0')
        return Decimal('0.14')
    
    def _get_print_price(self, print_type: str) -> Decimal:
        """Get print price for cover"""
        if "1pp Colour" in print_type:
            return Decimal('0.04')
        elif "2pp Colour" in print_type:
            return Decimal('0.08')
        elif "1pp Black" in print_type:
            return Decimal('0.01')
        elif "2pp Black" in print_type:
            return Decimal('0.02')
        return Decimal('0.08')
    
    def _get_cello_price(self, cello: str) -> Decimal:
        """Get celloglaze price"""
        if "1 Side" in cello:
            return Decimal('0.41')
        elif "2 Sided" in cello:
            return Decimal('0.82')
        return Decimal('0')
    
    def _get_outer_back_price(self, outer_back: str) -> Decimal:
        """Get outer back cover price"""
        if "Clear PVC" in outer_back or "Black Leather" in outer_back or "Blank" in outer_back:
            return Decimal('0.12')
        return Decimal('0')
    
    def _get_internal_stock_price(self, stock: str) -> Tuple[Decimal, Decimal]:
        """Get internal stock price and thickness (includes additional stock options)"""
        stocks = {
            "Satin 128GSM": (Decimal('0.054'), Decimal('0.12')),
            "Satin 150GSM": (Decimal('0.064'), Decimal('0.135')),
            "Uncoated Bond 80GSM": (Decimal('0.075'), Decimal('0.1')),
            "Uncoated Bond 90GSM": (Decimal('0.03'), Decimal('0.11')),
            "Uncoated Bond 100GSM": (Decimal('0.054'), Decimal('0.125')),
            "Uncoated Bond 140GSM": (Decimal('0.072'), Decimal('0.2')),
            "Satin 300GSM": (Decimal('0.14'), Decimal('0.4'))
        }
        return stocks.get(stock, (Decimal('0.054'), Decimal('0.125')))
    
    def _get_internal_print_price(self, print_type: str) -> Decimal:
        """Get internal print price"""
        if "Full Colour" in print_type or "Full colour" in print_type:
            return Decimal('0.096')
        else:
            return Decimal('0.02')
    
    def _get_cover_thickness(self, front_stock: str, back_stock: str,
                            outer_front: str, outer_back: str) -> Decimal:
        """Calculate total cover thickness"""
        thickness = Decimal('0')
        
        if "250GSM" in front_stock:
            thickness += Decimal('0.3')
        elif "300GSM" in front_stock:
            thickness += Decimal('0.35')
        elif "350GSM" in front_stock:
            thickness += Decimal('0.4')
        
        if "250GSM" in back_stock:
            thickness += Decimal('0.3')
        elif "300GSM" in back_stock:
            thickness += Decimal('0.35')
        elif "350GSM" in back_stock:
            thickness += Decimal('0.4')
        
        if "Clear PVC" in outer_front:
            thickness += Decimal('0.2')
        if "Clear PVC" in outer_back or "Black Leather" in outer_back:
            thickness += Decimal('0.2')
        
        return thickness
    
    def _get_spiral_binding_price(self, thickness_mm: Decimal) -> Decimal:
        """
        Get SPIRAL binding price per book based on thickness
        Uses 17 price tiers from Shopify specification (DIFFERENT from Wire's 14 tiers)
        NOTE: Website mistakenly uses WIRE tiers for SPIRAL products (documented bug)
        """
        tiers = [
            (Decimal('8'), Decimal('0.13065')),
            (Decimal('10'), Decimal('0.157')),
            (Decimal('12'), Decimal('0.2242')),
            (Decimal('14'), Decimal('0.25')),
            (Decimal('16'), Decimal('0.2895')),
            (Decimal('18'), Decimal('0.321')),
            (Decimal('20'), Decimal('0.4141')),
            (Decimal('22'), Decimal('0.516')),
            (Decimal('24'), Decimal('0.563')),
            (Decimal('28'), Decimal('0.6392')),
            (Decimal('31'), Decimal('0.7172')),
            (Decimal('33'), Decimal('0.7558')),
            (Decimal('35'), Decimal('0.829')),
            (Decimal('38'), Decimal('0.9042')),
            (Decimal('41'), Decimal('1.201')),
            (Decimal('48'), Decimal('1.248')),
            (Decimal('53'), Decimal('1.248')),
            (Decimal('999'), Decimal('1.248'))
        ]
        
        for max_thickness, price in tiers:
            if thickness_mm <= max_thickness:
                return price
        
        return tiers[-1][1]
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """Get profit margin based on BizCost (SAME as Wire Bound)"""
        tiers = [
            (Decimal('500'), Decimal('0.9')),
            (Decimal('1000'), Decimal('0.9')),
            (Decimal('1500'), Decimal('0.8')),
            (Decimal('2000'), Decimal('0.75')),
            (Decimal('2500'), Decimal('0.7')),
            (Decimal('3000'), Decimal('0.67')),
            (Decimal('4000'), Decimal('0.65')),
            (Decimal('5000'), Decimal('0.55')),
            (Decimal('7500'), Decimal('0.52')),
            (Decimal('10000'), Decimal('0.47')),
            (Decimal('15000'), Decimal('0.42')),
            (Decimal('100000'), Decimal('0.41'))
        ]
        
        for max_cost, margin in tiers:
            if biz_cost <= max_cost:
                return margin
        
        return tiers[-1][1]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create calculator instance
    calc = SpiralBoundShopifyCalculator()
    
    # Example 1: Standard Spiral Bound Book
    print("=" * 80)
    print("EXAMPLE 1: Standard Spiral Bound Book")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=1000,
        artworks=1,
        finish_size="A4 Portrait",
        outer_front_cover="Clear PVC",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="1 Side Matt",
        outer_back_cover="Black Leather grain",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="1 Side Matt",
        internal_pages=150,
        internal_stock="Satin 150GSM",
        internal_print="Full Colour"
    )
    
    print(f"\nTotal Price: ${result.total_price:,.2f}")
    print(f"Unit Price: ${result.unit_price:.2f} per book")
    print(f"\nBreakdown:")
    print(f"  Business Cost: ${result.breakdown['biz_cost']:,.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_rate']*100:.0f}%")
    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
    print(f"  Price Increase ({(calc.PRICE_INCREASE_MULTIPLIER-1)*100:.0f}%): ${result.breakdown['subtotal_with_increase']:,.2f}")
    print(f"  GST ({(calc.GST_RATE-1)*100:.0f}%): ${result.breakdown['gst_amount']:,.2f}")
    print(f"  Surcharge: ${result.breakdown['surcharge']:,.2f}")
    print(f"  TOTAL: ${result.total_price:,.2f}")
    
    print(f"\nSpecifications:")
    print(f"  Quantity: {result.specifications['quantity']}")
    print(f"  Size: {result.specifications['finish_size']} ({result.specifications['book_dimensions']})")
    print(f"  Pages: {result.specifications['internal_pages']}")
    print(f"  Thickness: {result.specifications['total_thickness_mm']:.2f}mm")
    print(f"  Spiral cost per book: ${result.specifications['spiral_price_per_book']:.4f}")
