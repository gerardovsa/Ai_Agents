"""
Test All Shopify Calculators - Verify Config Manager Fix
=========================================================

This script tests that all 28 Shopify calculators can:
1. Import successfully
2. Initialize without errors
3. Load their config files via config_manager

Date: December 10, 2025
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from config_manager import config_manager

# List of all Shopify calculator classes
CALCULATOR_MODULES = [
    ("BollardSigns_Shopify_Calculator", "BollardSignsShopifyCalculator"),
    ("CustomPosterPrinting_Shopify_Calculator", "CustomPosterPrintingShopifyCalculator"),
    ("CustomVinylStickers_Shopify_Calculator", "CustomVinylStickersShopifyCalculator"),
    ("CorfluteInsertA_Frame_Shopify_Calculator", "CorfluteInsertAFrameShopifyCalculator"),
    ("CorfluteInsertA-Frame_Shopify_Calculator", "CorfluteInsertAFrameShopifyCalculator"),
    ("LuxuryClassicPullUpBanners_Shopify_Calculator", "LuxuryClassicPullUpBannersShopifyCalculator"),
    ("FoldedFlyers_Shopify_Calculator", "FoldedFlyersShopifyCalculator"),
    ("ElectionSigns_Shopify_Calculator", "ElectionSignsShopifyCalculator"),
    ("EconomicalBusinessCards_Shopify_Calculator", "EconomicalBusinessCardsShopifyCalculator"),
    ("ConstructionSigns_Shopify_Calculator", "ConstructionSignsShopifyCalculator"),
    ("NotepadsA6_Shopify_Calculator", "NotepadsA6ShopifyCalculator"),
    ("NotepadsA5_Shopify_Calculator", "NotepadsA5ShopifyCalculator"),
    ("NotepadsA4_Shopify_Calculator", "NotepadsA4ShopifyCalculator"),
    ("SpiralBoundBooks_Shopify_Calculator", "SpiralBoundBooksShopifyCalculator"),
    ("SelfieFrames_Shopify_Calculator", "SelfieFramesShopifyCalculator"),
    ("SaddleStitchBooks_Shopify_Calculator", "SaddleStitchBooksShopifyCalculator"),
    ("PrintedLetterheads_Shopify_Calculator", "PrintedLetterheadsShopifyCalculator"),
    ("PremiumBookmarks_Shopify_Calculator", "PremiumBookmarksShopifyCalculator"),
    ("StrutCardsA4_Shopify_Calculator", "StrutCardsA4ShopifyCalculator"),
    ("StrutCardsA3_Shopify_Calculator", "StrutCardsA3ShopifyCalculator"),
    ("WireBound_Shopify_Calculator", "WireBoundShopifyCalculator"),
    ("StackableCubes_Shopify_Calculator", "StackableCubesShopifyCalculator"),
    ("SpiralBound_Shopify_Calculator", "SpiralBoundShopifyCalculator"),
    ("MetalFaceA_Frame_Shopify_Calculator", "MetalFaceAFrameShopifyCalculator"),
    ("MetalFaceA-Frame_Shopify_Calculator", "MetalFaceAFrameShopifyCalculator"),
    ("WithComplimentsSlips_Shopify_Calculator", "WithComplimentsSlipsShopifyCalculator"),
]

def test_calculator(module_name: str, class_name: str) -> dict:
    """
    Test a single calculator
    
    Returns:
        {
            "success": bool,
            "has_config": bool,
            "error": str or None
        }
    """
    result = {
        "success": False,
        "has_config": False,
        "error": None
    }
    
    try:
        # Import module
        module = __import__(f"inhouse_modules.shopify_calculators.{module_name}", fromlist=[class_name])
        
        # Get calculator class
        calc_class = getattr(module, class_name)
        
        # Initialize calculator (should use config_manager)
        calculator = calc_class()
        
        # Check if config loaded
        if calculator.config:
            result["has_config"] = True
            result["success"] = True
        else:
            result["error"] = "Config is None (file not found)"
        
    except Exception as e:
        result["error"] = str(e)
    
    return result


def main():
    """Test all calculators"""
    
    print("\n" + "="*80)
    print("🧪 TESTING ALL 28 SHOPIFY CALCULATORS")
    print("="*80 + "\n")
    
    successes = 0
    failures = 0
    
    for module_name, class_name in CALCULATOR_MODULES:
        result = test_calculator(module_name, class_name)
        
        if result["success"]:
            print(f"✅ {class_name:50} - Config loaded")
            successes += 1
        else:
            print(f"❌ {class_name:50} - {result['error']}")
            failures += 1
    
    print("\n" + "="*80)
    print(f"📊 RESULTS: {successes}/28 calculators working ({(successes/28)*100:.1f}%)")
    print("="*80 + "\n")
    
    if successes == 28:
        print("🎉 SUCCESS! All calculators are working with config_manager!")
        print("\n✅ What this means:")
        print("   • All 28 Shopify calculators can find their config files")
        print("   • Config manager searches 3 paths automatically")
        print("   • No more hardcoded In_House_SQL paths")
        print("   • Calculators work in AI_agents repository")
        return 0
    else:
        print(f"⚠️  WARNING: {failures} calculator(s) failed")
        print("   Check config files exist in:")
        print("   • c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify/")
        return 1


if __name__ == "__main__":
    exit(main())
