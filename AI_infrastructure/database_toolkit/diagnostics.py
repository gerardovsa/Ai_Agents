"""
Database Diagnostics
===================

Health checks and troubleshooting tools.
"""

import os
import psycopg2
from typing import Dict, List
from datetime import datetime, timedelta


class Diagnostics:
    """Database diagnostic tools"""
    
    def __init__(self, db_path: str = "ai_infrastructure.db"):
        """Initialize diagnostics"""
        self.db_path = db_path
    
    def get_connection(self) -> psycopg2.connection:
        """Get database connection"""
        return psycopg2.connect(self.db_path)
    
    def check_database_exists(self) -> Dict:
        """Check if database file exists"""
        exists = os.path.exists(self.db_path)
        size = os.path.getsize(self.db_path) if exists else 0
        
        return {
            "exists": exists,
            "path": self.db_path,
            "size_bytes": size,
            "size_mb": round(size / (1024 * 1024), 2)
        }
    
    def check_tables(self) -> Dict:
        """Check which tables exist"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Expected tables
                expected = [
                    "users", "user_sessions", "user_platform_credentials",
                    "user_gmail_accounts", "user_email_aliases", "workspaces",
                    "user_account_links", "account_link_requests", "kanban_task_links"
                ]
                
                # Get actual tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='ai_infrastructure'
                    ORDER BY table_name
                """)
                actual = [row[0] if isinstance(row, tuple) else row for row in cursor.fetchall()]
                
                return {
                    "expected_count": len(expected),
                    "actual_count": len(actual),
                    "missing": [t for t in expected if t not in actual],
                    "extra": [t for t in actual if t not in expected],
                    "all_present": set(expected) == set(actual)
                }
    
    def check_table_counts(self) -> Dict:
        """Get row counts for all tables"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Get all tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='ai_infrastructure'
                """)
                tables = [row[0] if isinstance(row, tuple) else row for row in cursor.fetchall()]
        
        counts = {}
        with self.get_connection() as conn:
            for table in tables:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
        
        return counts
    
    def check_foreign_keys(self) -> List[Dict]:
        """Validate foreign key constraints"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                # Get all tables
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='ai_infrastructure'
                """)
                tables = [row[0] if isinstance(row, tuple) else row for row in cursor.fetchall()]
        
        violations = []
        with self.get_connection() as conn:
            for table in tables:
                with conn.cursor() as cursor:
                    try:
                        cursor.execute("""
                            SELECT constraint_name, table_name 
                            FROM information_schema.table_constraints 
                            WHERE constraint_type='FOREIGN KEY' 
                            AND table_name=%s
                        """, (table,))
                        issues = cursor.fetchall()
                        if issues:
                            violations.append({
                                "table": table,
                                "violations": issues
                            })
                    except Exception as e:
                        violations.append({
                            "table": table,
                            "error": str(e)
                        })
        
        return violations
    
    def check_indexes(self) -> Dict:
        """Check database indexes"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT 
                        indexname AS name,
                        tablename AS tbl_name,
                        indexdef AS sql
                    FROM pg_indexes
                    WHERE schemaname = 'ai_infrastructure'
                    AND indexname NOT LIKE 'pg_%'
                    ORDER BY tablename, indexname
                """)
                indexes = cursor.fetchall()
                
                return {
                    "total_indexes": len(indexes),
                    "indexes": [
                        {"name": idx[0], "table": idx[1], "sql": idx[2]}
                        for idx in indexes
                    ]
                }
    
    def check_recent_activity(self) -> Dict:
        """Check recent database activity"""
        activity = {}
        
        with self.get_connection() as conn:
            # Recent users
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM users 
                        WHERE created_at > NOW() - INTERVAL '7 days'
                    """)
                    activity["users_created_7d"] = cursor.fetchone()[0]
            except:
                activity["users_created_7d"] = None
            
            # Active sessions
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM user_sessions 
                        WHERE expires_at > NOW()
                    """)
                    activity["active_sessions"] = cursor.fetchone()[0]
            except:
                activity["active_sessions"] = None
            
            # Recent session activity
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT COUNT(*) FROM user_sessions 
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                    """)
                    activity["sessions_24h"] = cursor.fetchone()[0]
            except:
                activity["sessions_24h"] = None
        
        return activity
    
    def run_full_health_check(self) -> Dict:
        """Run complete health check"""
        print("🔍 Running Database Health Check...")
        print("-" * 50)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "database": self.check_database_exists(),
            "tables": self.check_tables(),
            "row_counts": self.check_table_counts(),
            "foreign_keys": self.check_foreign_keys(),
            "indexes": self.check_indexes(),
            "activity": self.check_recent_activity()
        }
        
        # Print summary
        print("\n📊 Database File:")
        print(f"  Exists: {results['database']['exists']}")
        print(f"  Size: {results['database']['size_mb']} MB")
        
        print("\n📋 Tables:")
        print(f"  Expected: {results['tables']['expected_count']}")
        print(f"  Actual: {results['tables']['actual_count']}")
        print(f"  All Present: {results['tables']['all_present']}")
        if results['tables']['missing']:
            print(f"  ⚠️  Missing: {', '.join(results['tables']['missing'])}")
        
        print("\n📈 Row Counts:")
        for table, count in sorted(results['row_counts'].items()):
            print(f"  {table}: {count}")
        
        print("\n🔗 Foreign Keys:")
        if results['foreign_keys']:
            print(f"  ⚠️  {len(results['foreign_keys'])} violations found!")
        else:
            print("  All constraints valid")
        
        print("\n📇 Indexes:")
        print(f"  Total: {results['indexes']['total_indexes']}")
        
        print("\n⚡ Recent Activity:")
        for key, value in results['activity'].items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 50)
        print("Health Check Complete")
        
        return results


if __name__ == "__main__":
    # Run health check
    diag = Diagnostics()
    diag.run_full_health_check()