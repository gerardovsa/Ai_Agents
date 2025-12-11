"""
Test semantic search accuracy after adding short_description to Google tools.
Measures if accuracy improved from baseline 75% to target 90%+.
"""

from tools.intelligent_discovery import IntelligentToolSuggestion, SemanticToolSearch
from tools.registry_v3 import RegistryV3

def test_semantic_search():
    """Test semantic search with various queries."""
    
    # Initialize
    print("\n" + "="*80)
    print("INITIALIZING INTELLIGENT TOOL DISCOVERY")
    print("="*80)
    
    registry = RegistryV3()  # Auto-loads schemas in __init__
    suggester = IntelligentToolSuggestion(registry)
    
    # Test queries covering different categories
    test_cases = [
        {
            "query": "How much does it cost to print a book?",
            "expected_category": "calculator",
            "expected_keywords": ["calculate", "spiral", "book", "pricing"]
        },
        {
            "query": "I need pricing for hardcover binding",
            "expected_category": "calculator",
            "expected_keywords": ["calculate", "hardcover", "binding", "quote"]
        },
        {
            "query": "Calculate quote for business cards",
            "expected_category": "calculator",
            "expected_keywords": ["calculate", "business", "cards"]
        },
        {
            "query": "What's the price for saddle stitch booklets?",
            "expected_category": "calculator",
            "expected_keywords": ["calculate", "saddle", "stitch"]
        },
        {
            "query": "Get my Gmail inbox messages",
            "expected_category": "google",
            "expected_keywords": ["gmail", "list", "inbox", "messages"]
        },
        {
            "query": "Create a Google Doc report",
            "expected_category": "google",
            "expected_keywords": ["google", "docs", "create", "document"]
        },
        {
            "query": "Debug my Apps Script code",
            "expected_category": "google",
            "expected_keywords": ["apps", "script", "debug", "analyze"]
        },
        {
            "query": "Deploy container to Cloud Run",
            "expected_category": "google",
            "expected_keywords": ["cloud", "run", "deploy", "container"]
        },
        {
            "query": "Check my Outlook calendar appointments",
            "expected_category": "microsoft",
            "expected_keywords": ["outlook", "calendar", "list", "events"]
        },
        {
            "query": "Query the print database",
            "expected_category": "database",
            "expected_keywords": ["sql", "query", "database", "execute"]
        }
    ]
    
    print(f"\nTesting {len(test_cases)} queries...\n")
    
    passed = 0
    failed = 0
    results_summary = []
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        expected_cat = test["expected_category"]
        expected_kw = test["expected_keywords"]
        
        print(f"\n{'='*80}")
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}: {query}")
        print(f"Expected: {expected_cat} tools with keywords {expected_kw}")
        print('='*80)
        
        # Get suggestions (returns tuple: results, overall_confidence)
        results, overall_confidence = suggester.suggest_tools(query, user_id=None, top_k=5)
        
        # Display results
        print(f"\nTop 5 Results (overall confidence: {overall_confidence:.3f}):")
        for j, tool in enumerate(results, 1):
            tool_name = tool["tool_name"]
            confidence = tool["confidence"]
            short_desc = tool.get("short_description", "")
            full_desc = tool.get("description", "")[:100]
            
            print(f"\n{j}. {tool_name} (confidence: {confidence:.3f})")
            if short_desc:
                print(f"   📝 Short: {short_desc}")
            print(f"   📄 Full:  {full_desc}...")
        
        # Evaluate if top result matches expected category
        top_result = results[0]["tool_name"].lower() if results else ""
        
        # Check if any expected keyword appears in top result
        match = any(kw in top_result for kw in expected_kw)
        
        if match:
            print(f"\n✅ PASS: Top result '{results[0]['tool_name']}' matches expected category")
            passed += 1
            results_summary.append(("PASS", query, results[0]["tool_name"], results[0]["confidence"]))
        else:
            print(f"\n❌ FAIL: Top result '{results[0]['tool_name'] if results else 'NONE'}' does not match expected category")
            failed += 1
            results_summary.append(("FAIL", query, results[0]["tool_name"] if results else "NONE", results[0]["confidence"] if results else 0))
    
    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    accuracy = (passed / len(test_cases)) * 100 if test_cases else 0
    
    print(f"\nTotal Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Accuracy: {accuracy:.1f}%")
    
    print("\n" + "-"*80)
    print("BASELINE vs CURRENT")
    print("-"*80)
    print("Baseline (before short_description): 75% (3/4 queries)")
    print(f"Current  (after short_description):  {accuracy:.1f}% ({passed}/{len(test_cases)} queries)")
    
    if accuracy >= 90:
        print("\n🎉 SUCCESS: Achieved 90%+ target accuracy!")
    elif accuracy > 75:
        print(f"\n📈 IMPROVEMENT: Accuracy improved from 75% to {accuracy:.1f}%")
    else:
        print(f"\n⚠️  WARNING: Accuracy at {accuracy:.1f}% - needs investigation")
    
    print("\n" + "-"*80)
    print("DETAILED RESULTS")
    print("-"*80)
    
    for status, query, tool, score in results_summary:
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {query[:40]:40} → {tool[:30]:30} ({score:.3f})")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_semantic_search()
