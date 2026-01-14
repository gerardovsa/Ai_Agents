"""
Wire Bound Books Shopify Calculator
Exact implementation of Shopify DPO JavaScript formula for Wire Bound Books

Based on: Wire_Spiral_Bound.json specification
Fields: F1-F14 (Quantity, Artworks, Finish Size, Layered Cover Structure, etc.)
"""

import json
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class WireBoundQuoteResult:
    """Result from Wire Bound book calculation"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class WireBoundShopifyCalculator:
    """
    Wire Bound Books Calculator - Exact Shopify DPO Implementation
    
    Features:
    - F1-F14 Shopify field structure
    - Layered cover: Outer PVC + Printed Cover + Celloglaze
    - Separate front/back specifications
    - Thickness-based binding cost tiers (14 tiers)
    - Artworks parameter (F2: 1-50, first free, $15 each additional)
    - Configurable price increase, GST rate, and surcharge
    """
    
    # ============================================================================
    # CONFIGURABLE PRICING VARIABLES (Defaults - overridden by JSON config)
    # ============================================================================
    PRICE_INCREASE_TYPE = "percentage"           # "percentage" or "fixed_amount"
    PRICE_INCREASE_VALUE = Decimal('5')          # 5% (or $5.00 if fixed) - HIDDEN markup
    PRICE_INCREASE_MULTIPLIER = Decimal('1.05')  # Legacy: 5% price increase
    GST_RATE = Decimal('1.10')                   # 10% GST (standard Australian GST)
    SURCHARGE_TYPE = "fixed_amount"              # "percentage" or "fixed_amount"
    SURCHARGE_VALUE = Decimal('44.00')           # $44 surcharge
    SURCHARGE = Decimal('44.00')                 # Legacy: Fixed $44 surcharge
    
    def __init__(self, config_path: str = None, pricing_config_path: str = None):
        """
        Initialize Wire Bound calculator
        
        Args:
            config_path: Optional path to Wire_Spiral_Bound.json config file
            pricing_config_path: Optional path to calculator_pricing_config.json for dynamic pricing
        """
        self.config = self._load_config(config_path) if config_path else None
        
        # Load pricing overrides from JSON config if provided
        if pricing_config_path:
            self._load_pricing_config(pricing_config_path)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data.get('shopify_wire_bound_books', {})
    
    def _load_pricing_config(self, pricing_config_path: str):
        """Load pricing configuration from calculator_pricing_config.json"""
        try:
            with open(pricing_config_path, 'r') as f:
                pricing_data = json.load(f)
            
            # Get this calculator's pricing config
            if 'wire_bound_books' in pricing_data:
                calc_config = pricing_data['wire_bound_books']
                
                # Load price increase
                if 'price_increase' in calc_config:
                    self.PRICE_INCREASE_TYPE = calc_config['price_increase'].get('type', 'percentage')
                    self.PRICE_INCREASE_VALUE = Decimal(str(calc_config['price_increase'].get('value', '5')))
                    
                    # Convert to multiplier format for legacy code compatibility
                    if self.PRICE_INCREASE_TYPE == 'percentage':
                        self.PRICE_INCREASE_MULTIPLIER = Decimal('1') + (self.PRICE_INCREASE_VALUE / Decimal('100'))
                    else:
                        # For fixed amount, store as-is (will be added, not multiplied)
                        self.PRICE_INCREASE_MULTIPLIER = self.PRICE_INCREASE_VALUE
                
                # Load GST rate
                if 'gst_rate' in calc_config:
                    gst_pct = Decimal(str(calc_config['gst_rate'].get('value', '15')))
                    self.GST_RATE = Decimal('1') + (gst_pct / Decimal('100'))
                
                # Load surcharge
                if 'surcharge' in calc_config:
                    self.SURCHARGE_TYPE = calc_config['surcharge'].get('type', 'fixed_amount')
                    self.SURCHARGE_VALUE = Decimal(str(calc_config['surcharge'].get('value', '44')))
                    self.SURCHARGE = self.SURCHARGE_VALUE  # Legacy compatibility
        
        except FileNotFoundError:
            # Config file doesn't exist yet, use class defaults
            pass
    
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
                  ) -> WireBoundQuoteResult:
        """
        Calculate Wire Bound book quote using exact Shopify DPO formula
        
        Args:
            quantity: Number of books (F1)
            artworks: Number of different artworks/designs (F2: 1-50, first free, $15 each)
            finish_size: Book size (F14: A6/DL/A5/A4 Portrait/Landscape)
            outer_front_cover: Clear PVC overlay on front (F3)
            printed_front_cover: Front printed cover stock (F4: 250/300/350GSM Satin)
            front_cover_print: Front cover print type (F5: 1pp/2pp Colour/B&W)
            front_celloglaze: Front cover celloglaze (F6: None/1 Side/2 Sided Gloss/Matt)
            outer_back_cover: Back cover outer layer (F7: None/Clear PVC/Black Leather/Blank)
            printed_back_cover: Back printed cover stock (F8)
            back_cover_print: Back cover print type (F9)
            back_celloglaze: Back cover celloglaze (F10)
            internal_pages: Number of internal pages (F11: 1-500)
            internal_stock: Internal paper stock (F12: Satin/Uncoated Bond)
            internal_print: Internal print type (F13: Full Colour/B&W)
            
        Returns:
            WireBoundQuoteResult with total price, unit price, and breakdown
        """
        
        # Convert parameters to correct types if needed
        quantity = int(quantity) if isinstance(quantity, str) else quantity
        artworks = int(artworks) if isinstance(artworks, str) else artworks
        internal_pages = int(internal_pages) if isinstance(internal_pages, str) else internal_pages
        
        # ========================================================================
        # STEP 1: Calculate Artwork Costs (F2)
        # ========================================================================
        # Formula: First artwork free, $15 per additional artwork
        artwork_cost = Decimal(max(0, (artworks - 1) * 15))
        
        # ========================================================================
        # STEP 2: Determine Finish Size Parameters (F14)
        # ========================================================================
        size_params = self._get_finish_size_params(finish_size)
        imposition = size_params['imposition']  # Books per sheet
        book_width = size_params['width']
        book_height = size_params['height']
        
        # ========================================================================
        # STEP 3: Calculate Front Cover Costs (F3, F4, F5, F6)
        # ========================================================================
        # Outer Front Cover (F3: Clear PVC)
        outer_front_price = Decimal('0.12') if "Clear PVC" in outer_front_cover else Decimal('0')
        
        # Printed Front Cover (F4: 250/300/350GSM Satin)
        front_stock_price = self._get_stock_price(printed_front_cover)
        
        # Front Cover Print (F5: 1pp/2pp Colour/B&W)
        front_print_price = self._get_print_price(front_cover_print)
        
        # Front Celloglaze (F6: None/1 Side/2 Sided Gloss/Matt)
        front_cello_price = self._get_cello_price(front_celloglaze)
        
        # Calculate front cover sheets
        cover_sheets = Decimal(quantity) * Decimal('1.05')  # 5% waste
        
        # Total front cover cost
        front_cover_cost = cover_sheets * (outer_front_price + front_stock_price + 
                                           front_print_price + front_cello_price)
        
        # ========================================================================
        # STEP 4: Calculate Back Cover Costs (F7, F8, F9, F10)
        # ========================================================================
        # Outer Back Cover (F7: None/Clear PVC/Black Leather/Blank)
        outer_back_price = self._get_outer_back_price(outer_back_cover)
        
        # Printed Back Cover (F8)
        back_stock_price = self._get_stock_price(printed_back_cover)
        
        # Back Cover Print (F9)
        back_print_price = self._get_print_price(back_cover_print)
        
        # Back Celloglaze (F10)
        back_cello_price = self._get_cello_price(back_celloglaze)
        
        # Total back cover cost
        back_cover_cost = cover_sheets * (outer_back_price + back_stock_price + 
                                          back_print_price + back_cello_price)
        
        # ========================================================================
        # STEP 5: Calculate Internal/Content Costs (F11, F12, F13)
        # ========================================================================
        # Internal sheets calculation
        internal_sheets = ((Decimal(quantity) * Decimal(internal_pages)) / Decimal(imposition)) * Decimal('1.05')
        
        # Internal stock price (F12)
        internal_stock_price, internal_thickness = self._get_internal_stock_price(internal_stock)
        
        # Internal print price (F13)
        internal_print_price = self._get_internal_print_price(internal_print)
        
        # Total content cost
        content_cost = internal_sheets * (internal_stock_price + internal_print_price)
        
        # ========================================================================
        # STEP 6: Calculate Book Thickness and Wire Binding Cost
        # ========================================================================
        # Calculate total thickness in mm
        cover_thickness = self._get_cover_thickness(printed_front_cover, printed_back_cover,
                                                    outer_front_cover, outer_back_cover)
        internal_total_thickness = Decimal(internal_pages) * internal_thickness
        total_thickness = cover_thickness + internal_total_thickness
        
        # Get wire binding price per book based on thickness (14 tiers)
        wire_price_per_book = self._get_wire_binding_price(total_thickness)
        
        # Adjust for small sizes (A6, DL Landscape, A5 Landscape use HALF wire cost)
        if self._is_small_size(finish_size):
            wire_price_per_book = wire_price_per_book / Decimal('2')
        
        wire_binding_cost = Decimal(quantity) * wire_price_per_book
        
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
        wirebind_per_book = Decimal('1.16')
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
                   wire_binding_cost +
                   punch_cost +
                   cutting_cost +
                   bindery_labor_cost)
        
        # ========================================================================
        # STEP 9: Apply Profit Margin (based on BizCost tiers)
        # ========================================================================
        profit_margin = self._get_profit_margin(biz_cost)
        subtotal = biz_cost + (biz_cost * profit_margin)
        
        # ========================================================================
        # STEP 10: Apply Price Increase (Configurable % or $)
        # ========================================================================
        if self.PRICE_INCREASE_TYPE == "percentage":
            # Percentage: multiply by (1 + percentage)
            multiplier = Decimal('1') + (self.PRICE_INCREASE_VALUE / Decimal('100'))
            subtotal_with_increase = subtotal * multiplier
            price_increase_amount = subtotal * (self.PRICE_INCREASE_VALUE / Decimal('100'))
        else:  # fixed_amount
            # Fixed dollar amount: add directly
            subtotal_with_increase = subtotal + self.PRICE_INCREASE_VALUE
            price_increase_amount = self.PRICE_INCREASE_VALUE
        
        # ========================================================================
        # STEP 11: Apply GST
        # ========================================================================
        subtotal_after_gst = subtotal_with_increase * self.GST_RATE
        gst_amount = subtotal_with_increase * (self.GST_RATE - Decimal('1'))
        
        # ========================================================================
        # STEP 12: Apply Surcharge (Configurable % or $)
        # ========================================================================
        if self.SURCHARGE_TYPE == "percentage":
            # Percentage: multiply by surcharge percentage
            surcharge_amount = subtotal_after_gst * (self.SURCHARGE_VALUE / Decimal('100'))
        else:  # fixed_amount
            # Fixed dollar amount: use directly
            surcharge_amount = self.SURCHARGE_VALUE
        
        total_price = subtotal_after_gst + surcharge_amount
        
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
            'wire_binding_cost': wire_binding_cost,
            'punch_cost': punch_cost,
            'cutting_cost': cutting_cost,
            'bindery_labor_cost': bindery_labor_cost,
            'setup_costs': setup_costs,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin,
            'profit_amount': biz_cost * profit_margin,
            'subtotal': subtotal,
            'price_increase_type': self.PRICE_INCREASE_TYPE,
            'price_increase_value': self.PRICE_INCREASE_VALUE,
            'price_increase_amount': price_increase_amount,
            'subtotal_with_increase': subtotal_with_increase,
            'gst_rate': self.GST_RATE,
            'gst_amount': gst_amount,
            'subtotal_after_gst': subtotal_after_gst,
            'surcharge_type': self.SURCHARGE_TYPE,
            'surcharge_value': self.SURCHARGE_VALUE,
            'surcharge_amount': surcharge_amount,
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
            'wire_price_per_book': float(wire_price_per_book)
        }
        
        return WireBoundQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    # ============================================================================
    # HELPER METHODS
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
        """Check if size qualifies for half wire cost"""
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
        return Decimal('0.14')  # Default 300GSM
    
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
        return Decimal('0.08')  # Default 2pp Colour
    
    def _get_cello_price(self, cello: str) -> Decimal:
        """Get celloglaze price"""
        if "1 Side" in cello:
            return Decimal('0.41')
        elif "2 Sided" in cello:
            return Decimal('0.82')
        return Decimal('0')  # None
    
    def _get_outer_back_price(self, outer_back: str) -> Decimal:
        """Get outer back cover price"""
        if "Clear PVC" in outer_back or "Black Leather" in outer_back or "Blank" in outer_back:
            return Decimal('0.12')
        return Decimal('0')  # None
    
    def _get_internal_stock_price(self, stock: str) -> Tuple[Decimal, Decimal]:
        """Get internal stock price and thickness"""
        stocks = {
            "Satin 128GSM": (Decimal('0.054'), Decimal('0.12')),
            "Satin 150GSM": (Decimal('0.064'), Decimal('0.135')),
            "Uncoated Bond 80GSM": (Decimal('0.075'), Decimal('0.1')),
            "Uncoated Bond 90GSM": (Decimal('0.03'), Decimal('0.11')),
            "Uncoated Bond 100GSM": (Decimal('0.054'), Decimal('0.125'))
        }
        return stocks.get(stock, (Decimal('0.054'), Decimal('0.125')))
    
    def _get_internal_print_price(self, print_type: str) -> Decimal:
        """Get internal print price"""
        if "Full Colour" in print_type or "Full colour" in print_type:
            return Decimal('0.096')
        else:  # Black & White
            return Decimal('0.02')
    
    def _get_cover_thickness(self, front_stock: str, back_stock: str,
                            outer_front: str, outer_back: str) -> Decimal:
        """Calculate total cover thickness"""
        thickness = Decimal('0')
        
        # Front printed cover
        if "250GSM" in front_stock:
            thickness += Decimal('0.3')
        elif "300GSM" in front_stock:
            thickness += Decimal('0.35')
        elif "350GSM" in front_stock:
            thickness += Decimal('0.4')
        
        # Back printed cover
        if "250GSM" in back_stock:
            thickness += Decimal('0.3')
        elif "300GSM" in back_stock:
            thickness += Decimal('0.35')
        elif "350GSM" in back_stock:
            thickness += Decimal('0.4')
        
        # PVC overlays
        if "Clear PVC" in outer_front:
            thickness += Decimal('0.2')
        if "Clear PVC" in outer_back or "Black Leather" in outer_back:
            thickness += Decimal('0.2')
        
        return thickness
    
    def _get_wire_binding_price(self, thickness_mm: Decimal) -> Decimal:
        """
        Get wire binding price per book based on thickness
        Uses 14 price tiers from Shopify specification
        NOTE: Website mistakenly uses SPIRAL tiers for WIRE products (documented bug)
        """
        tiers = [
            (Decimal('4.7'), Decimal('0.1477')),
            (Decimal('5.7'), Decimal('0.156')),
            (Decimal('7.7'), Decimal('0.2146')),
            (Decimal('8.7'), Decimal('0.2344')),
            (Decimal('10.7'), Decimal('0.2958')),
            (Decimal('11.7'), Decimal('0.327')),
            (Decimal('12.7'), Decimal('0.3966')),
            (Decimal('15.7'), Decimal('0.518')),
            (Decimal('18.7'), Decimal('0.565')),
            (Decimal('21.7'), Decimal('0.6936')),
            (Decimal('24.7'), Decimal('0.832')),
            (Decimal('27.7'), Decimal('1.413')),
            (Decimal('32.7'), Decimal('1.75')),
            (Decimal('999'), Decimal('2.111'))
        ]
        
        for max_thickness, price in tiers:
            if thickness_mm <= max_thickness:
                return price
        
        return tiers[-1][1]  # Return highest tier if over maximum
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """
        Get profit margin based on BizCost (NOT quantity)
        Uses 12 tiers from Shopify specification
        """
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
        
        return tiers[-1][1]  # Return lowest margin if over maximum


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create calculator instance
    calc = WireBoundShopifyCalculator()
    
    # Example 1: Standard Wire Bound Book
    print("=" * 80)
    print("EXAMPLE 1: Standard Wire Bound Book")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=500,
        artworks=1,
        finish_size="A5 Portrait",
        outer_front_cover="Clear PVC",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="1 Side Gloss",
        outer_back_cover="Clear PVC",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="1 Side Gloss",
        internal_pages=100,
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Black & White"
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
    print(f"  Wire cost per book: ${result.specifications['wire_price_per_book']:.4f}")
