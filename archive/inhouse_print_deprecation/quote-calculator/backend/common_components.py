"""
Common Components Library
Reusable logic components for custom calculators

These components handle complex calculations that can't be expressed as simple formulas:
- Tiered pricing lookups
- Quantity break calculations  
- Profit margin calculations
- Labor rate resolution
- GST application
- Area calculations
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional


class CommonComponents:
    """Reusable calculation components"""
    
    @staticmethod
    def tiered_pricing_lookup(lookup_value: float, tier_table: List[Dict[str, float]], 
                              tier_column: str = 'max_value', rate_column: str = 'rate') -> Decimal:
        """
        Lookup rate from tiered pricing table
        
        Args:
            lookup_value: Value to lookup (e.g., 0.54 for area in m²)
            tier_table: List of tiers [{"max_value": 0.01, "rate": 950}, ...]
            tier_column: Column name for tier threshold
            rate_column: Column name for rate value
        
        Returns:
            Rate from matching tier
        
        Example:
            tiers = [
                {"max_value": 0.01, "rate": 950},
                {"max_value": 0.02, "rate": 475},
                {"max_value": 999999, "rate": 14}
            ]
            tiered_pricing_lookup(0.015, tiers) -> 475
        """
        for tier in tier_table:
            if lookup_value <= tier[tier_column]:
                return Decimal(str(tier[rate_column]))
        
        # If no tier matched, return last tier (fallback)
        return Decimal(str(tier_table[-1][rate_column]))
    
    @staticmethod
    def quantity_break_discount(quantity: int, break_points: List[Dict[str, Any]]) -> Decimal:
        """
        Calculate discount rate based on quantity breaks
        
        Args:
            quantity: Number of units
            break_points: [{"min_qty": 1, "discount": 0}, {"min_qty": 100, "discount": 0.10}, ...]
        
        Returns:
            Discount rate (e.g., 0.10 for 10% discount)
        """
        applicable_discount = Decimal('0')
        
        for break_point in sorted(break_points, key=lambda x: x['min_qty'], reverse=True):
            if quantity >= break_point['min_qty']:
                applicable_discount = Decimal(str(break_point['discount']))
                break
        
        return applicable_discount
    
    @staticmethod
    def calculate_profit_margin(base_cost: Decimal, margin_rate: Decimal) -> Decimal:
        """
        Calculate profit amount from cost and margin rate
        
        Args:
            base_cost: Base cost before profit
            margin_rate: Profit margin rate (e.g., 0.50 for 50%)
        
        Returns:
            Profit amount
        """
        return (base_cost * margin_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def apply_complexity_multiplier(base_cost: Decimal, complexity: str, 
                                    multipliers: Dict[str, float]) -> Decimal:
        """
        Apply complexity multiplier to base cost
        
        Args:
            base_cost: Base cost
            complexity: Complexity level ('standard', 'challenging', 'rush')
            multipliers: {'standard': 1.0, 'challenging': 1.35, 'rush': 1.75}
        
        Returns:
            Adjusted cost
        """
        multiplier = Decimal(str(multipliers.get(complexity, 1.0)))
        return (base_cost * multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_gst(subtotal: Decimal, gst_rate: Decimal = Decimal('1.10')) -> Dict[str, Decimal]:
        """
        Calculate GST and total
        
        Args:
            subtotal: Subtotal before GST
            gst_rate: GST rate (1.10 for 10% GST)
        
        Returns:
            {'gst_amount': ..., 'total_with_gst': ...}
        """
        total_with_gst = (subtotal * gst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        gst_amount = (total_with_gst - subtotal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            'gst_amount': gst_amount,
            'total_with_gst': total_with_gst
        }
    
    @staticmethod
    def calculate_double_gst_shopify(subtotal: Decimal) -> Dict[str, Decimal]:
        """
        Shopify-specific double GST application
        Total = (Subtotal * 1.1) * 1.1
        
        Args:
            subtotal: Subtotal before GST
        
        Returns:
            {'total_with_gst': ..., 'gst_amount': ...}
        """
        gst_rate = Decimal('1.10')
        total = ((subtotal * gst_rate) * gst_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        gst_amount = (total - subtotal).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return {
            'total_with_gst': total,
            'gst_amount': gst_amount
        }
    
    @staticmethod
    def calculate_area_m2(width_mm: float, height_mm: float) -> Decimal:
        """
        Calculate area in square meters from millimeters
        
        Args:
            width_mm: Width in millimeters
            height_mm: Height in millimeters
        
        Returns:
            Area in square meters
        """
        area = Decimal(str(width_mm)) * Decimal(str(height_mm)) / Decimal('1000000')
        return area.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_labor_cost(hours: Decimal, labor_rate: Decimal, 
                            multiplier: Decimal = Decimal('1.0')) -> Decimal:
        """
        Calculate labor cost with optional multiplier
        
        Args:
            hours: Labor hours required
            labor_rate: Hourly labor rate
            multiplier: Time-based multiplier (1.5 for after hours, 2.0 for holidays)
        
        Returns:
            Total labor cost
        """
        effective_rate = labor_rate * multiplier
        cost = (hours * effective_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return cost
    
    @staticmethod
    def calculate_material_waste(base_amount: Decimal, waste_percentage: Decimal = Decimal('0.10')) -> Decimal:
        """
        Calculate material amount with waste factor
        
        Args:
            base_amount: Base material amount needed
            waste_percentage: Waste factor (0.10 for 10% waste)
        
        Returns:
            Amount including waste
        """
        return (base_amount * (Decimal('1') + waste_percentage)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calculate_setup_cost(base_setup: Decimal, artworks: int = 1, 
                           additional_artwork_cost: Decimal = Decimal('25.00')) -> Decimal:
        """
        Calculate setup cost with additional artwork charges
        
        Args:
            base_setup: Base setup cost (first artwork included)
            artworks: Number of artworks
            additional_artwork_cost: Cost per additional artwork
        
        Returns:
            Total setup cost
        """
        additional_artworks = max(0, artworks - 1)
        total_setup = base_setup + (Decimal(str(additional_artworks)) * additional_artwork_cost)
        return total_setup.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def minimum_order_check(calculated_price: Decimal, minimum_order: Decimal = Decimal('45.00'),
                           handling_fee: Decimal = Decimal('10.00')) -> Dict[str, Decimal]:
        """
        Apply minimum order value and handling fee
        
        Args:
            calculated_price: Calculated price
            minimum_order: Minimum order value
            handling_fee: Handling fee for below-minimum orders
        
        Returns:
            {'final_price': ..., 'handling_fee_applied': ..., 'below_minimum': bool}
        """
        if calculated_price < minimum_order:
            final_price = minimum_order + handling_fee
            return {
                'final_price': final_price,
                'handling_fee_applied': handling_fee,
                'below_minimum': True
            }
        else:
            return {
                'final_price': calculated_price,
                'handling_fee_applied': Decimal('0'),
                'below_minimum': False
            }
