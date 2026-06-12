"""
IMMEDIATE FIX - Connection Pool Exhausted

RUN THIS NOW to clear leaked connections and restore service:
"""

# Option 1: Quick reset in terminal
# cd AI_infrastructure
# python reset_connection_pool.py

# Option 2: In Python console
from AI_infrastructure.shared.database_utils import reset_connection_pool, log_pool_usage

# Show current status
print("\n🔍 CURRENT POOL STATUS:")
log_pool_usage()

# Reset all pools
print("\n🔧 RESETTING POOLS...")
reset_connection_pool()

print("\n✅ POOL RESET COMPLETE!")
print("   Restart your application to apply fixes")
print("   Leaked connections cleared")
print("   Next database access will create fresh pool\n")

# OR reset specific schema only
# reset_connection_pool('ai_infrastructure')
