"""
Config Manager - Shopify calculators configuration loader
==========================================================

Loads Shopify calculator configuration files from G_Folder.
Some calculators (like Saddle Stitch) need config, others have hardcoded pricing.
"""

import json
from pathlib import Path


class ConfigManager:
    """Config manager for Shopify calculators"""
    
    # Config file locations to search
    CONFIG_PATHS = [
        Path(__file__).parent.parent.parent / "config" / "shopify",  # AI_agents/UI/modules_external/quote-calculator/config/shopify
        r"c:\Users\gpoli\GIT\AI_Agents_V11\AI_agents\UI\modules_external\quote-calculator\config\shopify"
    ]
    
    def __init__(self):
        """Initialize config manager"""
        self.config = {}
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value"""
        self.config[key] = value
    
    def load_shopify_config(self, config_file):
        """
        Load Shopify config file from G_Folder
        
        Args:
            config_file: Filename (e.g., "Shopify_Saddle_Stitch_Books.json")
            
        Returns:
            Dict with config data, or empty dict if file not found
        """
        # Try each config path
        for base_path in self.CONFIG_PATHS:
            try:
                config_path = Path(base_path) / config_file
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception as e:
                continue
        
        # File not found in any location - return empty dict
        # (Most calculators have hardcoded pricing and don't need config)
        return {}


# Global singleton instance
config_manager = ConfigManager()
