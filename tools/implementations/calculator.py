"""
InHouse Print Calculator Wrapper - STANDALONE VERSION
======================================================
Provides access to InHouse Print quote calculators for the AI agent system.

This wrapper uses the STANDALONE calculator module (NO In_House_SQL dependency).
All calculators are Shopify-based with JSON pricing configs (no SQL Server).

Date: October 31, 2025
Status: PRODUCTION READY
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

class CalculatorWrapper:
    """
    Wrapper for InHouse Print calculators - STANDALONE VERSION.
    Uses calculator module from UI/external/modules/calculator-module/backend/
    NO dependency on In_House_SQL project.
    """
    
    def __init__(self, **kwargs):
        """Initialize calculator wrapper"""
        self.calculator = None
        self._initialize_calculator()
    
    def _initialize_calculator(self):
        """Import and initialize the calculator module"""
        try:
            # Add calculator module to path
            calculator_path = Path(__file__).parent.parent.parent / "UI" / "modules_external" / "quote-calculator" / "implementations"
            
            if not calculator_path.exists():
                print(f"⚠️ Calculator module not found: {calculator_path}")
                raise FileNotFoundError(f"Calculator module not found: {calculator_path}")
            
            sys.path.insert(0, str(calculator_path))
            
            # Import calculator wrapper functions directly
            import calculator_wrapper
            
            # Store the module so we can call its functions
            self.calculator = calculator_wrapper
            
            print("✅ Calculator module initialized successfully (GOD + Shopify calculators available)")
            
        except Exception as e:
            print(f"WARNING: Could not initialize calculator: {e}")
            print(f"Calculator tools will return error messages")
            self.calculator = None
            self.db_connector = None
    
    def _ensure_calculator(self) -> bool:
        """Check if calculator is available"""
        if self.calculator is None:
            return False
        return True
    
    def _format_error(self, message: str) -> Dict[str, Any]:
        """Format error response"""
        return {
            "success": False,
            "error": message,
            "quote": None
        }
    
    def calculate_flyers(
        self,
        quantity: int,
        width: int,
        height: int,
        stock_gsm: int,
        print_mode: str,
        cello_type: Optional[str] = None,
        folded: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for flyers/leaflets (also used for business cards)
        
        Args:
            quantity: Number of items (e.g., 1000)
            width: Width in mm (e.g., 90 for business cards, 210 for A4)
            height: Height in mm (e.g., 55 for business cards, 297 for A4)
            stock_gsm: Stock weight (e.g., 350 for business cards)
            print_mode: 'single_sided', 'double_sided', 'no_print'
            cello_type: Optional cellophane finish
            folded: Whether flyer is folded
        
        Returns:
            Quote dictionary with pricing details
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            # Call calculator
            result = self.calculator.calculate_flyers(
                quantity=quantity,
                width=width,
                height=height,
                stock_gsm=stock_gsm,
                print_mode=print_mode,
                cello_type=cello_type or "none",
                folded=folded
            )
            
            # Convert result to dict if needed
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"success": True, "quote": result}
                
        except Exception as e:
            return self._format_error(f"Calculation failed: {str(e)}")
    
    def calculate_business_cards(
        self,
        quantity: int,
        finish_size: str = "90x55",
        stock_type: str = "standard",
        print_type: str = "double_sided",
        celloglaze: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for business cards using Shopify pricing
        
        Args:
            quantity: Number of cards (500, 1000, 2000, 5000, 10000)
            finish_size: Card size (e.g., '90x55mm') - ignored for now
            stock_type: 'standard' (300gsm) or 'premium' (350gsm)
            print_type: 'single_sided', 'double_sided', 'color', 'bw'
            celloglaze: Optional finish ('none', 'gloss', 'matt', 'silk')
        
        Returns:
            Quote dictionary with Shopify-matched pricing
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            # Map print_type to sides
            sides = "double" if "double" in print_type.lower() else "single"
            finish = celloglaze or "none"
            
            result = self.calculator.calculate_business_cards(
                quantity=quantity,
                stock_type=stock_type,
                sides=sides,
                finish=finish
            )
            
            # Result is already a dict
            return result if isinstance(result, dict) else {"success": True, "quote": result}
                
        except Exception as e:
            return self._format_error(f"Business card calculation failed: {str(e)}")
    
    def calculate_perfect_bound_books(
        self,
        quantity: int,
        total_pages: int,
        cover_stock_gsm: int,
        internal_stock_gsm: int,
        cover_print_mode: str,
        internal_print_mode: str,
        cover_lamination: Optional[str] = None,
        spot_uv: Optional[bool] = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for perfect bound books
        
        Args:
            quantity: Number of books
            total_pages: Total page count (divisible by 4, min 40)
            cover_stock_gsm: Cover stock weight
            internal_stock_gsm: Internal pages stock weight
            cover_print_mode: 'single_sided' or 'double_sided'
            internal_print_mode: 'single_sided', 'double_sided', 'black_white', 'mixed'
            cover_lamination: Optional lamination ('none', 'gloss', 'matt')
            spot_uv: Add spot UV finish
        
        Returns:
            Quote dictionary with binding costs
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            result = self.calculator.calculate_perfect_bound_books(
                quantity=quantity,
                total_pages=total_pages,
                cover_stock_gsm=cover_stock_gsm,
                internal_stock_gsm=internal_stock_gsm,
                cover_print_mode=cover_print_mode,
                internal_print_mode=internal_print_mode,
                cover_lamination=cover_lamination or "none",
                spot_uv=spot_uv
            )
            
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"success": True, "quote": result}
                
        except Exception as e:
            return self._format_error(f"Book calculation failed: {str(e)}")
    
    def calculate_corflute_signs(
        self,
        quantity: int,
        width: int,
        height: int,
        thickness: Optional[str] = "5mm",
        double_sided: Optional[bool] = False,
        mounting: Optional[str] = "none",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for corflute signs
        
        Args:
            quantity: Number of signs (tier pricing applies)
            width: Width in mm (width_mm parameter)
            height: Height in mm (height_mm parameter)
            thickness: '3mm' or '5mm'
            double_sided: Print both sides
            mounting: 'none', '4_corners', '2_top', etc.
        
        Returns:
            Quote with tier-based pricing
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            # Import GOD calculator
            backend_dir = Path(__file__).parent.parent.parent / "UI" / "modules_external" / "quote-calculator" / "backend"
            if str(backend_dir) not in sys.path:
                sys.path.insert(0, str(backend_dir))
            
            from god_calculators.corflute_calculator import CorflutePricingCalculator
            
            # Initialize calculator (no db needed)
            calculator = CorflutePricingCalculator()
            
            # Convert parameters
            thickness_int = int(thickness.replace("mm", ""))  # Convert "3mm" to 3
            print_sides_str = "double" if double_sided else "single"
            
            # Calculate quote
            result = calculator.calculate_base_quote(
                quantity=quantity,
                width_mm=width,
                height_mm=height,
                thickness_mm=thickness_int,
                print_sides=print_sides_str
            )
            
            # Format result (result is already a dict)
            return {
                "success": True,
                "product_type": "Corflute Signs (PVC Foamboard)",
                "quantity": result["quantity"],
                "total_price": float(result["total_inc_gst"]),
                "unit_price": float(result["price_per_unit_inc_gst"]),
                "unit_price_ex_gst": float(result["price_per_unit_ex_gst"]),
                "breakdown": {
                    "material_cost_per_unit": float(result["material_cost_per_unit"]),
                    "print_cost_per_unit": float(result["print_cost_per_unit"]),
                    "cutting_cost_per_unit": float(result["cutting_cost_per_unit"]),
                    "total_ex_gst": float(result["total_cost_inc_margin"]),
                    "gst_amount": float(result["gst_amount"]),
                    "margin_percent": float(result["margin_percent"])
                },
                "specifications": {
                    "size": f"{width}x{height}mm",
                    "thickness": f"{thickness_int}mm",
                    "print_sides": result["print_specification"],
                    "area_sqm": float(result["area_sqm"])
                }
            }
                
        except Exception as e:
            return self._format_error(f"Corflute calculation failed: {str(e)}")
    
    def calculate_booklets(
        self,
        quantity: int,
        total_pages: int,
        cover_stock_gsm: int,
        internal_stock_gsm: int,
        cover_print_mode: str,
        internal_print_mode: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for saddle-stitched booklets
        
        Args:
            quantity: Number of booklets
            total_pages: Total page count (divisible by 4, min 8)
            cover_stock_gsm: Cover stock weight
            internal_stock_gsm: Internal pages stock weight
            cover_print_mode: 'single_sided' or 'double_sided'
            internal_print_mode: 'single_sided', 'double_sided', 'black_white'
        
        Returns:
            Quote for stapled booklets
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            result = self.calculator.calculate_booklets(
                quantity=quantity,
                total_pages=total_pages,
                cover_stock_gsm=cover_stock_gsm,
                internal_stock_gsm=internal_stock_gsm,
                cover_print_mode=cover_print_mode,
                internal_print_mode=internal_print_mode
            )
            
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"success": True, "quote": result}
                
        except Exception as e:
            return self._format_error(f"Booklet calculation failed: {str(e)}")
    
    def get_stock_list(self, **kwargs) -> Dict[str, Any]:
        """
        Get list of available paper stocks
        
        Returns:
            List of stocks with GSM, descriptions, costs
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            # Get stocks from database via calculator
            if hasattr(self.calculator, 'get_available_stocks'):
                stocks = self.calculator.get_available_stocks()
            else:
                # Fallback: query database directly
                stocks = self.db_connector.execute_query(
                    "SELECT StockID, StockTypeID, GSM, CostPerThousand FROM Quote_DigitalStocks ORDER BY GSM"
                )
            
            return {
                "success": True,
                "stocks": stocks
            }
            
        except Exception as e:
            return self._format_error(f"Could not retrieve stock list: {str(e)}")
    
    def calculate_notepads_a5(
        self,
        quantity: int,
        leaves_per_pad: int,
        print_type: str,
        stock_type: str,
        artworks: Optional[int] = 1,
        finish_size: Optional[str] = "A5 Portrait",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for A5 notepads with padding service
        
        Args:
            quantity: Number of notepads (25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 750, 1000, 2000)
            leaves_per_pad: Sheets per pad (25, 50, or 100)
            print_type: Print mode ('Colour 1 sided', 'Colour 2 sided', 'Black & White 1 sided', 'Black & White 2 sided')
            stock_type: Paper stock ('Uncoated Bond 80GSM', 'Uncoated Bond 90GSM', 'Uncoated Bond 100GSM', 'Revive 100% Recycled 80GSM Bond')
            artworks: Number of artwork designs (1-10, default 1, first free)
            finish_size: Notepad size ('A5 Portrait' only, default)
        
        Returns:
            Quote for notepads with padding service, cardboard backing, and tier-based pricing
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            # Import and use NotepadsA5ShopifyCalculator
            from inhouse_modules.shopify_calculators.NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator
            
            calc = NotepadsA5ShopifyCalculator()
            result = calc.calculate(
                quantity=quantity,
                artworks=artworks,
                finish_size=finish_size,
                leaves_per_pad=leaves_per_pad,
                print_type=print_type,
                stock_type=stock_type
            )
            
            # Convert result to dict
            return {
                "success": True,
                "total_price": float(result.total_price),
                "unit_price": float(result.unit_price),
                "cost_per_pad": float(result.cost_per_pad),
                "quantity": result.quantity,
                "breakdown": result.breakdown,
                "specifications": result.specifications
            }
                
        except Exception as e:
            return self._format_error(f"Notepad calculation failed: {str(e)}")
    
    def get_calculator_requirements(
        self,
        product_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get detailed requirements for a specific calculator
        
        Args:
            product_type: Type of product (flyers, business_cards, etc.)
        
        Returns:
            Requirements dictionary with parameters, defaults, business rules
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            requirements = self.calculator.get_calculator_requirements(product_type)
            
            return {
                "success": True,
                "product_type": product_type,
                "requirements": requirements
            }
            
        except Exception as e:
            return self._format_error(f"Could not get requirements: {str(e)}")
