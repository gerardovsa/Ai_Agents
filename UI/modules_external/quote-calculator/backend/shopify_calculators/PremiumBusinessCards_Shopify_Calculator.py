"""
Premium Business Cards Shopify Calculator
Exact implementation of Shopify JavaScript formula for Premium Business Cards

Based on: Business_Cards_Premium_Shopify.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: F1-F7 (Shopify-specific Premium card structure with celloglaze options)
Key Features: Dual profit structure, premium stocks, luxury finishes, double GST application
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PremiumBusinessCardsShopifyQuoteResult:
    """Result from Premium Business Cards Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_card: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class PremiumBusinessCardsShopifyCalculator:
    """
    Premium Business Cards Shopify Calculator - Exact Shopify JavaScript Implementation
    
    ⚠️ SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE ⚠️
    
    Features:
    - F1-F7 Shopify field structure
    - DUAL profit margin structure (higher margins without lamination)
    - Premium celloglaze options (Gloss, Matt, SILK FEEL Matt)
    - Premium stocks (Satin 350GSM, King Kong 420GSM, EcoStar 350GSM)
    - Artwork setup costs (first free, $15 per extra)
    - Cards-per-sheet calculation (21 or 30 based on size)
    - DOUBLE GST APPLICATION (Shopify-specific quirk: Total * 1.1 * 1.1)
    
    Key Differences from WooCommerce:
    - Double GST multiplication (apparent error in original Shopify code)
    - Shopify-specific field naming and structure
    - Different profit margin tiers
    - Artwork cost added AFTER margin calculation
    """
    
    # Configuration file path
    CONFIG_FILE = "Business_Cards_Premium_Shopify.json"
    
    def __init__(self, config_path: str = None):
        """
        Initialize Premium Business Cards Shopify calculator
        
        Args:
            config_path: Optional path to Business_Cards_Premium_Shopify.json config file
        """
        if config_path:
            self.config = self._load_config(config_path)
        else:
            # Try to load from default location
            default_path = Path(__file__).parent / self.CONFIG_FILE
            if default_path.exists():
                self.config = self._load_config(str(default_path))
            else:
                self.config = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data.get('shopify_premium_business_cards', {})
    
    def calculate(self,
                  quantity: int,                                  # F1: 250-10,000
                  print_sides: str = "Single side print",         # F2: Single/Double
                  print_type: str = "Colour",                     # F3: Colour/Black & White
                  finish_size: str = "90mm x 55mm",               # F4: 90x55mm or 90x45mm
                  paper_stock: str = "Satin 350GSM",              # F5: Satin/King Kong/EcoStar
                  artworks: int = 1,                              # F6: Number of designs
                  celloglaze: str = "1 Side Gloss"                # F7: Lamination type
                  ) -> PremiumBusinessCardsShopifyQuoteResult:
        """
        Calculate Premium Business Cards Shopify quote using exact Shopify JavaScript formula
        
        Args:
            quantity: Number of cards (F1: 250, 500, 1000, 2000, 5000, 10000)
            print_sides: Printing sides (F2: "Single side print" / "Double side print")
            print_type: Print color mode (F3: "Colour" / "Black & White")
            finish_size: Card size (F4: "90mm x 55mm" / "90mm x 45mm")
            paper_stock: Paper stock (F5: "Satin 350GSM" / "King Kong High Bulk" / "EcoStar 350GSM Uncoated")
            artworks: Number of artwork designs (F6: 1-50, default 1)
            celloglaze: Lamination type (F7: "None" / "1 Side Gloss" / "2 Side Gloss" / "1 Side Matt" / 
                       "2 Side Matt" / "1 Side SILK FEEL Matt" / "2 Side SILK FEEL Matt")
            
        Returns:
            PremiumBusinessCardsShopifyQuoteResult with total price, unit price, cost per card, and breakdown
        """
        
        # Validate quantity
        valid_quantities = [250, 500, 1000, 2000, 5000, 10000]
        if quantity not in valid_quantities:
            raise ValueError(f"Quantity must be one of: {valid_quantities}. Got: {quantity}")
        
        # Validate artworks
        if artworks < 1 or artworks > 50:
            raise ValueError(f"Artworks must be between 1 and 50. Got: {artworks}")
        
        # ========================================================================
        # STEP 1: Setup Costs (NO artwork setup in main setup for premium)
        # ========================================================================
        impos_setup = Decimal('15')    # Imposition setup
        guilo_setup = Decimal('10')    # Guillotine setup
        extra_arts = Decimal('15')     # Cost per extra artwork
        
        # Celloglaze setup cost
        cello_setup = Decimal('0')
        if "None" not in celloglaze:
            cello_setup = Decimal('17')  # Premium lamination setup (Shopify-specific)
        
        total_setup_cost = impos_setup + guilo_setup + cello_setup
        
        # NOTE: Artwork setup cost calculated separately and added AFTER margin
        if artworks > 1:
            artwork_setup_cost = (Decimal(artworks) * extra_arts) - extra_arts
        else:
            artwork_setup_cost = Decimal('0')
        
        # ========================================================================
        # STEP 2: Print Sides Multiplier (F2)
        # ========================================================================
        if "Double" in print_sides:
            sides_multiplier = Decimal('2')
        else:  # Single side
            sides_multiplier = Decimal('1')
        
        # ========================================================================
        # STEP 3: Print Type Cost Per Sheet (F3)
        # ========================================================================
        if "Colour" in print_type:
            print_mode_cost = Decimal('0.048')  # Full color CMYK
        else:  # Black & White
            print_mode_cost = Decimal('0.02')   # B&W only
        
        # ========================================================================
        # STEP 4: Finish Size - Cards Per Sheet (F4)
        # ========================================================================
        if "90mm x 55mm" in finish_size:
            cards_per_sheet = Decimal('21')
        elif "90mm x 45mm" in finish_size:
            cards_per_sheet = Decimal('30')  # Smaller cards, more per sheet
        else:
            raise ValueError(f"Invalid finish size. Must be '90mm x 55mm' or '90mm x 45mm'. Got: {finish_size}")
        
        # ========================================================================
        # STEP 5: Paper Stock Cost (F5)
        # ========================================================================
        if "Satin 350GSM" in paper_stock:
            stock_cost_per_1000_sheets = Decimal('180')
        elif "King Kong" in paper_stock:
            stock_cost_per_1000_sheets = Decimal('300')  # Ultra-premium
        elif "EcoStar" in paper_stock:
            stock_cost_per_1000_sheets = Decimal('500')  # Premium eco-friendly
        else:
            raise ValueError(f"Invalid paper stock. Got: {paper_stock}")
        
        # ========================================================================
        # STEP 6: Calculate Sheets Needed
        # ========================================================================
        stock_waste = Decimal('1.05')  # 5% waste allowance
        
        # Calculate sheets needed with waste
        sheets_needed = (Decimal(quantity) / cards_per_sheet) * stock_waste
        
        # ========================================================================
        # STEP 7: Stock Cost Calculation
        # ========================================================================
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000_sheets
        
        # ========================================================================
        # STEP 8: Click Cost (Printing Cost)
        # ========================================================================
        click_cost = sheets_needed * sides_multiplier * print_mode_cost
        
        # ========================================================================
        # STEP 9: Cutting Cost
        # ========================================================================
        cutting_block = Decimal('500')  # Cutting cost per 500 sheets
        cut_cost = Decimal('10')        # Cost per cutting block
        
        cutting_cost = (sheets_needed / cutting_block) * cut_cost
        
        # ========================================================================
        # STEP 10: Celloglaze Cost (F7)
        # ========================================================================
        cello_cost = Decimal('0')
        
        # FIX: Case-insensitive check for "none" to prevent $8 overcharge
        if "None" in celloglaze or celloglaze.lower() == "none":
            cello_per_sheet = Decimal('0')
        elif "SILK FEEL" in celloglaze:
            if "2 Side" in celloglaze:
                cello_per_sheet = Decimal('0.64')  # Premium silk feel both sides
            else:
                cello_per_sheet = Decimal('0.32')  # Premium silk feel one side
        elif "2 Side" in celloglaze:
            cello_per_sheet = Decimal('0.32')      # Standard lamination both sides
        else:  # 1 Side
            cello_per_sheet = Decimal('0.16')      # Standard lamination one side
        
        cello_cost = sheets_needed * cello_per_sheet
        
        # ========================================================================
        # STEP 11: Calculate Business Cost (BizCost)
        # ========================================================================
        biz_cost = total_setup_cost + stock_cost + click_cost + cutting_cost + cello_cost
        
        # ========================================================================
        # STEP 12: Apply Profit Margin (DUAL STRUCTURE - CRITICAL)
        # ========================================================================
        has_celloglaze = "None" not in celloglaze
        profit_margin_rate = self._get_profit_margin(biz_cost, has_celloglaze)
        profit_amount = biz_cost * profit_margin_rate
        
        # CRITICAL: Premium adds artwork setup cost AFTER margin calculation
        sub_total = biz_cost + artwork_setup_cost + profit_amount
        
        # ========================================================================
        # STEP 13: Apply DOUBLE GST (Shopify-Specific Quirk)
        # ========================================================================
        # ⚠️ WARNING: This is the EXACT Shopify formula including apparent bug
        # The original Shopify code applies GST twice: Total * 1.1 * 1.1
        # This results in 21% total tax instead of 10%
        
        gst_rate = Decimal('1.1')  # 10% GST
        
        # First GST application
        subtotal_after_first_gst = sub_total * gst_rate
        first_gst_amount = sub_total * (gst_rate - Decimal('1'))
        
        # Second GST application (Shopify quirk)
        total_price = subtotal_after_first_gst * gst_rate
        second_gst_amount = subtotal_after_first_gst * (gst_rate - Decimal('1'))
        
        # Total GST applied
        total_gst_amount = first_gst_amount + second_gst_amount
        
        # Round to nearest cent
        total_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # ========================================================================
        # STEP 14: Calculate Unit Prices
        # ========================================================================
        cost_per_card = total_price / Decimal(quantity)
        unit_price = cost_per_card  # Same as cost per card for business cards
        
        # ========================================================================
        # Build Detailed Breakdown
        # ========================================================================
        breakdown = {
            'setup_costs': total_setup_cost,
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'cello_setup': cello_setup,
            'artwork_setup_cost': artwork_setup_cost,
            'stock_cost': stock_cost,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'cello_cost': cello_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'first_gst_application': subtotal_after_first_gst,
            'first_gst_amount': first_gst_amount,
            'second_gst_application': total_price,
            'second_gst_amount': second_gst_amount,
            'total_gst_amount': total_gst_amount,
            'gst_rate': gst_rate,
            'total_price': total_price,
            'cost_per_card': cost_per_card,
            'sheets_needed': sheets_needed,
            'cards_per_sheet': cards_per_sheet,
            'has_celloglaze': has_celloglaze
        }
        
        specifications = {
            'quantity': quantity,
            'print_sides': print_sides,
            'print_type': print_type,
            'finish_size': finish_size,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'celloglaze': celloglaze,
            'sheets_used': float(sheets_needed),
            'cards_per_sheet': float(cards_per_sheet),
            'sides_multiplier': float(sides_multiplier),
            'print_mode_cost': float(print_mode_cost),
            'cello_per_sheet': float(cello_per_sheet),
            'platform': 'Shopify'
        }
        
        return PremiumBusinessCardsShopifyQuoteResult(
            total_price=total_price,
            unit_price=unit_price,
            cost_per_card=cost_per_card,
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications
        )
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _get_profit_margin(self, biz_cost: Decimal, has_celloglaze: bool) -> Decimal:
        """
        Get profit margin based on BizCost with DUAL TIER STRUCTURE
        NOTE: Premium cards have HIGHER margins when NO lamination is selected
        
        Args:
            biz_cost: Business cost before profit
            has_celloglaze: True if lamination is selected, False if "None"
        
        Returns:
            Profit margin rate as decimal (e.g., 0.5 = 50%, 1.09 = 109%)
        """
        
        if not has_celloglaze:
            # NO CELLOGLAZE: Higher profit margins (109%-120%)
            tiers = [
                (Decimal('50.999'), Decimal('1.2')),     # $1-$50.99: 120% margin
                (Decimal('60.999'), Decimal('1.09')),    # $51-$60.99: 109% margin
                (Decimal('65.999'), Decimal('1.09')),    # All remaining tiers: 109% margin
                (Decimal('70.999'), Decimal('1.09')),
                (Decimal('80.999'), Decimal('1.09')),
                (Decimal('100.999'), Decimal('1.09')),
                (Decimal('150.999'), Decimal('1.09')),
                (Decimal('200.999'), Decimal('1.09')),
                (Decimal('300.999'), Decimal('1.09')),
                (Decimal('400.999'), Decimal('1.09')),
                (Decimal('500.999'), Decimal('1.09')),
                (Decimal('1000.999'), Decimal('1.09')),
                (Decimal('10000'), Decimal('1.09'))
            ]
        else:
            # WITH CELLOGLAZE: Standard margins (30%-90%)
            tiers = [
                (Decimal('50.999'), Decimal('0.5')),     # $1-$50.99: 50% margin
                (Decimal('60.999'), Decimal('0.51')),    # $51-$60.99: 51% margin
                (Decimal('65.999'), Decimal('0.6')),     # $61-$65.99: 60% margin
                (Decimal('70.999'), Decimal('0.6')),     # $66-$70.99: 60% margin
                (Decimal('80.999'), Decimal('0.7')),     # $71-$80.99: 70% margin
                (Decimal('100.999'), Decimal('0.6')),    # $81-$100.99: 60% margin
                (Decimal('150.999'), Decimal('0.75')),   # $101-$150.99: 75% margin
                (Decimal('200.999'), Decimal('0.9')),    # $151-$200.99: 90% margin (peak)
                (Decimal('300.999'), Decimal('0.3')),    # $201-$300.99: 30% margin (volume)
                (Decimal('400.999'), Decimal('0.4')),    # $301-$400.99: 40% margin
                (Decimal('500.999'), Decimal('0.45')),   # $401-$500.99: 45% margin
                (Decimal('1000.999'), Decimal('0.3')),   # $501-$1000.99: 30% margin
                (Decimal('10000'), Decimal('0.3'))       # $1001+: 30% margin
            ]
        
        for max_cost, margin in tiers:
            if biz_cost <= max_cost:
                return margin
        
        return tiers[-1][1]  # Return last tier margin as default


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Create calculator instance
    calc = PremiumBusinessCardsShopifyCalculator()
    
    # Example 1: Standard premium cards with gloss lamination
    print("=" * 80)
    print("EXAMPLE 1: Standard Premium Cards with 2 Side Gloss Lamination (SHOPIFY)")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=500,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 350GSM",
        artworks=1,
        celloglaze="2 Side Gloss"
    )
    
    print(f"\nTotal Price: ${result.total_price:,.2f}")
    print(f"Cost Per Card: ${result.cost_per_card:.4f}")
    print(f"\nBreakdown:")
    print(f"  Business Cost: ${result.breakdown['biz_cost']:,.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_rate']*100:.0f}% (with lamination)")
    print(f"  Artwork Setup: ${result.breakdown['artwork_setup_cost']:,.2f}")
    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
    print(f"  First GST (10%): ${result.breakdown['first_gst_amount']:,.2f}")
    print(f"  After First GST: ${result.breakdown['first_gst_application']:,.2f}")
    print(f"  Second GST (10%): ${result.breakdown['second_gst_amount']:,.2f}")
    print(f"  ⚠️ TOTAL GST: ${result.breakdown['total_gst_amount']:,.2f} (21% due to double application)")
    print(f"  TOTAL: ${result.total_price:,.2f}")
    
    # Example 2: Premium without lamination (higher margins)
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Premium Cards WITHOUT Lamination (Higher Profit Margins)")
    print("=" * 80)
    
    result2 = calc.calculate(
        quantity=1000,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 350GSM",
        artworks=1,
        celloglaze="None"
    )
    
    print(f"\nTotal Price: ${result2.total_price:,.2f}")
    print(f"Cost Per Card: ${result2.cost_per_card:.4f}")
    print(f"Profit Margin: {result2.breakdown['profit_margin_rate']*100:.0f}% (NO lamination = higher margin)")
    print(f"Cello Setup: ${result2.breakdown['cello_setup']:,.2f} (No lamination = no setup)")
    
    # Example 3: Ultra-premium with King Kong stock and SILK FEEL
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Ultra-Premium King Kong Stock with SILK FEEL Matt Lamination")
    print("=" * 80)
    
    result3 = calc.calculate(
        quantity=250,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="King Kong High Bulk",
        artworks=1,
        celloglaze="2 Side SILK FEEL Matt"
    )
    
    print(f"\nTotal Price: ${result3.total_price:,.2f}")
    print(f"Cost Per Card: ${result3.cost_per_card:.4f}")
    print(f"Stock Cost: ${result3.breakdown['stock_cost']:,.2f} (King Kong premium)")
    print(f"Cello Cost: ${result3.breakdown['cello_cost']:,.2f} (SILK FEEL premium)")
    
    # Example 4: Multiple artworks with eco-friendly stock
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Multiple Artworks (5 designs) with EcoStar Stock")
    print("=" * 80)
    
    result4 = calc.calculate(
        quantity=500,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="EcoStar 350GSM Uncoated",
        artworks=5,
        celloglaze="1 Side Matt"
    )
    
    print(f"\nTotal Price: ${result4.total_price:,.2f}")
    print(f"Cost Per Card: ${result4.cost_per_card:.4f}")
    print(f"Artwork Setup: ${result4.breakdown['artwork_setup_cost']:,.2f} (5 designs = 4 extra @ $15)")
    print(f"Stock Cost: ${result4.breakdown['stock_cost']:,.2f} (EcoStar premium eco)")
    
    print("\n" + "=" * 80)
    print("⚠️ SHOPIFY-SPECIFIC NOTE:")
    print("=" * 80)
    print("This calculator implements the EXACT Shopify JavaScript formula,")
    print("including the DOUBLE GST application (Total * 1.1 * 1.1).")
    print("This results in 21% total tax instead of the expected 10% GST.")
    print("This appears to be an error in the original Shopify code but is")
    print("replicated here for exact formula matching.")
