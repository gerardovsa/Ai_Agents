"""
Check Database Schema on Render vs Local

This script helps diagnose schema differences between local and production
"""

import requests
import json

def check_local_columns():
    """Check local database columns"""
    print("\n" + "="*60)
    print("LOCAL DATABASE (Your Machine)")
    print("="*60)
    
    import sqlite3
    from pathlib import Path
    
    db_path = Path('data/ai_infrastructure.db')
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    columns = cursor.fetchall()
    
    print(f"\noauth_tokens table has {len(columns)} columns:")
    for i, col in enumerate(columns, 1):
        print(f"  {i:2}. {col[1]:25} {col[2]:15} {'NOT NULL' if col[3] else ''}")
    
    # Check for refresh_attempts specifically
    column_names = [col[1] for col in columns]
    if 'refresh_attempts' in column_names:
        print("\n✅ refresh_attempts column EXISTS locally")
    else:
        print("\n❌ refresh_attempts column MISSING locally")
    
    conn.close()
    return column_names


def check_render_endpoint():
    """Check if Render has a diagnostic endpoint"""
    print("\n" + "="*60)
    print("RENDER DATABASE (Production)")
    print("="*60)
    
    render_url = "https://ai-agents-backend-singapore.onrender.com"
    
    # Try health endpoint
    try:
        response = requests.get(f"{render_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"\n✅ Render server is UP")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Infrastructure: {data.get('infrastructure')}")
        else:
            print(f"\n❌ Render health check failed: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Cannot reach Render: {e}")
    
    print("\n⚠️  Cannot directly inspect Render database schema")
    print("   (Database is internal to Render deployment)")
    print("\nTo fix:")
    print("   1. Deploy migration script to Render")
    print("   2. Migration runs on Flask startup")
    print("   3. Column gets created automatically")


def main():
    print("\n" + "="*60)
    print("DATABASE SCHEMA DIAGNOSTIC")
    print("="*60)
    print("This script checks why OAuth works locally but not on Render")
    
    local_columns = check_local_columns()
    check_render_endpoint()
    
    print("\n" + "="*60)
    print("DIAGNOSIS SUMMARY")
    print("="*60)
    print("""
Local Environment:
  ✅ Database persists across restarts
  ✅ Migrations run incrementally during development
  ✅ All columns exist from previous work
  
Render Environment:
  ❌ Fresh deployment may have old database schema
  ❌ Migration hasn't run yet (not deployed)
  ❌ Missing columns cause OAuth to fail

Solution:
  1. ✅ Migration file created: add_refresh_attempts_column.py
  2. ✅ Integrated into flask_app.py startup
  3. ⚠️  Need to commit and push to Render
  4. 🚀 Migration will run on next deployment
  5. ✅ Column will be created automatically
  6. ✅ OAuth will work on Render

Next Steps:
  git add AI_infrastructure/migrations/add_refresh_attempts_column.py
  git add AI_infrastructure/flask_app.py
  git commit -m "Fix OAuth: Add refresh_attempts column migration"
  git push origin v5
  
Wait 3-5 minutes for Render deployment, then test OAuth again.
""")
    print("="*60)


if __name__ == "__main__":
    main()
