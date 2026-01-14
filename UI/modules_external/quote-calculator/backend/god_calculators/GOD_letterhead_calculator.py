"""
Letterhead Calculator - GOD Version (Database-Driven)
====================================================

Extracted from complete_calculator_implementation.py lines 3803-3882
VB.NET Source: LetterheadQuote.vb

Database Tables Used:
  - Quote_DigitalStocks
  - Quote_DigitalClicks
  - Quote_ProfitMargins (ProductTypeID = 8 for letterheads)
  - Quote_GenericSetting

Letterheads are simplified flyers without folding or celloglaze:
  - Stock selection and optimization
  - Printing costs (colour/B&W on both sides)
  - Cutting costs
  - Profit margins based on cost tiers

Author: Extracted from InHousePrint VB.NET LetterheadQuote.vb
Date: October 12, 2025
Status: GOD Calculator (Database-Driven, Modular, Tool-Ready)
"""

import math
from decimal import Decimal
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Tuple


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Stock:
    """Stock/paper specification from database"""
    stock_id: int
    stock_type_id: int
    length: int
    width: int
    height: int
    cost_per_thousand: Decimal
    gsm: int
    markup: Decimal
    description: str = ""


@dataclass
class ClickPrice:
    """Click/printing price from database"""
    click_id: int
    click_type_id: int
    description: str
    price_per_a4: Decimal


@dataclass
class ProfitMargin:
    """Profit margin tier from database"""
    product_type_id: int
    start_price: Decimal
    end_price: Decimal
    margin: Decimal


@dataclass
class QuoteResult:
    """Quote calculation result - Standard interface for all GOD calculators"""
    product_type: str
    quantity: int
    cost_to_business: Decimal
    profit_margin: Decimal
    total_cost_ex_gst: Decimal
    total_cost_inc_gst: Decimal
    breakdown: Dict[str, Any]
    specifications: Dict[str, Any]
    
    @property
    def success(self) -> bool:
        """Indicates successful calculation"""
        return self.total_cost_inc_gst > 0
    
    @property
    def gst_amount(self) -> Decimal:
        """Calculate GST amount"""
        return self.total_cost_inc_gst - self.total_cost_ex_gst
    
    @property
    def cost_per_unit_ex_gst(self) -> Decimal:
        """Cost per unit excluding GST"""
        return self.total_cost_ex_gst / self.quantity if self.quantity > 0 else Decimal('0')
    
    @property
    def cost_per_unit_inc_gst(self) -> Decimal:
        """Cost per unit including GST"""
        return self.total_cost_inc_gst / self.quantity if self.quantity > 0 else Decimal('0')


# ============================================================================
# LETTERHEAD CALCULATOR (GOD VERSION - DATABASE DRIVEN)
# ============================================================================

class LetterheadCalculatorGOD:
    """
    Database-driven letterhead calculator
    Replicates VB.NET LetterheadQuote.vb logic exactly
    
    Letterheads are official stationery with no folding or celloglaze.
    Simplified version of flyer calculator.
    """
    
    def __init__(self, db_connector):
        """
        Initialize calculator with database connection
        
        Args:
            db_connector: InHousePrintDB instance for database access
        """
        self.db = db_connector
        
        # Configuration from Quote_GenericSetting
        self.config: Dict[str, Any] = {}
        
        # Pricing data from database
        self.stocks: List[Stock] = []
        self.digital_clicks: Dict[int, ClickPrice] = {}  # Keyed by click_type_id
        self.profit_margins: Dict[int, List[ProfitMargin]] = {}
        
        # Load all data from database
        self._load_configuration()
        self._load_pricing_data()
    
    def _load_configuration(self):
        """Load all configuration values from Quote_GenericSetting - DATABASE ONLY"""
        try:
            query = "SELECT SettingDesc, SettingValue FROM Quote_GenericSetting"
            results = self.db.execute_query(query)
            
            for row in results.itertuples(index=False):
                setting_name = row[0]
                setting_value = row[1]
                
                # Parse value to appropriate type
                if setting_value is None:
                    self.config[setting_name] = None
                elif str(setting_value).lower() in ('true', 'false'):
                    self.config[setting_name] = str(setting_value).lower() == 'true'
                else:
                    try:
                        if '.' in str(setting_value):
                            self.config[setting_name] = Decimal(str(setting_value))
                        else:
                            self.config[setting_name] = int(setting_value)
                    except (ValueError, TypeError):
                        self.config[setting_name] = str(setting_value)
            
            print(f"[OK] Loaded {len(self.config)} configuration settings from database")
                
        except Exception as e:
            print(f"[ERROR] Could not load configuration from database: {e}")
            raise
    
    def _load_pricing_data(self):
        """Load pricing data from database tables"""
        
        # Load stocks from Quote_DigitalStocks
        stock_query = """
            SELECT StockID, StockTypeID, Length, Width, CostPerThousand, GSM, Markup
            FROM Quote_DigitalStocks
            ORDER BY GSM, Length, Width
        """
        
        stock_results = self.db.execute_query(stock_query)
        
        for row in stock_results.itertuples(index=False):
            stock = Stock(
                stock_id=int(row[0]),
                stock_type_id=int(row[1]),
                length=int(row[2]),
                width=int(row[3]),
                cost_per_thousand=Decimal(str(row[4])),
                gsm=int(row[5]),
                markup=Decimal(str(row[6])),
                height=int(row[2]),  # Height = Length for sheet
                description=f"{row[3]}x{row[2]} {row[5]}gsm"
            )
            self.stocks.append(stock)
        
        # Load click prices from Quote_DigitalClicks
        click_query = """
            SELECT DigitalClickID, ClickDesc, ClickPricePerA4
            FROM Quote_DigitalClicks
            ORDER BY DigitalClickID
        """
        
        click_results = self.db.execute_query(click_query)
        
        for row in click_results.itertuples(index=False):
            click = ClickPrice(
                click_id=int(row[0]),
                click_type_id=int(row[0]),  # Use ID as type ID
                description=row[1],
                price_per_a4=Decimal(str(row[2]))
            )
            self.digital_clicks[click.click_type_id] = click
        
        # Load profit margins from Quote_ProfitMargins
        margin_query = """
            SELECT ProductTypeID, StartPrice, EndPrice, Margin
            FROM Quote_ProfitMargins
            ORDER BY ProductTypeID, StartPrice
        """
        
        margin_results = self.db.execute_query(margin_query)
        
        for row in margin_results.itertuples(index=False):
            product_type = int(row[0])
            
            if product_type not in self.profit_margins:
                self.profit_margins[product_type] = []
            
            self.profit_margins[product_type].append(ProfitMargin(
                product_type_id=product_type,
                start_price=Decimal(str(row[1])),
                end_price=Decimal(str(row[2])),
                margin=Decimal(str(row[3]))
            ))
        
        print(f"[OK] Loaded {len(self.stocks)} stocks, {len(self.digital_clicks)} click prices, "
              f"{len(self.profit_margins)} profit margin tiers from database")
    
    def calculate(self, 
                  quantity: int,
                  width: int,
                  height: int,
                  gsm: int,
                  print_side1: int = 1,
                  print_side2: int = 0,
                  discount: Decimal = Decimal('0')) -> QuoteResult:
        """
        Calculate letterhead quote
        
        Extracted from complete_calculator_implementation.py lines 3803-3882
        VB.NET Source: LetterheadQuote.vb
        
        Args:
            quantity: Number of letterheads to print
            width: Width in millimeters
            height: Height in millimeters
            gsm: Paper weight (grams per square meter)
            print_side1: Print mode for side 1 (0=None, 1=Colour, 2=B&W, 3=B&W on Colour)
            print_side2: Print mode for side 2 (0=None, 1=Colour, 2=B&W, 3=B&W on Colour)
            discount: Discount as decimal (0.10 = 10%)
        
        Returns:
            QuoteResult object with pricing and specifications
        """
        
        # Configuration
        waste_percentage = (Decimal(str(self.config['MaterialWastePercentage'])) / Decimal('100')) + Decimal('1')
        colour_click = self.digital_clicks[1].price_per_a4
        bw_click = self.digital_clicks[2].price_per_a4
        bw_on_colour_click = self.digital_clicks[3].price_per_a4
        imposition_setup = Decimal(str(self.config['DigitalImpositionSetup']))
        guillo_setup = Decimal(str(self.config['GuilloSetup']))
        cutting_blocks = Decimal(str(self.config['CuttingBlockSheets']))
        cost_per_block = Decimal(str(self.config['CostPerBlock']))
        gst_rate = Decimal(str(self.config['GST'])) / Decimal('100')
        bleed = Decimal(str(self.config['FlyerBleedMeasurement']))
        
        # Stock optimization (VB.NET adds bleed ONCE per dimension inside imposition calculation)
        best_stock, best_ups, sheets_needed = self._optimize_stock_selection(
            width, height, quantity, gsm=gsm, bleed=bleed
        )
        
        sheets_with_waste = int(sheets_needed * waste_percentage)
        
        # Paper cost
        stock_markup = best_stock.markup / Decimal('100')
        paper_cost = (Decimal(str(sheets_with_waste)) / Decimal('1000')) * (
            best_stock.cost_per_thousand * (Decimal('1') + stock_markup)
        )
        
        # Print costs
        a4_multiplier = 3 if best_stock.height > 483 else 2
        
        side1_cost = self._calculate_side_cost(
            print_side1, sheets_with_waste, a4_multiplier,
            colour_click, bw_click, bw_on_colour_click
        )
        side2_cost = self._calculate_side_cost(
            print_side2, sheets_with_waste, a4_multiplier,
            colour_click, bw_click, bw_on_colour_click
        )
        total_click_cost = side1_cost + side2_cost
        
        # Cutting cost
        cutting_blocks_needed = math.ceil(sheets_with_waste / cutting_blocks)
        cutting_cost = guillo_setup + (cutting_blocks_needed * cost_per_block)
        
        # Total cost
        total_cost = paper_cost + total_click_cost + cutting_cost + imposition_setup
        
        # Profit margin (Product Type 8 for letterheads)
        profit_margin = self._get_profit_margin(8, total_cost)
        
        # Final pricing
        cost_ex_gst = total_cost * (1 + profit_margin)
        discount_amount = cost_ex_gst * discount
        cost_ex_gst -= discount_amount
        cost_inc_gst = cost_ex_gst * (1 + gst_rate)
        
        return QuoteResult(
            product_type="Letterheads",
            quantity=quantity,
            cost_to_business=total_cost,
            profit_margin=profit_margin,
            total_cost_ex_gst=cost_ex_gst,
            total_cost_inc_gst=cost_inc_gst,
            breakdown={
                'paper_cost': float(paper_cost),
                'click_cost': float(total_click_cost),
                'cutting_cost': float(cutting_cost),
                'setup_cost': float(imposition_setup),
                'side1_cost': float(side1_cost),
                'side2_cost': float(side2_cost),
                'sheets_with_waste': sheets_with_waste,
                'cutting_blocks': cutting_blocks_needed
            },
            specifications={
                'size': f"{width}x{height}mm",
                'stock': best_stock.description,
                'stock_size': f"{best_stock.width}x{best_stock.height}mm",
                'gsm': str(gsm),
                'sheets_needed': str(sheets_with_waste),
                'ups_per_sheet': str(best_ups),
                'print_side1': self._print_mode_name(print_side1),
                'print_side2': self._print_mode_name(print_side2),
                'a4_multiplier': str(a4_multiplier),
                'profit_margin_pct': float(profit_margin * 100)
            }
        )
    
    # ========================================================================
    # HELPER METHODS (From VB.NET)
    # ========================================================================
    
    def _optimize_stock_selection(self, width: int, height: int, quantity: int,
                                  gsm: int, bleed: Decimal) -> Tuple[Stock, int, int]:
        """
        Find optimal stock that fits the job with maximum UPS
        VB.NET adds bleed measurement ONCE per dimension
        """
        best_stock = None
        best_ups = 0
        best_sheets = float('inf')
        
        # Filter stocks by GSM
        matching_stocks = [s for s in self.stocks if s.gsm == gsm]
        
        if not matching_stocks:
            # Fallback: use closest GSM
            matching_stocks = self.stocks
        
        for stock in matching_stocks:
            # Add bleed once per dimension (VB.NET pattern)
            item_width_with_bleed = width + int(bleed)
            item_height_with_bleed = height + int(bleed)
            
            # Try both orientations
            for item_w, item_h in [(item_width_with_bleed, item_height_with_bleed),
                                   (item_height_with_bleed, item_width_with_bleed)]:
                
                if item_w <= stock.width and item_h <= stock.height:
                    # Calculate UPS
                    ups_width = stock.width // item_w
                    ups_height = stock.height // item_h
                    ups = ups_width * ups_height
                    
                    if ups > 0:
                        sheets = math.ceil(quantity / ups)
                        
                        # Prefer higher UPS, then fewer sheets
                        if ups > best_ups or (ups == best_ups and sheets < best_sheets):
                            best_stock = stock
                            best_ups = ups
                            best_sheets = sheets
        
        if not best_stock:
            # Emergency fallback: use largest stock
            best_stock = max(self.stocks, key=lambda s: s.width * s.height)
            best_ups = 1
            best_sheets = quantity
        
        return best_stock, best_ups, best_sheets
    
    def _calculate_side_cost(self, print_mode: int, sheets: int, a4_multiplier: int,
                            colour_click: Decimal, bw_click: Decimal, 
                            bw_on_colour_click: Decimal) -> Decimal:
        """
        Calculate printing cost for one side
        
        Print modes:
        0 = No print
        1 = Colour
        2 = Black & White
        3 = B&W on colour machine
        """
        if print_mode == 0:
            return Decimal('0')
        elif print_mode == 1:
            return Decimal(str(sheets)) * colour_click * Decimal(str(a4_multiplier))
        elif print_mode == 2:
            return Decimal(str(sheets)) * bw_click * Decimal(str(a4_multiplier))
        elif print_mode == 3:
            return Decimal(str(sheets)) * bw_on_colour_click * Decimal(str(a4_multiplier))
        else:
            return Decimal('0')
    
    def _get_profit_margin(self, product_type_id: int, cost: Decimal) -> Decimal:
        """
        Get profit margin from tiered structure in database
        
        Args:
            product_type_id: Product type ID from Quote_ProfitMargins table
                            (8 = Letterheads)
            cost: Cost amount to find margin tier for
        
        Returns:
            Profit margin as decimal (0.30 = 30%)
        """
        margins = self.profit_margins.get(product_type_id, [])
        
        for margin in margins:
            if cost >= margin.start_price and cost <= margin.end_price + Decimal('0.99'):
                return Decimal(str(margin.margin)) / Decimal('100')
        
        return Decimal('1.0')  # 100% default margin if no tier found
    
    def _print_mode_name(self, mode: int) -> str:
        """Convert print mode number to human-readable name"""
        modes = {0: 'No Print', 1: 'Colour', 2: 'Black & White', 3: 'B&W on Colour'}
        return modes.get(mode, 'Unknown')


# ============================================================================
# TOOL INTERFACE (For AI Agents and External Scripts)
# ============================================================================

def calculate_letterhead_quote(db_connector, quantity: int, width: int, height: int, gsm: int, **kwargs) -> Dict[str, Any]:
    """
    Tool-ready interface for letterhead quote calculation
    
    This function provides a simple dictionary-based interface for AI agents
    and external scripts that need letterhead quotes.
    
    Args:
        db_connector: InHousePrintDB instance
        quantity: Number of letterheads
        width: Width in mm
        height: Height in mm
        gsm: Paper weight
        **kwargs: Additional parameters (print_side1, print_side2, discount)
    
    Returns:
        Dictionary with quote results
    """
    calc = LetterheadCalculatorGOD(db_connector)
    result = calc.calculate(quantity, width, height, gsm, **kwargs)
    
    return {
        'success': result.success,
        'product_type': result.product_type,
        'quantity': result.quantity,
        'cost_to_business': float(result.cost_to_business),
        'profit_margin': float(result.profit_margin),
        'total_cost_ex_gst': float(result.total_cost_ex_gst),
        'total_cost_inc_gst': float(result.total_cost_inc_gst),
        'gst_amount': float(result.gst_amount),
        'cost_per_unit_inc_gst': float(result.cost_per_unit_inc_gst),
        'breakdown': result.breakdown,
        'specifications': result.specifications
    }


# ============================================================================
# TEST SUITE
# ============================================================================

if __name__ == '__main__':
    """Test the letterhead calculator"""
    import sys
    import os
    
    # Add tools path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
    
    from db_connector import InHousePrintDB
    
    print("=" * 80)
    print("LETTERHEAD CALCULATOR TEST")
    print("=" * 80)
    
    # Initialize
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json')
    db = InHousePrintDB(config_path)
    calc = LetterheadCalculatorGOD(db)
    
    # Test 1: A4 Letterheads - 1000qty, 100GSM, Double-sided colour
    print("\nTest 1: A4 Letterheads - 1000qty, 100GSM, Colour both sides")
    result1 = calc.calculate(
        quantity=1000,
        width=210,
        height=297,
        gsm=100,
        print_side1=1,  # Colour
        print_side2=1   # Colour
    )
    
    print(f"   Stock: {result1.specifications['stock']}")
    print(f"   UPS: {result1.specifications['ups_per_sheet']}")
    print(f"   Cost to Business: ${result1.cost_to_business:.2f}")
    print(f"   Profit Margin: {result1.specifications['profit_margin_pct']:.0f}%")
    print(f"   Total inc GST: ${result1.total_cost_inc_gst:.2f}")
    print(f"   Per Unit: ${result1.cost_per_unit_inc_gst:.3f}")
    
    # Test 2: DL Letterheads - 500qty, 120GSM, Single-sided colour
    print("\nTest 2: DL Letterheads - 500qty, 120GSM, Single-sided colour")
    result2 = calc.calculate(
        quantity=500,
        width=99,
        height=210,
        gsm=120,
        print_side1=1,  # Colour
        print_side2=0   # No print
    )
    
    print(f"   Stock: {result2.specifications['stock']}")
    print(f"   UPS: {result2.specifications['ups_per_sheet']}")
    print(f"   Cost to Business: ${result2.cost_to_business:.2f}")
    print(f"   Profit Margin: {result2.specifications['profit_margin_pct']:.0f}%")
    print(f"   Total inc GST: ${result2.total_cost_inc_gst:.2f}")
    print(f"   Per Unit: ${result2.cost_per_unit_inc_gst:.3f}")
    
    # Test tool interface
    print("\nTest 3: Tool interface test")
    result3 = calculate_letterhead_quote(db, 250, 210, 297, 150, print_side1=1, print_side2=0)
    print(f"   Success: {result3['success']}")
    print(f"   Total inc GST: ${result3['total_cost_inc_gst']:.2f}")
    
    db.close()
    print("\n[SUCCESS] All tests completed!")
