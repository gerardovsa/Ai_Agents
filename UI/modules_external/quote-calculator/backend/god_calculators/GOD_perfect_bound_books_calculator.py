"""
GOD Perfect Bound Books Calculator
===================================
Database-driven perfect bound book quote calculator using SQL Server production data.

Extracted from complete_calculator_implementation.py lines 3097-3450 + helper methods 5900-6170.
Based on VB.NET source: PerfectBBQuote.vb lines 1-745

Key Features:
- Perfect Bound binding (database tier pricing)
- Cover calculation with optimized stock selection
- Internal pages (simple/scattered/sequential color modes)
- Celloglaze lamination
- Scoring support
- Extra books scale (after profit margin)
- GST calculation

Database Tables Used:
- Quote_DigitalStocks: Paper stock pricing
- Quote_DigitalStockType: Stock type names
- Quote_DigitalClicks: Digital printing click prices
- Quote_ProfitMargins: Profit margin by product
- Quote_GenericSetting: Configuration values
- Quote_PBBPerBookBindCost: Perfect binding cost tiers
- Quote_PBBExtraBookScale: Extra book quantities by order size

Version: 1.0
Date: October 2025
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import sys
import os

# Database connector path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from inhouse_modules.db_connector import InHousePrintDB


@dataclass
class QuoteResult:
    """Perfect Bound Books quote calculation result"""
    # Pricing
    unit_price: Decimal
    total_price: Decimal
    total_inc_gst: Decimal
    
    # Cost breakdown
    cover_cost: Decimal
    internal_cost: Decimal
    cello_cost: Decimal
    binding_cost: Decimal
    trimming_cost: Decimal
    cutting_cost: Decimal
    scoring_cost: Decimal
    imposition_setup: Decimal
    proof_cost: Decimal
    extra_books: Decimal
    
    # Specifications
    specifications: Dict[str, Any]


class PerfectBoundBooksCalculator:
    """Database-driven Perfect Bound Books quote calculator"""
    
    def __init__(self, config_path: str = None):
        """Initialize calculator with database connection"""
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 
                'config', 
                'database-config.json'
            )
        
        self.db = InHousePrintDB(config_path)
        self._load_database_configuration()
    
    def _load_database_configuration(self):
        """Load all configuration from database (same pattern as flyer calculator)"""
        # Digital stocks (paper types)
        stocks_query = """
        SELECT 
            StockID,
            StockTypeID,
            Length,
            Width,
            CostPerThousand,
            GSM,
            Markup
        FROM Quote_DigitalStocks
        ORDER BY StockID
        """
        stocks_df = self.db.execute_query(stocks_query)
        self.digital_stocks = []
        for row in stocks_df.itertuples(index=False):
            self.digital_stocks.append({
                'stock_id': int(row.StockID),
                'stock_type_id': int(row.StockTypeID),
                'width': int(row.Length),  # Note: Length is width in database
                'height': int(row.Width),  # Note: Width is height in database
                'cost_per_thousand': Decimal(str(row.CostPerThousand)),
                'gsm': int(row.GSM),  # Convert to int for type consistency
                'markup': Decimal(str(row.Markup))
            })
        
        # Digital clicks (printing prices)
        clicks_query = """
        SELECT 
            DigitalClickID,
            ClickDesc,
            ClickPricePerA4
        FROM Quote_DigitalClicks
        ORDER BY DigitalClickID
        """
        clicks_df = self.db.execute_query(clicks_query)
        self.digital_clicks = {}
        for row in clicks_df.itertuples(index=False):
            self.digital_clicks[row.DigitalClickID] = {
                'description': row.ClickDesc,
                'price_per_a4': Decimal(str(row.ClickPricePerA4))
            }
        
        # Profit margins (tiered by cost)
        margins_query = """
        SELECT 
            ProductTypeID,
            StartPrice,
            EndPrice,
            Margin
        FROM Quote_ProfitMargins
        WHERE ProductTypeID = 4
        ORDER BY StartPrice
        """
        margins_df = self.db.execute_query(margins_query)
        self.profit_margin_tiers = []
        for row in margins_df.itertuples(index=False):
            self.profit_margin_tiers.append({
                'product_type_id': row.ProductTypeID,
                'start_price': Decimal(str(row.StartPrice)),
                'end_price': Decimal(str(row.EndPrice)),
                'margin': Decimal(str(row.Margin))
            })
        
        # Generic settings (parse with type handling)
        settings_query = """
        SELECT 
            SettingDesc,
            SettingValue
        FROM Quote_GenericSetting
        """
        settings_df = self.db.execute_query(settings_query)
        self.generic_settings = {}
        for row in settings_df.itertuples(index=False):
            self.generic_settings[row.SettingDesc] = self._parse_config_value(row.SettingValue)
        
        # Perfect Bound Book binding cost tiers
        binding_query = """
        SELECT 
            StartQty,
            EndQTY,
            CostPerBook
        FROM Quote_PBBPerBookBindCost
        ORDER BY StartQty
        """
        binding_df = self.db.execute_query(binding_query)
        self.pbb_binding_costs = []
        for row in binding_df.itertuples(index=False):
            self.pbb_binding_costs.append({
                'start_qty': row.StartQty,
                'end_qty': row.EndQTY,
                'cost_per_book': Decimal(str(row.CostPerBook))
            })
        
        # Extra book scale
        extra_query = """
        SELECT 
            StartQty,
            EndQty,
            BookAmount
        FROM Quote_PBBExtraBookScale
        ORDER BY StartQty
        """
        extra_df = self.db.execute_query(extra_query)
        self.pbb_extra_books = []
        for row in extra_df.itertuples(index=False):
            self.pbb_extra_books.append({
                'start_qty': row.StartQty,
                'end_qty': row.EndQty,
                'book_amount': row.BookAmount
            })
    
    def _parse_config_value(self, value_str: str):
        """Parse configuration value to appropriate type"""
        if value_str is None:
            return None
        
        value_str = str(value_str).strip()
        
        # Handle booleans
        if value_str.lower() in ('true', 'false'):
            return value_str.lower() == 'true'
        
        # Try parsing as number (int or Decimal)
        try:
            if '.' in value_str:
                return Decimal(value_str)
            else:
                return int(value_str)
        except (ValueError, InvalidOperation):
            pass
        
        # Return as string if nothing else works
        return value_str
    
    def get_config(self, setting_name: str) -> Decimal:
        """Get configuration value from generic settings"""
        if setting_name not in self.generic_settings:
            raise ValueError(f"Configuration setting '{setting_name}' not found in database")
        value = self.generic_settings[setting_name]
        # Convert to Decimal for calculations
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        elif isinstance(value, Decimal):
            return value
        else:
            return Decimal(str(value))
    
    def calculate(
        self,
        quantity: int,
        book_width: int,
        book_height: int,
        pages: int,
        stock_type_id: int = 1,  # 1 = Standard Digital (Bond)
        internal_stock_gsm: int = 80,
        internal_print_mode: int = 0,  # 0=Colour, 1=B&W, 2=Both (scattered)
        cover_stock_type_id: int = 1,
        cover_stock_gsm: int = 300,
        cover_print_mode: int = 1,  # 0=2pp (one side), 1=4pp (both sides)
        cello_type: int = 0,  # 0=None, 1=Gloss, 2=Matt
        is_scored: bool = False,
        colour_pages: int = 0,  # For scattered color mode
        colour_insert_type: str = "simple",  # "simple", "scattered", "sequential"
        artworks: int = 1,
        discount: Decimal = Decimal('0')
    ) -> QuoteResult:
        """
        Calculate Perfect Bound Book quote
        
        Parameters:
        -----------
        quantity : int
            Number of books to print
        book_width : int
            Book width in mm (closed)
        book_height : int
            Book height in mm
        pages : int
            Total number of internal pages (must be divisible by 4)
        stock_type_id : int
            Internal stock type (1=Bond, 2=Silk, etc.)
        internal_stock_gsm : int
            Internal paper weight (80, 100, 120, etc.)
        internal_print_mode : int
            0=Colour, 1=B&W (only for simple mode)
        cover_stock_type_id : int
            Cover stock type
        cover_stock_gsm : int
            Cover paper weight (250, 300, 350, etc.)
        cover_print_mode : int
            0=2pp (one side), 1=4pp (both sides)
        cello_type : int
            0=None, 1=Gloss, 2=Matt
        is_scored : bool
            Whether cover needs scoring
        colour_pages : int
            Number of color pages for scattered/sequential modes
        colour_insert_type : str
            "simple", "scattered", or "sequential"
        artworks : int
            Number of different artworks/designs
        discount : Decimal
            Discount percentage (0-100)
            
        Returns:
        --------
        QuoteResult with pricing and cost breakdown
        """
        # Convert all numeric parameters to proper types (defensive programming)
        quantity = int(quantity)
        book_width = int(book_width)
        book_height = int(book_height)
        pages = int(pages)
        stock_type_id = int(stock_type_id)
        internal_stock_gsm = int(internal_stock_gsm)
        internal_print_mode = int(internal_print_mode)
        cover_stock_type_id = int(cover_stock_type_id)
        cover_stock_gsm = int(cover_stock_gsm)
        cover_print_mode = int(cover_print_mode)
        cello_type = int(cello_type)
        colour_pages = int(colour_pages)
        artworks = int(artworks)
        
        # Validate pages (must be divisible by 4)
        if pages % 4 != 0:
            raise ValueError("Pages must be divisible by 4 for proper imposition")
        
        # Load configuration values
        waste_percentage = (self.get_config('MaterialWastePercentage') / Decimal('100')) + Decimal('1')
        imposition_setup = self.get_config('DigitalImpositionSetup') * Decimal('2')  # DOUBLED per VB.NET
        
        # Cutting cost components (VB.NET: PBBGuiloSetup, PBBCuttingBlocks, PBBGuiloCostPerBlock)
        guillo_setup = self.get_config('PBBGuiloSetup')  # SettingID 58: $10
        cutting_blocks = self.get_config('PBBCuttingBlocks')  # SettingID 59: 500 sheets
        cost_per_block = self.get_config('PBBGuiloCostPerBlock')  # SettingID 60: $5
        
        # Trimming cost components (VB.NET: PBBTrimmerSetup, PBBThreeWayCostPerBook)
        trimmer_setup = self.get_config('PBBTrimmerSetup')  # SettingID 49: $10
        three_way_cost = self.get_config('PBBThreeWayCostPerBook')  # SettingID 52: $0.30/book
        
        # Proof cost (VB.NET: PBBProofCost)
        proof_cost = self.get_config('PBBProofCost') * Decimal(str(artworks))  # SettingID 50: $60
        
        # === COVER CALCULATION ===
        open_width = book_width * 2  # Cover wraps around front and back
        cover_cost, cover_sheets, cover_stock = self._calculate_pbb_cover(
            cover_stock_type_id, cover_stock_gsm, quantity,
            open_width, book_height, cover_print_mode
        )
        
        # === CELLOGLAZE COST ===
        if cello_type > 0:
            cello_cost = self._calculate_pbb_cello(
                cello_type, cover_sheets, cover_stock['width'], cover_stock['height']
            )
        else:
            cello_cost = Decimal('0')
        
        # === INTERNAL PAGES CALCULATION ===
        if colour_insert_type == "simple":
            internal_cost, internal_sheets = self._calculate_pbb_internals_simple(
                stock_type_id, internal_stock_gsm, quantity,
                book_width, book_height, pages, internal_print_mode
            )
        elif colour_insert_type == "scattered":
            internal_cost, internal_sheets = self._calculate_pbb_internals_scattered(
                stock_type_id, internal_stock_gsm, quantity,
                book_width, book_height, pages, colour_pages
            )
        elif colour_insert_type == "sequential":
            internal_cost, internal_sheets = self._calculate_pbb_internals_sequential(
                stock_type_id, internal_stock_gsm, quantity,
                book_width, book_height, pages, colour_pages
            )
        else:
            raise ValueError(f"Invalid colour_insert_type: {colour_insert_type}")
        
        # === BINDING COST ===
        cost_per_book = self._get_binding_cost(quantity)
        binding_setup = self.get_config('PBBBinderSetup')  # From database (SettingID 48)
        total_binding_cost = binding_setup + (Decimal(str(quantity)) * cost_per_book)
        
        # === CUTTING COST (VB.NET Lines 227-228) ===
        # Must calculate AFTER cover and internals to get total sheets
        total_sheets = cover_sheets + internal_sheets
        cutting_cost = guillo_setup + ((total_sheets / cutting_blocks) * cost_per_block)
        
        # === SCORING COST ===
        if is_scored:
            scoring_cost = self._calculate_scoring_cost(quantity)
        else:
            scoring_cost = Decimal('0')
        
        # === TRIMMING COST (VB.NET Lines 238-239) ===
        # Three-way trim: setup + per-book cost × quantity
        trimming_cost = trimmer_setup + (three_way_cost * Decimal(str(quantity)))
        
        # === TOTAL COST BEFORE PROFIT ===
        subtotal = (
            cover_cost +
            cello_cost +
            internal_cost +
            imposition_setup +
            cutting_cost +
            scoring_cost +
            total_binding_cost +
            trimming_cost +
            proof_cost
        )
        
        # === PROFIT MARGIN (Tiered by cost) ===
        profit_margin = self._get_profit_margin(subtotal)
        profit_multiplier = Decimal('1') + (profit_margin / Decimal('100'))
        job_value_with_profit = subtotal * profit_multiplier
        
        # === EXTRA BOOKS COST (AFTER PROFIT MARGIN - VB.NET line 256) ===
        extra_books_cost = self._calculate_extra_book_cost(quantity, job_value_with_profit)
        
        # === DISCOUNT ===
        if discount > Decimal('0'):
            discount_multiplier = Decimal('1') - (discount / Decimal('100'))
            job_value_with_profit = job_value_with_profit * discount_multiplier
        
        # === FINAL TOTAL ===
        total_ex_gst = job_value_with_profit + extra_books_cost
        gst = total_ex_gst * Decimal('0.10')
        total_inc_gst = total_ex_gst + gst
        
        # Unit price
        unit_price = total_ex_gst / Decimal(str(quantity))
        
        # Build specifications
        specifications = {
            'quantity': quantity,
            'size': f"{book_width}x{book_height}mm",
            'pages': pages,
            'cover_gsm': cover_stock_gsm,
            'internal_gsm': internal_stock_gsm,
            'cover_print': '4pp (both sides)' if cover_print_mode == 1 else '2pp (one side)',
            'internal_print': 'Colour' if internal_print_mode == 0 else 'B&W',
            'cello': 'None' if cello_type == 0 else ('Gloss' if cello_type == 1 else 'Matt'),
            'scored': is_scored,
            'colour_insert_type': colour_insert_type,
            'artworks': artworks
        }
        
        return QuoteResult(
            unit_price=unit_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            total_price=total_ex_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            total_inc_gst=total_inc_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            cover_cost=cover_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            internal_cost=internal_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            cello_cost=cello_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            binding_cost=total_binding_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            trimming_cost=trimming_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            cutting_cost=cutting_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            scoring_cost=scoring_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            imposition_setup=imposition_setup.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            proof_cost=proof_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            extra_books=extra_books_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            specifications=specifications
        )
    
    # ========================================================================
    # HELPER METHODS (Extracted from complete_calculator_implementation.py)
    # ========================================================================
    
    def _calculate_pbb_cover(
        self, 
        stock_type_id: int, 
        cover_gsm: int, 
        quantity: int,
        open_width: int, 
        book_height: int, 
        print_mode: int
    ):
        """
        Calculate PBB cover cost using EXACT VB.NET logic from PerfectBBQuote.vb lines 240-337
        
        VB.NET Key Points:
        - 1 cover per book (ups = 1)
        - Select cheapest stock that fits open_width x book_height
        - Sheets = quantity × wastePercentage
        - Paper cost = (sheets / 1000) × (cost_per_thousand × (1 + markup))
        - Click count based on stock height: >483mm = Banner (3 A4), else SRA3 (2 A4)
        """
        bleed = self.get_config('FlyerBleedMeasurement')
        waste_percentage = (self.get_config('MaterialWastePercentage') / Decimal('100')) + Decimal('1')
        colour_click = self.digital_clicks[1]['price_per_a4']  # Colour click
        
        # Find matching stocks
        stocks = [s for s in self.digital_stocks 
                 if s['stock_type_id'] == stock_type_id and s['gsm'] == cover_gsm]
        
        if not stocks:
            # Debug: Show ALL available stocks
            all_types = set((s['stock_type_id'], s['gsm']) for s in self.digital_stocks)
            raise ValueError(f"No cover stock found for type {stock_type_id} GSM {cover_gsm}. Available stocks (type_id, GSM): {sorted(all_types)}")
        
        # Find cheapest stock that fits (VB.NET logic)
        best_stock = None
        cheapest_cost = None
        
        for stock in stocks:
            # Check if size fits (need room for bleed) - try both orientations
            # Orientation 1: open_width along height dimension
            fit1 = int(stock['height'] / (open_width + bleed)) * int(stock['width'] / (book_height + bleed))
            
            # Orientation 2: open_width along width dimension
            fit2 = int(stock['width'] / (open_width + bleed)) * int(stock['height'] / (book_height + bleed))
            
            # Use best orientation
            ups = max(fit1, fit2)
            
            if ups == 0:
                continue  # Can't fit
            
            cost_of_sheet = stock['cost_per_thousand'] / Decimal('1000')
            
            if cheapest_cost is None or cost_of_sheet < cheapest_cost:
                cheapest_cost = cost_of_sheet
                best_stock = stock
        
        if best_stock is None:
            # Debug info
            all_sheets = [(s['width'], s['height']) for s in stocks[:5]]
            raise ValueError(f"Cover size {open_width}x{book_height}mm cannot fit on available sheets. Sample sheets: {all_sheets}")
        
        # Calculate cover costs (VB.NET formula)
        markup = best_stock['markup'] / Decimal('100')
        cover_sheets = Decimal(str(quantity)) * waste_percentage
        
        # Determine click count based on stock height
        if best_stock['height'] > 483:
            a4_clicks = 3  # Banner
        else:
            a4_clicks = 2  # SRA3
        
        # Paper cost
        paper_cost = (cover_sheets / Decimal('1000')) * (best_stock['cost_per_thousand'] * (Decimal('1') + markup))
        
        # Click cost based on print mode
        if print_mode == 0:  # 2pp (one side only)
            click_cost = cover_sheets * (colour_click * Decimal(str(a4_clicks)))
        elif print_mode == 1:  # 4pp (both sides)
            click_cost = (cover_sheets * (colour_click * Decimal(str(a4_clicks)))) * Decimal('2')
        else:
            click_cost = Decimal('0')
        
        total_cover_cost = paper_cost + click_cost
        
        return total_cover_cost, cover_sheets, best_stock
    
    def _calculate_pbb_cello(
        self, 
        cello_type: int, 
        cover_sheets: Decimal, 
        stock_width: int, 
        stock_height: int
    ):
        """
        Calculate PBB cello cost using EXACT VB.NET logic from PerfectBBQuote.vb lines 382-432
        
        VB.NET Key Points:
        - If stock_height < 455: Use WIDE roll (based on stock_width)
        - If stock_height >= 455: Use SHORT roll (based on stock_height)
        - Material cost = ((sheets × dimension) / 1000) × rate_per_meter
        - Time = ((sheets × stock_width) / 1000) / meters_per_min
        - Labor = (time / 60) × cost_per_hour
        - Total = material + setup + labor
        
        cello_type: 0=None, 1=Gloss, 2=Matt
        """
        if cello_type == 0:
            return Decimal('0')
        
        # Get config values
        cello_setup = self.get_config('CelloSetupCost')
        cello_gloss_short = self.get_config('CelloGlossShortPerM')
        cello_gloss_wide = self.get_config('CelloGlossWidePerM')
        cello_matt_short = self.get_config('CellMattShortPerM')
        cello_matt_wide = self.get_config('CelloMattWidePerM')
        cello_cost_per_hour = self.get_config('CelloCostPerHour')
        cello_meters_per_min = self.get_config('SpeedMPerMin')
        
        sheets = Decimal(str(cover_sheets))
        width = Decimal(str(stock_width))
        height = Decimal(str(stock_height))
        
        # Determine roll type and calculate (VB.NET logic)
        if height < Decimal('455'):
            # Wide roll
            if cello_type == 1:  # Gloss
                material_cost = ((sheets * width) / Decimal('1000')) * cello_gloss_wide
            else:  # Matt
                material_cost = ((sheets * width) / Decimal('1000')) * cello_matt_wide
            
            # Time calculation (ALWAYS uses width for time, even for wide roll)
            time_to_cello = ((sheets * width) / Decimal('1000')) / cello_meters_per_min
        else:
            # Short roll
            if cello_type == 1:  # Gloss
                material_cost = ((sheets * height) / Decimal('1000')) * cello_gloss_short
            else:  # Matt
                material_cost = ((sheets * height) / Decimal('1000')) * cello_matt_short
            
            # Time calculation (ALWAYS uses width for time, VB.NET line 418)
            time_to_cello = ((sheets * width) / Decimal('1000')) / cello_meters_per_min
        
        # Labor cost
        labor_cost = (time_to_cello / Decimal('60')) * cello_cost_per_hour
        
        # Total
        total_cello_cost = material_cost + cello_setup + labor_cost
        
        return total_cello_cost
    
    def _calculate_pbb_internals_simple(
        self,
        stock_type_id: int,
        internal_gsm: int,
        quantity: int,
        book_width: int,
        book_height: int,
        pages: int,
        print_mode: int
    ):
        """
        Calculate PBB internal pages using EXACT VB.NET logic from PerfectBBQuote.vb lines 660-730
        
        VB.NET Key Points:
        - Calculate best ups (pages per sheet) by trying both orientations
        - Sheets = ((quantity × pages) / 2) / ups × wastePercentage
        - Paper cost = (sheets / 1000) × (cost_per_thousand × (1 + markup))
        - Click cost = (sheets × 2) × (click_price × A4_clicks)
        - print_mode: 0=Colour, 1=B&W
        """
        bleed = self.get_config('FlyerBleedMeasurement')
        waste_percentage = (self.get_config('MaterialWastePercentage') / Decimal('100')) + Decimal('1')
        colour_click = self.digital_clicks[1]['price_per_a4']  # Colour
        bw_click = self.digital_clicks[2]['price_per_a4']      # B&W
        
        # Find matching stocks
        stocks = [s for s in self.digital_stocks 
                 if s['stock_type_id'] == stock_type_id and s['gsm'] == internal_gsm]
        
        if not stocks:
            raise ValueError(f"No internal stock found for type {stock_type_id} GSM {internal_gsm}")
        
        # Find best ups and cheapest stock (VB.NET logic lines 688-726)
        best_stock = None
        best_ups = 0
        cheapest_unit_cost = None
        
        for stock in stocks:
            # Try orientation 1: book_width × book_height
            across1 = int(stock['width'] / (Decimal(str(book_width)) + bleed))
            down1 = int(stock['height'] / (Decimal(str(book_height)) + bleed))
            ups1 = across1 * down1
            
            # Try orientation 2: book_height × book_width (rotated)
            across2 = int(stock['width'] / (Decimal(str(book_height)) + bleed))
            down2 = int(stock['height'] / (Decimal(str(book_width)) + bleed))
            ups2 = across2 * down2
            
            # Best ups for this stock
            temp_best_ups = max(ups1, ups2)
            
            if temp_best_ups == 0:
                continue  # Can't fit
            
            # Calculate unit cost
            cost_of_sheet = stock['cost_per_thousand'] / Decimal('1000')
            unit_cost = cost_of_sheet / Decimal(str(temp_best_ups))
            
            if cheapest_unit_cost is None or unit_cost < cheapest_unit_cost:
                cheapest_unit_cost = unit_cost
                best_stock = stock
                best_ups = temp_best_ups
        
        if best_stock is None:
            raise ValueError(f"Internal size {book_width}x{book_height}mm cannot fit on available sheets")
        
        # Calculate internal costs (VB.NET formulas)
        markup = best_stock['markup'] / Decimal('100')
        
        # Sheet count: ((qty × pages) / 2) / ups × waste
        # Pages / 2 because each sheet prints 2 pages (front and back)
        internal_sheets = ((Decimal(str(quantity)) * Decimal(str(pages))) / Decimal('2')) / Decimal(str(best_ups))
        internal_sheets = internal_sheets * waste_percentage
        
        # Determine click count based on stock height
        if best_stock['height'] > 483:
            a4_clicks = 3  # Banner
        else:
            a4_clicks = 2  # SRA3
        
        # Paper cost
        paper_cost = (internal_sheets / Decimal('1000')) * (best_stock['cost_per_thousand'] * (Decimal('1') + markup))
        
        # Click cost (sheets × 2 for front and back)
        if print_mode == 0:  # Colour
            click_cost = (internal_sheets * Decimal('2')) * (colour_click * Decimal(str(a4_clicks)))
        elif print_mode == 1:  # B&W
            click_cost = (internal_sheets * Decimal('2')) * (bw_click * Decimal(str(a4_clicks)))
        else:
            click_cost = Decimal('0')
        
        total_internal_cost = paper_cost + click_cost
        
        return total_internal_cost, internal_sheets
    
    def _calculate_pbb_internals_scattered(
        self,
        stock_type_id: int,
        internal_gsm: int,
        quantity: int,
        book_width: int,
        book_height: int,
        total_pages: int,
        colour_pages: int
    ):
        """
        Calculate scattered colour internals (colour pages distributed throughout)
        """
        # Calculate B&W pages
        bw_pages = total_pages - colour_pages
        
        # Calculate costs separately
        colour_cost, colour_sheets = self._calculate_pbb_internals_simple(
            stock_type_id, internal_gsm, quantity, book_width, book_height, colour_pages, 0
        )
        
        bw_cost, bw_sheets = self._calculate_pbb_internals_simple(
            stock_type_id, internal_gsm, quantity, book_width, book_height, bw_pages, 1
        )
        
        return colour_cost + bw_cost, colour_sheets + bw_sheets
    
    def _calculate_pbb_internals_sequential(
        self,
        stock_type_id: int,
        internal_gsm: int,
        quantity: int,
        book_width: int,
        book_height: int,
        total_pages: int,
        colour_pages: int
    ):
        """
        Calculate sequential colour internals (colour pages at start or end)
        """
        # For sequential, use same logic as scattered (simplified)
        return self._calculate_pbb_internals_scattered(
            stock_type_id, internal_gsm, quantity,
            book_width, book_height, total_pages, colour_pages
        )
    
    def _calculate_scoring_cost(self, quantity: int) -> Decimal:
        """Calculate scoring cost"""
        setup = self.get_config('FoldingSetupCost')
        per_1000 = self.get_config('FoldingCostPer1000')
        return setup + ((Decimal(str(quantity)) / Decimal('1000')) * per_1000)
    
    def _get_binding_cost(self, quantity: int) -> Decimal:
        """
        Get binding cost per book from Quote_PBBPerBookBindCost table
        VB.NET: Lines 524-535 in PerfectBBQuote.vb
        """
        # Default to $1.00/book if no scale found (VB.NET behavior)
        cost_per_book = Decimal('1.00')
        
        # Lookup in scale table
        for scale in self.pbb_binding_costs:
            if quantity >= scale['start_qty'] and quantity <= scale['end_qty']:
                cost_per_book = scale['cost_per_book']
                break
        
        return cost_per_book
    
    def _get_profit_margin(self, cost_to_business: Decimal) -> Decimal:
        """
        Get profit margin percentage based on cost to business
        Uses tiered margin system from Quote_ProfitMargins (ProductTypeID 4)
        """
        # Default to 45% if no tier found
        margin = Decimal('45')
        
        # Lookup in tier table
        for tier in self.profit_margin_tiers:
            if cost_to_business >= tier['start_price'] and cost_to_business <= tier['end_price']:
                margin = tier['margin']
                break
        
        return margin
    
    def _calculate_extra_book_cost(self, quantity: int, job_value: Decimal) -> Decimal:
        """
        Calculate extra book allowance from Quote_PBBExtraBookScale table
        VB.NET: Lines 537-551 in PerfectBBQuote.vb
        
        This calculates the cost of "extra books" (over-run) which is added
        to the final price AFTER profit margin is applied.
        
        Formula: (job_value / quantity) * extra_book_count
        """
        # Default to 4 extra books if no scale found (VB.NET behavior)
        extra_book_count = 4
        
        # Lookup in scale table
        for scale in self.pbb_extra_books:
            if quantity >= scale['start_qty'] and quantity <= scale['end_qty']:
                extra_book_count = scale['book_amount']
                break
        
        # Calculate cost: price per unit × extra book count
        return (job_value / Decimal(str(quantity))) * Decimal(str(extra_book_count))
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# ============================================================================
# TOOL INTERFACE FOR CLAUDE AI
# ============================================================================

def calculate_perfect_bound_book_quote(
    quantity: int,
    book_width: int,
    book_height: int,
    pages: int,
    internal_gsm: int = 80,
    cover_gsm: int = 300,
    cello: str = "none",
    internal_print: str = "colour",
    cover_print: str = "both_sides",
    scored: bool = False
) -> Dict[str, Any]:
    """
    Calculate Perfect Bound Book quote using GOD (database-driven) pricing
    
    Tool interface for Claude AI to generate perfect bound book quotes.
    
    Parameters:
    -----------
    quantity : int
        Number of books to print (minimum 50)
    book_width : int
        Book width in mm (closed size)
    book_height : int
        Book height in mm
    pages : int
        Number of internal pages (must be divisible by 4)
    internal_gsm : int
        Internal paper weight (80, 100, 120, etc.)
    cover_gsm : int
        Cover paper weight (250, 300, 350, etc.)
    cello : str
        Celloglaze type: "none", "gloss", or "matt"
    internal_print : str
        Internal printing: "colour" or "bw"
    cover_print : str
        Cover printing: "one_side" or "both_sides"
    scored : bool
        Whether cover needs scoring
        
    Returns:
    --------
    Dictionary with quote details:
        - unit_price: Price per book
        - total_price: Total ex GST
        - total_inc_gst: Total inc GST
        - breakdown: Cost components
        - specifications: Quote specifications
    """
    # Input validation
    if quantity < 50:
        return {"error": "Minimum quantity is 50 books"}
    
    if pages % 4 != 0:
        return {"error": "Pages must be divisible by 4 for proper imposition"}
    
    # Map string parameters to numeric codes
    cello_map = {"none": 0, "gloss": 1, "matt": 2}
    cello_code = cello_map.get(cello.lower(), 0)
    
    print_map = {"colour": 0, "bw": 1}
    internal_print_code = print_map.get(internal_print.lower(), 0)
    
    cover_map = {"one_side": 0, "both_sides": 1}
    cover_print_code = cover_map.get(cover_print.lower(), 1)
    
    try:
        with PerfectBoundBooksCalculator() as calc:
            result = calc.calculate(
                quantity=quantity,
                book_width=book_width,
                book_height=book_height,
                pages=pages,
                internal_stock_gsm=internal_gsm,
                cover_stock_gsm=cover_gsm,
                cello_type=cello_code,
                internal_print_mode=internal_print_code,
                cover_print_mode=cover_print_code,
                is_scored=scored,
                colour_insert_type="simple"
            )
            
            return {
                "unit_price": float(result.unit_price),
                "total_price": float(result.total_price),
                "total_inc_gst": float(result.total_inc_gst),
                "breakdown": {
                    "cover": float(result.cover_cost),
                    "internals": float(result.internal_cost),
                    "celloglaze": float(result.cello_cost),
                    "binding": float(result.binding_cost),
                    "trimming": float(result.trimming_cost),
                    "cutting": float(result.cutting_cost),
                    "scoring": float(result.scoring_cost),
                    "setup": float(result.imposition_setup),
                    "proof": float(result.proof_cost),
                    "extra_books": float(result.extra_books)
                },
                "specifications": result.specifications
            }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("GOD Perfect Bound Books Calculator - Test Run")
    print("="*70 + "\n")
    
    # Test case: A5 book, 100 pages
    print("Test Case: A5 Book (148x210mm), 100 pages, 300GSM cover, gloss cello")
    print("-" * 70)
    
    result = calculate_perfect_bound_book_quote(
        quantity=250,
        book_width=148,
        book_height=210,
        pages=100,
        internal_gsm=80,
        cover_gsm=300,
        cello="gloss",
        internal_print="bw",
        cover_print="both_sides",
        scored=True
    )
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print(f"\nUnit Price: ${result['unit_price']:.2f}")
        print(f"Total (ex GST): ${result['total_price']:.2f}")
        print(f"Total (inc GST): ${result['total_inc_gst']:.2f}")
        print(f"\nCost Breakdown:")
        for component, cost in result['breakdown'].items():
            print(f"  {component.title():.<20} ${cost:>8.2f}")
        print(f"\nSpecifications:")
        for key, value in result['specifications'].items():
            print(f"  {key.title():.<20} {value}")
    
    print("\n" + "="*70 + "\n")
