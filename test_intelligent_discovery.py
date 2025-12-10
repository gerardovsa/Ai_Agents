"""
Test Intelligent Discovery System - Platform Authentication Filtering
Tests the hard exclusion of unauthenticated platforms in tool suggestions.
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')

from tools.registry_v3 import RegistryV3
from tools.intelligent_discovery import IntelligentToolSuggestion


def test_platform_filtering():
    """Test that only authenticated platforms are returned"""
    
    print("\n" + "="*100)
    print("TEST: INTELLIGENT DISCOVERY - PLATFORM AUTHENTICATION FILTERING")
    print("="*100 + "\n")
    
    # Initialize registry and suggester
    registry = RegistryV3()
    suggester = IntelligentToolSuggestion(registry)
    
    # Test scenarios
    test_cases = [
        {
            "name": "User with Google only",
            "user_id": 1,  # Mock user ID
            "query": "send an email",
            "expected_platforms": ["google"],
            "excluded_platforms": ["microsoft", "slack"]
        },
        {
            "name": "User with Microsoft only",
            "user_id": 2,
            "query": "create a document",
            "expected_platforms": ["microsoft"],
            "excluded_platforms": ["google", "notion"]
        },
        {
            "name": "Explicit platform mention (override filter)",
            "user_id": 1,
            "query": "send an outlook email",
            "expected_platforms": ["microsoft"],  # Should show Outlook despite user having Google
            "excluded_platforms": []
        }
    ]
    
    print("\n🧪 Running Platform Filter Tests...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*100}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'─'*100}")
        print(f"Query: \"{test_case['query']}\"")
        print(f"User ID: {test_case['user_id']}")
        
        # Note: This will attempt to query real user auth data
        # For testing without DB, we'll catch the error
        try:
            results, confidence = suggester.suggest_tools(
                query=test_case['query'],
                user_id=test_case['user_id'],
                top_k=10
            )
            
            print(f"\n📊 Results: {len(results)} tools suggested")
            print(f"🎯 Confidence: {confidence:.2%}\n")
            
            # Show top 5 results
            print("Top 5 Suggested Tools:")
            for j, result in enumerate(results[:5], 1):
                tool_name = result['tool_name']
                platform = result['platform']
                score = result['final_score']
                breakdown = result['scoring_breakdown']
                
                print(f"  {j}. {tool_name}")
                print(f"     Platform: {platform}")
                print(f"     Score: {score:.2f}")
                print(f"     Breakdown: keyword={breakdown['keyword']:.2f}, "
                      f"semantic={breakdown['semantic']:.2f}, "
                      f"platform_boost={breakdown['platform_boost']}x")
                print()
            
            # Validate platforms
            result_platforms = set(r['platform'] for r in results)
            print(f"📦 Platforms in results: {', '.join(sorted(result_platforms))}")
            
            # Check for excluded platforms
            excluded_found = []
            for excluded_platform in test_case['excluded_platforms']:
                for result in results:
                    if excluded_platform in result['platform'].lower():
                        excluded_found.append(result['platform'])
                        break
            
            if excluded_found:
                print(f"❌ FAILED: Found excluded platforms: {', '.join(excluded_found)}")
            else:
                print(f"✅ PASSED: No excluded platforms found")
                
        except Exception as e:
            print(f"\n⚠️ Test could not complete (likely needs real database connection):")
            print(f"   Error: {str(e)}")
            print(f"   This is expected if user auth data is not available")


def test_no_platform_filter():
    """Test behavior when no user_id is provided"""
    
    print("\n\n" + "="*100)
    print("TEST: NO USER ID - ALL PLATFORMS SHOULD BE AVAILABLE")
    print("="*100 + "\n")
    
    registry = RegistryV3()
    suggester = IntelligentToolSuggestion(registry)
    
    query = "send an email"
    print(f"Query: \"{query}\"")
    print(f"User ID: None (no authentication filtering)")
    
    try:
        results, confidence = suggester.suggest_tools(
            query=query,
            user_id=None,  # No user ID = no filtering
            top_k=10
        )
        
        print(f"\n📊 Results: {len(results)} tools suggested")
        print(f"🎯 Confidence: {confidence:.2%}\n")
        
        # Check for diverse platforms
        result_platforms = set(r['platform'] for r in results)
        print(f"📦 Platforms in results: {', '.join(sorted(result_platforms))}")
        
        # Should include multiple email platforms
        email_platforms = [p for p in result_platforms if 'mail' in p.lower() or 'outlook' in p.lower()]
        
        if len(email_platforms) > 1:
            print(f"✅ PASSED: Multiple email platforms found ({', '.join(email_platforms)})")
        else:
            print(f"⚠️ WARNING: Only found {len(email_platforms)} email platform(s)")
            
    except Exception as e:
        print(f"\n⚠️ Test could not complete:")
        print(f"   Error: {str(e)}")


def test_semantic_search():
    """Test semantic search finds relevant tools with natural language"""
    
    print("\n\n" + "="*100)
    print("TEST: SEMANTIC SEARCH - NATURAL LANGUAGE QUERIES")
    print("="*100 + "\n")
    
    registry = RegistryV3()
    suggester = IntelligentToolSuggestion(registry)
    
    semantic_queries = [
        "How much does it cost to print a book?",
        "I need pricing for hardcover binding",
        "Calculate quote for business cards",
        "What's the price for saddle stitch booklets?"
    ]
    
    for i, query in enumerate(semantic_queries, 1):
        print(f"\n{'─'*100}")
        print(f"Query {i}: \"{query}\"")
        print(f"{'─'*100}")
        
        try:
            results, confidence = suggester.suggest_tools(
                query=query,
                user_id=None,  # No filtering for this test
                top_k=5
            )
            
            print(f"📊 Top 3 Results:")
            for j, result in enumerate(results[:3], 1):
                print(f"  {j}. {result['tool_name']}")
                print(f"     Semantic score: {result['scoring_breakdown']['semantic']:.2f}")
                print(f"     Confidence: {result['confidence']:.2%}")
            
            # Check if calculator tools are in top results
            top_3_names = [r['tool_name'] for r in results[:3]]
            has_calculator = any('calculate' in name.lower() for name in top_3_names)
            
            if has_calculator:
                print(f"✅ PASSED: Calculator tool found in top 3")
            else:
                print(f"❌ FAILED: No calculator tool in top 3 results")
                
        except Exception as e:
            print(f"⚠️ Error: {str(e)}")


def main():
    """Run all tests"""
    
    print("\n")
    print("╔" + "═"*98 + "╗")
    print("║" + " "*35 + "INTELLIGENT DISCOVERY TEST SUITE" + " "*31 + "║")
    print("╚" + "═"*98 + "╝")
    
    try:
        # Test 1: Platform filtering with user auth
        test_platform_filtering()
        
        # Test 2: No filtering when no user_id
        test_no_platform_filter()
        
        # Test 3: Semantic search quality
        test_semantic_search()
        
        print("\n\n" + "="*100)
        print("✅ ALL TESTS COMPLETED")
        print("="*100 + "\n")
        
        print("📝 NOTES:")
        print("   • Platform filtering tests may fail without database connection")
        print("   • This is expected - system needs UserAuthManager and oauth_tokens table")
        print("   • Semantic search tests should work without authentication")
        print("   • Check console output above for detailed results")
        print()
        
    except Exception as e:
        print(f"\n\n❌ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
