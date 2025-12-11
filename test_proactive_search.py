"""
TEST SCRIPT: Proactive Semantic Tool Search
Tests the new pre-search feature in agent_routes_v4.py

Usage:
    python test_proactive_search.py

Expected Output:
    - Should find 8 relevant tools for email query
    - Should display similarity scores
    - Should format suggestions block correctly
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.registry_v3 import get_registry
from tools.intelligent_discovery import SemanticToolSearch


def test_proactive_search():
    """Test the proactive semantic tool search feature"""
    
    print("\n" + "="*80)
    print("🧪 TESTING PROACTIVE SEMANTIC TOOL SEARCH")
    print("="*80 + "\n")
    
    # Initialize registry
    print("📦 Loading tool registry...")
    registry = get_registry()
    print(f"✅ Loaded {len(registry.tools)} tools\n")
    
    # Initialize semantic search
    print("🔍 Initializing semantic search engine...")
    semantic_search = SemanticToolSearch(registry)
    
    if not semantic_search.available:
        print("❌ ERROR: Semantic search not available!")
        print("   Install: pip install sentence-transformers")
        return
    
    print(f"✅ Semantic search ready with {len(semantic_search.tool_embeddings)} embeddings\n")
    
    # Test queries
    test_queries = [
        "Send an email to john@example.com about the project",
        "Check my Gmail inbox for new messages",
        "Create a spreadsheet with sales data",
        "Post a message to the engineering Slack channel",
        "Schedule a meeting for next Tuesday at 2pm",
        "Get weather forecast for New York",
        "Search for Python tutorials on the web"
    ]
    
    for idx, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"📝 TEST {idx}: '{query}'")
        print(f"{'='*80}\n")
        
        # Pre-search tools
        suggested_tools = semantic_search.search(query, top_k=8)
        
        if suggested_tools:
            print(f"✨ Found {len(suggested_tools)} relevant tools:\n")
            
            for rank, tool_result in enumerate(suggested_tools, 1):
                tool_name = tool_result['tool_name']
                similarity = tool_result.get('similarity', 0.0)
                platform = tool_result.get('platform', 'Unknown')
                short_desc = tool_result.get('short_description', 'No description')[:80]
                
                # Add relevance emoji
                if similarity >= 0.7:
                    relevance = "🔥"
                elif similarity >= 0.5:
                    relevance = "✅"
                else:
                    relevance = "💡"
                
                print(f"  {rank}. {relevance} {tool_name} ({platform})")
                print(f"     {short_desc}")
                print(f"     Similarity: {similarity:.1%}\n")
        else:
            print("❌ No tools found (threshold 0.3+)\n")
    
    # Test the formatting (as seen by AI)
    print("\n" + "="*80)
    print("📋 FORMATTED OUTPUT (As Seen by AI Agent)")
    print("="*80 + "\n")
    
    test_message = "Send an email to john@example.com about the project update"
    suggested_tools = semantic_search.search(test_message, top_k=8)
    
    if suggested_tools:
        intelligent_tool_suggestions = "\n\n" + "="*80 + "\n"
        intelligent_tool_suggestions += "🎯 INTELLIGENT TOOL SUGGESTIONS (Pre-searched for this query)\n"
        intelligent_tool_suggestions += "="*80 + "\n\n"
        intelligent_tool_suggestions += "Based on semantic analysis of the user's message, these tools are most relevant:\n\n"
        
        for idx, tool_result in enumerate(suggested_tools, 1):
            tool_name = tool_result['tool_name']
            short_desc = tool_result.get('short_description', 'No description')
            similarity = tool_result.get('similarity', 0.0)
            platform = tool_result.get('platform', 'Unknown')
            
            if similarity >= 0.7:
                relevance = "🔥 Highly Relevant"
            elif similarity >= 0.5:
                relevance = "✅ Relevant"
            else:
                relevance = "💡 Potentially Useful"
            
            intelligent_tool_suggestions += f"{idx}. **{tool_name}** ({platform}) - {relevance}\n"
            intelligent_tool_suggestions += f"   {short_desc}\n"
            intelligent_tool_suggestions += f"   Similarity: {similarity:.2%}\n\n"
        
        intelligent_tool_suggestions += "**How to Use These Suggestions:**\n"
        intelligent_tool_suggestions += "- These tools were pre-selected based on the user's message\n"
        intelligent_tool_suggestions += "- You can use them immediately if relevant (call get_tool_schema → execute_tool)\n"
        intelligent_tool_suggestions += "- You still have autonomy: if these don't fit, use search_tools() manually\n"
        intelligent_tool_suggestions += "- This saves you 1-2 discovery rounds for faster responses\n"
        intelligent_tool_suggestions += "\n" + "="*80 + "\n"
        
        print(intelligent_tool_suggestions)
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_proactive_search()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
