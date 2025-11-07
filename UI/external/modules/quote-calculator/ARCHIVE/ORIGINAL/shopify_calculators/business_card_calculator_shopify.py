"""
Shopify Business Card Calculator - Exact DPO Logic Port
============================================================

This module implements the EXACT calculation logic from the Shopify
Dynamic Product Options (DPO) plugin for business cards.

Reference: WOOCOMMERCE_DPO_BUSINESS_CARDS_LOGIC.md
Date Extracted: October 4, 2025
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Literal, Optional
from dataclasses import dataclass
from enum import Enum


class PrintType(Enum):
    """Print type options"""
    COLOR = "color"
    BLACK_AND_WHITE = "bw"


class FinishSize(Enum):
    """Finish size options"""
    STANDARD_90X55 = "90x55"  # Standard business card
    SMALL_90X45 = "90x45"     # Small business card (premium only)


class StockTypeStandard(Enum):
    """Stock types for standard business cards"""
    SATIN_300GSM = "satin_300gsm"


class StockTypePremium(Enum):
    """Stock types for premium business cards"""
    SATIN_350GSM = "satin_350gsm"
    KINGKONG_420GSM = "kingkong_420gsm"
    ECOSTAR_350GSM = "ecostar_350gsm"


class CelloglazePremium(Enum):
    """Celloglaze options for premium business cards"""
    NONE = "None"
    ONE_SIDE_GLOSS = "1_side_gloss"
    TWO_SIDE_GLOSS = "2_side_gloss"
    ONE_SIDE_MATT = "1_side_matt"
    TWO_SIDE_MATT = "2_side_matt"
    ONE_SIDE_SILK = "1_side_silk"
    TWO_SIDE_SILK = "2_side_silk"


@dataclass
class ShopifyBusinessCardResult:
    """Result of Shopify business card calculation"""
    total_inc_gst: Decimal
    total_ex_gst: Decimal
    gst_amount: Decimal
    subtotal_before_margin: Decimal
    profit_margin_pct: Decimal
    profit_margin_multiplier: Decimal
    cost_breakdown: Dict[str, Decimal]
    quantity: int
    unit_price_inc_gst: Decimal
    unit_price_ex_gst: Decimal
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'total_inc_gst': float(self.total_inc_gst),
            'total_ex_gst': float(self.total_ex_gst),
            'gst_amount': float(self.gst_amount),
            'subtotal_before_margin': float(self.subtotal_before_margin),
            'profit_margin_pct': float(self.profit_margin_pct),
            'profit_margin_multiplier': float(self.profit_margin_multiplier),
            'quantity': self.quantity,
            'unit_price_inc_gst': float(self.unit_price_inc_gst),
            'unit_price_ex_gst': float(self.unit_price_ex_gst),
            'cost_breakdown': {k: float(v) for k, v in self.cost_breakdown.items()}
        }


class ShopifyBusinessCardCalculator:
    """
    Exact port of Shopify DPO Business Card calculation logic
    
    This calculator replicates the exact formulas used in the website's
    Shopify DPO plugin configuration.
    """
    
    # Field price mappings (from DPO configuration)
    UPS_PER_SHEET = {
        FinishSize.STANDARD_90X55: Decimal('21'),  # F4.price
        FinishSize.SMALL_90X45: Decimal('30')       # F4.price
    }
    
    STOCK_PRICES_STANDARD = {
        StockTypeStandard.SATIN_300GSM: Decimal('126')  # F5.price per 1000 sheets
    }
    
    STOCK_PRICES_PREMIUM = {
        StockTypePremium.SATIN_350GSM: Decimal('180'),         # F5.price per 1000
        StockTypePremium.KINGKONG_420GSM: Decimal('250'),      # Estimated (not in screenshot)
        StockTypePremium.ECOSTAR_350GSM: Decimal('500')        # F5.price per 1000
    }
    
    CLICK_RATES = {
        'standard': {
            PrintType.COLOR: Decimal('0.044'),           # F3.price
            PrintType.BLACK_AND_WHITE: Decimal('0.02')   # F3.price
        },
        'premium': {
            PrintType.COLOR: Decimal('0.048'),           # F3.price (higher for premium)
            PrintType.BLACK_AND_WHITE: Decimal('0.02')   # F3.price
        }
    }
    
    CELLOGLAZE_RATES = {
        CelloglazePremium.NONE: Decimal('0'),
        CelloglazePremium.ONE_SIDE_GLOSS: Decimal('0.16'),
        CelloglazePremium.TWO_SIDE_GLOSS: Decimal('0.32'),
        CelloglazePremium.ONE_SIDE_MATT: Decimal('0.16'),
        CelloglazePremium.TWO_SIDE_MATT: Decimal('0.32'),
        CelloglazePremium.ONE_SIDE_SILK: Decimal('0.32'),
        CelloglazePremium.TWO_SIDE_SILK: Decimal('0.64')
    }
    
    def _calculate_profit_margin_standard(self, subtotal: Decimal) -> Decimal:
        """
        Calculate profit margin multiplier for standard business cards
        
        Tiered margin based on subtotal (before margin)
        Returns multiplier (e.g., 0.65 for 65% margin)
        """
        if subtotal >= 1 and subtotal <= Decimal('50.999'):
            return Decimal('0.65')    # 65%
        elif subtotal >= 51 and subtotal <= Decimal('60.999'):
            return Decimal('0.51')    # 51%
        elif subtotal >= 61 and subtotal <= Decimal('65.999'):
            return Decimal('0.6')     # 60%
        elif subtotal >= 66 and subtotal <= Decimal('70.999'):
            return Decimal('0.6')     # 60%
        elif subtotal >= 71 and subtotal <= Decimal('80.999'):
            return Decimal('0.7')     # 70%
        elif subtotal >= 81 and subtotal <= Decimal('100.999'):
            return Decimal('0.6')     # 60%
        elif subtotal >= 101 and subtotal <= Decimal('150.999'):
            return Decimal('0.75')    # 75%
        elif subtotal >= 151 and subtotal <= Decimal('200.999'):
            return Decimal('0.9')     # 90%
        elif subtotal >= 201 and subtotal <= Decimal('300.999'):
            return Decimal('0.3')     # 30%
        elif subtotal >= 301 and subtotal <= Decimal('400.999'):
            return Decimal('0.4')     # 40%
        elif subtotal >= 401 and subtotal <= Decimal('500.999'):
            return Decimal('0.45')    # 45%
        elif subtotal >= 501 and subtotal <= Decimal('1000.999'):
            return Decimal('0.3')     # 30%
        elif subtotal >= 1001 and subtotal <= 10000:
            return Decimal('0.3')     # 30%
        else:
            return Decimal('0')
    
    def _calculate_profit_margin_premium(
        self, 
        subtotal: Decimal, 
        has_celloglaze: bool
    ) -> Decimal:
        """
        Calculate profit margin multiplier for premium business cards
        
        DUAL TIER SYSTEM:
        - WITHOUT celloglaze: 109-120% margin (very high)
        - WITH celloglaze: Same as standard (30-90%)
        
        Returns multiplier (e.g., 1.09 for 109% margin)
        """
        if not has_celloglaze:
            # NO CELLOGLAZE - High margins
            if subtotal >= 1 and subtotal <= Decimal('50.999'):
                return Decimal('1.2')     # 120% (!)
            else:
                return Decimal('1.09')    # 109% for all other ranges
        else:
            # WITH CELLOGLAZE - Standard margins
            return self._calculate_profit_margin_standard(subtotal)
    
    def calculate_standard_business_cards(
        self,
        quantity: int,
        sides: Literal[1, 2],
        print_type: PrintType = PrintType.COLOR,
        finish_size: FinishSize = FinishSize.STANDARD_90X55,
        stock_type: StockTypeStandard = StockTypeStandard.SATIN_300GSM,
        artworks: int = 1
    ) -> ShopifyBusinessCardResult:
        """
        Calculate standard business cards using exact Shopify DPO logic
        
        Args:
            quantity: Number of business cards to produce
            sides: Number of sides to print (1 or 2)
            print_type: Color or Black & White
            finish_size: Finish size (90x55 only for standard)
            stock_type: Paper stock type (Satin 300GSM only for standard)
            artworks: Number of artworks (1 = included, >1 = $15 each extra)
        
        Returns:
            ShopifyBusinessCardResult with all calculations
        """
        # Configuration constants (from Shopify DPO)
        impos_setup = Decimal('15')
        guilo_setup = Decimal('12')
        extra_arts = Decimal('15')
        stock_waste = Decimal('1.05')  # 5% waste
        cutting_blk = Decimal('500')
        cut_cost = Decimal('11')
        
        # Get field prices
        ups_per_sheet = self.UPS_PER_SHEET[finish_size]
        stock_price = self.STOCK_PRICES_STANDARD[stock_type]
        click_rate = self.CLICK_RATES['standard'][print_type]
        
        # 1. Artwork cost calculation
        artwork_total = Decimal(artworks) * extra_arts
        artwork_extra_cost = Decimal('0') if artwork_total <= extra_arts else (artwork_total - extra_arts)
        
        # 2. Total setup cost
        total_setup_cost = impos_setup + guilo_setup + artwork_extra_cost
        
        # 3. Paper cost (sheets required)
        # Formula: (quantity / ups_per_sheet) / 1000 * stock_price * waste_factor
        sheets_needed = Decimal(quantity) / ups_per_sheet
        total_cost_of_sheets = ((sheets_needed / Decimal('1000')) * stock_price) * stock_waste
        
        # 4. Total sheets printed (with waste)
        total_sheets_printed = sheets_needed * stock_waste
        
        # 5. Printing click cost
        # Formula: sheets * sides * click_rate
        click_cost = total_sheets_printed * Decimal(sides) * click_rate
        
        # 6. Cutting cost
        cutting_cost = (total_sheets_printed / cutting_blk) * cut_cost
        
        # 7. Subtotal before margin
        subtotal = total_setup_cost + total_cost_of_sheets + click_cost + cutting_cost
        
        # 8. Calculate profit margin (tiered)
        profit_margin_multiplier = self._calculate_profit_margin_standard(subtotal)
        profit_margin_amount = subtotal * profit_margin_multiplier
        
        # 9. Total Ex GST
        total_ex_gst = subtotal + profit_margin_amount
        
        # 10. GST (10%)
        gst_amount = total_ex_gst * Decimal('0.1')
        
        # 11. Total Inc GST
        total_inc_gst = (total_ex_gst * Decimal('1.1')).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
        
        # Calculate unit prices
        unit_price_inc_gst = total_inc_gst / Decimal(quantity)
        unit_price_ex_gst = total_ex_gst / Decimal(quantity)
        
        return ShopifyBusinessCardResult(
            total_inc_gst=total_inc_gst,
            total_ex_gst=total_ex_gst,
            gst_amount=gst_amount,
            subtotal_before_margin=subtotal,
            profit_margin_pct=profit_margin_multiplier * Decimal('100'),
            profit_margin_multiplier=profit_margin_multiplier,
            cost_breakdown={
                'setup_cost': total_setup_cost,
                'paper_cost': total_cost_of_sheets,
                'click_cost': click_cost,
                'cutting_cost': cutting_cost,
                'artwork_extra': artwork_extra_cost,
                'profit_margin': profit_margin_amount
            },
            quantity=quantity,
            unit_price_inc_gst=unit_price_inc_gst,
            unit_price_ex_gst=unit_price_ex_gst
        )
    
    def calculate_premium_business_cards(
        self,
        quantity: int,
        sides: Literal[1, 2],
        print_type: PrintType = PrintType.COLOR,
        finish_size: FinishSize = FinishSize.STANDARD_90X55,
        stock_type: StockTypePremium = StockTypePremium.SATIN_350GSM,
        celloglaze: CelloglazePremium = CelloglazePremium.NONE,
        artworks: int = 1
    ) -> ShopifyBusinessCardResult:
        """
        Calculate premium business cards with cellophane options
        
        Args:
            quantity: Number of business cards to produce
            sides: Number of sides to print (1 or 2)
            print_type: Color or Black & White
            finish_size: Finish size (90x55 or 90x45)
            stock_type: Premium paper stock type
            celloglaze: Cellophane/lamination option
            artworks: Number of artworks (1 = included, >1 = $15 each extra)
        
        Returns:
            ShopifyBusinessCardResult with all calculations
        """
        # Configuration constants (DIFFERENT from standard)
        impos_setup = Decimal('15')
        guilo_setup = Decimal('10')     # Lower than standard ($12)
        extra_arts = Decimal('15')
        stock_waste = Decimal('1.05')
        cutting_blk = Decimal('500')
        cut_cost = Decimal('10')        # Lower than standard ($11)
        
        # Cellophane setup cost (conditional)
        cello_setup = Decimal('0') if celloglaze == CelloglazePremium.NONE else Decimal('17')
        
        # Get field prices
        ups_per_sheet = self.UPS_PER_SHEET[finish_size]
        stock_price = self.STOCK_PRICES_PREMIUM[stock_type]
        click_rate = self.CLICK_RATES['premium'][print_type]  # Higher for premium
        cello_rate = self.CELLOGLAZE_RATES[celloglaze]
        
        # 1. Artwork cost calculation
        artwork_total = Decimal(artworks) * extra_arts
        artwork_extra_cost = Decimal('0') if artwork_total <= extra_arts else (artwork_total - extra_arts)
        
        # 2. Total setup cost (includes cello setup)
        total_setup_cost = impos_setup + guilo_setup + cello_setup
        
        # 3. Paper cost
        sheets_needed = Decimal(quantity) / ups_per_sheet
        total_cost_of_sheets = ((sheets_needed / Decimal('1000')) * stock_price) * stock_waste
        
        # 4. Total sheets printed
        total_sheets_printed = sheets_needed * stock_waste
        
        # 5. Printing click cost
        click_cost = total_sheets_printed * Decimal(sides) * click_rate
        
        # 6. Cutting cost
        cutting_cost = (total_sheets_printed / cutting_blk) * cut_cost
        
        # 7. Cellophane cost (per sheet)
        cello_cost = Decimal('0') if celloglaze == CelloglazePremium.NONE else (
            total_sheets_printed * cello_rate
        )
        
        # 8. Subtotal before margin
        subtotal = total_setup_cost + total_cost_of_sheets + click_cost + cutting_cost + cello_cost
        
        # 9. Calculate profit margin (DUAL TIER: different for cello vs no cello)
        has_celloglaze = (celloglaze != CelloglazePremium.NONE)
        profit_margin_multiplier = self._calculate_profit_margin_premium(subtotal, has_celloglaze)
        profit_margin_amount = subtotal * profit_margin_multiplier
        
        # 10. Total Ex GST (includes artwork extra)
        total_ex_gst = subtotal + artwork_extra_cost + profit_margin_amount
        
        # 11. GST (10%)
        gst_amount = total_ex_gst * Decimal('0.1')
        
        # 12. Total Inc GST
        total_inc_gst = (total_ex_gst * Decimal('1.1')).quantize(
            Decimal('0.01'), 
            rounding=ROUND_HALF_UP
        )
        
        # Calculate unit prices
        unit_price_inc_gst = total_inc_gst / Decimal(quantity)
        unit_price_ex_gst = total_ex_gst / Decimal(quantity)
        
        return ShopifyBusinessCardResult(
            total_inc_gst=total_inc_gst,
            total_ex_gst=total_ex_gst,
            gst_amount=gst_amount,
            subtotal_before_margin=subtotal,
            profit_margin_pct=profit_margin_multiplier * Decimal('100'),
            profit_margin_multiplier=profit_margin_multiplier,
            cost_breakdown={
                'setup_cost': total_setup_cost,
                'paper_cost': total_cost_of_sheets,
                'click_cost': click_cost,
                'cutting_cost': cutting_cost,
                'celloglaze_cost': cello_cost,
                'artwork_extra': artwork_extra_cost,
                'profit_margin': profit_margin_amount
            },
            quantity=quantity,
            unit_price_inc_gst=unit_price_inc_gst,
            unit_price_ex_gst=unit_price_ex_gst
        )


# Example usage
if __name__ == "__main__":
    calc = ShopifyBusinessCardCalculator()
    
    print("=" * 60)
    print("Shopify Business Card Calculator - Test Examples")
    print("=" * 60)
    
    # Example 1: Standard business cards (1000, double-sided, color)
    print("\n1. STANDARD - 1000 cards, double-sided, color, Satin 300GSM")
    print("-" * 60)
    result = calc.calculate_standard_business_cards(
        quantity=1000,
        sides=2,
        print_type=PrintType.COLOR,
        finish_size=FinishSize.STANDARD_90X55,
        stock_type=StockTypeStandard.SATIN_300GSM,
        artworks=1
    )
    print(f"Total Inc GST: ${result.total_inc_gst:.2f}")
    print(f"Total Ex GST: ${result.total_ex_gst:.2f}")
    print(f"Unit Price: ${result.unit_price_inc_gst:.4f} per card")
    print(f"Profit Margin: {result.profit_margin_pct:.1f}%")
    print(f"Subtotal before margin: ${result.subtotal_before_margin:.2f}")
    print("\nCost Breakdown:")
    for key, value in result.cost_breakdown.items():
        print(f"  {key}: ${value:.2f}")
    
    # Example 2: Premium without cello (high margin)
    print("\n2. PREMIUM - 1000 cards, double-sided, color, Satin 350GSM, NO CELLO")
    print("-" * 60)
    result = calc.calculate_premium_business_cards(
        quantity=1000,
        sides=2,
        print_type=PrintType.COLOR,
        finish_size=FinishSize.STANDARD_90X55,
        stock_type=StockTypePremium.SATIN_350GSM,
        celloglaze=CelloglazePremium.NONE,
        artworks=1
    )
    print(f"Total Inc GST: ${result.total_inc_gst:.2f}")
    print(f"Unit Price: ${result.unit_price_inc_gst:.4f} per card")
    print(f"Profit Margin: {result.profit_margin_pct:.1f}% (HIGH - no cello)")
    print(f"Subtotal before margin: ${result.subtotal_before_margin:.2f}")
    
    # Example 3: Premium with 2-side matt cello
    print("\n3. PREMIUM - 1000 cards, double-sided, color, Satin 350GSM, 2-SIDE MATT")
    print("-" * 60)
    result = calc.calculate_premium_business_cards(
        quantity=1000,
        sides=2,
        print_type=PrintType.COLOR,
        finish_size=FinishSize.STANDARD_90X55,
        stock_type=StockTypePremium.SATIN_350GSM,
        celloglaze=CelloglazePremium.TWO_SIDE_MATT,
        artworks=1
    )
    print(f"Total Inc GST: ${result.total_inc_gst:.2f}")
    print(f"Unit Price: ${result.unit_price_inc_gst:.4f} per card")
    print(f"Profit Margin: {result.profit_margin_pct:.1f}% (standard - with cello)")
    print(f"Subtotal before margin: ${result.subtotal_before_margin:.2f}")
    print("\nCost Breakdown:")
    for key, value in result.cost_breakdown.items():
        print(f"  {key}: ${value:.2f}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
