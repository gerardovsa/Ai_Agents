"""
Test calculators with proper database configuration
"""
import sys
import os
from pathlib import Path
import json

# Add root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Add inhouse_modules to path (for shopify_calculators)
inhouse_modules_path = root_dir / "inhouse_modules"
if str(inhouse_modules_path) not in sys.path:
    sys.path.insert(0, str(inhouse_modules_path))

# Set encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

def create_test_db_config():
    """Create a test database configuration"""
    config = {
        "host": "localhost",  # Will be overridden by actual config
        "port": 1433,
        "database": "InHousePrint",
        "user": "test",
        "password": "test"
    }
    
    # Create config directory
    config_dir = root_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "database-config-test.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(config_file)


def test_calculator_initialization():
    """Test if we can initialize the calculator"""
    print("\n" + "="*80)
    print("CALCULATOR INITIALIZATION TEST")
    print("="*80)
    
    try:
        from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator
        from inhouse_modules.db_connector import InHousePrintDB
        print("[OK] Successfully imported ComprehensiveQuoteCalculator and InHousePrintDB")
        
        # Try to initialize database connector
        print("\nAttempting to initialize database connector...")
        try:
            # Try with default config path
            db = InHousePrintDB()
            print("[OK] Database connector initialized with default config")
        except Exception as db_error:
            print(f"[WARNING] Could not connect to database: {db_error}")
            print("  Attempting to create mock database connector...")
            
            # Create a mock database connector for testing
            class MockDB:
                def __init__(self):
                    self.connection = None
                def query(self, sql):
                    return pd.DataFrame()
                def execute(self, sql):
                    pass
                def close(self):
                    pass
            
            db = MockDB()
            print("[OK] Using mock database connector for testing")
        
        # Initialize calculator with database connector
        print("\nAttempting to initialize calculator with database connector...")
        calc = ComprehensiveQuoteCalculator(db_connector=db)
        print("[OK] Calculator initialized successfully")
        
        return calc
        
    except Exception as e:
        print(f"[FAIL] Could not initialize calculator: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_business_cards_direct(calc):
    """Test business cards calculator directly"""
    print("\n" + "="*80)
    print("BUSINESS CARDS - DIRECT TEST")
    print("="*80)
    
    if not calc:
        print("[SKIP] Calculator not initialized")
        return False
    
    test_params = {
        "quantity": 500,
        "stock_type": "satin_350gsm",
        "sides": 2,
        "print_type": "color",
        "finish_size": "standard",
        "celloglaze": "none",
        "artworks": 1
    }
    
    print(f"\nCalling calc.calculate_business_cards with:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    try:
        result = calc.calculate_business_cards(**test_params)
        
        print(f"\n[SUCCESS] Got result:")
        print(f"  Type: {type(result)}")
        print(f"  Product: {result.product_type if hasattr(result, 'product_type') else 'N/A'}")
        print(f"  Quantity: {result.quantity if hasattr(result, 'quantity') else 'N/A'}")
        print(f"  Cost Ex GST: ${result.total_cost_ex_gst if hasattr(result, 'total_cost_ex_gst') else 'N/A'}")
        print(f"  Cost Inc GST: ${result.total_cost_inc_gst if hasattr(result, 'total_cost_inc_gst') else 'N/A'}")
        
        if hasattr(result, 'breakdown'):
            print(f"\n  Breakdown:")
            for key, value in result.breakdown.items():
                print(f"    {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Error calling calculator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_perfect_bound_books_direct(calc):
    """Test perfect bound books calculator directly"""
    print("\n" + "="*80)
    print("PERFECT BOUND BOOKS - DIRECT TEST")
    print("="*80)
    
    if not calc:
        print("[SKIP] Calculator not initialized")
        return False
    
    # Find the correct method name
    print("\nLooking for perfect bound book methods...")
    methods = [m for m in dir(calc) if 'perfect' in m.lower() or 'bound' in m.lower()]
    print(f"Found methods: {methods}")
    
    # Try different potential method names
    method_names = [
        'calculate_perfect_bound_books',
        'calculate_perfect_bound',
        'calculate_perfectbound',
        'perfect_bound_books'
    ]
    
    for method_name in method_names:
        if hasattr(calc, method_name):
            print(f"\n[OK] Found method: {method_name}")
            
            # Get the method signature
            import inspect
            method = getattr(calc, method_name)
            sig = inspect.signature(method)
            print(f"  Signature: {sig}")
            
            # Try to call with minimal params
            try:
                print(f"\n  Attempting to call with minimal params...")
                result = method(quantity=100, pages=60, size="A5")
                print(f"  [SUCCESS] Method accepted minimal params")
                return True
            except TypeError as e:
                print(f"  [INFO] Needs more params: {e}")
                
                # Try with more params
                try:
                    result = method(
                        quantity=100,
                        pages=60,
                        cover_stock="250gsm",
                        inner_stock="100gsm",
                        size="A5"
                    )
                    print(f"  [SUCCESS] Method accepted full params")
                    print(f"    Result type: {type(result)}")
                    return True
                except Exception as e2:
                    print(f"  [FAIL] Still failed: {e2}")
    
    print("\n[FAIL] Could not find working perfect bound book method")
    return False


def test_all_calculator_methods(calc):
    """List all available calculator methods"""
    print("\n" + "="*80)
    print("AVAILABLE CALCULATOR METHODS")
    print("="*80)
    
    if not calc:
        print("[SKIP] Calculator not initialized")
        return
    
    # Get all methods that look like calculator methods
    methods = [m for m in dir(calc) if m.startswith('calculate_') and not m.startswith('_')]
    
    print(f"\nFound {len(methods)} calculator methods:\n")
    
    for i, method_name in enumerate(sorted(methods), 1):
        method = getattr(calc, method_name)
        
        # Get signature
        import inspect
        try:
            sig = inspect.signature(method)
            print(f"{i:2}. {method_name}")
            print(f"    Parameters: {sig}")
        except:
            print(f"{i:2}. {method_name}")
            print(f"    (Could not get signature)")
    
    print()


if __name__ == "__main__":
    try:
        # Initialize calculator
        calc = test_calculator_initialization()
        
        if calc:
            # List all methods
            test_all_calculator_methods(calc)
            
            # Test business cards
            bc_success = test_business_cards_direct(calc)
            
            # Test perfect bound books
            pbb_success = test_perfect_bound_books_direct(calc)
            
            # Summary
            print("\n" + "="*80)
            print("TEST SUMMARY")
            print("="*80)
            print(f"Business Cards: {'PASS' if bc_success else 'FAIL'}")
            print(f"Perfect Bound Books: {'PASS' if pbb_success else 'FAIL'}")
            print("="*80)
            
            sys.exit(0 if (bc_success or pbb_success) else 1)
        else:
            print("\n[FAIL] Could not initialize calculator")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
