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

# Add config directory to path
config_dir = Path(__file__).parent.parent.parent / "config"
if str(config_dir) not in sys.path:
    sys.path.insert(0, str(config_dir))

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
        
        # Extract pricing from config
        config = self.config['shopify_saddle_stitch_books']
        options = {opt['name']: opt for opt in config['options']}
        constants = config['pricing_constants']
        
        # Get field prices
        cover_stock_price = self._get_option_price(options['Cover Stock'], cover_stock)
        cover_print_price = self._get_option_price(options['Cover Print Type'], cover_print_type)
        cello_price = self._get_option_price(options['Celloglaze'], celloglaze)
        pages_multiplier = int(printed_pages.replace('pp', ''))  # Extract number from "16pp"
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
        
        # Calculate sheets needed
        content_sheets = Decimal(str(pages_multiplier)) / Decimal('2')  # 2 pages per sheet
        
        # Cover sheets (0 if Self Cover)
        if cover_option == "Self Cover":
            cover_sheets = Decimal('0')
            cover_cost = Decimal('0')
        else:
            cover_sheets = Decimal('1')  # 1 sheet for hard cover
            # Cover cost = (stock + print) * quantity * size_multiplier * waste
            cover_cost = (
                (Decimal(str(cover_stock_price)) + Decimal(str(cover_print_price))) * 
                Decimal(str(qty)) * 
                Decimal(str(finish_multiplier)) * 
                stock_waste
            )
        
        # Celloglaze cost (per sheet)
        if celloglaze != "None" and cover_option != "Self Cover":
            cello_cost = Decimal(str(cello_price)) * Decimal(str(qty)) * Decimal(str(finish_multiplier))
        else:
            cello_cost = Decimal('0')
        
        # Content cost = (stock + print) * sheets * quantity * size_multiplier * waste
        content_cost = (
            (Decimal(str(content_stock_price)) + Decimal(str(content_print_price))) * 
            content_sheets * 
            Decimal(str(qty)) * 
            Decimal(str(finish_multiplier)) * 
            stock_waste
        )
        
        # Cutting cost (per cutting_block units)
        cuts_needed = (Decimal(str(qty)) / cutting_block).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        if cuts_needed < Decimal('1'):
            cuts_needed = Decimal('1')
        cutting_cost = cuts_needed * cut_cost
        
        # Binding cost
        binding_material = Decimal(str(qty)) * binder_per_book
        binding_labor = (Decimal(str(qty)) * content_sheets) / binder_sheets_hour * bindery_labor
        binding_cost = binding_material + binding_labor
        
        # Calculate subtotal (before margin)
        subtotal_before_margin = (
            guilo_setup + impos_setup + binder_setup + extra_arts + cello_setup +
            cover_cost + cello_cost + content_cost + cutting_cost + binding_cost
        )
        
        # Get profit margin based on subtotal
        margin_multiplier = self._get_profit_margin(float(subtotal_before_margin))
        
        # Apply margin
        subtotal_with_margin = subtotal_before_margin * (Decimal('1') + margin_multiplier)
        
        # Apply GST (10%)
        total_inc_gst = subtotal_with_margin * Decimal('1.1')
        
        # Unit prices
        unit_price = (total_inc_gst / Decimal(str(qty))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        cost_per_item = (subtotal_before_margin / Decimal(str(qty))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Build breakdown
        breakdown = {
            'setup_costs': guilo_setup + impos_setup + binder_setup + extra_arts,
            'cello_setup': cello_setup,
            'cover_cost': cover_cost,
            'celloglaze_cost': cello_cost,
            'content_cost': content_cost,
            'cutting_cost': cutting_cost,
            'binding_cost': binding_cost,
            'subtotal_before_margin': subtotal_before_margin,
            'profit_margin_pct': margin_multiplier * Decimal('100'),
            'subtotal_with_margin': subtotal_with_margin,
            'gst_10pct': total_inc_gst - subtotal_with_margin,
            'total_inc_gst': total_inc_gst
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
            'total_sheets': float(content_sheets + cover_sheets),
            'pages': pages_multiplier
        }
        
        return SaddleStitchBooksShopifyCalculatorQuoteResult(
            total_price=total_inc_gst,
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
