"""
Economical Business Cards Shopify Calculator
Exact implementation of Shopify DPO JavaScript formula for Economical Business Cards

Based on: shopify_economical_business_cards.json specification
Fields: F1-F6 (Simple business card structure)
Key Features: Artwork setup costs, cards-per-sheet calculation, BizCost-based profit margins
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path
import sys

# Import config manager
from config_manager import config_manager


@dataclass
class EconomicalBusinessCardsQuoteResult:
    """Result from Economical Business Cards calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_card: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class EconomicalBusinessCardsShopifyCalculator:
    """
    Economical Business Cards Calculator - Exact Shopify DPO Implementation
    
    Features:
    - F1-F6 Shopify field structure
    - Artwork setup costs (first free, $15 per extra)
    - Cards-per-sheet calculation (21 cards per sheet for 90x55mm)
    - BizCost-based profit margins (13 tiers: 50%-90%)
    - Configurable price increase and GST rate (10% standard)
    - No binding costs - just cutting to finished size
    
    Key Differences from Perfect Bound Books:
    - Multiple artworks incur additional setup costs
    - Uses cards-per-sheet calculation vs page-based
    - Simpler structure: single stock type throughout
    - Different profit margin tiers optimized for small format
    """
    
    # ============================================================================
    # CONFIGURABLE PRICING VARIABLES
    # ============================================================================
    PRICE_INCREASE_MULTIPLIER = Decimal('1.00')  # NO price increase default (can be adjusted)
    GST_RATE = Decimal('1.10')                   # 10% GST (Australian standard)
    SURCHARGE = Decimal('0.00')                  # NO surcharge for economical cards
    
    def __init__(self, config_path: str = None):
        """
        Initialize Economical Business Cards calculator
        
        Args:
            config_path: Optional path to shopify_economical_business_cards.json config file
        """
        self.config = self._load_config(config_path) if config_path else None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        return data
    
    def calculate(self,
                  quantity: int,                          # F1: 250-10,000
                  print_sides: str = "Single side print", # F2: Single/Double
                  print_type: str = "Colour",             # F3: Colour/Black & White
                  finish_size: str = "90mm x 55mm",       # F4: Standard business card
                  paper_stock: str = "Satin 300GSM",      # F5: Paper stock type
                  artworks: int = 1                       # F6: Number of different designs
                  ) -> EconomicalBusinessCardsQuoteResult:
        """
        Calculate Economical Business Cards quote using exact Shopify DPO formula
        
        Args:
            quantity: Number of cards (F1: 250, 500, 1000, 2000, 5000, 10000)
            print_sides: Printing sides (F2: "Single side print" / "Double side print")
            print_type: Print color mode (F3: "Colour" / "Black & White")
            finish_size: Card size (F4: "90mm x 55mm" - standard only)
            paper_stock: Paper stock (F5: "Satin 300GSM" - standard only)
            artworks: Number of different artwork designs (F6: 1-50, default 1)
            
        Returns:
            EconomicalBusinessCardsQuoteResult with total price, unit price, cost per card, and breakdown
        """
        
        # Validate quantity
        valid_quantities = [250, 500, 1000, 2000, 5000, 10000]
        if quantity not in valid_quantities:
            raise ValueError(f"Quantity must be one of: {valid_quantities}. Got: {quantity}")
        
        # Validate artworks
        if artworks < 1 or artworks > 50:
            raise ValueError(f"Artworks must be between 1 and 50. Got: {artworks}")
        
        # ========================================================================
        # STEP 1: Setup Costs
        # ========================================================================
        impos_setup = Decimal('15')    # Imposition setup
        guilo_setup = Decimal('12')    # Guillotine setup
        extra_arts = Decimal('15')     # Cost per extra artwork
        
        # Artwork setup cost: First artwork is free, then $15 per additional artwork
        if artworks > 1:
            artwork_setup_cost = (Decimal(artworks) * extra_arts) - extra_arts
        else:
            artwork_setup_cost = Decimal('0')
        
        total_setup_cost = impos_setup + guilo_setup + artwork_setup_cost
        
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
            print_mode_cost = Decimal('0.044')  # Full color CMYK
        else:  # Black & White
            print_mode_cost = Decimal('0.02')   # B&W only
        
        # ========================================================================
        # STEP 4: Finish Size - Cards Per Sheet (F4)
        # ========================================================================
        # Standard business card 90x55mm fits 21 cards per SRA3 sheet
        if "90mm x 55mm" in finish_size or "90x55" in finish_size:
            cards_per_sheet = Decimal('21')
        else:
            raise ValueError(f"Only standard 90mm x 55mm size is currently supported. Got: {finish_size}")
        
        # ========================================================================
        # STEP 5: Paper Stock Cost (F5)
        # ========================================================================
        if "Satin 300GSM" in paper_stock:
            stock_cost_per_1000_sheets = Decimal('126')
        else:
            raise ValueError(f"Only Satin 300GSM is currently supported. Got: {paper_stock}")
        
        # ========================================================================
        # STEP 6: Calculate Sheets Needed
        # ========================================================================
        stock_waste = Decimal('1.05')  # 5% waste allowance
        
        # Calculate sheets needed with waste
        sheets_needed = (Decimal(quantity) / cards_per_sheet) * stock_waste
        
        # ========================================================================
        # STEP 7: Stock Cost Calculation
        # ========================================================================
        # Cost per 1000 sheets, so divide sheets by 1000 and multiply by cost
        stock_cost = (sheets_needed / Decimal('1000')) * stock_cost_per_1000_sheets
        
        # ========================================================================
        # STEP 8: Click Cost (Printing Cost)
        # ========================================================================
        # Click cost = sheets * sides * print_mode_cost
        click_cost = sheets_needed * sides_multiplier * print_mode_cost
        
        # ========================================================================
        # STEP 9: Cutting Cost
        # ========================================================================
        cutting_block = Decimal('500')  # Cutting cost per 500 sheets
        cut_cost = Decimal('11')        # Cost per cutting block
        
        cutting_cost = (sheets_needed / cutting_block) * cut_cost
        
        # ========================================================================
        # STEP 10: Calculate Business Cost (BizCost)
        # ========================================================================
        biz_cost = total_setup_cost + stock_cost + click_cost + cutting_cost
        
        # ========================================================================
        # STEP 11: Apply Profit Margin (based on BizCost tiers - CRITICAL)
        # ========================================================================
        profit_margin_rate = self._get_profit_margin(biz_cost)
        profit_amount = biz_cost * profit_margin_rate
        sub_total = biz_cost + profit_amount
        
        # ========================================================================
        # STEP 12: Apply Price Increase (if any)
        # ========================================================================
        subtotal_with_increase = sub_total * self.PRICE_INCREASE_MULTIPLIER
        
        # ========================================================================
        # STEP 13: Apply GST (10% for Business Cards - NO SURCHARGE)
        # ========================================================================
        total_price = (subtotal_with_increase * self.GST_RATE) + self.SURCHARGE
        
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
            'artwork_setup_cost': artwork_setup_cost,
            'impos_setup': impos_setup,
            'guilo_setup': guilo_setup,
            'stock_cost': stock_cost,
            'click_cost': click_cost,
            'cutting_cost': cutting_cost,
            'biz_cost': biz_cost,
            'profit_margin_rate': profit_margin_rate,
            'profit_amount': profit_amount,
            'subtotal': sub_total,
            'price_increase_multiplier': self.PRICE_INCREASE_MULTIPLIER,
            'subtotal_with_increase': subtotal_with_increase,
            'gst_rate': self.GST_RATE,
            'gst_amount': subtotal_with_increase * (self.GST_RATE - Decimal('1')),
            'surcharge': self.SURCHARGE,
            'total_price': total_price,
            'cost_per_card': cost_per_card,
            'sheets_needed': sheets_needed,
            'cards_per_sheet': cards_per_sheet
        }
        
        specifications = {
            'quantity': quantity,
            'print_sides': print_sides,
            'print_type': print_type,
            'finish_size': finish_size,
            'paper_stock': paper_stock,
            'artworks': artworks,
            'sheets_used': float(sheets_needed),
            'cards_per_sheet': float(cards_per_sheet),
            'sides_multiplier': float(sides_multiplier),
            'print_mode_cost': float(print_mode_cost)
        }
        
        return EconomicalBusinessCardsQuoteResult(
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
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """
        Get profit margin based on BizCost (13 tiers)
        NOTE: Based on BUSINESS COST, not quantity (critical difference)
        Margins range from 65% (low cost) to 90% (optimal volume)
        """
        tiers = [
            (Decimal('50.999'), Decimal('0.65')),   # $1-$50.99: 65% margin
            (Decimal('60.999'), Decimal('0.51')),   # $51-$60.99: 51% margin
            (Decimal('65.999'), Decimal('0.6')),    # $61-$65.99: 60% margin
            (Decimal('70.999'), Decimal('0.6')),    # $66-$70.99: 60% margin
            (Decimal('80.999'), Decimal('0.7')),    # $71-$80.99: 70% margin
            (Decimal('100.999'), Decimal('0.6')),   # $81-$100.99: 60% margin
            (Decimal('150.999'), Decimal('0.75')),  # $101-$150.99: 75% margin
            (Decimal('200.999'), Decimal('0.9')),   # $151-$200.99: 90% margin (peak)
            (Decimal('300.999'), Decimal('0.3')),   # $201-$300.99: 30% margin (volume)
            (Decimal('400.999'), Decimal('0.4')),   # $301-$400.99: 40% margin
            (Decimal('500.999'), Decimal('0.45')),  # $401-$500.99: 45% margin
            (Decimal('1000.999'), Decimal('0.3')),  # $501-$1000.99: 30% margin (high volume)
            (Decimal('10000'), Decimal('0.3'))      # $1001+: 30% margin (very high volume)
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
    calc = EconomicalBusinessCardsShopifyCalculator()
    
    # Example 1: Standard single-sided color business cards
    print("=" * 80)
    print("EXAMPLE 1: Standard Single-Sided Color Business Cards")
    print("=" * 80)
    
    result = calc.calculate(
        quantity=500,
        print_sides="Single side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    print(f"\nTotal Price: ${result.total_price:,.2f}")
    print(f"Cost Per Card: ${result.cost_per_card:.4f}")
    print(f"Unit Price: ${result.unit_price:.4f}")
    print(f"\nBreakdown:")
    print(f"  Business Cost: ${result.breakdown['biz_cost']:,.2f}")
    print(f"    - Setup Costs: ${result.breakdown['setup_costs']:,.2f}")
    print(f"    - Stock Cost: ${result.breakdown['stock_cost']:,.2f}")
    print(f"    - Click Cost: ${result.breakdown['click_cost']:,.2f}")
    print(f"    - Cutting Cost: ${result.breakdown['cutting_cost']:,.2f}")
    print(f"  Profit Margin: {result.breakdown['profit_margin_rate']*100:.0f}%")
    print(f"  Subtotal: ${result.breakdown['subtotal']:,.2f}")
    print(f"  Price Increase ({(calc.PRICE_INCREASE_MULTIPLIER-1)*100:.0f}%): ${result.breakdown['subtotal_with_increase']:,.2f}")
    print(f"  GST ({(calc.GST_RATE-1)*100:.0f}%): ${result.breakdown['gst_amount']:,.2f}")
    print(f"  Surcharge: ${result.breakdown['surcharge']:,.2f}")
    print(f"  TOTAL: ${result.total_price:,.2f}")
    
    print(f"\nSpecifications:")
    print(f"  Quantity: {result.specifications['quantity']} cards")
    print(f"  Sheets Used: {result.specifications['sheets_used']:.2f}")
    print(f"  Cards Per Sheet: {result.specifications['cards_per_sheet']:.0f}")
    print(f"  Print: {result.specifications['print_sides']}, {result.specifications['print_type']}")
    print(f"  Stock: {result.specifications['paper_stock']}")
    print(f"  Artworks: {result.specifications['artworks']}")
    
    # Example 2: Double-sided color cards with multiple designs
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Double-Sided Color Cards with 3 Artwork Designs")
    print("=" * 80)
    
    result2 = calc.calculate(
        quantity=1000,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=3
    )
    
    print(f"\nTotal Price: ${result2.total_price:,.2f}")
    print(f"Cost Per Card: ${result2.cost_per_card:.4f}")
    print(f"Artwork Setup Cost: ${result2.breakdown['artwork_setup_cost']:,.2f} (3 designs = 2 extra @ $15 each)")
    
    # Example 3: Budget black & white cards
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Budget Black & White Cards")
    print("=" * 80)
    
    result3 = calc.calculate(
        quantity=250,
        print_sides="Single side print",
        print_type="Black & White",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    print(f"\nTotal Price: ${result3.total_price:,.2f}")
    print(f"Cost Per Card: ${result3.cost_per_card:.4f}")
    print(f"Print Mode: B&W (cheaper click cost: ${result3.specifications['print_mode_cost']:.3f}/sheet)")
    
    # Example 4: High volume order
    print("\n" + "=" * 80)
    print("EXAMPLE 4: High Volume Order")
    print("=" * 80)
    
    result4 = calc.calculate(
        quantity=5000,
        print_sides="Double side print",
        print_type="Colour",
        finish_size="90mm x 55mm",
        paper_stock="Satin 300GSM",
        artworks=1
    )
    
    print(f"\nTotal Price: ${result4.total_price:,.2f}")
    print(f"Cost Per Card: ${result4.cost_per_card:.4f} (volume discount applied)")
    print(f"Profit Margin: {result4.breakdown['profit_margin_rate']*100:.0f}% (based on BizCost ${result4.breakdown['biz_cost']:.2f})")
