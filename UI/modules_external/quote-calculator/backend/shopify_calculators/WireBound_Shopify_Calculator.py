"""
Wire Bound Books Calculator - Shopify DPO Formula (Exact Match)
=================================================================

REWRITTEN: January 26, 2026
FORMULA SOURCE: Website JavaScript (NON-TRADE version)

Formula: (BizCost + (BizCost × ProfitMargin)) × 1.15 + $44

Key Formula Components:
- Cover sheets: (quantity / imposition) × 1.05
- Internal sheets: ((quantity × pages / 2) / imposition) × 1.05
- Wire binding: 14 thickness tiers, HALF cost for small sizes
- Profit margin: 12 BizCost tiers (90% down to 41%)
- Final pricing: subtotal × 1.15 + $44 surcharge
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class WireBoundQuoteResult:
    """Result from Wire Bound Books calculation"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict
    specifications: Dict


class WireBoundShopifyCalculator:
    """
    Shopify Wire Bound Books Calculator - Exact Website Formula
    
    Matches website JavaScript (NON-TRADE version) exactly:
    - F1-F14 field structure
    - Layered cover: Outer + Printed + Celloglaze
    - 14 wire binding thickness tiers
    - (BizCost + profit) × 1.15 + $44
    """
    
    # ========================================================================
    # CONSTANTS (from website JavaScript)
    # ========================================================================
    GUILO_SETUP = Decimal('12')
    IMPOS_SETUP = Decimal('15')
    STOCK_WASTE = Decimal('1.05')
    EXTRA_ARTS = Decimal('15')
    CUTTING_BLK = Decimal('500')
    CUT_COST = Decimal('11')
    PUNCH_SETUP = Decimal('15')
    WIREBIND_PER_BOOK = Decimal('1.16')
    BINDERY_LABOR_PER_HOUR = Decimal('70')
    PUNCH_SHEETS_PER_HOUR = Decimal('15000')
    
    # Final pricing multiplier (GST included)
    FINAL_MULTIPLIER = Decimal('1.15')  # 15% GST
    SURCHARGE = Decimal('44.00')
    
    def __init__(self, config_path: str = None):
        """Initialize Wire Bound calculator"""
        self.config = self._load_config(config_path) if config_path else None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data.get('shopify_wire_bound_books', {})
    
    def calculate(self,
                  quantity: int,                    # F1
                  artworks: int = 1,                # F2 (art)
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
        Calculate Wire Bound book quote using exact Shopify website formula
        
        Website Formula (NON-TRADE):
        var subTotal = (BizCost + (BizCost × profitMargin));
        var total = subTotal × 1.15;
        Run Always: total + 44
        """
        
        # Convert to Decimal for precision
        quantity = Decimal(str(quantity))
        artworks = Decimal(str(artworks))
        internal_pages = Decimal(str(internal_pages))
        
        # ====================================================================
        # STEP 1: Get Finish Size Parameters (F14)
        # ====================================================================
        size_params = self._get_finish_size_params(finish_size)
        imposition = Decimal(str(size_params['imposition']))  # F14.price
        book_width = size_params['width']
        book_height = size_params['height']
        
        # ====================================================================
        # STEP 2: Calculate Artwork Costs
        # ====================================================================
        # var _a = {art} * {extraArts};
        # var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});
        _a = artworks * self.EXTRA_ARTS
        _a2 = Decimal('0') if _a <= self.EXTRA_ARTS else (_a - self.EXTRA_ARTS)
        
        # ====================================================================
        # STEP 3: Calculate Cello Setup Cost
        # ====================================================================
        # var celloSetup = ({F6} == 'None' && {F10} == 'None') ? 0 : 25;
        has_cello = (front_celloglaze != "None" or back_celloglaze != "None")
        cello_setup = Decimal('25') if has_cello else Decimal('0')
        
        # ====================================================================
        # STEP 4: Calculate Front Cover Costs (F3, F4, F5, F6)
        # ====================================================================
        # Outer Front Cover (F3: PVC per book)
        # var outFront = ({F3.price} * {F1});
        outer_front_price = self._get_outer_front_price(outer_front_cover)
        out_front = outer_front_price * quantity
        
        # Front Cover Sheets
        # var totalFrontCoverSheets = ({F4} == 'None' ? 0 : (({F1} / {F14.price}) * {stockWaste}));
        if printed_front_cover == "None":
            total_front_cover_sheets = Decimal('0')
        else:
            total_front_cover_sheets = (quantity / imposition) * self.STOCK_WASTE
        
        # Front Cover Stock (F4)
        front_stock_price = self._get_stock_price(printed_front_cover)
        
        # Front Cover Print Click Cost (F5)
        # var coverClickCost = ({F5.price} * {totalFrontCoverSheets});
        front_print_price = self._get_print_price(front_cover_print)
        cover_click_cost = front_print_price * total_front_cover_sheets
        
        # Total Front Cover Cost
        # var totalFrontCoverCost = ({totalFrontCoverSheets} * {F4.price}) + {coverClickCost};
        total_front_cover_cost = (total_front_cover_sheets * front_stock_price) + cover_click_cost
        
        # Front Celloglaze (F6)
        # var FrontcelloCost = ({F6} == 'None' ? 0 : ({totalFrontCoverSheets} * {F6.price}));
        front_cello_price = self._get_cello_price(front_celloglaze)
        front_cello_cost = Decimal('0') if front_celloglaze == "None" else (total_front_cover_sheets * front_cello_price)
        
        # ====================================================================
        # STEP 5: Calculate Back Cover Costs (F7, F8, F9, F10)
        # ====================================================================
        # Outer Back Cover (F7: PVC/Leather per book)
        # var outBack = ({F7.price} * {F1});
        outer_back_price = self._get_outer_back_price(outer_back_cover)
        out_back = outer_back_price * quantity
        
        # Back Cover Sheets
        # var totalBackCoverSheets = ({F8} == 'None' ? 0 : (({F1} / {F14.price}) * {stockWaste}));
        if printed_back_cover == "None":
            total_back_cover_sheets = Decimal('0')
        else:
            total_back_cover_sheets = (quantity / imposition) * self.STOCK_WASTE
        
        # Back Cover Stock (F8)
        back_stock_price = self._get_stock_price(printed_back_cover)
        
        # Back Cover Print Click Cost (F9)
        # var coverClickCostBack = ({F9.price} * {totalBackCoverSheets});
        back_print_price = self._get_print_price(back_cover_print)
        cover_click_cost_back = back_print_price * total_back_cover_sheets
        
        # Total Back Cover Cost (NOTE: Website uses F4.price for back cover too!)
        # var totalBackCoverCost = ({totalBackCoverSheets} * {F4.price}) + {coverClickCostBack};
        total_back_cover_cost = (total_back_cover_sheets * front_stock_price) + cover_click_cost_back
        
        # Back Celloglaze (F10)
        # var BackcelloCost = ({F10} == 'None' ? 0 : ({totalBackCoverSheets} * {F10.price}));
        back_cello_price = self._get_cello_price(back_celloglaze)
        back_cello_cost = Decimal('0') if back_celloglaze == "None" else (total_back_cover_sheets * back_cello_price)
        
        # ====================================================================
        # STEP 6: Calculate Internal/Content Costs (F11, F12, F13)
        # ====================================================================
        # Internal Content Sheets
        # var totalContentSheets = ((({F1} * {F11}) / 2) / {F14.price}) * {stockWaste};
        total_content_sheets = (((quantity * internal_pages) / Decimal('2')) / imposition) * self.STOCK_WASTE
        
        # Internal Stock Price (F12)
        internal_stock_price, internal_thickness = self._get_internal_stock_price(internal_stock)
        
        # Internal Print Click Cost (F13)
        # var contentClickCost = ({totalContentSheets} * {F13.price});
        internal_print_price = self._get_internal_print_price(internal_print)
        content_click_cost = total_content_sheets * internal_print_price
        
        # Total Content Cost
        # var totalContentCost = ({totalContentSheets} * {F12.price}) + {contentClickCost};
        total_content_cost = (total_content_sheets * internal_stock_price) + content_click_cost
        
        # ====================================================================
        # STEP 7: Calculate Total Print Cost
        # ====================================================================
        # var totalPrintCost = {totalFrontCoverCost} + {totalBackCoverCost} + {FrontcelloCost} + {BackcelloCost} + {outFront} + {outBack} + {totalContentCost};
        total_print_cost = (total_front_cover_cost + total_back_cover_cost + 
                           front_cello_cost + back_cello_cost + 
                           out_front + out_back + total_content_cost)
        
        # ====================================================================
        # STEP 8: Calculate Total Setup Costs
        # ====================================================================
        # var totalSetupCosts = {guiloSetup} + {imposSetup} + {punchSetup} + {celloSetup} + {_a2};
        total_setup_costs = self.GUILO_SETUP + self.IMPOS_SETUP + self.PUNCH_SETUP + cello_setup + _a2
        
        # ====================================================================
        # STEP 9: Calculate Book Thickness and Wire Binding Cost
        # ====================================================================
        # var bookSheets = {F11} / 2;
        book_sheets = internal_pages / Decimal('2')
        
        # var contentSheetThickness = ...
        content_sheet_thickness = internal_thickness
        
        # var bookThickness = {bookSheets} * {contentSheetThickness};
        book_thickness = book_sheets * content_sheet_thickness
        
        # Get wire binding price per book (14 tiers)
        # var pricePerRing = ...
        price_per_ring = self._get_wire_binding_price(book_thickness)
        
        # Check if small size (half wire cost)
        # var priceofwire = ({F14} == 'A6 Portrait' || {F14} == 'A6 Landscape' || {F14} == 'DL Landscape' || {F14} == 'A5 Landscape') ? 
        #     ({pricePerRing} * {F1}) / 2 : ({pricePerRing} * {F1});
        is_small = self._is_small_size(finish_size)
        if is_small:
            price_of_wire = (price_per_ring * quantity) / Decimal('2')
        else:
            price_of_wire = price_per_ring * quantity
        
        # ====================================================================
        # STEP 10: Calculate Punch Cost
        # ====================================================================
        # var baseValue = ({F1} * {F11}) / 2;
        base_value = (quantity * internal_pages) / Decimal('2')
        
        # var additionalF8 = ({F8} == 'None' ? 0 : {F1});
        additional_f8 = Decimal('0') if printed_back_cover == "None" else quantity
        
        # var additionalF4 = ({F4} == 'None' ? 0 : {F1});
        additional_f4 = Decimal('0') if printed_front_cover == "None" else quantity
        
        # var totalPunch = {baseValue} + {additionalF8} + {additionalF4};
        total_punch = base_value + additional_f8 + additional_f4
        
        # var sheetsToPunch = {totalPunch} * {stockWaste};
        sheets_to_punch = total_punch * self.STOCK_WASTE
        
        # var punchPrice = ({sheetsToPunch} / {punchsheetsperhour}) * {binderyLaborperhour};
        punch_price = (sheets_to_punch / self.PUNCH_SHEETS_PER_HOUR) * self.BINDERY_LABOR_PER_HOUR
        
        # ====================================================================
        # STEP 11: Calculate Cutting Cost
        # ====================================================================
        # var cuttingCost = (({totalContentSheets} + {totalFrontCoverSheets} + {totalBackCoverSheets}) / {cuttingBlk}) * {cutCost};
        cutting_cost = ((total_content_sheets + total_front_cover_sheets + total_back_cover_sheets) / self.CUTTING_BLK) * self.CUT_COST
        
        # ====================================================================
        # STEP 12: Calculate BizCost
        # ====================================================================
        # var BizCost = {totalPrintCost} + {totalSetupCosts} + {priceofwire} + {punchPrice} + {cuttingCost} + ({F1} * {wirebindperbook});
        biz_cost = (total_print_cost + total_setup_costs + price_of_wire + 
                   punch_price + cutting_cost + (quantity * self.WIREBIND_PER_BOOK))
        
        # ====================================================================
        # STEP 13: Calculate Profit Margin (12 BizCost tiers)
        # ====================================================================
        profit_margin = self._get_profit_margin(biz_cost)
        
        # ====================================================================
        # STEP 14: Calculate Subtotal
        # ====================================================================
        # var subTotal = ({BizCost} + ({BizCost} * {profitMargin}));
        subtotal = biz_cost + (biz_cost * profit_margin)
        
        # ====================================================================
        # STEP 15: Calculate Final Total (×1.15 + $44)
        # ====================================================================
        # var total = {subTotal} * 1.15;
        # Run Always: {total} + 44
        total_before_surcharge = subtotal * self.FINAL_MULTIPLIER
        total_price = total_before_surcharge + self.SURCHARGE
        
        # ====================================================================
        # STEP 16: Calculate Unit Price
        # ====================================================================
        unit_price = total_price / quantity
        
        # ====================================================================
        # Build Breakdown
        # ====================================================================
        breakdown = {
            'artwork_cost': _a2,
            'out_front': out_front,
            'total_front_cover_sheets': total_front_cover_sheets,
            'front_stock_cost': total_front_cover_sheets * front_stock_price,
            'front_print_cost': cover_click_cost,
            'front_cello_cost': front_cello_cost,
            'total_front_cover_cost': total_front_cover_cost,
            'out_back': out_back,
            'total_back_cover_sheets': total_back_cover_sheets,
            'back_stock_cost': total_back_cover_sheets * front_stock_price,
            'back_print_cost': cover_click_cost_back,
            'back_cello_cost': back_cello_cost,
            'total_back_cover_cost': total_back_cover_cost,
            'total_content_sheets': total_content_sheets,
            'content_stock_cost': total_content_sheets * internal_stock_price,
            'content_print_cost': content_click_cost,
            'total_content_cost': total_content_cost,
            'total_print_cost': total_print_cost,
            'guilo_setup': self.GUILO_SETUP,
            'impos_setup': self.IMPOS_SETUP,
            'punch_setup': self.PUNCH_SETUP,
            'cello_setup': cello_setup,
            'total_setup_costs': total_setup_costs,
            'book_thickness': book_thickness,
            'price_per_ring': price_per_ring,
            'is_small_size': is_small,
            'price_of_wire': price_of_wire,
            'sheets_to_punch': sheets_to_punch,
            'punch_price': punch_price,
            'cutting_cost': cutting_cost,
            'bindery_labor': quantity * self.WIREBIND_PER_BOOK,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin,
            'profit_amount': biz_cost * profit_margin,
            'subtotal': subtotal,
            'gst_multiplier': self.FINAL_MULTIPLIER,
            'total_before_surcharge': total_before_surcharge,
            'surcharge': self.SURCHARGE,
            'total_price': total_price,
            'unit_price': unit_price
        }
        
        specifications = {
            'quantity': int(quantity),
            'artworks': int(artworks),
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
            'internal_pages': int(internal_pages),
            'internal_stock': internal_stock,
            'internal_print': internal_print,
            'book_thickness_mm': float(book_thickness),
            'wire_price_per_book': float(price_per_ring)
        }
        
        return WireBoundQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            quantity=int(quantity),
            breakdown=breakdown,
            specifications=specifications
        )
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
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
    
    def _get_outer_front_price(self, outer_front: str) -> Decimal:
        """Get outer front cover price (F3)"""
        if "Clear PVC" in outer_front:
            return Decimal('0.12')
        return Decimal('0')
    
    def _get_stock_price(self, stock: str) -> Decimal:
        """Get price for printed cover stock (F4/F8)"""
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
        """Get print price for cover (F5/F9)"""
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
        """Get celloglaze price (F6/F10)"""
        if "1 Side" in cello:
            return Decimal('0.41')
        elif "2 Sided" in cello or "2 Side" in cello:
            return Decimal('0.82')
        return Decimal('0')  # None
    
    def _get_outer_back_price(self, outer_back: str) -> Decimal:
        """Get outer back cover price (F7)"""
        if "Clear PVC" in outer_back or "Black Leather" in outer_back or "Blank" in outer_back:
            return Decimal('0.12')
        return Decimal('0')  # None
    
    def _get_internal_stock_price(self, stock: str) -> Tuple[Decimal, Decimal]:
        """Get internal stock price and thickness (F12)"""
        stocks = {
            "Satin 128GSM": (Decimal('0.054'), Decimal('0.12')),
            "Satin 150GSM": (Decimal('0.064'), Decimal('0.135')),
            "Uncoated Bond 80GSM": (Decimal('0.075'), Decimal('0.1')),
            "Uncoated Bond 90GSM": (Decimal('0.03'), Decimal('0.11')),
            "Uncoated Bond 100GSM": (Decimal('0.054'), Decimal('0.125'))
        }
        return stocks.get(stock, (Decimal('0.054'), Decimal('0.125')))
    
    def _get_internal_print_price(self, print_type: str) -> Decimal:
        """Get internal print price (F13)"""
        if "Full Colour" in print_type or "Full colour" in print_type:
            return Decimal('0.096')
        else:  # Black & White
            return Decimal('0.02')
    
    def _get_wire_binding_price(self, thickness_mm: Decimal) -> Decimal:
        """
        Get wire binding price per book based on thickness (14 tiers)
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
        
        return tiers[-1][1]  # Return highest tier
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """
        Get profit margin based on BizCost (12 tiers)
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
        
        return tiers[-1][1]  # Return lowest margin


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    calc = WireBoundShopifyCalculator()
    
    # Test 1: A4 Portrait Basic (should be $781.24, not $1125.25)
    print("=" * 80)
    print("TEST 1: A4 Portrait Basic - 100 books, 50 pages")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=100,
        artworks=1,
        internal_pages=50,
        finish_size="A4 Portrait",
        printed_front_cover="300GSM Satin",
        front_cover_print="2pp Colour",
        front_celloglaze="None",
        outer_front_cover="Not Required",
        printed_back_cover="300GSM Satin",
        back_cover_print="2pp Colour",
        back_celloglaze="None",
        outer_back_cover="None",
        internal_stock="Uncoated Bond 100GSM",
        internal_print="Black & White"
    )
    
    print(f"\nWebsite Price: $781.24")
    print(f"Backend Price: ${result.total_price:,.2f}")
    print(f"Unit Price: ${result.unit_price:.2f} per book")
    print(f"\nBreakdown:")
    print(f"  BizCost: ${result.breakdown['biz_cost']:,.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_rate']*100:.0f}%")
    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
    print(f"  ×1.15 GST: ${result.breakdown['total_before_surcharge']:,.2f}")
    print(f"  +$44 Surcharge: ${result.breakdown['surcharge']:,.2f}")
    print(f"  TOTAL: ${result.total_price:,.2f}")
