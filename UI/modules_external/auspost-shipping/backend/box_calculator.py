"""
Box Calculator - Determine Optimal Box Size
===========================================

Calculates required box size based on product dimensions and total weight.

Box Types:
- Small: 50g, 45mm depth (max 60mm)
- Large: 60g, 70mm depth (max 85mm)

FILE: UI/modules_external/auspost-shipping/backend/box_calculator.py
"""

from typing import Dict, Any, List


class BoxCalculator:
    """Calculate optimal box size for orders."""
    
    # Box specifications
    BOX_SPECS = {
        'small': {
            'weight_grams': 50,
            'depth_mm': 45,
            'max_depth_mm': 60,
            'dimensions_cm': {'length': 22, 'width': 16, 'height': 7.7}  # Standard Australia Post small box
        },
        'large': {
            'weight_grams': 60,
            'depth_mm': 70,
            'max_depth_mm': 85,
            'dimensions_cm': {'length': 31, 'width': 22.5, 'height': 10.2}  # Standard Australia Post medium box
        }
    }
    
    @staticmethod
    def calculate_box_requirements(order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate box requirements for an order.
        
        Args:
            order: Parsed order with total_weight_grams and total_thickness_mm
            
        Returns:
            Box details with type, dimensions, and total weight
        """
        total_thickness = order.get('total_thickness_mm', 0)
        product_weight = order.get('total_weight_grams', 0)
        
        # Determine box size based on thickness
        if total_thickness <= BoxCalculator.BOX_SPECS['small']['max_depth_mm']:
            box_type = 'small'
        elif total_thickness <= BoxCalculator.BOX_SPECS['large']['max_depth_mm']:
            box_type = 'large'
        else:
            # Need custom/oversized box
            box_type = 'custom'
        
        # Get box specifications
        if box_type in BoxCalculator.BOX_SPECS:
            box_spec = BoxCalculator.BOX_SPECS[box_type]
            total_weight_grams = product_weight + box_spec['weight_grams']
            
            return {
                'box_type': box_type,
                'box_weight_grams': box_spec['weight_grams'],
                'product_weight_grams': product_weight,
                'total_weight_grams': total_weight_grams,
                'total_weight_kg': round(total_weight_grams / 1000, 3),
                'total_thickness_mm': total_thickness,
                'dimensions_cm': box_spec['dimensions_cm'],
                'length_cm': box_spec['dimensions_cm']['length'],
                'width_cm': box_spec['dimensions_cm']['width'],
                'height_cm': box_spec['dimensions_cm']['height']
            }
        else:
            # Custom box needed
            return {
                'box_type': 'custom',
                'box_weight_grams': 100,  # Estimate
                'product_weight_grams': product_weight,
                'total_weight_grams': product_weight + 100,
                'total_weight_kg': round((product_weight + 100) / 1000, 3),
                'total_thickness_mm': total_thickness,
                'dimensions_cm': {'length': 40, 'width': 30, 'height': 15},  # Estimate
                'length_cm': 40,
                'width_cm': 30,
                'height_cm': 15,
                'note': 'Custom box required - thickness exceeds standard boxes'
            }
    
    @staticmethod
    def get_box_specs() -> Dict[str, Dict[str, Any]]:
        """Get box specifications."""
        return BoxCalculator.BOX_SPECS.copy()
    
    @staticmethod
    def calculate_multiple_orders(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate box requirements for multiple orders.
        
        Args:
            orders: List of parsed orders
            
        Returns:
            Orders with added box_details field
        """
        for order in orders:
            if 'error' not in order:
                order['box_details'] = BoxCalculator.calculate_box_requirements(order)
        
        return orders
