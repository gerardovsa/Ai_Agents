"""
Run ML Analytics Schema Migration
Applies the 008_ml_analytics_schema.sql migration to Supabase PostgreSQL
"""

import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
ai_infra_path = str(Path(__file__).parent)
if ai_infra_path not in sys.path:
    sys.path.insert(0, ai_infra_path)

from shared.database_utils import execute_query

def run_ml_schema_migration():
    """Run the ML analytics schema migration"""
    print("🚀 Running ML Analytics Schema Migration...")
    print("=" * 80)
    
    # Read migration file
    migration_file = Path(__file__).parent / "migrations" / "008_ml_analytics_schema.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    print(f"📄 Reading migration file: {migration_file}")
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    print(f"📊 Migration size: {len(migration_sql)} characters")
    print("=" * 80)
    
    try:
        # Execute migration
        print("⚙️ Executing migration...")
        execute_query(migration_sql)
        
        print("=" * 80)
        print("✅ ML Analytics schema migration completed successfully!")
        print()
        print("Tables created:")
        print("  ✓ ml_models (model storage)")
        print("  ✓ ml_predictions (prediction cache)")
        print("  ✓ customer_intelligence_cache (customer metrics)")
        print("  ✓ anomaly_detections (fraud/error log)")
        print("  ✓ xero_contacts_cache (Xero contact metrics)")
        print("  ✓ xero_invoices_cache (Xero invoice data)")
        print("  ✓ xero_payments_cache (Xero payment data)")
        print("=" * 80)
        
        return True
    
    except Exception as e:
        print("=" * 80)
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_ml_schema_migration()
    sys.exit(0 if success else 1)
