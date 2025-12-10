"""
Unified Configuration Manager for Quote Calculators
Handles config loading from multiple possible locations
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional


class CalculatorConfigManager:
    """
    Central config loader for all quote calculators
    Searches multiple paths to handle both AI_agents and In_House_SQL repos
    """
    
    def __init__(self):
        """Initialize config manager with search paths"""
        self.base_dir = Path(__file__).parent
        
        # Search paths in priority order
        self.shopify_config_paths = [
            # 1. Local configs (AI_agents/config/shopify/)
            self.base_dir / "shopify",
            
            # 2. Relative to In_House_SQL (if repositories are siblings)
            self.base_dir.parent.parent / "In_House_SQL" / "G_Folder" / "Quote_Calculator" / "shopify",
            
            # 3. Absolute path fallback
            Path("c:/Users/gpoli/GIT/In_House_SQL/G_Folder/Quote_Calculator/shopify"),
        ]
        
        self.database_config_paths = [
            # 1. Local config (AI_agents/config/)
            self.base_dir / "database-config.json",
            
            # 2. In_House_SQL config
            self.base_dir.parent.parent / "In_House_SQL" / "config" / "database-config.json",
            
            # 3. Absolute path fallback
            Path("c:/Users/gpoli/GIT/In_House_SQL/config/database-config.json"),
        ]
    
    def load_shopify_config(self, filename: str) -> Dict[str, Any]:
        """
        Load Shopify calculator config JSON file
        
        Args:
            filename: Config filename (e.g., "Shopify_Saddle_Stitch_Books.json")
        
        Returns:
            Config dictionary
        
        Raises:
            FileNotFoundError: If config not found in any search path
        """
        for path in self.shopify_config_paths:
            config_file = path / filename
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    print(f"✅ Loaded config from: {config_file}")
                    return config
                except Exception as e:
                    print(f"⚠️  Failed to load {config_file}: {e}")
                    continue
        
        # Config not found
        searched = "\n  - ".join(str(p) for p in self.shopify_config_paths)
        raise FileNotFoundError(
            f"Config file '{filename}' not found.\n"
            f"Searched paths:\n  - {searched}"
        )
    
    def load_database_config(self) -> Dict[str, Any]:
        """
        Load database configuration
        
        Returns:
            Database config dictionary with server, database, credentials
        
        Raises:
            FileNotFoundError: If database config not found
        """
        for path in self.database_config_paths:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    print(f"✅ Loaded database config from: {path}")
                    return config
                except Exception as e:
                    print(f"⚠️  Failed to load {path}: {e}")
                    continue
        
        # Database config not found
        searched = "\n  - ".join(str(p) for p in self.database_config_paths)
        raise FileNotFoundError(
            f"Database config not found.\n"
            f"Searched paths:\n  - {searched}"
        )
    
    def config_exists(self, filename: str) -> bool:
        """Check if a config file exists"""
        for path in self.shopify_config_paths:
            if (path / filename).exists():
                return True
        return False
    
    def get_available_configs(self) -> list:
        """Get list of all available Shopify config files"""
        configs = set()
        for path in self.shopify_config_paths:
            if path.exists():
                for config_file in path.glob("*.json"):
                    configs.add(config_file.name)
        return sorted(configs)


# Singleton instance - import this in calculators
config_manager = CalculatorConfigManager()


# Helper function for backward compatibility
def load_shopify_config(filename: str) -> Dict[str, Any]:
    """Load Shopify config (backward compatible function)"""
    return config_manager.load_shopify_config(filename)


def load_database_config() -> Dict[str, Any]:
    """Load database config (backward compatible function)"""
    return config_manager.load_database_config()


if __name__ == "__main__":
    # Test config manager
    print("🔍 Testing Config Manager\n")
    
    print("📁 Available Shopify configs:")
    configs = config_manager.get_available_configs()
    for config in configs:
        print(f"  - {config}")
    
    print("\n🗄️  Testing database config:")
    try:
        db_config = config_manager.load_database_config()
        print(f"✅ Database: {db_config.get('database', 'N/A')}")
        print(f"✅ Server: {db_config.get('server', 'N/A')}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
    
    print("\n📊 Testing Shopify config:")
    try:
        saddle_config = config_manager.load_shopify_config("Shopify_Saddle_Stitch_Books.json")
        print(f"✅ Loaded Saddle Stitch Books config")
        print(f"   Keys: {list(saddle_config.keys())}")
    except FileNotFoundError as e:
        print(f"❌ {e}")
