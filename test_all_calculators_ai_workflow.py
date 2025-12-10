"""
COMPREHENSIVE AI WORKFLOW TEST - ALL 28 SHOPIFY CALCULATORS

This is the "FUCKING OVER THE TOP" testing system.
Tests EXACTLY how AI agents will use these calculators:
1. Discovery - Can AI find the tool via search?
2. Schema - Does it return complete parameter definitions?
3. Requirements - Are there enums for AI guidance?

This is END-TO-END validation, not just "does the backend work".
"""

import json
import sys
from pathlib import Path

# Add paths
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.implementations.meta_tools import search_tools, get_tool_schema

# All 28 Shopify calculator tool names (from schema)
SHOPIFY_CALCULATORS = [
    "calculate_bollard_signs",
    "calculate_construction_signs",
    "calculate_corflute_insert_a_frame",
    "calculate_custom_poster_printing",
    "calculate_custom_vinyl_stickers",
    "calculate_economical_business_cards_shopify",
    "calculate_election_signs",
    "calculate_folded_flyers_shopify",
    "calculate_luxury_classic_pull_up_banners",
    "calculate_metal_face_a_frame",
    "calculate_notepads_a4",
    "calculate_notepads_a5",
    "calculate_notepads_a6",
    "calculate_premium_bookmarks",
    "calculate_premium_business_cards_shopify",
    "calculate_printed_letterheads",
    "calculate_saddle_stitch_books",
    "calculate_selfie_frames",
    "calculate_spiral_bound_books",
    "calculate_spiral_bound_books_shopify",
    "calculate_stackable_cubes",
    "calculate_strut_cards_a3",
    "calculate_strut_cards_a4",
    "calculate_wire_bound_books_shopify",
    "calculate_with_compliments_slips",
]


def test_all_calculators():
    """Run comprehensive AI workflow tests on all calculators"""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE AI WORKFLOW TEST - ALL 28 SHOPIFY CALCULATORS")
    print("="*80)
    
    results = {
        "total": len(SHOPIFY_CALCULATORS),
        "discovery": {"passed": 0, "failed": 0, "missing": []},
        "schema": {"passed": 0, "failed": 0, "no_params": []},
        "requirements": {"passed": 0, "failed": 0, "no_enums": []},
        "details": []
    }
    
    # Phase 1: Discovery - Can AI find all tools?
    print("\n" + "="*80)
    print("PHASE 1: DISCOVERY - Testing search_tools()")
    print("="*80 + "\n")
    
    print("Testing if AI can discover calculators via multiple search terms...")
    
    # Test multiple search terms (like a real AI would)
    search_terms = [
        "calculator", "quote", "shopify", "business cards", "booklet", 
        "signs", "notepad", "flyers", "letterhead", "poster", "banner", 
        "sticker", "frame", "vinyl", "strut", "selfie"
    ]
    
    found_tools = set()
    for term in search_terms:
        search_response = search_tools(term)
        for tool in search_response.get("tools", []):
            if tool["name"] in SHOPIFY_CALCULATORS:
                found_tools.add(tool["name"])
    
    for calc in SHOPIFY_CALCULATORS:
        if calc in found_tools:
            results["discovery"]["passed"] += 1
        else:
            results["discovery"]["failed"] += 1
            results["discovery"]["missing"].append(calc)
    
    print(f"✅ Discovery: {results['discovery']['passed']}/{results['total']} found")
    if results["discovery"]["missing"]:
        print(f"❌ Missing from search: {len(results['discovery']['missing'])} calculators")
    
    # Phase 2 & 3: Schema and Requirements
    print("\n" + "="*80)
    print("PHASE 2 & 3: SCHEMA + REQUIREMENTS VALIDATION")
    print("="*80 + "\n")
    
    for calc_name in SHOPIFY_CALCULATORS:
        print(f"\nTesting: {calc_name}")
        
        calc_result = {
            "name": calc_name,
            "discoverable": calc_name in found_tools,
            "has_schema": False,
            "param_count": 0,
            "has_enums": False,
            "enum_coverage": 0,
            "status": "UNKNOWN"
        }
        
        try:
            # Get schema
            schema = get_tool_schema(calc_name)
            
            if not schema or not schema.get("success"):
                print(f"   ❌ FAIL: Schema retrieval failed")
                calc_result["status"] = "NO_SCHEMA"
                results["schema"]["failed"] += 1
                results["details"].append(calc_result)
                continue
            
            calc_result["has_schema"] = True
            
            # Check parameters
            input_schema = schema.get("input_schema", {})
            properties = input_schema.get("properties", {})
            param_count = len(properties)
            calc_result["param_count"] = param_count
            
            if param_count == 0:
                print(f"   ❌ FAIL: No parameters in schema")
                calc_result["status"] = "NO_PARAMS"
                results["schema"]["failed"] += 1
                results["schema"]["no_params"].append(calc_name)
            else:
                print(f"   ✅ Schema: {param_count} parameters")
                results["schema"]["passed"] += 1
            
            # Check enums/guidance
            params_with_enums = 0
            for param_name, param_def in properties.items():
                if isinstance(param_def, dict):
                    # Check for enum or "Valid options:" in description
                    if "enum" in param_def or "Valid options:" in param_def.get("description", ""):
                        params_with_enums += 1
            
            enum_coverage = (params_with_enums / param_count * 100) if param_count > 0 else 0
            calc_result["enum_coverage"] = enum_coverage
            
            if params_with_enums > 0:
                calc_result["has_enums"] = True
                print(f"   ✅ Enums: {params_with_enums}/{param_count} params ({enum_coverage:.0f}%)")
                results["requirements"]["passed"] += 1
                
                if param_count > 0:
                    calc_result["status"] = "READY"
            else:
                print(f"   ❌ FAIL: No enum guidance")
                results["requirements"]["failed"] += 1
                results["requirements"]["no_enums"].append(calc_name)
                calc_result["status"] = "NO_ENUMS"
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            calc_result["status"] = "ERROR"
            calc_result["error"] = str(e)
            results["schema"]["failed"] += 1
        
        results["details"].append(calc_result)
    
    # Final Report
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST REPORT")
    print("="*80 + "\n")
    
    print(f"[1] DISCOVERY:")
    print(f"    ✅ Found: {results['discovery']['passed']}/{results['total']}")
    print(f"    ❌ Missing: {results['discovery']['failed']}/{results['total']}")
    
    print(f"\n[2] SCHEMA VALIDATION:")
    print(f"    ✅ Valid schemas: {results['schema']['passed']}/{results['total']}")
    print(f"    ❌ No parameters: {len(results['schema']['no_params'])}")
    
    print(f"\n[3] REQUIREMENTS GUIDANCE:")
    print(f"    ✅ Has enums: {results['requirements']['passed']}/{results['total']}")
    print(f"    ❌ No enums: {len(results['requirements']['no_enums'])}")
    
    # Calculate AI-ready count
    ai_ready = [r for r in results["details"] if r["status"] == "READY"]
    ai_ready_count = len(ai_ready)
    
    print(f"\n" + "="*80)
    print(f"AI-READY CALCULATORS: {ai_ready_count}/{results['total']} ({ai_ready_count/results['total']*100:.1f}%)")
    print("="*80 + "\n")
    
    if ai_ready_count == results['total']:
        print("🎉 SUCCESS: ALL CALCULATORS ARE AI-READY!")
        success = True
    else:
        print("⚠️  WARNING: SOME CALCULATORS NEED FIXES")
        
        # Show what needs fixing
        not_ready = [r for r in results["details"] if r["status"] != "READY"]
        
        print(f"\nNEED FIXING ({len(not_ready)} calculators):\n")
        
        for calc in not_ready:
            print(f"   • {calc['name']}")
            print(f"     Status: {calc['status']}")
            if calc['status'] == "NO_PARAMS":
                print(f"     Issue: Schema has 0 parameters")
            elif calc['status'] == "NO_ENUMS":
                print(f"     Issue: {calc['param_count']} params but no enum guidance")
            elif calc['status'] == "NO_SCHEMA":
                print(f"     Issue: Schema retrieval failed")
            print()
        
        success = False
    
    # Save detailed results
    output_file = root_dir / "test_results_all_calculators_ai_workflow.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Detailed results saved to: {output_file}\n")
    
    return success


if __name__ == "__main__":
    success = test_all_calculators()
    sys.exit(0 if success else 1)
