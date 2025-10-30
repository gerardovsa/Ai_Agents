"""
InHouse Print Calculator Wrapper
Provides access to InHouse Print quote calculators for the AI agent system.

This wrapper imports the calculator from the In_House_SQL project and provides
methods that match the tool schemas for use by the AI agent.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

class CalculatorWrapper:
    """
    Wrapper for InHouse Print calculators.
    Imports calculator from In_House_SQL project.
    """
    
    def __init__(self, **kwargs):
        """Initialize calculator wrapper"""
        self.calculator = None
        self.db_connector = None
        self._initialize_calculator()
    
    def _initialize_calculator(self):
        """Import and initialize the calculator from In_House_SQL project"""
        try:
            # Add In_House_SQL G_Folder to path
            inhouse_sql_path = Path(r"C:\Users\gpoli\GIT\In_House_SQL\G_Folder")
            if inhouse_sql_path.exists():
                sys.path.insert(0, str(inhouse_sql_path))
                sys.path.insert(0, str(inhouse_sql_path / "Quote_Calculator"))
            
            # Import database connector from In_House_SQL
            from tools.db_connector import InHousePrintDB
            
            # Import calculator
            from complete_calculator_implementation import ComprehensiveQuoteCalculator
            
            # Initialize database connection
            config_path = inhouse_sql_path / "config" / "database-config.json"
            self.db_connector = InHousePrintDB(str(config_path))
            
            # Initialize calculator
            self.calculator = ComprehensiveQuoteCalculator(self.db_connector)
            
            print("✅ Calculator initialized successfully")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize calculator: {e}")
            print(f"   Calculator tools will return error messages")
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
        finish_size: str,
        stock_type: str,
        print_type: str,
        celloglaze: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for business cards using Shopify pricing
        
        Args:
            quantity: Number of cards (250, 500, 1000, 2000, 5000)
            finish_size: Card size (e.g., '90x55mm')
            stock_type: 'standard' or 'premium'
            print_type: 'single_sided' or 'double_sided'
            celloglaze: Optional finish ('none', 'gloss', 'matt')
        
        Returns:
            Quote dictionary with Shopify-matched pricing
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            result = self.calculator.calculate_business_cards(
                quantity=quantity,
                finish_size=finish_size,
                stock_type=stock_type,
                print_type=print_type,
                celloglaze=celloglaze or "none"
            )
            
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"success": True, "quote": result}
                
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
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate quote for corflute signs
        
        Args:
            quantity: Number of signs (tier pricing applies)
            width: Width in mm
            height: Height in mm
            thickness: '3mm' or '5mm'
            double_sided: Print both sides
        
        Returns:
            Quote with tier-based pricing
        """
        if not self._ensure_calculator():
            return self._format_error("Calculator not available - check server logs")
        
        try:
            result = self.calculator.calculate_corflute_signs(
                quantity=quantity,
                width=width,
                height=height,
                thickness=thickness,
                double_sided=double_sided
            )
            
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                return result.__dict__
            else:
                return {"success": True, "quote": result}
                
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
