"""
Corflute Signs Calculator - Shopify Formula Match
Replicates exact pricing logic from inhouseprint.com.au product configurator

This calculator matches the website pricing formula EXACTLY:
- 43-tier volume pricing for 5mm corflute
- 43-tier volume pricing for 3mm corflute  
- Double-sided add $6/sqm
- Custom size add 10% premium
- Eyelets/grommets pricing
- Artwork costs (first 5 free)
- 5% discount applied
- $135 minimum order
"""

from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class CorfluteSizePreset(Enum):
    """Preset size options from Shopify"""
    SIZE_450x600 = ("450mm x 600mm", 450, 600)
    SIZE_600x900 = ("600mm x 900mm", 600, 900)
    SIZE_900x1200 = ("900mm x 1200mm", 900, 1200)
    SIZE_1200x2400 = ("1200mm x 2400mm", 1200, 2400)
    CUSTOM = ("Custom", 0, 0)
    
    def __init__(self, label: str, width_mm: int, height_mm: int):
        self.label = label
        self.width_mm = width_mm
        self.height_mm = height_mm


class CorfiuteThickness(Enum):
    """Thickness options"""
    MM_3 = "3mm"
    MM_5 = "5mm"
    # 10mm not offered on website


class EyeletOption(Enum):
    """Eyelet/grommet placement options"""
    NONE = ("None", 0)
    FOUR_CORNERS = ("4 x Eyelets (1 In Each Corner)", 4)
    TWO_TOP = ("2 x Eyelets (top left & right corners)", 2)
    TWO_CENTER_LR = ("2 x Eyelets (center left & right)", 2)
    TWO_CENTER_TB = ("2 x Eyelets (center top & bottom)", 2)
    SIX_TOP_BOTTOM = ("6 x Eyelets (3 each top & bottom)", 6)
    SIX_LEFT_RIGHT = ("6 x Eyelets (3 each left & right)", 6)
    
    def __init__(self, label: str, count: int):
        self.label = label
        self.count = count


class CuttingType(Enum):
    """Cutting options"""
    STANDARD = "Standard square edge"
    CUSTOM_SHAPE = "Custom Shape"


@dataclass
class ShopifyPricingTiers:
    """
    Tier pricing from Shopify formula
    Format: (sqm_threshold, price_per_sqm)
    """
    
    # 5mm Corflute - 43 tiers
    TIER_5MM = [
        (5, 31.25),
        (6, 28.35),
        (7, 25.15),
        (8, 24.71),
        (9, 22.74),
        (10, 22.64),
        (15, 21.24),
        (20, 19.50),
        (25, 17.05),
        (30, 17.30),
        (35, 16.44),
        (40, 16.16),
        (45, 15.60),
        (50, 15.43),
        (60, 15.03),
        (70, 14.60),
        (80, 14.26),
        (90, 13.99),
        (100, 13.75),
        (110, 13.56),
        (120, 13.38),
        (130, 13.23),
        (140, 13.10),
        (150, 12.97),
        (175, 12.86),
        (200, 12.65),
        (225, 12.43),
        (250, 12.29),
        (275, 12.12),
        (300, 12.01),
        (325, 11.88),
        (350, 11.80),
        (375, 11.69),
        (400, 11.61),
        (425, 11.53),
        (450, 11.47),
        (475, 11.39),
        (500, 11.34),
        (539, 11.17),
        (550, 11.17),
        (600, 11.17),
        (650, 11.08),
        (700, 11.00),
        (float('inf'), 10.97),  # 700+ sqm
    ]
    
    # 3mm Corflute - 43 tiers
    TIER_3MM = [
        (5, 25.00),
        (6, 25.00),
        (7, 21.09),
        (8, 20.48),
        (9, 19.02),
        (10, 18.75),
        (15, 17.73),
        (20, 16.13),
        (25, 14.82),
        (30, 14.28),
        (35, 13.61),
        (40, 13.32),
        (45, 12.89),
        (50, 12.70),
        (60, 12.40),
        (70, 12.03),
        (80, 11.74),
        (90, 11.50),
        (100, 11.30),
        (110, 11.13),
        (120, 10.98),
        (130, 10.85),
        (140, 10.74),
        (150, 10.63),
        (175, 10.54),
        (200, 10.35),
        (225, 10.16),
        (250, 10.03),
        (275, 9.89),
        (300, 9.80),
        (325, 9.69),
        (350, 9.61),
        (375, 9.52),
        (400, 9.46),
        (425, 9.39),
        (450, 9.34),
        (475, 9.27),
        (500, 9.22),
        (539, 9.08),
        (550, 9.08),
        (600, 9.08),
        (650, 9.00),
        (700, 8.93),
        (float('inf'), 8.91),  # 700+ sqm
    ]
    
    @classmethod
    def get_tier_price(cls, total_sqm: float, thickness: CorfiuteThickness) -> float:
        """Get price per sqm based on total order sqm and thickness"""
        tier_table = cls.TIER_5MM if thickness == CorfiuteThickness.MM_5 else cls.TIER_3MM
        
        for threshold, price in tier_table:
            if total_sqm < threshold:
                return price
        
        return tier_table[-1][1]  # Return highest volume price


@dataclass
class ShopifyConstants:
    """Constants from Shopify formula"""
    EYELET_COST_PER_UNIT = 0.55  # Cost per eyelet
    ARTWORK_VALUE = 5.00  # Each artwork worth $5
    FREE_ARTWORKS = 5  # First 5 artworks free
    DOUBLE_SIDED_COST_PER_SQM = 6.00  # Add $6/sqm for double-sided
    CUSTOM_SIZE_PREMIUM = 1.1  # 10% surcharge for custom sizes
    STANDARD_DISCOUNT = 0.95  # 5% discount applied to all orders
    MINIMUM_ORDER = 135.00  # Minimum order value


class CorflutePricingCalculatorShopify:
    """
    Shopify-matching corflute calculator.
    Replicates exact formula from inhouseprint.com.au product configurator.
    """
    
    def calculate_quote(
        self,
        size_preset: CorfluteSizePreset = CorfluteSizePreset.SIZE_600x900,
        custom_width_mm: int = 0,
        custom_height_mm: int = 0,
        thickness: CorfiuteThickness = CorfiuteThickness.MM_5,
        quantity: int = 10,
        double_sided: bool = False,
        eyelet_option: EyeletOption = EyeletOption.NONE,
        cutting_type: CuttingType = CuttingType.STANDARD,
        artworks: int = 1,
    ) -> Dict:
        """
        Calculate corflute quote using Shopify formula.
        
        Returns dict with:
        - total_sqm: Total square meters across all units
        - tier_price_per_sqm: Price per sqm from tier table
        - base_cost: Base material/print cost
        - double_sided_cost: Additional cost for double-sided
        - custom_premium: Custom size surcharge
        - eyelet_cost: Cost for eyelets/grommets
        - artwork_cost: Cost for additional artworks
        - subtotal_before_discount: Before 5% discount
        - discount_amount: 5% discount value
        - subtotal_after_discount: After 5% discount
        - total: Final price (with minimum applied)
        - per_unit: Price per unit
        """
        
        # 1. Calculate dimensions
        if size_preset == CorfluteSizePreset.CUSTOM:
            width_mm = custom_width_mm
            height_mm = custom_height_mm
            is_custom = True
        else:
            width_mm = size_preset.width_mm
            height_mm = size_preset.height_mm
            is_custom = False
        
        # 2. Calculate total square meters
        sqm_per_unit = (width_mm * height_mm) / 1_000_000
        total_sqm = sqm_per_unit * quantity
        
        # 3. Get tier price
        tier_price = ShopifyPricingTiers.get_tier_price(total_sqm, thickness)
        
        # 4. Calculate base cost
        base_cost = total_sqm * tier_price
        
        # 5. Add double-sided cost
        double_sided_cost = 0.0
        if double_sided:
            double_sided_cost = total_sqm * ShopifyConstants.DOUBLE_SIDED_COST_PER_SQM
        
        # 6. Apply custom size premium
        custom_premium = 0.0
        cost_before_custom = base_cost + double_sided_cost
        if is_custom:
            custom_premium = cost_before_custom * (ShopifyConstants.CUSTOM_SIZE_PREMIUM - 1)
        
        cost_after_custom = cost_before_custom * (ShopifyConstants.CUSTOM_SIZE_PREMIUM if is_custom else 1.0)
        
        # 7. Calculate eyelet cost
        eyelet_cost = eyelet_option.count * ShopifyConstants.EYELET_COST_PER_UNIT * quantity
        
        # 8. Calculate artwork cost (first 5 free, then $5 each)
        artwork_value = artworks * ShopifyConstants.ARTWORK_VALUE
        artwork_cost = 0.0 if artwork_value <= (ShopifyConstants.FREE_ARTWORKS * ShopifyConstants.ARTWORK_VALUE) else (
            artwork_value - (ShopifyConstants.FREE_ARTWORKS * ShopifyConstants.ARTWORK_VALUE)
        )
        
        # 9. Calculate subtotal before discount
        subtotal_before_discount = cost_after_custom + eyelet_cost + artwork_cost
        
        # 10. Apply 5% discount
        discount_amount = subtotal_before_discount * (1 - ShopifyConstants.STANDARD_DISCOUNT)
        subtotal_after_discount = subtotal_before_discount * ShopifyConstants.STANDARD_DISCOUNT
        
        # 11. Apply minimum order
        total = max(subtotal_after_discount, ShopifyConstants.MINIMUM_ORDER)
        minimum_applied = total > subtotal_after_discount
        
        # 12. Calculate per unit
        per_unit = total / quantity
        
        return {
            # Input parameters
            'width_mm': width_mm,
            'height_mm': height_mm,
            'thickness': thickness.value,
            'quantity': quantity,
            'double_sided': double_sided,
            'eyelets': eyelet_option.count,
            'artworks': artworks,
            'is_custom_size': is_custom,
            
            # Calculation breakdown
            'sqm_per_unit': round(sqm_per_unit, 4),
            'total_sqm': round(total_sqm, 2),
            'tier_price_per_sqm': round(tier_price, 2),
            'base_cost': round(base_cost, 2),
            'double_sided_cost': round(double_sided_cost, 2),
            'custom_premium': round(custom_premium, 2),
            'eyelet_cost': round(eyelet_cost, 2),
            'artwork_cost': round(artwork_cost, 2),
            'subtotal_before_discount': round(subtotal_before_discount, 2),
            'discount_amount': round(discount_amount, 2),
            'subtotal_after_discount': round(subtotal_after_discount, 2),
            'minimum_applied': minimum_applied,
            'total': round(total, 2),
            'per_unit': round(per_unit, 2),
        }
    
    def format_quote(self, quote: Dict) -> str:
        """Format quote result as readable string"""
        lines = [
            "=" * 70,
            "CORFLUTE SIGNS QUOTE - Shopify Formula",
            "=" * 70,
            "",
            "SPECIFICATIONS:",
            f"  Size: {quote['width_mm']}mm × {quote['height_mm']}mm" + 
                (" (CUSTOM)" if quote['is_custom_size'] else ""),
            f"  Thickness: {quote['thickness']}",
            f"  Quantity: {quote['quantity']} units",
            f"  Print: {'Double-sided' if quote['double_sided'] else 'Single-sided'}",
            f"  Eyelets: {quote['eyelets']} per unit" if quote['eyelets'] > 0 else "  Eyelets: None",
            f"  Artworks: {quote['artworks']}",
            "",
            "PRICING BREAKDOWN:",
            f"  Total area: {quote['total_sqm']} sqm ({quote['sqm_per_unit']} sqm per unit)",
            f"  Tier price: ${quote['tier_price_per_sqm']}/sqm",
            f"  Base cost: ${quote['base_cost']:.2f}",
        ]
        
        if quote['double_sided_cost'] > 0:
            lines.append(f"  Double-sided add: ${quote['double_sided_cost']:.2f} (+$6/sqm)")
        
        if quote['custom_premium'] > 0:
            lines.append(f"  Custom size premium: ${quote['custom_premium']:.2f} (10% surcharge)")
        
        if quote['eyelet_cost'] > 0:
            lines.append(f"  Eyelets: ${quote['eyelet_cost']:.2f} ({quote['eyelets']} × ${ShopifyConstants.EYELET_COST_PER_UNIT} × {quote['quantity']})")
        
        if quote['artwork_cost'] > 0:
            lines.append(f"  Artwork: ${quote['artwork_cost']:.2f} (artworks > 5)")
        
        lines.extend([
            "",
            f"  Subtotal: ${quote['subtotal_before_discount']:.2f}",
            f"  Discount (5%): -${quote['discount_amount']:.2f}",
            f"  After discount: ${quote['subtotal_after_discount']:.2f}",
        ])
        
        if quote['minimum_applied']:
            lines.append(f"  Minimum order applied: ${ShopifyConstants.MINIMUM_ORDER:.2f}")
        
        lines.extend([
            "",
            "=" * 70,
            f"TOTAL: ${quote['total']:.2f}",
            f"PER UNIT: ${quote['per_unit']:.2f}",
            "=" * 70,
            "",
            "Note: Prices ex GST (add 10% for inc GST)",
            "Largest sheet: 2400mm × 1200mm (larger signs supplied in panels)",
            "",
        ])
        
        return "\n".join(lines)


# ============================================================================
# TEST CASES - Match Shopify examples
# ============================================================================

if __name__ == "__main__":
    calc = CorflutePricingCalculatorShopify()
    
    print("\n" + "="*70)
    print("WOOCOMMERCE FORMULA VALIDATION TESTS")
    print("="*70 + "\n")
    
    # TEST 1: Standard 600×900mm, 5mm, 10 qty (most common)
    print("\n" + "="*70)
    print("TEST 1: Standard real estate sign")
    print("="*70)
    quote1 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.SIZE_600x900,
        thickness=CorfiuteThickness.MM_5,
        quantity=10,
        double_sided=False,
        eyelet_option=EyeletOption.FOUR_CORNERS,
        artworks=1,
    )
    print(calc.format_quote(quote1))
    print("Expected from formula:")
    print("  Total sqm: 5.4")
    print("  Tier (< 6 sqm): $28.35/sqm")
    print("  Base: 5.4 × $28.35 = $153.09")
    print("  Eyelets: 4 × $0.55 × 10 = $22.00")
    print("  Subtotal: $175.09 × 0.95 = $166.34")
    print(f"  MATCH: {' YES' if abs(quote1['total'] - 166.34) < 0.5 else ' NO'}")
    
    # TEST 2: Volume order (100 units)
    print("\n" + "="*70)
    print("TEST 2: Volume order (100 units)")
    print("="*70)
    quote2 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.SIZE_600x900,
        thickness=CorfiuteThickness.MM_5,
        quantity=100,
        double_sided=False,
        eyelet_option=EyeletOption.NONE,
        artworks=1,
    )
    print(calc.format_quote(quote2))
    print("Expected from formula:")
    print("  Total sqm: 54")
    print("  Tier (< 60 sqm): $15.03/sqm")
    print("  Base: 54 × $15.03 = $811.62")
    print("  Subtotal: $811.62 × 0.95 = $771.04")
    print(f"  MATCH: {' YES' if abs(quote2['total'] - 771.04) < 0.5 else ' NO'}")
    
    # TEST 3: Double-sided with custom size
    print("\n" + "="*70)
    print("TEST 3: Double-sided custom size")
    print("="*70)
    quote3 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.CUSTOM,
        custom_width_mm=800,
        custom_height_mm=1200,
        thickness=CorfiuteThickness.MM_5,
        quantity=20,
        double_sided=True,
        eyelet_option=EyeletOption.TWO_TOP,
        artworks=3,
    )
    print(calc.format_quote(quote3))
    print("Expected from formula:")
    print("  Total sqm: 19.2")
    print("  Tier (< 20 sqm): $19.50/sqm")
    print("  Base: 19.2 × $19.50 = $374.40")
    print("  Double-sided: 19.2 × $6 = $115.20")
    print("  Custom premium: ($374.40 + $115.20) × 0.1 = $48.96")
    print("  Eyelets: 2 × $0.55 × 20 = $22.00")
    print("  Subtotal: ($374.40 + $115.20 + $48.96 + $22.00) × 0.95 = $532.03")
    print(f"  MATCH: {' YES' if abs(quote3['total'] - 532.03) < 0.5 else ' NO'}")
    
    # TEST 4: Bulk volume (500+ units)
    print("\n" + "="*70)
    print("TEST 4: Bulk volume (500 units)")
    print("="*70)
    quote4 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.SIZE_450x600,
        thickness=CorfiuteThickness.MM_3,
        quantity=500,
        double_sided=False,
        eyelet_option=EyeletOption.NONE,
        artworks=1,
    )
    print(calc.format_quote(quote4))
    print("Expected from formula:")
    print("  Total sqm: 135")
    print("  Tier (< 140 sqm): $10.74/sqm")
    print("  Base: 135 × $10.74 = $1,449.90")
    print("  Subtotal: $1,449.90 × 0.95 = $1,377.41")
    print(f"  MATCH: {' YES' if abs(quote4['total'] - 1377.41) < 0.5 else ' NO'}")
    
    # TEST 5: Minimum order test (small qty)
    print("\n" + "="*70)
    print("TEST 5: Minimum order ($135)")
    print("="*70)
    quote5 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.SIZE_450x600,
        thickness=CorfiuteThickness.MM_3,
        quantity=2,
        double_sided=False,
        eyelet_option=EyeletOption.NONE,
        artworks=1,
    )
    print(calc.format_quote(quote5))
    print("Expected from formula:")
    print("  Total sqm: 0.54")
    print("  Tier (< 5 sqm): $25.00/sqm")
    print("  Base: 0.54 × $25.00 = $13.50")
    print("  Subtotal: $13.50 × 0.95 = $12.83")
    print("  Minimum applied: $135.00")
    print(f"  MATCH: {' YES' if quote5['minimum_applied'] and quote5['total'] == 135.00 else ' NO'}")
    
    # TEST 6: Artwork cost (> 5 artworks)
    print("\n" + "="*70)
    print("TEST 6: Multiple artworks (10 artworks)")
    print("="*70)
    quote6 = calc.calculate_quote(
        size_preset=CorfluteSizePreset.SIZE_600x900,
        thickness=CorfiuteThickness.MM_5,
        quantity=50,
        double_sided=False,
        eyelet_option=EyeletOption.NONE,
        artworks=10,  # First 5 free, charge for 5 more
    )
    print(calc.format_quote(quote6))
    print("Expected from formula:")
    print("  Total sqm: 27")
    print("  Tier (< 30 sqm): $17.30/sqm")
    print("  Base: 27 × $17.30 = $467.10")
    print("  Artwork: (10 - 5) × $5 = $25.00")
    print("  Subtotal: ($467.10 + $25.00) × 0.95 = $467.50")
    print(f"  MATCH: {' YES' if abs(quote6['total'] - 467.50) < 0.5 else ' NO'}")
    
    print("\n" + "="*70)
    print("VALIDATION COMPLETE")
    print("="*70 + "\n")
