"""
Meta Tools - Tool Discovery and Inspection
Provides tools for AI agents to discover and understand available tools
"""
from tools.registry_v3 import tool_executor
from typing import Dict, List, Any, Optional


@tool_executor()
def list_platform_tools(platform: str) -> Dict[str, Any]:
    """
    List all tools available for a specific platform.
    
    Args:
        platform: Platform name (e.g., 'quote_calculator', 'xero', 'shopify')
        
    Returns:
        dict: List of tools with names and descriptions
    """
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Filter tools by platform
        platform_tools = [
            {
                "name": name,
                "description": tool_def.get("description", ""),
                "short_description": tool_def.get("short_description", "")
            }
            for name, tool_def in registry.tools.items()
            if tool_def.get("platform") == platform
        ]
        
        if not platform_tools:
            return {
                "success": False,
                "error": f"No tools found for platform '{platform}'",
                "suggestion": "Call list_available_platforms() to see available platforms"
            }
        
        return {
            "success": True,
            "platform": platform,
            "tool_count": len(platform_tools),
            "tools": platform_tools
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }


@tool_executor()
def search_tools(query: str) -> Dict[str, Any]:
    """
    Search for tools by keyword or description.
    
    Args:
        query: Search query
        
    Returns:
        dict: Matching tools with relevance scores
    """
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        query_lower = query.lower()
        
        # Search in tool names and descriptions
        matches = []
        for name, tool_def in registry.tools.items():
            score = 0
            
            # Exact name match
            if query_lower in name.lower():
                score += 10
            
            # Description match
            description = tool_def.get("description", "").lower()
            short_desc = tool_def.get("short_description", "").lower()
            
            if query_lower in description:
                score += 5
            if query_lower in short_desc:
                score += 5
            
            # Word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in name.lower():
                    score += 2
                if word in description:
                    score += 1
            
            if score > 0:
                matches.append({
                    "name": name,
                    "platform": tool_def.get("platform", "unknown"),
                    "description": tool_def.get("short_description") or tool_def.get("description", "")[:100],
                    "relevance_score": score
                })
        
        # Sort by relevance
        matches.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "success": True,
            "query": query,
            "match_count": len(matches),
            "matches": matches[:20]  # Top 20 results
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }


@tool_executor()
def get_tool_schema(tool_name: str) -> Dict[str, Any]:
    """
    Get detailed parameter schema for a specific tool.
    
    Args:
        tool_name: Exact name of the tool
        
    Returns:
        dict: Complete tool schema
    """
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        if tool_name not in registry.tools:
            # Find similar tools
            similar = [name for name in registry.tools.keys() 
                      if tool_name.lower() in name.lower()][:5]
            
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}",
                "suggestion": "Call list_available_platforms() then list_platform_tools(platform) to see available tools",
                "similar_tools": similar if similar else None
            }
        
        tool_def = registry.tools[tool_name]
        
        return {
            "success": True,
            "name": tool_name,
            "platform": tool_def.get("platform"),
            "description": tool_def.get("description"),
            "short_description": tool_def.get("short_description"),
            "parameters": tool_def.get("parameters", {}),
            "returns": tool_def.get("returns", {})
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }


@tool_executor()
def list_available_platforms() -> Dict[str, Any]:
    """
    List all available platforms/modules in the system.
    
    Returns:
        dict: List of platforms with tool counts
    """
    try:
        from tools.registry_v3 import RegistryV3
        
        registry = RegistryV3()
        
        # Group tools by platform
        platforms = {}
        for name, tool_def in registry.tools.items():
            platform = tool_def.get("platform", "unknown")
            if platform not in platforms:
                platforms[platform] = {
                    "platform": platform,
                    "tool_count": 0,
                    "tools": []
                }
            platforms[platform]["tool_count"] += 1
            platforms[platform]["tools"].append(name)
        
        # Convert to list and sort by tool count
        platform_list = sorted(
            platforms.values(),
            key=lambda x: x["tool_count"],
            reverse=True
        )
        
        return {
            "success": True,
            "platform_count": len(platform_list),
            "platforms": platform_list,
            "total_tools": len(registry.tools)
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "details": traceback.format_exc()
        }
