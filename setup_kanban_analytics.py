"""
Setup Kanban Analytics Database

This script initializes the SQLite database and performs the first sync.

Usage:
    python setup_kanban_analytics.py

Options:
    --force      Force re-initialization (drops existing database)
    --no-sync    Skip initial sync (just create schema)
"""

import sys
import logging
from pathlib import Path
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from AI_infrastructure.sync.kanban_db_sync import KanbanDatabaseSync

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description='Setup Kanban Analytics Database')
    parser.add_argument('--force', action='store_true', help='Force re-initialization')
    parser.add_argument('--no-sync', action='store_true', help='Skip initial sync')
    args = parser.parse_args()
    
    db_path = PROJECT_ROOT / 'data' / 'kanban_analytics.db'
    
    print("=" * 60)
    print("KANBAN ANALYTICS DATABASE SETUP")
    print("=" * 60)
    print(f"Database path: {db_path}")
    print()
    
    # Check if database exists
    if db_path.exists():
        if args.force:
            print(" WARNING: Forcing re-initialization (deleting existing database)")
            db_path.unlink()
        else:
            print(" Database already exists. Use --force to re-initialize.")
            return
    
    print(" Step 1: Creating database and schema...")
    
    try:
        with KanbanDatabaseSync(str(db_path)) as syncer:
            # Initialize schema
            syncer.initialize_schema()
            print(" Schema created successfully!")
            
            if not args.no_sync:
                print()
                print(" Step 2: Performing initial sync from SQL Server...")
                print("   This may take 30-60 seconds...")
                print()
                
                result = syncer.full_sync()
                
                print()
                print(" SYNC COMPLETED!")
                print(f"   Duration: {result['duration']:.2f}s")
                print(f"   Stages: {result['records_synced']['stages']}")
                print(f"   Clients: {result['records_synced']['clients']}")
                print(f"   Orders: {result['records_synced']['orders']}")
                print(f"   Jobs: {result['records_synced']['jobs']}")
            else:
                print()
                print(" Step 2: Skipped (--no-sync flag)")
        
        print()
        print("=" * 60)
        print(" SUCCESS! Kanban Analytics Database is ready!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Register the blueprint in flask_app.py:")
        print("   from routes.kanban_analytics_routes import kanban_analytics_bp")
        print("   app.register_blueprint(kanban_analytics_bp)")
        print()
        print("2. Test the API:")
        print("   curl http://localhost:5001/api/kanban-analytics/health")
        print()
        print("3. Schedule incremental syncs (e.g., daily cron job):")
        print("   python -c \"from AI_infrastructure.sync.kanban_db_sync import sync_from_sql_server; sync_from_sql_server()\"")
        print()
        
    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        print()
        print(" ERROR: Setup failed!")
        print(f"   {str(e)}")
        print()
        print("Common issues:")
        print("- SQL Server connection failed: Check network/credentials")
        print("- Schema file missing: Ensure kanban_analytics.sql exists in data/")
        print()
        sys.exit(1)


if __name__ == '__main__':
    main()
