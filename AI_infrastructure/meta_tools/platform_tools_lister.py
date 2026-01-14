"""
Platform Tools Lister - List all tools available for a platform
Part of V4 Modular Architecture - Meta-Tools

Responsibilities:
- List all tools for a specific platform
- Return tool names and descriptions
- Filter by platform name
- Format for display
"""

from typing import Dict, Any, List, Optional
import sys
import logging
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from tools.registry_v3 import RegistryV3

logger = logging.getLogger(__name__)


class PlatformToolsLister:
    """
    Lists tools available for specific platforms.
    
    This is a meta-tool that helps AI discover what tools are available.
    
    Usage:
        lister = PlatformToolsLister()
        
        # List Google tools
        tools = lister.list_tools('google_workspace')
        for tool in tools:
            print(f"{tool['name']}: {tool['description']}")
    """

    def __init__(self):
        """Initialize platform tools lister with registry."""
        self.registry = RegistryV3()
        logger.info(f"PlatformToolsLister initialized: "
                   f"{len(self.registry.tools)} tools available")

    def list_tools(self, platform: str) -> List[Dict[str, str]]:
        """
        List all tools for a platform.
        
        Args:
            platform: Platform name (e.g., 'google_workspace', 'microsoft_365')
            
        Returns:
            List of tool dicts:
            [
                {
                    "name": "tool_name",
                    "description": "Tool description",
                    "platform": "platform_name"
                },
                ...
            ]
            
        Example:
            tools = lister.list_tools('google_workspace')
            print(f"Found {len(tools)} Google tools")
        """
        logger.debug(f"Listing tools for platform: {platform}")
        
        platform_lower = platform.lower()
        tools = []
        
        for tool_name, tool_schema in self.registry.tools.items():
            tool_platform = tool_schema.get('platform', '').lower()
            
            # Check if platform matches
            if platform_lower in tool_platform or tool_platform in platform_lower:
                tools.append({
                    'name': tool_schema.get('name', tool_name),
                    'short_description': tool_schema.get('short_description', tool_schema.get('description', 'No description')),
                    'platform': tool_schema.get('platform', 'unknown')
                })
        
        logger.info(f"Found {len(tools)} tools for {platform}")
        return tools

    def list_all_platforms(self) -> List[str]:
        """
        List all available platforms.
        
        Returns:
            List of unique platform names
            
        Example:
            platforms = lister.list_all_platforms()
            print(f"Available: {', '.join(platforms)}")
        """
        logger.debug("Listing all platforms")
        
        platforms = set()
        for tool_schema in self.registry.tools.values():
            platform = tool_schema.get('platform', 'unknown')
            platforms.add(platform)
        
        platforms_list = sorted(list(platforms))
        logger.info(f"Found {len(platforms_list)} platforms")
        
        return platforms_list

    def get_tool_count_by_platform(self) -> Dict[str, int]:
        """
        Get tool count for each platform.
        
        Returns:
            Dict mapping platform name to tool count
            
        Example:
            counts = lister.get_tool_count_by_platform()
            for platform, count in counts.items():
                print(f"{platform}: {count} tools")
        """
        logger.debug("Counting tools by platform")
        
        counts = {}
        for tool_schema in self.registry.tools.values():
            platform = tool_schema.get('platform', 'unknown')
            counts[platform] = counts.get(platform, 0) + 1
        
        logger.info(f"Counted tools across {len(counts)} platforms")
        return counts

    def format_tools_list(self, platform: str) -> str:
        """
        Format tools list as readable string.
        
        Args:
            platform: Platform name
            
        Returns:
            Formatted string with tool list
            
        Example:
            text = lister.format_tools_list('google_workspace')
            print(text)
        """
        logger.debug(f"Formatting tools list for {platform}")
        
        tools = self.list_tools(platform)
        
        if not tools:
            return f"No tools found for platform: {platform}"
        
        lines = [
            f"=== {platform.upper()} TOOLS ({len(tools)} available) ===",
            ""
        ]
        
        for i, tool in enumerate(tools, 1):
            lines.append(f"{i}. {tool['name']}")
            lines.append(f"   {tool['description']}")
            lines.append("")
        
        formatted = '\n'.join(lines)
        logger.info(f"Formatted {len(tools)} tools")
        
        return formatted


# Export
__all__ = ['PlatformToolsLister']
