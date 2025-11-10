"""
Apply SQL migration to Supabase database

Usage:
    python Supabase/apply_migration.py migrations/005_my_feature.sql
    
Features:
- Reads migration SQL file
- Applies to Supabase PostgreSQL
- Records in migration_history table
- Updates migration_log.md
- Transaction-based (all-or-nothing)
"""
import sys
import os
import re
from pathlib import Path
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env.master')

def get_db_connection():
    """Get PostgreSQL connection to Supabase"""
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        raise ValueError("SUPABASE_DB_URL not found in .env.master")
    
    return psycopg2.connect(db_url)


def parse_migration_file(filepath):
    """Parse migration file and extract metadata"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract migration number from filename
    filename = Path(filepath).name
    match = re.match(r'(\d+)_(.+)\.sql', filename)
    if not match:
        raise ValueError(f"Invalid migration filename: {filename}. Expected: 001_description.sql")
    
    migration_number = int(match.group(1))
    description = match.group(2).replace('_', ' ').title()
    
    # Extract metadata from comments
    author = "Unknown"
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Look for Author and Date in comments
    author_match = re.search(r'--\s*Author:\s*(.+)', content)
    if author_match:
        author = author_match.group(1).strip()
    
    date_match = re.search(r'--\s*Date:\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        date = date_match.group(1)
    
    # Extract UP section (between BEGIN and COMMIT after "UP MIGRATION")
    up_match = re.search(
        r'-- UP MIGRATION.*?BEGIN;(.*?)COMMIT;',
        content,
        re.DOTALL | re.IGNORECASE
    )
    if not up_match:
        raise ValueError("No UP MIGRATION section found in migration file")
    
    up_sql = up_match.group(1).strip()
    
    # Extract DOWN section (between BEGIN and COMMIT after "DOWN MIGRATION")
    down_match = re.search(
        r'-- DOWN MIGRATION.*?BEGIN;(.*?)COMMIT;',
        content,
        re.DOTALL | re.IGNORECASE
    )
    down_sql = down_match.group(1).strip() if down_match else None
    
    return {
        'number': migration_number,
        'description': description,
        'author': author,
        'date': date,
        'filename': filename,
        'up_sql': up_sql,
        'down_sql': down_sql,
        'full_content': content
    }


def ensure_migration_history_table(conn):
    """Create migration_history table if it doesn't exist"""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.migration_history (
                id SERIAL PRIMARY KEY,
                migration_number INTEGER UNIQUE NOT NULL,
                description TEXT NOT NULL,
                filename TEXT NOT NULL,
                author TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_by TEXT DEFAULT CURRENT_USER,
                status TEXT DEFAULT 'success',
                error_message TEXT,
                sql_content TEXT
            );
        """)
        conn.commit()


def check_if_applied(conn, migration_number):
    """Check if migration was already applied"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT migration_number, applied_at, status
            FROM public.migration_history
            WHERE migration_number = %s
        """, (migration_number,))
        return cursor.fetchone()


def apply_migration(filepath):
    """Apply migration to Supabase database"""
    print("=" * 80)
    print("SUPABASE MIGRATION APPLICATION")
    print("=" * 80)
    
    # Parse migration file
    print(f"\n📄 Reading migration file: {filepath}")
    try:
        migration = parse_migration_file(filepath)
    except Exception as e:
        print(f"❌ Error parsing migration file: {e}")
        return False
    
    print(f"\n📋 Migration Details:")
    print(f"   Number: {migration['number']}")
    print(f"   Description: {migration['description']}")
    print(f"   Author: {migration['author']}")
    print(f"   Date: {migration['date']}")
    print(f"   Filename: {migration['filename']}")
    
    # Connect to database
    print(f"\n🔌 Connecting to Supabase...")
    try:
        conn = get_db_connection()
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    try:
        # Ensure migration history table exists
        ensure_migration_history_table(conn)
        
        # Check if already applied
        existing = check_if_applied(conn, migration['number'])
        if existing:
            print(f"\n⚠️  Migration {migration['number']} already applied!")
            print(f"    Applied at: {existing[1]}")
            print(f"    Status: {existing[2]}")
            
            response = input("\n    Apply again anyway? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Migration cancelled")
                return False
        
        # Show SQL preview
        print(f"\n📝 Migration SQL (first 500 chars):")
        print("─" * 80)
        print(migration['up_sql'][:500])
        if len(migration['up_sql']) > 500:
            print(f"... ({len(migration['up_sql']) - 500} more characters)")
        print("─" * 80)
        
        # Confirm
        response = input("\n⚠️  Apply this migration to Supabase? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Migration cancelled")
            return False
        
        # Apply migration
        print(f"\n⚡ Applying migration...")
        with conn.cursor() as cursor:
            try:
                # Execute migration SQL
                cursor.execute(migration['up_sql'])
                
                # Record in migration history
                cursor.execute("""
                    INSERT INTO public.migration_history 
                    (migration_number, description, filename, author, status, sql_content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (migration_number) 
                    DO UPDATE SET 
                        applied_at = CURRENT_TIMESTAMP,
                        applied_by = CURRENT_USER,
                        status = 'success';
                """, (
                    migration['number'],
                    migration['description'],
                    migration['filename'],
                    migration['author'],
                    'success',
                    migration['full_content']
                ))
                
                conn.commit()
                print("✅ Migration applied successfully!")
                
                # Update migration log
                update_migration_log(migration)
                
                return True
                
            except Exception as e:
                conn.rollback()
                print(f"❌ Migration failed: {e}")
                
                # Record failure
                cursor.execute("""
                    INSERT INTO public.migration_history 
                    (migration_number, description, filename, author, status, error_message)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (migration_number) 
                    DO UPDATE SET 
                        applied_at = CURRENT_TIMESTAMP,
                        status = 'failed',
                        error_message = EXCLUDED.error_message;
                """, (
                    migration['number'],
                    migration['description'],
                    migration['filename'],
                    migration['author'],
                    'failed',
                    str(e)
                ))
                conn.commit()
                
                return False
    
    finally:
        conn.close()
        print("\n🔌 Connection closed")


def update_migration_log(migration):
    """Update migration_log.md file"""
    log_file = Path(__file__).parent / 'migrations' / 'migration_log.md'
    
    # Create log entry
    entry = f"""
## Migration {migration['number']:03d} - {migration['description']}

**Date:** {migration['date']}  
**Author:** {migration['author']}  
**Filename:** {migration['filename']}  
**Status:** ✅ Applied  
**Applied at:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

**Changes:**
- Applied migration {migration['number']:03d}

---

"""
    
    # Append to log file
    try:
        if log_file.exists():
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry)
        else:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# Migration Log\n\n")
                f.write(entry)
        
        print(f"✅ Updated {log_file}")
    except Exception as e:
        print(f"⚠️  Could not update migration log: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python Supabase/apply_migration.py migrations/XXX_name.sql")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    
    # Resolve path
    if not os.path.isabs(migration_file):
        migration_file = os.path.join(os.getcwd(), migration_file)
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    # Apply migration
    success = apply_migration(migration_file)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Verify with: python Supabase/supabase_toolkit.py summary")
        print("2. Test your application")
        print("3. Commit migration file to Git:")
        print(f"   git add {migration_file}")
        print(f"   git commit -m 'Add: Migration {Path(migration_file).name}'")
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ MIGRATION FAILED")
        print("=" * 80)
        sys.exit(1)


if __name__ == '__main__':
    main()
