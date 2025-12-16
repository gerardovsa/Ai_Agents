"""
Reset Supabase Connection Pool
Clears leaked connections and resets pool statistics

Use this when:
- Connection pool is exhausted
- Network connectivity was lost and recovered
- Database connections are stuck
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI_infrastructure.shared.database_utils import reset_connection_pool, log_pool_usage

def main():
    print("\n" + "="*70)
    print(" SUPABASE CONNECTION POOL RESET")
    print("="*70 + "\n")
    
    # Show current pool status
    print("BEFORE RESET:")
    log_pool_usage()
    
    # Reset all pools
    reset_connection_pool()
    
    print("\nAFTER RESET:")
    log_pool_usage()
    
    print("\n✅ Connection pool reset complete!")
    print("   All leaked connections cleared")
    print("   Pool statistics reset to zero")
    print("   New connections will be created on next database access\n")

if __name__ == "__main__":
    main()
