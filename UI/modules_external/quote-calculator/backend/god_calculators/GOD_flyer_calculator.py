#!/usr/bin/env python3
"""
Flyer Calculator - GOD Version (Database-Driven)
================================================

Extracted from complete_calculator_implementation.py lines 2863-2969
VB.NET Source: FlyerQuote.vb

Database Tables Used:
  - Quote_DigitalStocks (stock pricing and sizes)
  - Quote_DigitalClicks (printing costs per A4)
  - Quote_ProfitMargins (tiered profit margins by product type)
  - Quote_GenericSetting (configuration: waste %, setup costs, labor rates)

Product Type IDs for Profit Margins:
  - 1: Flyers < 4000, No Folding
  - 5: Flyers >= 4000, No Folding
  - 6: Flyers < 4000, With Folding
  - 7: Flyers >= 4000, With Folding

Author: Extracted from InHousePrint VB.NET FlyerQuote.vb
Date: October 12, 2025
Status: GOD Calculator (Database-Driven, Modular, Tool-Ready)
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class StockInfo:
    """Digital stock information from database"""
    stock_id: int
    stock_type_id: int
    width: int          # mm
    height: int         # mm
    gsm: int
    cost_per_thousand: Decimal
    markup: Decimal     # percentage
    description: str


@dataclass
class DigitalClick:
    """Digital click pricing from database"""
    click_id: int
    description: str
    price_per_a4: Decimal


@dataclass
class ProfitMargin:
    """Profit margin tier from database"""
    product_type_id: int
    start_price: Decimal
    end_price: Decimal
    margin: Decimal     # percentage


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
# FLYER CALCULATOR (GOD VERSION - DATABASE DRIVEN)
# ============================================================================

class FlyerCalculatorGOD:
    """
    Database-driven flyer/leaflet calculator
    Replicates VB.NET FlyerQuote.vb logic exactly
    
    Features:
    - Dynamic stock selection from Quote_DigitalStocks
    - Automatic imposition calculation (units per sheet)
    - Folding cost calculation
    - Cellophane lamination options
    - Tiered profit margins from database
    - All configuration from Quote_GenericSetting
    
    Usage:
        db = InHousePrintDB("config/database-config.json")
        calc = FlyerCalculatorGOD(db)
        result = calc.calculate(
            quantity=1000,
            width=210,
            height=297,
            gsm=300,
            print_side1=1,  # Colour
            print_side2=0   # No print
        )
        print(f"Total: ${result.total_cost_inc_gst:.2f}")
    """
    
    def __init__(self, db_connector):
        """
        Initialize with database connection (REQUIRED)
        
        Args:
            db_connector: Database connection object with execute_query() method
        """
        self.db = db_connector
        self.digital_stocks: List[StockInfo] = []
        self.digital_clicks: Dict[int, DigitalClick] = {}
        self.profit_margins: Dict[int, List[ProfitMargin]] = {}
        self.config: Dict[str, Any] = {}
        
        # Load all pricing data from database
        self._load_configuration()
        self._load_pricing_data()
    
    # ========================================================================
    # DATABASE LOADING METHODS
    # ========================================================================
    
    def _load_configuration(self):
        """Load all configuration values from Quote_GenericSetting - DATABASE ONLY"""
        try:
            query = "SELECT SettingDesc, SettingValue FROM Quote_GenericSetting"
            results = self.db.execute_query(query)
            
            for row in results.itertuples(index=False):
                self.config[row[0]] = self._parse_config_value(row[1])
            
            print(f"✓ Loaded {len(self.config)} configuration settings from database")
                
        except Exception as e:
            print(f"✗ FATAL: Could not load configuration from database: {e}")
            raise  # Fail fast - NO fallbacks (VB.NET behavior)
    
    def _parse_config_value(self, value_str: str):
        """Parse configuration value to appropriate type"""
        if value_str is None:
            return None
        
        value_str = str(value_str).strip()
        
        # Handle booleans
        if value_str.lower() in ('true', 'false'):
            return value_str.lower() == 'true'
        
        # Try to parse as number
        try:
            if '.' in value_str or value_str.isdigit() or (value_str.startswith('-') and value_str[1:].replace('.', '').isdigit()):
                return Decimal(value_str)
        except:
            pass
        
        # Return as string
        return value_str
    
    def _load_pricing_data(self):
        """Load all pricing data from database"""
        try:
            # Load digital stocks
            stock_query = """
                SELECT StockID, StockTypeID, Length, Width, CostPerThousand, GSM, Markup
                FROM Quote_DigitalStocks
                ORDER BY StockTypeID, GSM, CostPerThousand
            """
            stock_results = self.db.execute_query(stock_query)
            
            for row in stock_results.itertuples(index=False):
                stock = StockInfo(
                    stock_id=int(row[0]),
                    stock_type_id=int(row[1]),
                    width=int(row[3]),
                    height=int(row[2]),
                    gsm=int(row[5]),  # Convert to int to ensure type consistency
                    cost_per_thousand=Decimal(str(row[4])) if row[4] is not None else Decimal('0'),
                    markup=Decimal(str(row[6])) if row[6] is not None else Decimal('0'),
                    description=f"{row[3]}x{row[2]} {row[5]}gsm"
                )
                self.digital_stocks.append(stock)
            
            # Load digital clicks
            click_query = "SELECT DigitalClickID, ClickDesc, ClickPricePerA4 FROM Quote_DigitalClicks"
            click_results = self.db.execute_query(click_query)
            
            for row in click_results.itertuples(index=False):
                self.digital_clicks[row[0]] = DigitalClick(
                    click_id=row[0],
                    description=row[1],
                    price_per_a4=Decimal(str(row[2])) if row[2] is not None else Decimal('0')
                )
            
            # Load profit margins
            margin_query = """
                SELECT ProductTypeID, StartPrice, EndPrice, Margin
                FROM Quote_ProfitMargins
                ORDER BY ProductTypeID, StartPrice
            """
            margin_results = self.db.execute_query(margin_query)
            
            for row in margin_results.itertuples(index=False):
                product_type = row[0]
                if product_type not in self.profit_margins:
                    self.profit_margins[product_type] = []
                
                self.profit_margins[product_type].append(ProfitMargin(
                    product_type_id=product_type,
                    start_price=Decimal(str(row[1])) if row[1] is not None else Decimal('0'),
                    end_price=Decimal(str(row[2])) if row[2] is not None else Decimal('999999'),
                    margin=Decimal(str(row[3])) if row[3] is not None else Decimal('0')
                ))
            
            print(f"✓ Loaded {len(self.digital_stocks)} stocks, {len(self.digital_clicks)} click prices, "
                  f"{len(self.profit_margins)} profit margin tiers from database")
            
        except Exception as e:
            print(f"✗ FATAL: Could not load pricing data from database: {e}")
            raise  # Fail fast - NO fallbacks (VB.NET behavior)
    
    def get_config(self, key: str, default=None):
        """
        Get configuration value from database settings
        If default is None and key not found, raises KeyError (VB.NET behavior - fail fast)
        """
        if key not in self.config and default is None:
            raise KeyError(f"Configuration key '{key}' not found in database Quote_GenericSetting table")
        return self.config.get(key, default)
    
    # ========================================================================
    # MAIN CALCULATION METHOD
    # ========================================================================
    
    def calculate(
        self,
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
        discount: Decimal = Decimal('0')
    ) -> QuoteResult:
        """
        Calculate flyer quote using complete VB.NET algorithm
        
        Args:
            quantity: Number of flyers to produce
            width: Finished width in mm (e.g., 210 for A4)
            height: Finished height in mm (e.g., 297 for A4)
            gsm: Paper weight (e.g., 300)
            print_side1: Print mode for side 1 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
            print_side2: Print mode for side 2 (0=none, 1=colour, 2=b&w, 3=b&w on colour)
            folding_required: Whether folding is required
            folding_passes: Number of folds (1=half fold, 2=z-fold, etc.)
            folding_extra_mins: Extra minutes for complex folding
            cello_required: Whether cellophane lamination is required
            cello_side1: Cello type for side 1 (0=none, 1=gloss, 2=matt)
            cello_side2: Cello type for side 2 (0=none, 1=gloss, 2=matt)
            discount: Discount as decimal (0.1 = 10% off)
        
        Returns:
            QuoteResult with complete cost breakdown and specifications
        
        Raises:
            KeyError: If required configuration missing from database
            Exception: If no suitable stock found for dimensions
        """
        
        # Convert all parameters to proper types (defensive programming - handle string inputs)
        quantity = int(quantity)
        width = int(width)
        height = int(height)
        gsm = int(gsm)
        print_side1 = int(print_side1)
        print_side2 = int(print_side2)
        folding_passes = int(folding_passes)
        folding_extra_mins = int(folding_extra_mins)
        cello_side1 = int(cello_side1)
        cello_side2 = int(cello_side2)
        
        # 1. Load configuration from database (NO DEFAULTS - database only, VB.NET behavior)
        waste_percentage = (Decimal(str(self.get_config('MaterialWastePercentage'))) / Decimal('100')) + Decimal('1')
        colour_click = self.digital_clicks[1].price_per_a4
        bw_click = self.digital_clicks[2].price_per_a4
        bw_on_colour_click = self.digital_clicks[3].price_per_a4
        imposition_setup = Decimal(str(self.get_config('DigitalImpositionSetup')))
        bindery_rate = Decimal(str(self.get_config('BinderyLaborPerHour')))
        guillo_setup = Decimal(str(self.get_config('GuilloSetup')))
        cutting_blocks = Decimal(str(self.get_config('CuttingBlockSheets')))
        cost_per_block = Decimal(str(self.get_config('CostPerBlock')))
        gst_rate = Decimal(str(self.get_config('GST'))) / Decimal('100')
        bleed = Decimal(str(self.get_config('FlyerBleedMeasurement')))
        
        # 2. Stock optimization (VB.NET adds bleed ONCE per dimension inside imposition calculation)
        best_stock, best_ups, sheets_needed = self._optimize_stock_selection(
            width, height, quantity, gsm=gsm, bleed=bleed
        )
        
        sheets_with_waste = int(sheets_needed * waste_percentage)
        
        # 3. Paper cost
        stock_markup = best_stock.markup / Decimal('100')
        paper_cost = (Decimal(str(sheets_with_waste)) / Decimal('1000')) * (
            best_stock.cost_per_thousand * (Decimal('1') + stock_markup)
        )
        
        # 4. Print costs
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
        
        # 5. Folding cost
        folding_cost = Decimal('0')
        if folding_required:
            folding_setup = Decimal(str(self.get_config('FoldingSetupCost')))
            folding_per_1000 = Decimal(str(self.get_config('FoldingCostPer1000')))
            
            folding_running = ((Decimal(str(quantity)) / Decimal('1000')) * folding_per_1000) * Decimal(str(folding_passes))
            folding_extra = (Decimal(str(folding_extra_mins)) / Decimal('60')) * bindery_rate
            folding_cost = folding_setup + folding_running + folding_extra
        
        # 6. Cello cost
        cello_cost = Decimal('0')
        if cello_required:
            cello_cost = self._calculate_cello_cost(
                cello_side1, cello_side2, sheets_with_waste,
                best_stock.width, best_stock.height
            )
        
        # 7. Cutting cost (VB.NET uses division, not ceiling)
        cutting_charge = (Decimal(str(sheets_with_waste)) / cutting_blocks) * cost_per_block
        cutting_cost = guillo_setup + cutting_charge
        
        # 8. Total cost
        total_cost = (paper_cost + total_click_cost + folding_cost + 
                     cello_cost + cutting_cost + imposition_setup)
        
        # 9. Profit margin
        profit_margin = self._get_flyer_profit_margin(quantity, folding_required, total_cost)
        
        # 10. Final pricing
        cost_ex_gst = total_cost * (1 + profit_margin)
        discount_amount = cost_ex_gst * discount
        cost_ex_gst -= discount_amount
        cost_inc_gst = cost_ex_gst * (1 + gst_rate)
        
        return QuoteResult(
            product_type="Flyers",
            quantity=quantity,
            cost_to_business=total_cost,
            profit_margin=profit_margin,
            total_cost_ex_gst=cost_ex_gst,
            total_cost_inc_gst=cost_inc_gst,
            breakdown={
                'paper_cost': float(paper_cost),
                'click_cost': float(total_click_cost),
                'folding_cost': float(folding_cost),
                'cello_cost': float(cello_cost),
                'cutting_cost': float(cutting_cost),
                'setup_cost': float(imposition_setup),
                'profit_amount': float(total_cost * profit_margin),
                'discount_amount': float(discount_amount),
                'gst_amount': float(cost_inc_gst - cost_ex_gst)
            },
            specifications={
                'size': f"{width}x{height}mm",
                'stock': best_stock.description,
                'stock_id': best_stock.stock_id,
                'stock_size': f"{best_stock.width}x{best_stock.height}mm",
                'gsm': gsm,
                'sheets_needed': sheets_with_waste,
                'ups_per_sheet': best_ups,
                'print_side1': self._print_mode_name(print_side1),
                'print_side2': self._print_mode_name(print_side2),
                'folding': 'Yes' if folding_required else 'No',
                'folding_passes': folding_passes if folding_required else 0,
                'cello': 'Yes' if cello_required else 'No',
                'cello_side1': self._cello_type_name(cello_side1) if cello_required else 'None',
                'cello_side2': self._cello_type_name(cello_side2) if cello_required else 'None',
                'profit_margin_pct': float(profit_margin * 100)
            }
        )
    
    # ========================================================================
    # HELPER METHODS (EXTRACTED FROM COMPLETE IMPLEMENTATION)
    # ========================================================================
    
    def _optimize_stock_selection(
        self,
        finish_width: int,
        finish_height: int,
        quantity: int,
        stock_type_id: int = None,
        gsm: int = None,
        bleed: Decimal = Decimal('0')
    ) -> Tuple[StockInfo, int, int]:
        """
        Find optimal stock for given requirements
        
        VB.NET Logic: Adds bleed ONCE per dimension when calculating imposition
        finish_width + bleed, finish_height + bleed
        
        Args:
            finish_width: Final width in mm
            finish_height: Final height in mm
            quantity: Number of units needed
            stock_type_id: Optional filter by stock type
            gsm: Optional filter by GSM
            bleed: Bleed measurement to add to dimensions
        
        Returns:
            Tuple of (best_stock, ups_per_sheet, sheets_needed)
        """
        best_stock = None
        best_cost_per_unit = Decimal('999999')
        best_ups = 0
        
        # Ensure types are correct for comparison
        if gsm is not None:
            gsm = int(gsm)
        if stock_type_id is not None:
            stock_type_id = int(stock_type_id)
        
        # Filter stocks by requirements
        candidate_stocks = self.digital_stocks
        if gsm:
            candidate_stocks = [s for s in candidate_stocks if int(s.gsm) == gsm]  # Ensure both sides are int
        if stock_type_id:
            candidate_stocks = [s for s in candidate_stocks if int(s.stock_type_id) == stock_type_id]
        
        # Add bleed once per dimension (VB.NET behavior)
        required_width = Decimal(str(finish_width)) + bleed
        required_height = Decimal(str(finish_height)) + bleed
        
        for stock in candidate_stocks:
            # Calculate impositions both orientations (VB.NET uses Math.Floor = int() in Python)
            ups_normal = int(stock.width // required_width) * int(stock.height // required_height)
            ups_rotated = int(stock.width // required_height) * int(stock.height // required_width)
            ups = max(ups_normal, ups_rotated)
            
            if ups > 0:
                cost_per_sheet = Decimal(str(stock.cost_per_thousand)) / Decimal('1000')
                cost_per_unit = cost_per_sheet / Decimal(str(ups))
                
                if cost_per_unit < best_cost_per_unit:
                    best_cost_per_unit = cost_per_unit
                    best_stock = stock
                    best_ups = ups
        
        if not best_stock:
            raise Exception(f"No suitable stock found for {finish_width}x{finish_height}mm at {gsm}GSM")
        
        sheets_needed = math.ceil(quantity / best_ups)
        
        return best_stock, best_ups, sheets_needed
    
    def _calculate_side_cost(
        self,
        print_mode: int,
        sheets: int,
        a4_multiplier: int,
        colour_rate: Decimal,
        bw_rate: Decimal,
        bw_on_colour_rate: Decimal
    ) -> Decimal:
        """
        Calculate printing cost for one side
        
        Args:
            print_mode: 0=no print, 1=colour, 2=b&w, 3=b&w on colour
            sheets: Number of sheets
            a4_multiplier: Click multiplier (2 for up to A3, 3 for larger)
            colour_rate: Colour click rate per A4
            bw_rate: B&W click rate per A4
            bw_on_colour_rate: B&W on colour rate per A4
        
        Returns:
            Total cost for printing this side
        """
        if print_mode == 0:      # No print
            return Decimal('0')
        elif print_mode == 1:    # Colour
            return Decimal(str(sheets)) * (colour_rate * Decimal(str(a4_multiplier)))
        elif print_mode == 2:    # B&W
            return Decimal(str(sheets)) * (bw_rate * Decimal(str(a4_multiplier)))
        elif print_mode == 3:    # B&W on colour
            return Decimal(str(sheets)) * (bw_on_colour_rate * Decimal(str(a4_multiplier)))
        else:
            return Decimal('0')
    
    def _calculate_cello_cost(
        self,
        side1_type: int,
        side2_type: int,
        sheets: int,
        stock_width: int,
        stock_height: int
    ) -> Decimal:
        """
        Calculate cellophane lamination cost
        
        Args:
            side1_type: 0=none, 1=gloss, 2=matt
            side2_type: 0=none, 1=gloss, 2=matt
            sheets: Number of sheets
            stock_width: Stock width in mm
            stock_height: Stock height in mm
        
        Returns:
            Total cello cost including setup, material, and labor
        """
        cello_setup = Decimal(str(self.get_config('CelloSetupCost')))
        cello_gloss_short = Decimal(str(self.get_config('CelloGlossShortPerM')))
        cello_gloss_wide = Decimal(str(self.get_config('CelloGlossWidePerM')))
        cello_matt_short = Decimal(str(self.get_config('CellMattShortPerM')))
        cello_matt_wide = Decimal(str(self.get_config('CelloMattWidePerM')))
        cello_rate = Decimal(str(self.get_config('CelloCostPerHour')))
        speed_per_min = Decimal(str(self.get_config('SpeedMPerMin')))
        
        total_time = Decimal('0')
        total_material_cost = Decimal('0')
        
        use_wide_roll = stock_height < 455
        
        for side_type in [side1_type, side2_type]:
            if side_type == 0:  # No cello
                continue
            elif side_type == 1:  # Gloss
                if use_wide_roll:
                    material_cost = ((Decimal(str(sheets)) * Decimal(str(stock_width))) / Decimal('1000')) * cello_gloss_wide
                else:
                    # VB.NET bug: short roll uses celloGlossWide (not Short)!
                    material_cost = ((Decimal(str(sheets)) * Decimal(str(stock_height))) / Decimal('1000')) * cello_gloss_wide
            elif side_type == 2:  # Matt
                if use_wide_roll:
                    material_cost = ((Decimal(str(sheets)) * Decimal(str(stock_width))) / Decimal('1000')) * cello_matt_wide
                else:
                    # VB.NET bug: short roll uses celloMattWide (not Short)!
                    material_cost = ((Decimal(str(sheets)) * Decimal(str(stock_height))) / Decimal('1000')) * cello_matt_wide
            else:
                material_cost = Decimal('0')
            
            # VB.NET: time calculation always uses stockWidth regardless of roll type
            time_to_cello = ((Decimal(str(sheets)) * Decimal(str(stock_width))) / Decimal('1000')) / speed_per_min
            total_material_cost += material_cost
            total_time += time_to_cello
        
        labor_cost = (total_time / Decimal('60')) * cello_rate
        return total_material_cost + cello_setup + labor_cost
    
    def _get_flyer_profit_margin(self, quantity: int, folding: bool, cost: Decimal) -> Decimal:
        """
        Get flyer profit margin based on specifications
        
        Product Type IDs:
        - 1: Flyers < 4000, No Folding
        - 5: Flyers >= 4000, No Folding
        - 6: Flyers < 4000, With Folding
        - 7: Flyers >= 4000, With Folding
        """
        if quantity < 4000 and not folding:
            product_type_id = 1
        elif quantity >= 4000 and not folding:
            product_type_id = 5
        elif quantity < 4000 and folding:
            product_type_id = 6
        else:
            product_type_id = 7
        
        return self._get_profit_margin(product_type_id, cost)
    
    def _get_profit_margin(self, product_type_id: int, cost: Decimal) -> Decimal:
        """
        Get profit margin from tiered structure in database
        
        Args:
            product_type_id: Product type ID from Quote_ProfitMargins table
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
    
    def _cello_type_name(self, cello_type: int) -> str:
        """Convert cello type number to human-readable name"""
        types = {0: 'None', 1: 'Gloss', 2: 'Matt'}
        return types.get(cello_type, 'Unknown')


# ============================================================================
# TOOL INTERFACE (For AI Agents and External Scripts)
# ============================================================================

def calculate_flyer_quote(
    db_connector,
    quantity: int,
    width: int,
    height: int,
    gsm: int,
    **kwargs
) -> Dict[str, Any]:
    """
    Tool-ready interface for flyer calculation
    
    This function provides a simple interface for AI agents and external scripts
    to calculate flyer quotes without dealing with class instantiation.
    
    Args:
        db_connector: Database connection object
        quantity: Number of flyers
        width: Width in mm
        height: Height in mm
        gsm: Paper weight
        **kwargs: Additional options (print_side1, print_side2, folding_required, etc.)
    
    Returns:
        Dictionary with quote result
    
    Example:
        from inhouse_modules.db_connector import InHousePrintDB
        
        db = InHousePrintDB("config/database-config.json")
        result = calculate_flyer_quote(
            db,
            quantity=1000,
            width=210,
            height=297,
            gsm=300,
            print_side1=1
        )
        print(f"Total: ${result['total_cost_inc_gst']:.2f}")
    """
    calc = FlyerCalculatorGOD(db_connector)
    result = calc.calculate(quantity, width, height, gsm, **kwargs)
    
    return {
        'success': result.success,
        'product_type': result.product_type,
        'quantity': result.quantity,
        'cost_to_business': float(result.cost_to_business),
        'profit_margin': float(result.profit_margin),
        'total_cost_ex_gst': float(result.total_cost_ex_gst),
        'total_cost_inc_gst': float(result.total_cost_inc_gst),
        'cost_per_unit_ex_gst': float(result.cost_per_unit_ex_gst),
        'cost_per_unit_inc_gst': float(result.cost_per_unit_inc_gst),
        'breakdown': result.breakdown,
        'specifications': result.specifications
    }


# ============================================================================
# TESTING AND DEMONSTRATION
# ============================================================================

def test_calculator():
    """Test the flyer calculator with various scenarios"""
    import sys
    import os
    
    # Add parent directories to path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools'))
    
    try:
        from db_connector import InHousePrintDB
    except ImportError:
        print("✗ Cannot import InHousePrintDB. Run from project root or ensure tools/db_connector.py exists.")
        return
    
    print("=" * 80)
    print("FLYER CALCULATOR GOD - TEST SUITE")
    print("=" * 80)
    
    # Initialize database connection
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database-config.json')
    db = InHousePrintDB(config_path)
    
    # Initialize calculator
    calc = FlyerCalculatorGOD(db)
    
    # Test 1: Standard A4 flyer, single-sided colour
    print("\n1. STANDARD A4 FLYER - 1000 qty, Single-Sided Colour")
    result1 = calc.calculate(
        quantity=1000,
        width=210,
        height=297,
        gsm=300,
        print_side1=1,  # Colour
        print_side2=0   # No print
    )
    print(f"   Stock: {result1.specifications['stock']}")
    print(f"   UPS: {result1.specifications['ups_per_sheet']}")
    print(f"   Sheets: {result1.specifications['sheets_needed']}")
    print(f"   Cost to Business: ${result1.cost_to_business:.2f}")
    print(f"   Profit Margin: {result1.specifications['profit_margin_pct']:.0f}%")
    print(f"   Price Ex GST: ${result1.total_cost_ex_gst:.2f}")
    print(f"   Price Inc GST: ${result1.total_cost_inc_gst:.2f}")
    print(f"   Cost per flyer: ${result1.cost_per_unit_inc_gst:.3f}")
    
    # Test 2: DL flyer with folding
    print("\n2. DL FLYER WITH FOLDING - 5000 qty, Double-Sided Colour, Half Fold")
    result2 = calc.calculate(
        quantity=5000,
        width=99,
        height=210,
        gsm=150,
        print_side1=1,  # Colour
        print_side2=1,  # Colour
        folding_required=True,
        folding_passes=1
    )
    print(f"   Stock: {result2.specifications['stock']}")
    print(f"   UPS: {result2.specifications['ups_per_sheet']}")
    print(f"   Folding: {result2.specifications['folding_passes']} pass(es)")
    print(f"   Price Inc GST: ${result2.total_cost_inc_gst:.2f}")
    print(f"   Folding cost: ${result2.breakdown['folding_cost']:.2f}")
    
    # Test 3: Business card size (using flyer calculator)
    print("\n3. BUSINESS CARDS (using flyer calculator) - 1000 qty, 90x55mm")
    result3 = calc.calculate(
        quantity=1000,
        width=90,
        height=55,
        gsm=350,
        print_side1=1,  # Colour
        print_side2=1   # Colour
    )
    print(f"   Stock: {result3.specifications['stock']}")
    print(f"   UPS: {result3.specifications['ups_per_sheet']}")
    print(f"   Price Inc GST: ${result3.total_cost_inc_gst:.2f}")
    print(f"   Cost per card: ${result3.cost_per_unit_inc_gst:.3f}")
    
    # Test 4: With cellophane lamination
    print("\n4. A5 FLYER WITH GLOSS CELLO - 2000 qty, Single-Sided")
    result4 = calc.calculate(
        quantity=2000,
        width=148,
        height=210,
        gsm=300,
        print_side1=1,  # Colour
        print_side2=0,  # No print
        cello_required=True,
        cello_side1=1,  # Gloss
        cello_side2=0   # No cello
    )
    print(f"   Stock: {result4.specifications['stock']}")
    print(f"   Cello: {result4.specifications['cello_side1']}")
    print(f"   Price Inc GST: ${result4.total_cost_inc_gst:.2f}")
    print(f"   Cello cost: ${result4.breakdown['cello_cost']:.2f}")
    
    # Test 5: Using tool interface
    print("\n5. USING TOOL INTERFACE - A4, 500 qty")
    result5 = calculate_flyer_quote(
        db,
        quantity=500,
        width=210,
        height=297,
        gsm=300,
        print_side1=1
    )
    print(f"   Total: ${result5['total_cost_inc_gst']:.2f}")
    print(f"   Success: {result5['success']}")
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)
    
    db.close()


if __name__ == '__main__':
    test_calculator()
