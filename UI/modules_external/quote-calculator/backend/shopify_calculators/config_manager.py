"""
Config Manager - Dummy module for Shopify calculators compatibility
=====================================================================

This module is imported by Shopify calculators but not actually used.
It's a legacy import from the original Shopify WooCommerce implementation.

The calculators have all pricing hardcoded and don't need configuration.
"""


class ConfigManager:
    """Dummy config manager for compatibility"""
    
    def __init__(self):
        """Initialize empty config manager"""
        self.config = {}
    
    def get(self, key, default=None):
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set config value"""
        self.config[key] = value
    
    def load_shopify_config(self, config_file):
        """
        Load Shopify config file (dummy implementation)
        
        Returns empty dict - calculators have all pricing hardcoded.
        This method exists for compatibility with calculator __init__ calls.
        """
        return {}


# Global singleton instance
config_manager = ConfigManager()
