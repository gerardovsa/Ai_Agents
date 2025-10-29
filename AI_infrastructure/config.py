"""
Configuration loader for new Flask app
Loads database config and initializes core components
"""

import json
import os
from pathlib import Path


class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent  # AI_infrastructure folder
    
    # Database config - use local path if G_Folder doesn't exist
    try:
        G_FOLDER = BASE_DIR.parent.parent / 'G_Folder'
        if not G_FOLDER.exists():
            # Fallback to AI_infrastructure/data
            DB_CONFIG_PATH = BASE_DIR / 'data' / 'database-config.json'
        else:
            DB_CONFIG_PATH = G_FOLDER / 'config' / 'database-config.json'
    except:
        # Final fallback
        DB_CONFIG_PATH = BASE_DIR / 'data' / 'database-config.json'
    
    # Session database
    SESSION_DB_PATH = BASE_DIR / 'data' / 'sessions.db'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True
    
    # CORS settings - Allow all local origins for development
    CORS_ORIGINS = [
        'http://localhost:4000',
        'http://localhost:5000', 
        'http://localhost:5001',
        'http://localhost:8501',
        'http://127.0.0.1:4000',
        'http://127.0.0.1:5000',
        'http://127.0.0.1:5001',
        'http://127.0.0.1:5550',
        'http://127.0.0.1:8501',
        'null',  # For file:// protocol
        '*'  # Allow all for development
    ]
    
    # Load database config
    @staticmethod
    def load_db_config():
        """Load database configuration from JSON"""
        with open(Config.DB_CONFIG_PATH, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_sql_connection_string():
        """Get SQL Server connection string"""
        db_config = Config.load_db_config()
        primary = db_config['DatabaseConnections']['Primary']
        return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={primary['Server']};DATABASE={primary['Database']};Trusted_Connection=yes;"
    
    @staticmethod
    def get_anthropic_api_key():
        """Get Anthropic API key"""
        db_config = Config.load_db_config()
        return db_config['AI']['AnthropicAPIKey']
    
    @staticmethod
    def get_deepseek_api_key():
        """Get DeepSeek API key (if configured)"""
        db_config = Config.load_db_config()
        return db_config['AI'].get('DeepSeekAPIKey', '')
    
    @staticmethod
    def get_openai_api_key():
        """Get OpenAI API key (if configured)"""
        db_config = Config.load_db_config()
        return db_config['AI'].get('OpenAIAPIKey', '')
