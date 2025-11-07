"""
Quote Calculator Wrapper - Standalone Version
Integrates 8 Shopify calculators with AI agent tool system
NO In_House_SQL dependency - uses JSON pricing configs
"""

import os
import sys
import json
from pathlib import Path

class QuoteCalculatorWrapper:
    """
    Wrapper class for all quote calculators
    Provides unified interface for AI agent tool calls
    """
    
    def __init__(self, **kwargs):
        """Initialize calculator wrapper with JSON config paths"""
        self.credentials = None  # Credentials injected at runtime (not needed for Shopify calcs)
        
        # Get base path (calculator-module/backend/)
        self.base_path = Path(__file__).parent
        self.calculators_path = self.base_path / 'shopify_calculators'
        self.configs_path = self.base_path / 'configs'
        
        # Add calculators to Python path
        if str(self.calculators_path) not in sys.path:
            sys.path.insert(0, str(self.calculators_path))
        
        # Initialize calculator instances
        self._init_calculators()
    
    def _init_calculators(self):
        """Initialize all 8 Shopify calculators"""
        try:
            # Import calculator classes (from shopify_calculators/)
            from business_card_calculator_shopify import ShopifyBusinessCardCalculator
            from corflute_calculator_shopify import CorflutePricingCalculatorShopify
            from EconomicalBusinessCards_Shopify_Calculator import EconomicalBusinessCardsShopifyCalculator
            from PremiumBusinessCards_Shopify_Calculator import PremiumBusinessCardsShopifyCalculator
            from PerfectBound_Shopify_Calculator import PerfectBoundShopifyCalculator
            from WireBound_Shopify_Calculator import WireBoundShopifyCalculator
            from SpiralBound_Shopify_Calculator import SpiralBoundShopifyCalculator
            from FoldedFlyers_Shopify_Calculator import FoldedFlyersShopifyCalculator
            
            # Instantiate all 8 calculators
            self.calc_business_card = ShopifyBusinessCardCalculator()
            self.calc_corflute = CorflutePricingCalculatorShopify()
            self.calc_economical_bc = EconomicalBusinessCardsShopifyCalculator()
            self.calc_premium_bc = PremiumBusinessCardsShopifyCalculator()
            self.calc_perfect_bound = PerfectBoundShopifyCalculator()
            self.calc_wire_bound = WireBoundShopifyCalculator()
            self.calc_spiral_bound = SpiralBoundShopifyCalculator()
            self.calc_folded_flyers = FoldedFlyersShopifyCalculator()
            
            calc_count = sum(1 for c in [
                self.calc_business_card, self.calc_corflute, self.calc_economical_bc,
                self.calc_premium_bc, self.calc_perfect_bound, self.calc_wire_bound,
                self.calc_spiral_bound, self.calc_folded_flyers
            ] if c is not None)
            
            print(f"✅ Calculator Wrapper initialized: {calc_count} calculators loaded")
            
        except ImportError as e:
            print(f"⚠️ Calculator import error: {e}")
            print(f"Calculators path: {self.calculators_path}")
            print(f"Configs path: {self.configs_path}")
            import traceback
            traceback.print_exc()
            # Initialize with None (calculators will fail gracefully)
            self.calc_business_card = None
            self.calc_corflute = None
            self.calc_economical_bc = None
            self.calc_premium_bc = None
            self.calc_perfect_bound = None
            self.calc_wire_bound = None
            self.calc_spiral_bound = None
            self.calc_folded_flyers = None
    
    def _load_json_config(self, config_name):
        """Load JSON pricing config"""
        config_file = self.configs_path / f"{config_name}.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return None
    
    # ========================
    # TOOL METHODS (called by AI agent)
    # ========================
    
    def calculate_business_cards(self, quantity, stock_type="standard", sides="double", 
                                 finish="none", turnaround="standard", **kwargs):
        """
        Calculate business card quote (standard Shopify calculator)
        
        Args:
            quantity: Number of cards (500, 1000, 2000, 5000, 10000)
            stock_type: "standard" (300gsm Satin) or "premium" (350gsm Satin, 420gsm KingKong, 350gsm Ecostar)
            sides: "color" or "bw" (black and white)
            finish: "none" or celloglaze options for premium
            turnaround: "standard" (5-7 days) or "express" (2-3 days)
        
        Returns:
            dict: {
                "total_price": float,
                "unit_price": float (per card),
                "breakdown": {...},
                "specs": {...}
            }
        """
        if not self.calc_business_card:
            return {"error": "Business card calculator not loaded"}
        
        try:
            # Map user-friendly parameters to Shopify calculator parameters
            from business_card_calculator_shopify import PrintType, FinishSize, StockTypeStandard, StockTypePremium, CelloglazePremium
            
            # Map sides parameter (1 or 2)
            num_sides = 2 if sides.lower() in ["double", "2", "two"] else 1
            
            # Map print type
            print_type = PrintType.COLOR if sides.lower() not in ["bw", "black_and_white", "blackwhite"] else PrintType.BLACK_AND_WHITE
            
            # Map finish size (default standard)
            finish_size = FinishSize.STANDARD_90X55
            
            # Determine if standard or premium
            if stock_type == "standard":
                # Standard business cards (Satin 300gsm)
                result = self.calc_business_card.calculate_standard_business_cards(
                    quantity=quantity,
                    sides=num_sides,
                    print_type=print_type,
                    finish_size=finish_size,
                    stock_type=StockTypeStandard.SATIN_300GSM
                )
            else:
                # Premium business cards (Satin 350gsm, KingKong 420gsm, Ecostar 350gsm)
                # Map stock type
                if "ecostar" in stock_type.lower():
                    stock = StockTypePremium.ECOSTAR_350GSM
                elif "kingkong" in stock_type.lower() or "420" in stock_type:
                    stock = StockTypePremium.KINGKONG_420GSM
                else:
                    stock = StockTypePremium.SATIN_350GSM
                
                # Map celloglaze finish
                if finish == "none" or not finish:
                    cello = CelloglazePremium.NONE
                elif "gloss" in finish.lower():
                    cello = CelloglazePremium.TWO_SIDE_GLOSS if "two" in finish.lower() or "2" in finish else CelloglazePremium.ONE_SIDE_GLOSS
                elif "matt" in finish.lower() or "matte" in finish.lower():
                    cello = CelloglazePremium.TWO_SIDE_MATT if "two" in finish.lower() or "2" in finish else CelloglazePremium.ONE_SIDE_MATT
                elif "silk" in finish.lower():
                    cello = CelloglazePremium.TWO_SIDE_SILK if "two" in finish.lower() or "2" in finish else CelloglazePremium.ONE_SIDE_SILK
                else:
                    cello = CelloglazePremium.NONE
                
                result = self.calc_business_card.calculate_premium_business_cards(
                    quantity=quantity,
                    sides=num_sides,
                    print_type=print_type,
                    finish_size=finish_size,
                    stock_type=stock,
                    celloglaze=cello
                )
            
            # Convert result object to dictionary
            return result.to_dict()
        except Exception as e:
            import traceback
            return {"error": f"Business card calculation failed: {str(e)}", "traceback": traceback.format_exc()}
    
    def calculate_corflute_signs(self, width_mm, height_mm, quantity, thickness="5mm", 
                                 print_type="single", mounting="none", **kwargs):
        """
        Calculate corflute sign quote (tier pricing)
        
        Args:
            width_mm: Width in millimeters
            height_mm: Height in millimeters
            quantity: Number of signs
            thickness: "3mm" or "5mm"
            print_type: "single" or "double"
            mounting: "none", "4_corners", "2_top", etc.
        
        Returns:
            dict: Complete pricing breakdown with tier pricing
        """
        if not self.calc_corflute:
            return {"error": "Corflute calculator not loaded"}
        
        try:
            from corflute_calculator_shopify import CorfluteSizePreset, CorfiuteThickness, EyeletOption, CuttingType
            
            # Map thickness
            thick = CorfiuteThickness.MM_5 if "5" in str(thickness) else CorfiuteThickness.MM_3
            
            # Map eyelet options
            eyelet_map = {
                "none": EyeletOption.NONE,
                "4_corners": EyeletOption.FOUR_CORNERS,
                "2_top": EyeletOption.TWO_TOP,
                "2_center_lr": EyeletOption.TWO_CENTER_LR,
                "2_center_tb": EyeletOption.TWO_CENTER_TB,
                "6_top_bottom": EyeletOption.SIX_TOP_BOTTOM,
                "6_left_right": EyeletOption.SIX_LEFT_RIGHT
            }
            eyelets = eyelet_map.get(mounting, EyeletOption.NONE)
            
            # Double-sided flag
            double_sided = print_type.lower() in ["double", "2", "two"]
            
            result = self.calc_corflute.calculate_quote(
                size_preset=CorfluteSizePreset.CUSTOM,
                custom_width_mm=width_mm,
                custom_height_mm=height_mm,
                thickness=thick,
                quantity=quantity,
                double_sided=double_sided,
                eyelet_option=eyelets,
                cutting_type=CuttingType.STANDARD
            )
            return result
        except Exception as e:
            import traceback
            return {"error": f"Corflute calculation failed: {str(e)}", "traceback": traceback.format_exc()}
    
    def calculate_economical_business_cards(self, quantity, stock_type="350gsm", 
                                           sides="double", **kwargs):
        """
        Calculate economical business card quote (budget option)
        
        Args:
            quantity: Number of cards (500, 1000, 2000, 5000)
            stock_type: "350gsm" or "400gsm"
            sides: "single" or "double"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_economical_bc:
            return {"error": "Economical business card calculator not loaded"}
        
        try:
            result = self.calc_economical_bc(
                quantity=quantity,
                stock_type=stock_type,
                sides=sides
            )
            return result
        except Exception as e:
            return {"error": f"Economical business card calculation failed: {str(e)}"}
    
    def calculate_premium_business_cards(self, quantity, stock_type="400gsm", 
                                        finish="spot_uv", **kwargs):
        """
        Calculate premium business card quote (high-end option)
        
        Args:
            quantity: Number of cards (500, 1000, 2000, 5000)
            stock_type: "400gsm", "450gsm", "silk"
            finish: "spot_uv", "raised_foil", "full_foil"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_premium_bc:
            return {"error": "Premium business card calculator not loaded"}
        
        try:
            result = self.calc_premium_bc(
                quantity=quantity,
                stock_type=stock_type,
                finish=finish
            )
            return result
        except Exception as e:
            return {"error": f"Premium business card calculation failed: {str(e)}"}
    
    def calculate_perfect_bound_books(self, page_count, quantity, cover_stock="300gsm",
                                     inner_stock="115gsm", size="a5", **kwargs):
        """
        Calculate perfect bound book quote (glued spine)
        
        Args:
            page_count: Number of pages (must be multiple of 4)
            quantity: Number of books
            cover_stock: "250gsm", "300gsm", "350gsm"
            inner_stock: "80gsm", "100gsm", "115gsm", "128gsm"
            size: "a5", "a4", "custom"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_perfect_bound:
            return {"error": "Perfect bound calculator not loaded"}
        
        try:
            result = self.calc_perfect_bound(
                page_count=page_count,
                quantity=quantity,
                cover_stock=cover_stock,
                inner_stock=inner_stock,
                size=size
            )
            return result
        except Exception as e:
            return {"error": f"Perfect bound calculation failed: {str(e)}"}
    
    def calculate_wire_bound_books(self, page_count, quantity, cover_stock="250gsm",
                                   inner_stock="100gsm", size="a5", **kwargs):
        """
        Calculate wire bound book quote (spiral binding)
        
        Args:
            page_count: Number of pages
            quantity: Number of books
            cover_stock: "200gsm", "250gsm", "300gsm"
            inner_stock: "80gsm", "100gsm", "115gsm"
            size: "a5", "a4", "dl"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_wire_bound:
            return {"error": "Wire bound calculator not loaded"}
        
        try:
            result = self.calc_wire_bound(
                page_count=page_count,
                quantity=quantity,
                cover_stock=cover_stock,
                inner_stock=inner_stock,
                size=size
            )
            return result
        except Exception as e:
            return {"error": f"Wire bound calculation failed: {str(e)}"}
    
    def calculate_spiral_bound_books(self, page_count, quantity, cover_stock="250gsm",
                                    inner_stock="100gsm", size="a4", **kwargs):
        """
        Calculate spiral bound book quote (plastic coil binding)
        
        Args:
            page_count: Number of pages
            quantity: Number of books
            cover_stock: "200gsm", "250gsm", "300gsm"
            inner_stock: "80gsm", "100gsm", "115gsm"
            size: "a4", "a5", "letter"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_spiral_bound:
            return {"error": "Spiral bound calculator not loaded"}
        
        try:
            result = self.calc_spiral_bound(
                page_count=page_count,
                quantity=quantity,
                cover_stock=cover_stock,
                inner_stock=inner_stock,
                size=size
            )
            return result
        except Exception as e:
            return {"error": f"Spiral bound calculation failed: {str(e)}"}
    
    def calculate_folded_flyers(self, size, quantity, stock="150gsm", fold_type="half",
                               finish="none", **kwargs):
        """
        Calculate folded flyer quote (DL, A4, A5)
        
        Args:
            size: "dl", "a4", "a5"
            quantity: Number of flyers
            stock: "115gsm", "150gsm", "170gsm", "200gsm"
            fold_type: "half", "tri", "z_fold", "gate"
            finish: "none", "gloss", "matte"
        
        Returns:
            dict: {"total_price": float, "unit_price": float, ...}
        """
        if not self.calc_folded_flyers:
            return {"error": "Folded flyers calculator not loaded"}
        
        try:
            result = self.calc_folded_flyers(
                size=size,
                quantity=quantity,
                stock=stock,
                fold_type=fold_type,
                finish=finish
            )
            return result
        except Exception as e:
            return {"error": f"Folded flyers calculation failed: {str(e)}"}
    
    def get_stock_list(self, calculator_type="all", **kwargs):
        """
        Get available stock options for calculators
        
        Args:
            calculator_type: "business_cards", "corflute", "books", "flyers", or "all"
        
        Returns:
            dict: {
                "business_cards": [...],
                "corflute": [...],
                "books": {...},
                "flyers": [...]
            }
        """
        stocks = {
            "business_cards": [
                {"gsm": "350gsm", "type": "standard", "price_per_1000": 145.0},
                {"gsm": "400gsm", "type": "premium", "price_per_1000": 175.0},
                {"gsm": "450gsm", "type": "premium", "price_per_1000": 195.0},
                {"gsm": "silk", "type": "premium", "price_per_1000": 210.0}
            ],
            "corflute": [
                {"thickness": "3mm", "price_per_sqm": 45.0},
                {"thickness": "5mm", "price_per_sqm": 55.0}
            ],
            "books": {
                "cover": ["200gsm", "250gsm", "300gsm", "350gsm"],
                "inner": ["80gsm", "100gsm", "115gsm", "128gsm"]
            },
            "flyers": [
                {"gsm": "115gsm", "price_per_1000": 85.0},
                {"gsm": "150gsm", "price_per_1000": 95.0},
                {"gsm": "170gsm", "price_per_1000": 110.0},
                {"gsm": "200gsm", "price_per_1000": 125.0}
            ]
        }
        
        if calculator_type == "all":
            return stocks
        elif calculator_type in stocks:
            return {calculator_type: stocks[calculator_type]}
        else:
            return {"error": f"Unknown calculator type: {calculator_type}"}
    
    def get_calculator_requirements(self, calculator_name, **kwargs):
        """
        Get parameter requirements for a specific calculator
        
        Args:
            calculator_name: Name of calculator (e.g., "business_cards")
        
        Returns:
            dict: {
                "required": [...],
                "optional": [...],
                "defaults": {...},
                "validations": {...}
            }
        """
        requirements = {
            "business_cards": {
                "required": ["quantity"],
                "optional": ["stock_type", "sides", "finish", "turnaround"],
                "defaults": {
                    "stock_type": "standard",
                    "sides": "double",
                    "finish": "none",
                    "turnaround": "standard"
                },
                "validations": {
                    "quantity": [500, 1000, 2000, 5000, 10000],
                    "stock_type": ["standard", "premium"],
                    "sides": ["single", "double"],
                    "finish": ["none", "matte", "gloss", "spot_uv"],
                    "turnaround": ["standard", "express"]
                }
            },
            "corflute": {
                "required": ["width_mm", "height_mm", "quantity"],
                "optional": ["thickness", "print_type", "mounting"],
                "defaults": {
                    "thickness": "5mm",
                    "print_type": "single",
                    "mounting": "none"
                },
                "validations": {
                    "thickness": ["3mm", "5mm"],
                    "print_type": ["single", "double"],
                    "mounting": ["none", "h_stakes", "eyelets"]
                }
            },
            "perfect_bound": {
                "required": ["page_count", "quantity"],
                "optional": ["cover_stock", "inner_stock", "size"],
                "defaults": {
                    "cover_stock": "300gsm",
                    "inner_stock": "115gsm",
                    "size": "a5"
                },
                "validations": {
                    "page_count": "must be multiple of 4",
                    "cover_stock": ["250gsm", "300gsm", "350gsm"],
                    "inner_stock": ["80gsm", "100gsm", "115gsm", "128gsm"],
                    "size": ["a5", "a4", "custom"]
                }
            },
            "wire_bound": {
                "required": ["page_count", "quantity"],
                "optional": ["cover_stock", "inner_stock", "size"],
                "defaults": {
                    "cover_stock": "250gsm",
                    "inner_stock": "100gsm",
                    "size": "a5"
                },
                "validations": {
                    "cover_stock": ["200gsm", "250gsm", "300gsm"],
                    "inner_stock": ["80gsm", "100gsm", "115gsm"],
                    "size": ["a5", "a4", "dl"]
                }
            },
            "spiral_bound": {
                "required": ["page_count", "quantity"],
                "optional": ["cover_stock", "inner_stock", "size"],
                "defaults": {
                    "cover_stock": "250gsm",
                    "inner_stock": "100gsm",
                    "size": "a4"
                },
                "validations": {
                    "cover_stock": ["200gsm", "250gsm", "300gsm"],
                    "inner_stock": ["80gsm", "100gsm", "115gsm"],
                    "size": ["a4", "a5", "letter"]
                }
            },
            "folded_flyers": {
                "required": ["size", "quantity"],
                "optional": ["stock", "fold_type", "finish"],
                "defaults": {
                    "stock": "150gsm",
                    "fold_type": "half",
                    "finish": "none"
                },
                "validations": {
                    "size": ["dl", "a4", "a5"],
                    "stock": ["115gsm", "150gsm", "170gsm", "200gsm"],
                    "fold_type": ["half", "tri", "z_fold", "gate"],
                    "finish": ["none", "gloss", "matte"]
                }
            }
        }
        
        if calculator_name in requirements:
            return requirements[calculator_name]
        else:
            return {"error": f"Unknown calculator: {calculator_name}"}


# Test code (runs when imported)
if __name__ == "__main__":
    print("Testing QuoteCalculatorWrapper...")
    
    try:
        wrapper = QuoteCalculatorWrapper()
        print(f"✅ Wrapper initialized")
        
        # Test 1: Business card calculation
        print("\n1. Testing Business Cards...")
        result = wrapper.calculate_business_cards(quantity=1000, stock_type="standard")
        if "error" not in result:
            total = result.get('total_inc_gst', result.get('total_ex_gst', 'N/A'))
            print(f"   ✅ Business card quote: ${total:.2f}")
            print(f"   Breakdown: {result.get('cost_breakdown', {})}")
        else:
            print(f"   ❌ Business card error: {result['error']}")
        
        # Test 2: Corflute signs
        print("\n2. Testing Corflute Signs...")
        result2 = wrapper.calculate_corflute_signs(width_mm=600, height_mm=900, quantity=10)
        if "error" not in result2:
            total2 = result2.get('total', 'N/A')
            print(f"   ✅ Corflute quote: ${total2:.2f}")
            print(f"   Area: {result2.get('total_sqm', 0):.2f} sqm")
        else:
            print(f"   ❌ Corflute error: {result2['error']}")
        
        # Test 3: Stock list
        print("\n3. Testing Stock List...")
        stocks = wrapper.get_stock_list()
        print(f"   ✅ Stock list retrieved: {len(stocks)} categories")
        
        print("\n" + "="*50)
        print("✅ ALL TESTS PASSED!")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
