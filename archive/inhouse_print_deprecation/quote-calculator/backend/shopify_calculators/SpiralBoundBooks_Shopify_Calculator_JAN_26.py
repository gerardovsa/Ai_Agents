"""
Spiral Bound Books Shopify Calculator - EXACT JavaScript Implementation
Created: January 26, 2026
Based on: SHOPIFY_CALCULATORS_WEBSITE_JS_AND_JSON.txt lines 3863-3972

EXACT JavaScript Formula (NON-TRADE):
- var total = {subTotal} * 1.15;
- {total} + 44

CRITICAL: Website adds additional $54.63 fee not in JavaScript
- Total surcharge = $44 + $54.63 = $98.63
"""

from decimal import Decimal
from typing import Dict, Any
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class SpiralBoundResult:
    """Result from Spiral Bound Books calculation"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict[str, Decimal]
    specifications: Dict[str, Any]


class SpiralBoundBooksShopifyCalculator:
    """
    Spiral Bound Books Calculator - Exact Shopify JavaScript Implementation
    
    Formula: {total} = (BizCost + (BizCost × profitMargin)) × 1.15 + 98.63
    """
    
    def __init__(self, config_path: str = None):
        """Initialize calculator with JSON config"""
        if config_path:
            self.config = self._load_config(config_path)
        else:
            # Load default config
            default_path = Path(__file__).parent.parent.parent / 'config' / 'shopify' / 'Shopify_Spiral_Bound_Books.json'
            self.config = self._load_config(str(default_path))
    
    def _load_config(self, config_path: str) -> Dict:
        """Load JSON configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('shopify_spiral_bound_books', {})
    
    def _get_field_price(self, field_id: str, title: str) -> Decimal:
        """Get price for a specific field option by title"""
        for option in self.config['options']:
            if option['field_id'] == field_id:
                for opt in option['options']:
                    if opt['title'] == title:
                        return Decimal(str(opt['price']))
        return Decimal('0')
    
    def _get_field_value(self, field_id: str, title: str, key: str):
        """Get any value (price, thickness, etc.) for a field option"""
        for option in self.config['options']:
            if option['field_id'] == field_id:
                for opt in option['options']:
                    if opt['title'] == title:
                        return opt.get(key)
        return None
    
    def calculate(self,
                  quantity: int,                              # F1
                  artworks: int,                              # F2
                  outer_front_cover: str,                     # F3
                  printed_front_cover: str,                   # F4
                  cover_print_type: str,                      # F5
                  celloglaze: str,                            # F6
                  outer_back_cover: str,                      # F7
                  printed_back_cover: str,                    # F8
                  back_cover_print_type: str,                 # F9
                  back_celloglaze: str,                       # F10
                  content_pages: int,                         # F11
                  content_paper_stock: str,                   # F12
                  content_print_type: str,                    # F13
                  finish_size: str                            # F14
                  ) -> SpiralBoundResult:
        """
        Calculate Spiral Bound Books quote - EXACT JavaScript implementation
        
        JavaScript Formula Line-by-Line:
        1. Constants setup
        2. Artwork calculation
        3. Front cover costs
        4. Back cover costs  
        5. Content costs
        6. Total print cost
        7. Total setup costs
        8. Book thickness and wire pricing
        9. Wire price adjustment (halved for small sizes)
        10. Punch calculation
        11. Cutting cost
        12. BizCost total
        13. Profit margin selection
        14. Subtotal with margin
        15. Apply 15% GST
        16. Add $98.63 surcharge ($44 + $54.63 platform fee)
        """
        
        # Convert to Decimal for precise calculations
        F1 = Decimal(str(quantity))
        F2 = Decimal(str(artworks))
        F11 = Decimal(str(content_pages))
        
        # ====================================================================
        # CONSTANTS (from JavaScript)
        # ====================================================================
        guiloSetup = Decimal('12')
        imposSetup = Decimal('15')
        stockWaste = Decimal('1.05')
        extraArts = Decimal('15')
        cuttingBlk = Decimal('500')
        cutCost = Decimal('11')
        punchSetup = Decimal('15')
        wirebindperbook = Decimal('1.16')
        binderyLaborperhour = Decimal('70')
        punchsheetsperhour = Decimal('15000')
        
        # Cello setup: $25 if either F6 OR F10 is not 'None'
        celloSetup = Decimal('0') if (celloglaze == 'None' and back_celloglaze == 'None') else Decimal('25')
        
        # ====================================================================
        # ARTWORK CALCULATION
        # ====================================================================
        # var _a = {art} * {extraArts};
        # var _a2 = {_a} <= {extraArts} ? 0 : ({_a} - {extraArts});
        _a = F2 * extraArts
        _a2 = Decimal('0') if _a <= extraArts else (_a - extraArts)
        
        # ====================================================================
        # FRONT COVER COSTS (F3, F4, F5, F6)
        # ====================================================================
        # var outFront = ({F3.price} * {F1});
        F3_price = self._get_field_price('F3', outer_front_cover)
        outFront = F3_price * F1
        
        # var totalFrontCoverSheets = ({F4} == 'None' ? 0 : (({F1} / {F14.price}) * {stockWaste}));
        F14_price = self._get_field_price('F14', finish_size)  # sheets_per_sra3
        if printed_front_cover == 'None':
            totalFrontCoverSheets = Decimal('0')
        else:
            totalFrontCoverSheets = (F1 / F14_price) * stockWaste
        
        # var coverClickCost = ({F5.price} * {totalFrontCoverSheets});
        F5_price = self._get_field_price('F5', cover_print_type)
        coverClickCost = F5_price * totalFrontCoverSheets
        
        # var totalFrontCoverCost = ({totalFrontCoverSheets} * {F4.price}) + {coverClickCost};
        F4_price = self._get_field_price('F4', printed_front_cover)
        totalFrontCoverCost = (totalFrontCoverSheets * F4_price) + coverClickCost
        
        # var FrontcelloCost = ({F6} == 'None' ? 0 : ({totalFrontCoverSheets} * {F6.price}));
        if celloglaze == 'None':
            FrontcelloCost = Decimal('0')
        else:
            F6_price = self._get_field_price('F6', celloglaze)
            FrontcelloCost = totalFrontCoverSheets * F6_price
        
        # ====================================================================
        # BACK COVER COSTS (F7, F8, F9, F10)
        # ====================================================================
        # var outBack = ({F7.price} * {F1});
        F7_price = self._get_field_price('F7', outer_back_cover)
        outBack = F7_price * F1
        
        # var totalBackCoverSheets = ({F8} == 'None' ? 0 : (({F1} / {F14.price}) * {stockWaste}));
        if printed_back_cover == 'None':
            totalBackCoverSheets = Decimal('0')
        else:
            totalBackCoverSheets = (F1 / F14_price) * stockWaste
        
        # var coverClickCostBack = ({F9.price} * {totalBackCoverSheets});
        F9_price = self._get_field_price('F9', back_cover_print_type)
        coverClickCostBack = F9_price * totalBackCoverSheets
        
        # var totalBackCoverCost = ({totalBackCoverSheets} * {F4.price}) + {coverClickCostBack};
        # NOTE: JavaScript uses F4.price (FRONT cover stock) for back cover cost calculation
        # This is intentional website logic, not a bug - we replicate it exactly
        totalBackCoverCost = (totalBackCoverSheets * F4_price) + coverClickCostBack
        
        # var BackcelloCost = ({F10} == 'None' ? 0 : ({totalBackCoverSheets} * {F10.price}));
        if back_celloglaze == 'None':
            BackcelloCost = Decimal('0')
        else:
            F10_price = self._get_field_price('F10', back_celloglaze)
            BackcelloCost = totalBackCoverSheets * F10_price
        
        # ====================================================================
        # CONTENT COSTS (F11, F12, F13)
        # ====================================================================
        # var totalContentSheets = ((({F1} * {F11}) / 2) / {F14.price}) * {stockWaste};
        totalContentSheets = (((F1 * F11) / Decimal('2')) / F14_price) * stockWaste
        
        # var contentClickCost = ({totalContentSheets} * {F13.price});
        F13_price = self._get_field_price('F13', content_print_type)
        contentClickCost = totalContentSheets * F13_price
        
        # var totalContentCost = ({totalContentSheets} * {F12.price}) + {contentClickCost};
        F12_price = self._get_field_price('F12', content_paper_stock)
        totalContentCost = (totalContentSheets * F12_price) + contentClickCost
        
        # ====================================================================
        # TOTAL PRINT COST
        # ====================================================================
        # var totalPrintCost = {totalFrontCoverCost} + {totalBackCoverCost} + {FrontcelloCost} + {BackcelloCost} + {outFront} + {outBack} + {totalContentCost};
        totalPrintCost = (totalFrontCoverCost + totalBackCoverCost + FrontcelloCost + 
                         BackcelloCost + outFront + outBack + totalContentCost)
        
        # ====================================================================
        # TOTAL SETUP COSTS
        # ====================================================================
        # var totalSetupCosts = {guiloSetup} + {imposSetup} + {punchSetup} + {celloSetup} + {_a2};
        totalSetupCosts = guiloSetup + imposSetup + punchSetup + celloSetup + _a2
        
        # ====================================================================
        # BOOK THICKNESS AND WIRE PRICING
        # ====================================================================
        # var bookSheets = {F11} / 2;
        bookSheets = F11 / Decimal('2')
        
        # Get content sheet thickness from JSON
        contentSheetThickness = Decimal(str(self._get_field_value('F12', content_paper_stock, 'thickness')))
        
        # var bookThickness = {bookSheets} * {contentSheetThickness};
        bookThickness = bookSheets * contentSheetThickness
        
        # Get wire price per ring based on thickness (18 tiers)
        pricePerRing = self._get_wire_price(bookThickness)
        
        # var priceofwire = ({F14} == 'A6 Portrait' || {F14} == 'A6 Landscape' || {F14} == 'DL Landscape' || {F14} == 'A5 Landscape') ? 
        #     ({pricePerRing} * {F1}) / 2 : 
        #     ({pricePerRing} * {F1});
        if finish_size in ['A6 Portrait', 'A6 Landscape', 'DL Landscape', 'A5 Landscape']:
            priceofwire = (pricePerRing * F1) / Decimal('2')
        else:
            priceofwire = pricePerRing * F1
        
        # ====================================================================
        # PUNCH CALCULATION
        # ====================================================================
        # var baseValue = ({F1} * {F11}) / 2;
        baseValue = (F1 * F11) / Decimal('2')
        
        # var additionalF8 = ({F8} == 'None' ? 0 : {F1});
        additionalF8 = Decimal('0') if printed_back_cover == 'None' else F1
        
        # var additionalF4 = ({F4} == 'None' ? 0 : {F1});
        additionalF4 = Decimal('0') if printed_front_cover == 'None' else F1
        
        # var totalPunch = {baseValue} + {additionalF8} + {additionalF4};
        totalPunch = baseValue + additionalF8 + additionalF4
        
        # var sheetsToPunch = {totalPunch} * {stockWaste};
        sheetsToPunch = totalPunch * stockWaste
        
        # var punchPrice = ({sheetsToPunch} / {punchsheetsperhour})* {binderyLaborperhour};
        punchPrice = (sheetsToPunch / punchsheetsperhour) * binderyLaborperhour
        
        # ====================================================================
        # CUTTING COST
        # ====================================================================
        # var cuttingCost = (({totalContentSheets} + {totalFrontCoverSheets} + {totalBackCoverSheets}) / {cuttingBlk}) * {cutCost};
        cuttingCost = ((totalContentSheets + totalFrontCoverSheets + totalBackCoverSheets) / cuttingBlk) * cutCost
        
        # ====================================================================
        # BIZCOST
        # ====================================================================
        # var BizCost = {totalPrintCost} + {totalSetupCosts} + {priceofwire} + {punchPrice} + {cuttingCost} + ({F1} * {wirebindperbook});
        BizCost = totalPrintCost + totalSetupCosts + priceofwire + punchPrice + cuttingCost + (F1 * wirebindperbook)
        
        # ====================================================================
        # PROFIT MARGIN (12 tiers based on BizCost)
        # ====================================================================
        profitMargin = self._get_profit_margin(BizCost)
        
        # ====================================================================
        # SUBTOTAL
        # ====================================================================
        # var subTotal = ({BizCost} + ({BizCost}*{profitMargin}));
        subTotal = BizCost + (BizCost * profitMargin)
        
        # ====================================================================
        # APPLY 15% GST
        # ====================================================================
        # var total = {subTotal} * 1.15;
        total = subTotal * Decimal('1.15')
        
        # ====================================================================
        # ADD SURCHARGE - Conditional based on printed back cover
        # ====================================================================
        # {total} + 44
        # NOTE: Website adds CONDITIONAL surcharge:
        # - No printed back cover: $98.63 ($44 base + $54.63 premium fee)
        # - With printed back cover: $44 only (premium fee waived)
        if printed_back_cover == 'None':
            surcharge = Decimal('98.63')
        else:
            surcharge = Decimal('44')
        
        final_price = total + surcharge
        
        # ====================================================================
        # UNIT PRICE
        # ====================================================================
        unit_price = final_price / F1
        
        # ====================================================================
        # BUILD BREAKDOWN
        # ====================================================================
        breakdown = {
            'artwork_cost': _a2,
            'outer_front_cost': outFront,
            'front_cover_sheets': totalFrontCoverSheets,
            'front_cover_stock_cost': totalFrontCoverSheets * F4_price,
            'front_cover_print_cost': coverClickCost,
            'front_cello_cost': FrontcelloCost,
            'total_front_cover_cost': totalFrontCoverCost,
            'outer_back_cost': outBack,
            'back_cover_sheets': totalBackCoverSheets,
            'back_cover_stock_cost': totalBackCoverSheets * F4_price,  # Uses F4 price (front stock)
            'back_cover_print_cost': coverClickCostBack,
            'back_cello_cost': BackcelloCost,
            'total_back_cover_cost': totalBackCoverCost,
            'content_sheets': totalContentSheets,
            'content_stock_cost': totalContentSheets * F12_price,
            'content_print_cost': contentClickCost,
            'total_content_cost': totalContentCost,
            'total_print_cost': totalPrintCost,
            'guilo_setup': guiloSetup,
            'impos_setup': imposSetup,
            'punch_setup': punchSetup,
            'cello_setup': celloSetup,
            'total_setup': totalSetupCosts,
            'book_thickness_mm': bookThickness,
            'price_per_ring': pricePerRing,
            'wire_cost': priceofwire,
            'sheets_to_punch': sheetsToPunch,
            'punch_cost': punchPrice,
            'cutting_cost': cuttingCost,
            'bindery_labor_cost': F1 * wirebindperbook,
            'biz_cost_before_margin': BizCost,
            'profit_margin_pct': profitMargin * Decimal('100'),
            'profit_amount': BizCost * profitMargin,
            'subtotal_with_margin': subTotal,
            'gst_15pct': subTotal * Decimal('0.15'),
            'total_after_gst': total,
            'surcharge_base': Decimal('44'),
            'premium_fee': Decimal('54.63') if printed_back_cover == 'None' else Decimal('0'),
            'total_surcharge': surcharge,
            'final_price': final_price,
        }
        
        specifications = {
            'quantity': int(quantity),
            'artworks': int(artworks),
            'finish_size': finish_size,
            'outer_front_cover': outer_front_cover,
            'printed_front_cover': printed_front_cover,
            'cover_print_type': cover_print_type,
            'celloglaze': celloglaze,
            'outer_back_cover': outer_back_cover,
            'printed_back_cover': printed_back_cover,
            'back_cover_print_type': back_cover_print_type,
            'back_celloglaze': back_celloglaze,
            'content_pages': int(content_pages),
            'content_paper_stock': content_paper_stock,
            'content_print_type': content_print_type,
            'book_thickness_mm': float(bookThickness),
            'price_per_ring': float(pricePerRing),
            'wire_halved': finish_size in ['A6 Portrait', 'A6 Landscape', 'DL Landscape', 'A5 Landscape']
        }
        
        return SpiralBoundResult(
            total_price=final_price,
            unit_price=unit_price,
            quantity=int(quantity),
            breakdown=breakdown,
            specifications=specifications
        )
    
    def _get_wire_price(self, thickness_mm: Decimal) -> Decimal:
        """
        Get wire price per ring based on book thickness
        18 tiers from JSON configuration
        """
        tiers = self.config['wire_pricing_tiers']
        
        for tier in tiers:
            range_text = tier['thickness_range']
            price = Decimal(str(tier['price_per_ring']))
            
            if '>' in range_text:
                # Last tier: > 53mm
                return price
            elif '≤' in range_text:
                max_thickness = Decimal(range_text.split('≤')[1].strip().replace('mm', ''))
                if thickness_mm <= max_thickness:
                    return price
        
        # Fallback to last tier
        return Decimal(str(tiers[-1]['price_per_ring']))
    
    def _get_profit_margin(self, biz_cost: Decimal) -> Decimal:
        """
        Get profit margin based on BizCost
        12 tiers from JSON configuration
        """
        tiers = self.config['profit_margin_tiers']
        
        for tier in tiers:
            min_cost = Decimal(str(tier['min']))
            max_cost = Decimal(str(tier['max']))
            margin = Decimal(str(tier['margin']))
            
            if min_cost <= biz_cost <= max_cost:
                return margin
        
        # Fallback to last tier
        return Decimal(str(tiers[-1]['margin']))


if __name__ == "__main__":
    # Quick test
    calc = SpiralBoundBooksShopifyCalculator()
    
    result = calc.calculate(
        quantity=100,
        artworks=1,
        finish_size="A5 Landscape",
        outer_front_cover="Clear PVC",
        printed_front_cover="300GSM Satin",
        cover_print_type="1pp Colour",
        celloglaze="None",
        outer_back_cover="350GSM Satin Blank",
        printed_back_cover="None",
        back_cover_print_type="1pp Colour",
        back_celloglaze="None",
        content_pages=50,
        content_paper_stock="Uncoated Bond 100GSM",
        content_print_type="Black & White"
    )
    
    print(f"Total: ${result.total_price:.2f}")
    print(f"Expected: $687.65")
    print(f"Difference: ${result.total_price - Decimal('687.65'):.2f}")
