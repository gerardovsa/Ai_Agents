"""
Perfect Bound Books Shopify Calculator
Exact implementation of Shopify DPO JavaScript formula for Perfect Bound Books

Based on: Perfect_Bound_books.json specification
Fields: F1-F11 (Simpler structure than Wire/Spiral)
Key Differences: 10% GST only (no surcharge), BizCost-based profit margins, quantity-based binding
"""

import json
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass


@dataclass
class PerfectBoundQuoteResult:
    """Result from Perfect Bound book calculation"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class PerfectBoundShopifyCalculator:
    """
    Perfect Bound Books Calculator - Exact Shopify DPO Implementation
    
    Features:
    - F1-F11 Shopify field structure (simpler than Wire/Spiral)
    - Simple cover structure (no layered PVC overlays)
    - Quantity-based binding cost tiers (8 tiers)
    - BizCost-based profit margins (12 tiers)
    - Proof requirements option ($0 digital / $40 physical)
    - Configurable price increase, GST rate (10% standard), and surcharge
    
    Key Differences from Wire/Spiral:
    - NO artworks parameter
    - NO layered cover (no separate front/back, no PVC overlays)
    - 10% GST standard (SAME as Wire/Spiral)
    - NO $44 surcharge (vs Wire/Spiral $44)
    - NO 5% price increase (vs Wire/Spiral 5% hidden markup)
    - Quantity-based binding (vs thickness-based for Wire/Spiral)
    - BizCost-based profit margins (vs same margin tiers)
    """
    
    # ============================================================================
    # CONFIGURABLE PRICING VARIABLES (Matches Wire/Spiral structure)
    # ============================================================================
    PRICE_INCREASE_TYPE = "percentage"           # "percentage" or "fixed_amount"
    PRICE_INCREASE_VALUE = Decimal('0')          # 0% for Perfect Bound (no hidden markup)
    PRICE_INCREASE_MULTIPLIER = Decimal('1.00')  # NO price increase for Perfect Bound
    GST_RATE = Decimal('1.10')                   # 10% GST (standard Australian GST - SAME as Wire/Spiral)
    SURCHARGE_TYPE = "fixed_amount"              # "percentage" or "fixed_amount"
    SURCHARGE_VALUE = Decimal('0.00')            # $0 surcharge (DIFFERENT from Wire/Spiral $44)
    SURCHARGE = Decimal('0.00')                  # Legacy: NO surcharge for Perfect Bound
    
    def __init__(self, config_path: str = None):
        """
        Initialize Perfect Bound calculator
        
        Args:
            config_path: Optional path to Perfect_Bound_books.json config file
        """
        self.config = self._load_config(config_path) if config_path else None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data
    
    def calculate(self,
                  quantity: int,                    # F1
                  printed_pages: int,               # F2
                  proof_requirements: str = "Digital Emailed Proof",  # F3
                  cover_stock: str = "Satin 300GSM",  # F4
                  cover_print_type: str = "2 side colour (4pp)",  # F5
                  celloglaze: str = "None",         # F6
                  finish_size: str = "A5 Portrait", # F8
                  content_print_type: str = "Black & White",  # F10
                  content_stock_type: str = "Uncoated Bond 100GSM"  # F11
                  ) -> PerfectBoundQuoteResult:
        """
        Calculate Perfect Bound book quote using exact Shopify DPO formula
        
        Args:
            quantity: Number of books (F1: 1-20,000)
            printed_pages: Number of internal pages (F2: 40-800, must be divisible by 4)
            proof_requirements: Proof type (F3: Digital $0 / Physical $40)
            cover_stock: Cover paper stock (F4: Satin 300GSM default)
            cover_print_type: Cover printing (F5: 1 side/2 side colour/B&W)
            celloglaze: Cover finish (F6: None/Gloss/Matt outside only)
            finish_size: Book size (F8: A5 Portrait/A4 Portrait/A4 Landscape/US Trade)
            content_print_type: Internal printing (F10: Full Colour/Black & White)
            content_stock_type: Internal paper stock (F11: Satin 128/150GSM, Uncoated 80/90/100GSM)
            
        Returns:
            PerfectBoundQuoteResult with total price, unit price, and breakdown
        """
        
        # Convert parameters to correct types if needed
        quantity = int(quantity) if isinstance(quantity, str) else quantity
        printed_pages = int(printed_pages) if isinstance(printed_pages, str) else printed_pages
        
        # Validate pages divisible by 4
        if printed_pages % 4 != 0:
            raise ValueError(f"Pages must be divisible by 4. Got: {printed_pages}")
        
        # ========================================================================
        # STEP 1: Setup Costs
        # ========================================================================
        guilo_setup = Decimal('10')
        impos_setup = Decimal('50')
        binder_setup = Decimal('35')
        
        # Cello setup (F6)
        cello_setup = Decimal('0') if celloglaze == "None" else Decimal('16')
        
        total_setup_cost = impos_setup + guilo_setup + cello_setup + binder_setup
        
        # ========================================================================
        # STEP 2: Proof Cost (F3)
        # ========================================================================
        proof_cost = Decimal('40') if "Physical" in proof_requirements else Decimal('0')
        
        # ========================================================================
        # STEP 3: Cover Calculations (F4, F5, F6)
        # ========================================================================
        stock_waste = Decimal('1.05')  # 5% waste allowance
        
        # Cover sheets needed
        total_cover_sheets_a3 = Decimal(quantity) * stock_waste
        
        # Cover stock price (F4)
        cover_stock_price = self._get_cover_stock_price(cover_stock)
        
        # Cover print price (F5)
        cover_print_price = self._get_cover_print_price(cover_print_type)
        
        # Cover click cost
        cover_click_cost = cover_print_price * total_cover_sheets_a3
        
        # Total cover cost
        total_cover_cost = (total_cover_sheets_a3 * cover_stock_price) + cover_click_cost
        
        # ========================================================================
        # STEP 4: Celloglaze Cost (F6)
        # ========================================================================
        cello_price = self._get_cello_price(celloglaze)
        cello_cost = Decimal('0') if celloglaze == "None" else (total_cover_sheets_a3 * cello_price)
        
        # ========================================================================
        # STEP 5: Content/Internal Calculations (F8, F10, F11)
        # ========================================================================
        # Finish size imposition (F8)
        imposition = self._get_finish_size_imposition(finish_size)
        
        # Content sheets needed
        total_content_sheets = ((Decimal(quantity) * Decimal(printed_pages)) / Decimal(imposition)) * stock_waste
        
        # Content stock price (F11)
        content_stock_price = self._get_content_stock_price(content_stock_type)
        
        # Content print price (F10)
        content_print_price = self._get_content_print_price(content_print_type)
        
        # Content click cost
        content_click_cost = total_content_sheets * content_print_price
        
        # Total content cost
        total_content_cost = (total_content_sheets * content_stock_price) + content_click_cost
        
        # ========================================================================
        # STEP 6: Cutting Cost
        # ========================================================================
        total_sheets_printed = total_content_sheets + total_cover_sheets_a3
        cutting_block = Decimal('500')
        cut_cost = Decimal('11')
        cutting_cost = (total_sheets_printed / cutting_block) * cut_cost
        
        # ========================================================================
        # STEP 7: Binding Cost (Quantity-based tiers)
        # ========================================================================
        bind_cost_per_book = self._get_bind_cost_per_book(quantity)
        trimmer_per_book = Decimal('0.3')
        bind_run_cost = Decimal(quantity) * (bind_cost_per_book + trimmer_per_book)
        
        # ========================================================================
        # STEP 8: Calculate Business Cost (BizCost)
        # ========================================================================
        biz_cost = (total_setup_cost + 
                   total_cover_cost + 
                   total_content_cost + 
                   cutting_cost + 
                   cello_cost + 
                   bind_run_cost + 
                   proof_cost)
        
        # ========================================================================
        # STEP 9: Apply Profit Margin (based on BizCost tiers - CRITICAL)
        # ========================================================================
        profit_margin_rate = self._get_profit_margin(biz_cost)
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount
        
        # ========================================================================
        # STEP 10: Calculate Extra Books (Overs)
        # ========================================================================
        extra_books_qty = self._get_extra_books(quantity)
        unit_price_before_gst = sub_total / Decimal(quantity)
        overs_book_price = unit_price_before_gst * Decimal(extra_books_qty)
        
        sub_total_2 = sub_total + overs_book_price
        
        # ========================================================================
        # STEP 11: Apply Price Increase (Configurable % or $ - Currently 0%)
        # ========================================================================
        if self.PRICE_INCREASE_TYPE == "percentage":
            # Percentage: multiply by (1 + percentage)
            multiplier = Decimal('1') + (self.PRICE_INCREASE_VALUE / Decimal('100'))
            subtotal_with_increase = sub_total_2 * multiplier
            price_increase_amount = sub_total_2 * (self.PRICE_INCREASE_VALUE / Decimal('100'))
        else:  # fixed_amount
            # Fixed dollar amount: add directly
            subtotal_with_increase = sub_total_2 + self.PRICE_INCREASE_VALUE
            price_increase_amount = self.PRICE_INCREASE_VALUE
        
        # ========================================================================
        # STEP 12: Apply GST (10% standard Australian GST)
        # ========================================================================
        subtotal_after_gst = subtotal_with_increase * self.GST_RATE
        gst_amount = subtotal_with_increase * (self.GST_RATE - Decimal('1'))
        
        # ========================================================================
        # STEP 13: Apply Surcharge (Configurable % or $ - Currently $0)
        # ========================================================================
        if self.SURCHARGE_TYPE == "percentage":
            # Percentage: multiply by surcharge percentage
            surcharge_amount = subtotal_after_gst * (self.SURCHARGE_VALUE / Decimal('100'))
        else:  # fixed_amount
            # Fixed dollar amount: use directly
            surcharge_amount = self.SURCHARGE_VALUE
        
        total_price = subtotal_after_gst + surcharge_amount
        
        # ========================================================================
        # STEP 14: Calculate Final Unit Price
        # ========================================================================
        unit_price = total_price / Decimal(quantity)
        
        # ========================================================================
        # Build Detailed Breakdown
        # ========================================================================
        breakdown = {
            'setup_costs': total_setup_cost,
            'proof_cost': proof_cost,
            'cover_cost': total_cover_cost,
            'content_cost': total_content_cost,
            'cello_cost': cello_cost,
            'cutting_cost': cutting_cost,
            'binding_cost': bind_run_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'extra_books_qty': Decimal(extra_books_qty),
            'overs_cost': overs_book_price,
            'subtotal_with_overs': sub_total_2,
            # Price increase configuration (0% for Perfect Bound)
            'price_increase_type': self.PRICE_INCREASE_TYPE,
            'price_increase_value': self.PRICE_INCREASE_VALUE,
            'price_increase_amount': price_increase_amount,
            'subtotal_with_increase': subtotal_with_increase,
            # GST configuration (10% standard Australian GST)
            'gst_rate': self.GST_RATE,
            'gst_amount': gst_amount,
            'subtotal_after_gst': subtotal_after_gst,
            # Surcharge configuration ($0 for Perfect Bound)
            'surcharge_type': self.SURCHARGE_TYPE,
            'surcharge_value': self.SURCHARGE_VALUE,
            'surcharge_amount': surcharge_amount,
            # Final pricing
            'total_price': total_price,
            'unit_price': unit_price,
            'cover_sheets': total_cover_sheets_a3,
            'content_sheets': total_content_sheets,
            'total_sheets': total_sheets_printed
        }
        
        specifications = {
            'quantity': quantity,
            'printed_pages': printed_pages,
            'proof_requirements': proof_requirements,
            'cover_stock': cover_stock,
            'cover_print_type': cover_print_type,
            'celloglaze': celloglaze,
            'finish_size': finish_size,
            'content_print_type': content_print_type,
            'content_stock_type': content_stock_type,
            'bind_cost_per_book': float(bind_cost_per_book),
            'extra_books_included': extra_books_qty
        }
        
        return PerfectBoundQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_cover_stock_price(self, stock: str) -> Decimal:
        """Get cover stock price (F4)"""
        # Currently only Satin 300GSM in spec, but ready for expansion
        if "300GSM" in stock:
            return Decimal('0.14')
        return Decimal('0.14')  # Default
    
    def _get_cover_print_price(self, print_type: str) -> Decimal:
        """Get cover print price (F5)"""
        if "1 side colour" in print_type:
            return Decimal('0.048')
        elif "2 side colour" in print_type:
            return Decimal('0.096')
        elif "1 side Black" in print_type:
            return Decimal('0.01')
        elif "2 side Black" in print_type:
            return Decimal('0.02')
        return Decimal('0.096')  # Default 2 side colour
    
    def _get_cello_price(self, cello: str) -> Decimal:
        """Get celloglaze price (F6)"""
        if "Gloss outside" in cello or "Matt outside" in cello:
            return Decimal('0.19')
        return Decimal('0')  # None
    
    def _get_finish_size_imposition(self, finish_size: str) -> int:
        """Get imposition (books per sheet) for finish size (F8)"""
        sizes = {
            "A5 Portrait": 8,
            "A4 Portrait": 4,
            "A4 Landscape": 4,
            "US Trade - 152mm x 229mm": 4
        }
        return sizes.get(finish_size, 8)
    
    def _get_content_stock_price(self, stock: str) -> Decimal:
        """Get content stock price (F11)"""
        stocks = {
            "Satin 128GSM": Decimal('0.054'),
            "Satin 150GSM": Decimal('0.064'),
            "Uncoated Bond 80GSM": Decimal('0.0322'),
            "Uncoated Bond 90GSM": Decimal('0.0354'),
            "Uncoated Bond 100GSM": Decimal('0.0392')
        }
        return stocks.get(stock, Decimal('0.0392'))
    
    def _get_content_print_price(self, print_type: str) -> Decimal:
        """Get content print price (F10)"""
        if "Full Colour" in print_type:
            return Decimal('0.088')
        else:  # Black & White
            return Decimal('0.015')
    
    def _get_bind_cost_per_book(self, quantity: int) -> Decimal:
        """
        Get binding cost per book based on quantity (8 tiers)
        DIFFERENT from Wire/Spiral which use thickness-based tiers
        """
        tiers = [
            (250, Decimal('1.25')),
            (500, Decimal('1.0')),
            (1000, Decimal('0.9')),
            (1500, Decimal('0.85')),
            (2000, Decimal('0.8')),
            (3000, Decimal('0.75')),
            (10000, Decimal('0.7')),
            (999999, Decimal('0.7'))
        ]
        
        for max_qty, rate in tiers:
            if quantity <= max_qty:
                return rate
        
        return tiers[-1][1]
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """
        Get profit margin based on BizCost (12 tiers)
        NOTE: Based on BUSINESS COST, not quantity (critical difference)
        """
        tiers = [
            (Decimal('500'), Decimal('0.4')),
            (Decimal('1000'), Decimal('0.4')),
            (Decimal('1500'), Decimal('0.6')),
            (Decimal('2000'), Decimal('0.72')),
            (Decimal('2500'), Decimal('0.75')),
            (Decimal('3000'), Decimal('0.75')),
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
    
    def _get_extra_books(self, quantity: int) -> int:
        """Get number of extra books (overs) based on quantity (8 tiers)"""
        tiers = [
            (100, 4),
            (250, 8),
            (500, 12),
            (1000, 20),
            (2000, 50),
            (3000, 75),
            (5000, 100),
            (20000, 150)
        ]
        
        for max_qty, extra in tiers:
            if quantity <= max_qty:
                return extra
        
        return tiers[-1][1]


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create calculator instance
    calc = PerfectBoundShopifyCalculator()
    
    # Example 1: Standard Perfect Bound Book
    print("=" * 80)
    print("EXAMPLE 1: Standard Perfect Bound Book (B&W Novel)")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=500,
        printed_pages=200,
        proof_requirements="Digital Emailed Proof",
        cover_stock="Satin 300GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="Matt outside only",
        finish_size="A5 Portrait",
        content_print_type="Black & White",
        content_stock_type="Uncoated Bond 100GSM"
    )
    
    print(f"\nTotal Price: ${result.total_price:,.2f}")
    print(f"Unit Price: ${result.unit_price:.2f} per book")
    print(f"\nBreakdown:")
    print(f"  Business Cost: ${result.breakdown['biz_cost']:,.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_rate']*100:.0f}%")
    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
    print(f"  Extra Books ({result.breakdown['extra_books_qty']:.0f}): ${result.breakdown['overs_cost']:,.2f}")
    print(f"  Price Increase ({(calc.PRICE_INCREASE_MULTIPLIER-1)*100:.0f}%): ${result.breakdown['subtotal_with_increase']:,.2f}")
    print(f"  GST ({(calc.GST_RATE-1)*100:.0f}%): ${result.breakdown['gst_amount']:,.2f}")
    print(f"  Surcharge: ${result.breakdown['surcharge']:,.2f}")
    print(f"  TOTAL: ${result.total_price:,.2f}")
    
    print(f"\nSpecifications:")
    print(f"  Quantity: {result.specifications['quantity']} + {result.specifications['extra_books_included']} overs")
    print(f"  Pages: {result.specifications['printed_pages']}")
    print(f"  Size: {result.specifications['finish_size']}")
    print(f"  Cover: {result.specifications['cover_stock']} - {result.specifications['celloglaze']}")
    print(f"  Content: {result.specifications['content_stock_type']} - {result.specifications['content_print_type']}")
    print(f"  Bind cost per book: ${result.specifications['bind_cost_per_book']:.2f}")
    
    # Example 2: Full Color Magazine
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Full Color Magazine with Physical Proof")
    print("=" * 80)
    
    result2 = calc.calculate(
        quantity=250,
        printed_pages=48,
        proof_requirements="Physical Unbound Proof",
        cover_stock="Satin 300GSM",
        cover_print_type="2 side colour (4pp)",
        celloglaze="Gloss outside only",
        finish_size="A4 Portrait",
        content_print_type="Full Colour",
        content_stock_type="Satin 128GSM"
    )
    
    print(f"\nTotal Price: ${result2.total_price:,.2f}")
    print(f"Unit Price: ${result2.unit_price:.2f} per book")
    print(f"Includes: {result2.specifications['extra_books_included']} extra books + Physical Proof ($40)")
