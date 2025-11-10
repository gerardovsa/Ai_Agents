"""
Show all applied migrations from Supabase

Usage:
    python Supabase/show_migrations.py
"""
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env.master')

def show_migrations():
    """Show all applied migrations"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("❌ SUPABASE_DB_URL not found in .env.master")
        return
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check if migration_history table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'migration_history'
            );
        """)
        
        if not cursor.fetchone()[0]:
            print("ℹ️  No migration history found")
            print("   Migration system not initialized yet")
            print("   Apply your first migration to create history table")
            return
        
        # Get all migrations
        cursor.execute("""
            SELECT 
                migration_number,
                description,
                filename,
                author,
                applied_at,
                applied_by,
                status,
                error_message
            FROM public.migration_history
            ORDER BY migration_number;
        """)
        
        migrations = cursor.fetchall()
        
        if not migrations:
            print("ℹ️  No migrations applied yet")
            return
        
        print("=" * 100)
        print("APPLIED MIGRATIONS")
        print("=" * 100)
        print()
        
        for i, row in enumerate(migrations, 1):
            num, desc, filename, author, applied_at, applied_by, status, error = row
            
            status_icon = "✅" if status == 'success' else "❌"
            
            print(f"{i}. {status_icon} Migration {num:03d}: {desc}")
            print(f"   File: {filename}")
            print(f"   Author: {author}")
            print(f"   Applied: {applied_at}")
            print(f"   By: {applied_by}")
            print(f"   Status: {status}")
            if error:
                print(f"   Error: {error}")
            print()
        
        print("=" * 100)
        print(f"Total migrations: {len(migrations)}")
        success_count = sum(1 for m in migrations if m[6] == 'success')
        failed_count = len(migrations) - success_count
        print(f"✅ Successful: {success_count}")
        if failed_count > 0:
            print(f"❌ Failed: {failed_count}")
        print("=" * 100)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    show_migrations()
