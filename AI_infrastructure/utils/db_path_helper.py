"""
Database Path Helper
Provides consistent database path resolution for local and Render environments

CRITICAL: 
- Local: Uses data/ai_infrastructure.db and data/sessions.db
- Render: Uses /data/ai_infrastructure.db and /data/sessions.db (persistent disk)
"""

import os
from pathlib import Path


def get_ai_infrastructure_db_path() -> str:
    """
    Get path to ai_infrastructure.db
    
    Returns:
        - /data/ai_infrastructure.db on Render (persistent disk)
        - <project_root>/data/ai_infrastructure.db locally
    """
    if os.getenv('RENDER') == 'true':
        return '/data/ai_infrastructure.db'
    else:
        # Calculate from this file: AI_infrastructure/utils/db_path_helper.py -> AI_agents/
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'ai_infrastructure.db')


def get_sessions_db_path() -> str:
    """
    Get path to sessions.db
    
    Returns:
        - /data/sessions.db on Render (persistent disk)
        - <project_root>/data/sessions.db locally
    """
    if os.getenv('RENDER') == 'true':
        return '/data/sessions.db'
    else:
        # Calculate from this file: AI_infrastructure/utils/db_path_helper.py -> AI_agents/
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'sessions.db')


def get_stock_db_path() -> str:
    """
    Get path to stock.db
    
    Returns:
        - /data/stock.db on Render (persistent disk)
        - <project_root>/data/stock.db locally
    """
    if os.getenv('RENDER') == 'true':
        return '/data/stock.db'
    else:
        # Calculate from this file: AI_infrastructure/utils/db_path_helper.py -> AI_agents/
        root_dir = Path(__file__).parent.parent.parent
        return str(root_dir / 'data' / 'stock.db')


def ensure_data_directory():
    """
    Ensure /data directory exists with proper permissions on Render
    
    On Render, /data is the persistent disk mount point.
    On local, uses <project_root>/data/
    """
    if os.getenv('RENDER') == 'true':
        data_dir = '/data'
        if not os.path.exists(data_dir):
            print(f"⚠️ Creating {data_dir} directory")
            os.makedirs(data_dir, mode=0o777, exist_ok=True)
        
        # Verify write permissions
        test_file = os.path.join(data_dir, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✓ {data_dir} is writable")
        except Exception as e:
            print(f"❌ ERROR: {data_dir} is NOT writable: {e}")
            raise
    else:
        # Local development - ensure data/ folder exists
        root_dir = Path(__file__).parent.parent.parent
        data_dir = root_dir / 'data'
        data_dir.mkdir(exist_ok=True)
