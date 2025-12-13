#!/usr/bin/env python3
"""
System Smoke Test - Verify all critical components
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test critical package imports"""
    print("\n=== Testing Python Package Imports ===")
    
    packages = [
        ('psycopg2', 'PostgreSQL driver'),
        ('sqlalchemy', 'SQL toolkit'),
        ('flask', 'Web framework'),
        ('anthropic', 'AI SDK'),
    ]
    
    for package, desc in packages:
        try:
            __import__(package)
            print(f"✅ {package:20s} - {desc}")
        except ImportError as e:
            print(f"❌ {package:20s} - FAILED: {e}")

def test_infrastructure():
    """Test AI Infrastructure modules"""
    print("\n=== Testing AI Infrastructure ===")
    
    try:
        from AI_infrastructure.database_toolkit.session_manager import SessionManager
        sm = SessionManager()
        print(f"✅ SessionManager        - Initialized")
    except Exception as e:
        print(f"❌ SessionManager        - FAILED: {e}")
    
    try:
        from AI_infrastructure.config.logging_config import get_logger
        logger = get_logger(__name__)
        print(f"✅ Logging Config        - Available")
    except Exception as e:
        print(f"❌ Logging Config        - FAILED: {e}")

def test_database_connection():
    """Test database connectivity"""
    print("\n=== Testing Database Connection ===")
    
    try:
        from AI_infrastructure.database_toolkit.session_manager import SessionManager
        sm = SessionManager()
        conn = sm.get_connection()
        cursor = conn.cursor()
        
        # Test query on SQLite
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
        tables = cursor.fetchall()
        
        print(f"✅ Database connected    - SQLite")
        print(f"   Tables found: {len(tables)}")
        for table in tables[:3]:
            print(f"   - {table[0]}")
        
        cursor.close()
    except Exception as e:
        print(f"❌ Database connection   - FAILED: {e}")

def test_file_structure():
    """Test critical file existence"""
    print("\n=== Testing File Structure ===")
    
    files = [
        'UI/business-ai-platform-v2.html',
        'UI/modules_internal/internal_docs/card-renderer.js',
        'UI/modules_internal/internal_docs/card-renderer.css',
        'UI/modules_internal/synergy/synergy-doc-picker.js',
        'UI/modules_internal/internal-docs/internal-docs-link-modal.js',
        'AI_infrastructure/flask_app.py',
    ]
    
    for file_path in files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path:60s} ({size:,} bytes)")
        else:
            print(f"❌ {file_path:60s} - NOT FOUND")

def test_js_syntax():
    """Test JavaScript files are readable"""
    print("\n=== Testing JavaScript Files ===")
    
    js_files = [
        'UI/modules_internal/internal_docs/card-renderer.js',
        'UI/modules_internal/synergy/synergy-doc-picker.js',
        'UI/modules_internal/internal-docs/internal-docs-link-modal.js',
        'UI/modules_internal/workflow/workflow-link-modal.js',
    ]
    
    for js_file in js_files:
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                print(f"✅ {os.path.basename(js_file):40s} ({lines:4d} lines)")
        except Exception as e:
            print(f"❌ {os.path.basename(js_file):40s} - FAILED: {e}")

if __name__ == '__main__':
    print("=" * 80)
    print("🧪 SYSTEM SMOKE TEST")
    print("=" * 80)
    
    test_imports()
    test_infrastructure()
    test_database_connection()
    test_file_structure()
    test_js_syntax()
    
    print("\n" + "=" * 80)
    print("✅ SMOKE TEST COMPLETE")
    print("=" * 80)
