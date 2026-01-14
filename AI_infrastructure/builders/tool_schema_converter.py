"""
Tool Schema Converter - Convert ToolRegistry schemas to Anthropic format
Part of V4 Modular Architecture

Responsibilities:
- Convert tool schemas from registry format to Anthropic API format
- Filter tools by platform
- Add input_schema validation
- Format tool descriptions
"""

from typing import Dict, Any, List, Optional
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

tools_dir = ai_infra_dir.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.utils.logger import get_logger

logger = get_logger(__name__)


class ToolSchemaConverter:
    """
    Converts tool schemas to Anthropic API format.
    
    Features:
    - Convert registry schemas to Anthropic format
    - Filter tools by platform
    - Add input_schema with proper types
    - Format descriptions for clarity
    
    Usage:
        converter = ToolSchemaConverter()
        
        # Convert all tools
        anthropic_tools = converter.convert_tools(registry_tools)
        
        # Filter by platform
        google_tools = converter.filter_by_platform(
            registry_tools, 
            platform='google_workspace'
        )
    """

    def __init__(self):
        """Initialize tool schema converter."""
        logger.info("🔄 ToolSchemaConverter initialized")

    def convert_tool(self, tool_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert single tool schema to Anthropic format.
        
        Args:
            tool_schema: Tool schema from registry
            
        Returns:
            Anthropic-formatted tool schema:
            {
                "name": str,
                "description": str,
                "input_schema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
            
        Example:
            registry_tool = registry.get_tool('send_gmail')
            anthropic_tool = converter.convert_tool(registry_tool)
        """
        logger.debug(f"🔄 Converting tool: {tool_schema.get('name', 'unknown')}")
        
        # Extract basic info
        name = tool_schema.get('name')
        description = tool_schema.get('description', '')
        
        # Get parameters
        parameters = tool_schema.get('parameters', {})
        properties = parameters.get('properties', {})
        required = parameters.get('required', [])
        
        # Build input_schema
        input_schema = {
            'type': 'object',
            'properties': properties,
            'required': required
        }
        
        # Build Anthropic format
        anthropic_tool = {
            'name': name,
            'description': description,
            'input_schema': input_schema
        }
        
        logger.debug(f"Converted: {name} ({len(properties)} params, "
                    f"{len(required)} required)")
        
        return anthropic_tool

    def convert_tools(self, tool_schemas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert multiple tool schemas.
        
        Args:
            tool_schemas: List of tool schemas from registry
            
        Returns:
            List of Anthropic-formatted tool schemas
            
        Example:
            registry_tools = registry.get_all_tools()
            anthropic_tools = converter.convert_tools(registry_tools)
            print(f"Converted {len(anthropic_tools)} tools")
        """
        logger.debug(f"🔄 Converting {len(tool_schemas)} tools")
        
        anthropic_tools = []
        
        for schema in tool_schemas:
            try:
                converted = self.convert_tool(schema)
                anthropic_tools.append(converted)
            except Exception as e:
                tool_name = schema.get('name', 'unknown')
                logger.error(f" Error converting {tool_name}: {e}")
                continue
        
        logger.info(f"Converted {len(anthropic_tools)}/{len(tool_schemas)} tools")
        
        return anthropic_tools

    def filter_by_platform(self, 
                          tool_schemas: List[Dict[str, Any]], 
                          platform: str) -> List[Dict[str, Any]]:
        """
        Filter tools by platform.
        
        Args:
            tool_schemas: List of tool schemas
            platform: Platform name (e.g., 'google_workspace', 'microsoft_365')
            
        Returns:
            Filtered list of tool schemas
            
        Example:
            google_tools = converter.filter_by_platform(
                all_tools, 
                platform='google_workspace'
            )
            print(f"Found {len(google_tools)} Google tools")
        """
        logger.debug(f"🔍 Filtering tools for platform: {platform}")
        
        # Normalize platform name
        platform_lower = platform.lower()
        
        filtered = []
        for schema in tool_schemas:
            tool_platform = schema.get('platform', '').lower()
            
            # Check if platform matches
            if platform_lower in tool_platform or tool_platform in platform_lower:
                filtered.append(schema)
        
        logger.info(f"Filtered to {len(filtered)} tools for {platform}")
        
        return filtered

    def filter_by_platforms(self,
                           tool_schemas: List[Dict[str, Any]],
                           platforms: List[str]) -> List[Dict[str, Any]]:
        """
        Filter tools by multiple platforms.
        
        Args:
            tool_schemas: List of tool schemas
            platforms: List of platform names
            
        Returns:
            Filtered list of tool schemas
            
        Example:
            tools = converter.filter_by_platforms(
                all_tools,
                platforms=['google_workspace', 'calculator']
            )
        """
        logger.debug(f"🔍 Filtering tools for {len(platforms)} platforms")
        
        # Normalize platform names
        platforms_lower = [p.lower() for p in platforms]
        
        filtered = []
        for schema in tool_schemas:
            tool_platform = schema.get('platform', '').lower()
            
            # Check if tool platform matches any requested platform
            for platform in platforms_lower:
                if platform in tool_platform or tool_platform in platform:
                    filtered.append(schema)
                    break
        
        logger.info(f"Filtered to {len(filtered)} tools for {len(platforms)} platforms")
        
        return filtered

    def get_tool_summary(self, tool_schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for tools.
        
        Args:
            tool_schemas: List of tool schemas
            
        Returns:
            Summary dict:
            {
                "total_tools": int,
                "platforms": {...},  # Count per platform
                "total_params": int,
                "avg_params_per_tool": float
            }
            
        Example:
            summary = converter.get_tool_summary(all_tools)
            print(f"Total: {summary['total_tools']} tools")
        """
        logger.debug(f"📊 Generating summary for {len(tool_schemas)} tools")
        
        # Count platforms
        platform_counts = {}
        total_params = 0
        
        for schema in tool_schemas:
            platform = schema.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Count parameters
            params = schema.get('parameters', {}).get('properties', {})
            total_params += len(params)
        
        avg_params = total_params / len(tool_schemas) if tool_schemas else 0
        
        summary = {
            'total_tools': len(tool_schemas),
            'platforms': platform_counts,
            'total_params': total_params,
            'avg_params_per_tool': round(avg_params, 1)
        }
        
        logger.info(f"Summary: {summary['total_tools']} tools across "
                   f"{len(platform_counts)} platforms")
        
        return summary

    def convert_and_filter(self,
                          tool_schemas: List[Dict[str, Any]],
                          platforms: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Convert and optionally filter tools in one operation.
        
        Args:
            tool_schemas: List of tool schemas from registry
            platforms: Optional list of platforms to filter by
            
        Returns:
            List of Anthropic-formatted, filtered tool schemas
            
        Example:
            anthropic_tools = converter.convert_and_filter(
                registry_tools,
                platforms=['google_workspace', 'calculator']
            )
        """
        logger.debug(f"🔄 Convert and filter: {len(tool_schemas)} tools")
        
        # Filter first if platforms specified
        if platforms:
            tool_schemas = self.filter_by_platforms(tool_schemas, platforms)
            logger.debug(f"🔍 Filtered to {len(tool_schemas)} tools")
        
        # Convert to Anthropic format
        anthropic_tools = self.convert_tools(tool_schemas)
        
        logger.info(f"Final result: {len(anthropic_tools)} Anthropic-formatted tools")
        
        return anthropic_tools


# Export
__all__ = ['ToolSchemaConverter']
