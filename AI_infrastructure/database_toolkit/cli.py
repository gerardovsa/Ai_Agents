"""
Database Toolkit CLI
===================

Command-line interface for database management.

Usage:
    python -m AI_infrastructure.database_toolkit.cli <command> [options]

Commands:
    health          - Run full health check
    schema          - Schema operations
    users           - User management
    sessions        - Session management
    query           - Execute SQL queries

Examples:
    python -m AI_infrastructure.database_toolkit.cli health
    python -m AI_infrastructure.database_toolkit.cli schema --view
    python -m AI_infrastructure.database_toolkit.cli users --list
    python -m AI_infrastructure.database_toolkit.cli sessions --cleanup
    python -m AI_infrastructure.database_toolkit.cli query "SELECT * FROM users LIMIT 5"
"""

import sys
import argparse
from .schema_manager import SchemaManager
from .user_manager import UserManager
from .session_manager import SessionManager
from .query_tool import QueryTool
from .diagnostics import Diagnostics


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Database Toolkit CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Health check command
    health_parser = subparsers.add_parser('health', help='Run database health check')
    
    # Schema commands
    schema_parser = subparsers.add_parser('schema', help='Schema operations')
    schema_parser.add_argument('--view', action='store_true', help='View schema')
    schema_parser.add_argument('--create', action='store_true', help='Create all tables')
    schema_parser.add_argument('--check', action='store_true', help='Check for missing tables')
    schema_parser.add_argument('--export', type=str, help='Export schema to JSON file')
    
    # User commands
    user_parser = subparsers.add_parser('users', help='User management')
    user_parser.add_argument('--list', action='store_true', help='List all users')
    user_parser.add_argument('--create', type=str, help='Create user (username)')
    user_parser.add_argument('--email', type=str, help='User email (for --create)')
    user_parser.add_argument('--password', type=str, help='User password (for --create)')
    user_parser.add_argument('--role', type=str, default='user', help='User role (default: user)')
    user_parser.add_argument('--get', type=int, help='Get user by ID')
    user_parser.add_argument('--delete', type=int, help='Delete user by ID')
    
    # Session commands
    session_parser = subparsers.add_parser('sessions', help='Session management')
    session_parser.add_argument('--list', action='store_true', help='List active sessions')
    session_parser.add_argument('--stats', action='store_true', help='Show session statistics')
    session_parser.add_argument('--cleanup', action='store_true', help='Clean up expired sessions')
    session_parser.add_argument('--create', type=int, help='Create session for user ID')
    session_parser.add_argument('--validate', type=str, help='Validate session token')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Execute SQL query')
    query_parser.add_argument('sql', type=str, help='SQL query to execute')
    query_parser.add_argument('--export', type=str, help='Export results to CSV file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Health check
        if args.command == 'health':
            diag = Diagnostics()
            diag.run_full_health_check()
        
        # Schema operations
        elif args.command == 'schema':
            schema = SchemaManager()
            
            if args.view:
                schema.view_schema()
            elif args.create:
                print("Creating all tables...")
                schema.create_all_tables()
                print("Tables created successfully")
            elif args.check:
                missing = schema.check_missing_tables()
                if missing:
                    print(f"⚠️  Missing tables: {', '.join(missing)}")
                else:
                    print("All tables present")
            elif args.export:
                schema.export_schema(args.export)
                print(f"Schema exported to {args.export}")
            else:
                schema.print_schema_summary()
        
        # User operations
        elif args.command == 'users':
            users = UserManager()
            
            if args.list:
                all_users = users.list_users()
                users.print_user_list(all_users)
            elif args.create:
                if not args.email:
                    print(" Error: --email required for user creation")
                    return
                user_id = users.create_user(
                    args.create,
                    args.email,
                    role=args.role,
                    password=args.password
                )
                print(f"User created with ID: {user_id}")
            elif args.get:
                user = users.get_user(args.get)
                if user:
                    print(f"\nUser ID: {user['id']}")
                    print(f"Username: {user['username']}")
                    print(f"Email: {user['email']}")
                    print(f"Role: {user['role']}")
                    print(f"Created: {user['created_at']}")
                    print(f"Last Active: {user['last_active']}")
                else:
                    print(f" User {args.get} not found")
            elif args.delete:
                users.delete_user(args.delete)
                print(f"User {args.delete} deleted")
            else:
                print("Please specify an operation: --list, --create, --get, or --delete")
        
        # Session operations
        elif args.command == 'sessions':
            sessions = SessionManager()
            
            if args.list:
                active = sessions.get_active_sessions()
                print(f"\n📋 Active Sessions: {len(active)}")
                print("-" * 60)
                for session in active:
                    print(f"Token: {session['token'][:16]}...")
                    print(f"  User ID: {session['user_id']}")
                    print(f"  Created: {session['created_at']}")
                    print(f"  Expires: {session['expires_at']}")
                    print()
            elif args.stats:
                stats = sessions.get_session_stats()
                print("\n📊 Session Statistics")
                print("-" * 40)
                print(f"Total Sessions: {stats['total_sessions']}")
                print(f"Active Sessions: {stats['active_sessions']}")
                print(f"Expired Sessions: {stats['expired_sessions']}")
                print(f"Active Users: {stats['active_users']}")
            elif args.cleanup:
                deleted = sessions.cleanup_expired_sessions()
                print(f"Cleaned up {deleted} expired sessions")
            elif args.create:
                token = sessions.create_session(args.create)
                print(f"Session created: {token}")
            elif args.validate:
                valid, data = sessions.validate_session(args.validate)
                if valid:
                    print(f"Session valid for user {data['user_id']}")
                    print(f"   Expires: {data['expires_at']}")
                else:
                    print(" Session invalid or expired")
            else:
                print("Please specify an operation: --list, --stats, --cleanup, --create, or --validate")
        
        # Query execution
        elif args.command == 'query':
            tool = QueryTool()
            results = tool.execute_query(args.sql)
            
            if args.export:
                rows = tool.export_to_csv(args.sql, args.export)
                print(f"{rows} rows exported to {args.export}")
            else:
                print(f"\n📊 Query Results ({len(results)} rows)")
                print("-" * 60)
                print(tool.format_results(results))
    
    except Exception as e:
        print(f"\n Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
