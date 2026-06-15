"""
Saddle Stitch Books Shopify Calculator
Exact implementation of Shopify JavaScript formula for Saddle Stitch Books

Based on: Shopify_Saddle_Stitch_Books.json specification
Platform: Shopify (separate from WooCommerce calculators)
Fields: 10 fields (Shopify-specific structure)
Key Features: Tiered padding rates, profit margins, double GST application
"""

import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# Import config manager
from config_manager import config_manager


@dataclass
class SaddleStitchBooksShopifyCalculatorQuoteResult:
    """Result from Saddle Stitch Books Shopify calculation"""
    total_price: Decimal
    unit_price: Decimal
    cost_per_item: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SaddleStitchBooksShopifyCalculator:
    """
    Saddle Stitch Books Shopify Calculator - Exact Shopify JavaScript Implementation
    
    SHOPIFY-SPECIFIC CALCULATOR - SEPARATE FROM WOOCOMMERCE
    
    Features:
    - 10-field Shopify structure
    - Tiered padding rates (0 tiers)
    - Tiered profit margins (14 tiers)
    - Artwork setup costs
    - DOUBLE GST APPLICATION (Shopify-specific: Total * 1.1 * 1.1)
    """
    
    CONFIG_FILE = "Shopify_Saddle_Stitch_Books.json"
    
    def __init__(self, config_path: str = None):
        """Initialize Saddle Stitch Books Shopify calculator"""
        if config_path:
            self.config = self._load_config(config_path)
        else:
            # Use unified config manager (searches multiple paths)
            try:
                self.config = config_manager.load_shopify_config(self.CONFIG_FILE)
            except FileNotFoundError as e:
                print(f"⚠️  Warning: {e}")
                self.config = None
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate(
        self,
        quantity: str,
        artworks: int = 1,
        cover_option: str = "Hard Cover",
        cover_stock: str = "Satin 200GSM",
        cover_print_type: str = "2 side colour (4pp)",
        celloglaze: str = "None",
        printed_pages: str = "16pp",
        finish_size: str = "A4 Portrait",
        content_print_type: str = "Colour",
        content_stock_type: str = "Uncoated Bond 80GSM"
    ) -> SaddleStitchBooksShopifyCalculatorQuoteResult:
        """
        Calculate Saddle Stitch Books Shopify quote
        
        Args:
            quantity: Number of books (as string: "25", "50", etc.)
            artworks: Number of different artwork designs
            cover_option: "Self Cover" or "Hard Cover"
            cover_stock: Cover paper stock (e.g., "Satin 200GSM")
            cover_print_type: Cover printing (e.g., "2 side colour (4pp)")
            celloglaze: Celloglaze option (e.g., "None", "Gloss outside only")
            printed_pages: Total page count (e.g., "16pp")
            finish_size: Book size (e.g., "A4 Portrait")
            content_print_type: Content printing (e.g., "Colour")
            content_stock_type: Content paper stock (e.g., "Uncoated Bond 80GSM")
        
        Returns:
            SaddleStitchBooksShopifyCalculatorQuoteResult with pricing details
        """
        if not self.config:
            raise ValueError("Configuration not loaded")
        
        # Parse quantity from string
        qty = int(quantity)
        
        # Convert artworks to int if it's a string
        artworks = int(artworks) if isinstance(artworks, str) else artworks
        
        # Extract pricing from config
        config = self.config['shopify_saddle_stitch_books']
        options = {opt['name']: opt for opt in config['options']}
        constants = config['pricing_constants']
        
        # Get field prices
        cover_stock_price = self._get_option_price(options['Cover Stock'], cover_stock)
        cover_print_price = self._get_option_price(options['Cover Print Type'], cover_print_type)
        cello_price = self._get_option_price(options['Celloglaze'], celloglaze)
        # F7: Printed Pages - the "price" field is the SHEET COUNT (e.g., "16pp" = price 4 = 4 sheets)
        pages_sheet_count = self._get_option_price(options['Printed Pages'], printed_pages)
        finish_multiplier = self._get_option_price(options['Finish Size'], finish_size)
        content_print_price = self._get_option_price(options['Content Print Type'], content_print_type)
        content_stock_price = self._get_option_price(options['Content Stock Type'], content_stock_type)
        
        # Setup costs
        setup = constants['setup_costs']
        guilo_setup = Decimal(str(setup['guilo_setup']))
        impos_setup = Decimal(str(setup['impos_setup']))
        binder_setup = Decimal(str(setup['binder_setup']))
        extra_arts = Decimal(str(setup['extra_arts'])) * max(0, artworks - 1)
        
        # Celloglaze setup (conditional)
        cello_setup = Decimal(str(constants['conditional_setup']['cello_setup'])) if celloglaze != "None" else Decimal('0')
        
        # Production constants
        prod = constants['production_constants']
        stock_waste = Decimal(str(prod['stock_waste']))
        cutting_block = Decimal(str(prod['cutting_block']))
        cut_cost = Decimal(str(prod['cut_cost']))
        binder_per_book = Decimal(str(prod['binder_per_book']))
        bindery_labor = Decimal(str(prod['bindery_labor_per_hour']))
        binder_sheets_hour = Decimal(str(prod['binder_sheets_per_hour']))
        
        # =========================================================================
        # EXACT TXT FORMULA IMPLEMENTATION (Lines 3078-3089)
        # =========================================================================
        
        # TXT Line 3078: totalCoverSheetsA3 = {F3} == 'Self Cover' ? 0 : (({f1.price} * {F8.price}) * {stockWaste})
        if cover_option == "Self Cover":
            total_cover_sheets_a3 = Decimal('0')
        else:
            total_cover_sheets_a3 = (Decimal(str(qty)) * Decimal(str(finish_multiplier))) * stock_waste
        
        # TXT Line 3079: coverClickCost = {F5.price} * {totalCoverSheetsA3}
        cover_click_cost = Decimal(str(cover_print_price)) * total_cover_sheets_a3
        
        # TXT Line 3080: totalCoverCost = ({totalCoverSheetsA3} * {F4.price}) + {coverClickCost}
        total_cover_cost = (total_cover_sheets_a3 * Decimal(str(cover_stock_price))) + cover_click_cost
        
        # TXT Line 3084: totalContentSheets = (({F1.price} * {F7.price}) * {stockWaste}) * {F8.price}
        # F7.price is the SHEET COUNT (e.g., "16pp" has price=4 meaning 4 sheets)
        total_content_sheets = ((Decimal(str(qty)) * Decimal(str(pages_sheet_count))) * stock_waste) * Decimal(str(finish_multiplier))
        
        # TXT Line 3085: contentClickCost = {totalContentSheets} * {F10.price}
        content_click_cost = total_content_sheets * Decimal(str(content_print_price))
        
        # TXT Line 3086: totalContentCost = ({totalContentSheets} * {F11.price}) + {contentClickCost}
        total_content_cost = (total_content_sheets * Decimal(str(content_stock_price))) + content_click_cost
        
        # TXT Line 3088: totalSheetsPrinted = {totalContentSheets} + {totalCoverSheetsA3}
        total_sheets_printed = total_content_sheets + total_cover_sheets_a3
        
        # TXT Line 3089: cuttingCost = {totalSheetsPrinted} / {cuttingBlk} * {cutCost}
        cutting_cost = (total_sheets_printed / cutting_block) * cut_cost
        
        # TXT Line 3091: celloCost = {F6} == 'None' ? 0 : ({totalCoverSheetsA3} * {F6.price})
        if celloglaze == "None":
            cello_cost = Decimal('0')
        else:
            cello_cost = total_cover_sheets_a3 * Decimal(str(cello_price))
        
        # TXT Line 3096: bindRunCost = ((({totalContentSheets} + {totalCoverSheetsA3}) / {bindersheetsperhour}) * {binderyLaborperhour}) + ({F1.price} * {binderPerBook})
        bind_run_cost = (((total_content_sheets + total_cover_sheets_a3) / binder_sheets_hour) * bindery_labor) + (Decimal(str(qty)) * binder_per_book)
        
        # TXT Line 3099: subTotal = {totalSetupCost} + {totalCoverCost} + {totalContentCost} + {cuttingCost} + {celloCost} + {bindRunCost}
        total_setup_cost = guilo_setup + impos_setup + binder_setup + extra_arts + cello_setup
        sub_total = total_setup_cost + total_cover_cost + total_content_cost + cutting_cost + cello_cost + bind_run_cost
        
        # TXT Lines 3101-3113: 14-tier profit margin
        # Get profit margin based on subtotal
        margin_multiplier = self._get_profit_margin(float(sub_total))
        
        # TXT Line 3116: total = ({subTotal} + ({subTotal} *{profitMargin})) * 1.1
        # This is: subtotal_with_margin = subtotal × (1 + profit_margin), then × 1.1
        subtotal_with_margin = sub_total * (Decimal('1') + margin_multiplier)
        total_after_first_gst = subtotal_with_margin * Decimal('1.1')
        
        # TXT Line 3118: {total}*1.1
        # ❗ DOUBLE GST APPLICATION - DELIBERATE PRICE INCREASE
        total_inc_double_gst = total_after_first_gst * Decimal('1.1')
        
        # Unit prices
        unit_price = (total_inc_double_gst / Decimal(str(qty))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cost_per_item = (sub_total / Decimal(str(qty))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Build breakdown
        breakdown = {
            'setup_costs': guilo_setup + impos_setup + binder_setup + extra_arts,
            'cello_setup': cello_setup,
            'total_setup': total_setup_cost,
            'cover_cost': total_cover_cost,
            'celloglaze_cost': cello_cost,
            'content_cost': total_content_cost,
            'cutting_cost': cutting_cost,
            'binding_cost': bind_run_cost,
            'subtotal_before_margin': sub_total,
            'profit_margin_pct': margin_multiplier * Decimal('100'),
            'subtotal_with_margin': subtotal_with_margin,
            'first_gst_10pct': total_after_first_gst - subtotal_with_margin,
            'total_after_first_gst': total_after_first_gst,
            'second_gst_10pct': total_inc_double_gst - total_after_first_gst,
            'total_inc_double_gst': total_inc_double_gst,
            'effective_gst_rate': Decimal('21')  # 1.1 × 1.1 = 1.21 = 21% total
        }
        
        # Build specifications
        specifications = {
            'quantity': qty,
            'artworks': artworks,
            'cover_option': cover_option,
            'cover_stock': cover_stock,
            'cover_print_type': cover_print_type,
            'celloglaze': celloglaze,
            'printed_pages': printed_pages,
            'finish_size': finish_size,
            'content_print_type': content_print_type,
            'content_stock_type': content_stock_type,
            'total_sheets_printed': float(total_sheets_printed),
            'content_sheets': float(total_content_sheets),
            'cover_sheets': float(total_cover_sheets_a3),
            'pages': int(printed_pages.replace('pp', '')),
            'pages_sheet_count': float(pages_sheet_count)
        }
        
        return SaddleStitchBooksShopifyCalculatorQuoteResult(
            total_price=total_inc_double_gst,
            unit_price=unit_price,
            cost_per_item=cost_per_item,
            quantity=qty,
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_option_price(self, option_config: Dict, selected_value: str) -> float:
        """Extract price for a selected option value"""
        for opt in option_config.get('options', []):
            if opt['title'] == selected_value:
                return opt['price']
        raise ValueError(f"Option value '{selected_value}' not found in {option_config['name']}")
    
    def _get_padding_rate(self, quantity: int) -> Decimal:
        """Get padding rate (no tiers defined)"""
        return Decimal('0.10')
    
    def _get_profit_margin(self, subtotal: float) -> Decimal:
        """
        Get profit margin rate based on subtotal tiers
        
        14 tiers based on subtotal amount
        """
        if subtotal <= 49.999:
            return Decimal('1.7')
        elif subtotal <= 99.999:
            return Decimal('1.54')
        elif subtotal <= 199.999:
            return Decimal('1.24')
        elif subtotal <= 299.999:
            return Decimal('1.1')
        elif subtotal <= 499.999:
            return Decimal('1.04')
        elif subtotal <= 749.999:
            return Decimal('0.88')
        elif subtotal <= 999.999:
            return Decimal('0.78')
        elif subtotal <= 1249.999:
            return Decimal('0.7')
        elif subtotal <= 1499.999:
            return Decimal('0.64')
        elif subtotal <= 1749.999:
            return Decimal('0.52')
        elif subtotal <= 1999.999:
            return Decimal('0.47')
        elif subtotal <= 2499.999:
            return Decimal('0.42')
        elif subtotal <= 2999.999:
            return Decimal('0.4')
        elif subtotal <= 100000:
            return Decimal('0.37')
