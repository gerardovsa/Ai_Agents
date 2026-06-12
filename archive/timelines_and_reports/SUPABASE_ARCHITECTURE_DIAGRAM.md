# 🏗️ Supabase Connection Architecture - Visual Guide

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI INFRASTRUCTURE APPLICATION                     │
│                          (Flask/Python Backend)                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ├─── Route Layer
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│ synergy_      │          │ account_      │          │ kanban_       │
│ routes.py     │          │ linking_      │          │ analytics_    │
│               │          │ routes.py     │          │ routes.py     │
│ get_db_       │          │               │          │               │
│ connection()  │          │ get_db_       │          │ get_db_       │
│     │         │          │ connection()  │          │ connection()  │
│     │         │          │     │         │          │     │         │
└─────┼─────────┘          └─────┼─────────┘          └─────┼─────────┘
      │                          │                          │
      └──────────────────────────┼──────────────────────────┘
                                 │
                                 ▼
        ┌─────────────────────────────────────────────────┐
        │   shared/database_utils.py (Connection Layer)   │
        └─────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ get_ai_          │   │ get_sessions_    │   │ get_synergy_     │
│ infrastructure_  │   │ connection()     │   │ sessions_        │
│ connection()     │   │                  │   │ connection()     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                                 ▼
        ┌─────────────────────────────────────────────────┐
        │   get_database_connection(schema_name)          │
        │   - Create/get connection pool for schema       │
        │   - Get connection from pool (max 5s timeout)   │
        │   - Set search_path TO {schema}, public         │
        │   - Configure RealDictCursor                    │
        │   - Set statement_timeout = 60s                 │
        └─────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Connection Pool  │   │ Connection Pool  │   │ Connection Pool  │
│ ai_infrastructure│   │ sessions         │   │ synergy_sessions │
│                  │   │                  │   │                  │
│ minconn: 4       │   │ minconn: 4       │   │ minconn: 4       │
│ maxconn: 12      │   │ maxconn: 12      │   │ maxconn: 12      │
│                  │   │                  │   │                  │
│ [🔵🔵🔵🔵○○○○]   │   │ [🔵🔵🔵🔵○○○○]   │   │ [🔵🔵🔵🔵○○○○]   │
│  4 ready         │   │  4 ready         │   │  4 ready         │
│  8 available     │   │  8 available     │   │  8 available     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     SUPABASE POSTGRESQL SERVER                           │
│                   aws-1-ap-southeast-2.pooler.supabase.com               │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Transaction Mode │   │ Session Mode     │   │ Direct Connection│
│ Port: 6543       │   │ Port: 5432       │   │ Port: 5432       │
│                  │   │                  │   │                  │
│ ✅ ACTIVE        │   │ ⏸️  FALLBACK     │   │ ❌ NOT USED      │
│ Max clients: 200 │   │ Max clients: 60  │   │ Max clients: 60  │
│ Short-lived      │   │ Persistent       │   │ Single session   │
└──────────────────┘   └──────────────────┘   └──────────────────┘
        │
        └─────────────────────────────────────────────────┐
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                SUPABASE POSTGRESQL DATABASE (Nano Tier)                  │
│                        ryoicrdifiqhqpsnjmdo                              │
│                     Max Connections: 60 total                            │
└─────────────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ SCHEMA:          │   │ SCHEMA:          │   │ SCHEMA:          │
│ ai_infrastructure│   │ sessions         │   │ synergy_sessions │
│                  │   │                  │   │                  │
│ 📋 20 Tables:    │   │ 📋 13 Tables:    │   │ 📋 9 Tables:     │
│ - users          │   │ - api_sessions   │   │ - milestones     │
│ - oauth_tokens   │   │ - messages       │   │ - tasks          │
│ - credentials    │   │ - saved_threads  │   │ - subtasks       │
│ - sessions       │   │ - threads        │   │ - synergy_config │
│ - preferences    │   │ - workspaces     │   │ - comments       │
│ - audit_log      │   │ - state          │   │ - history        │
│ - team_mgmt      │   │ - context        │   │ - sessions       │
│ ...              │   │ ...              │   │ ...              │
└──────────────────┘   └──────────────────┘   └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CONNECTION LIFECYCLE                             │
└─────────────────────────────────────────────────────────────────────────┘

1️⃣  Application Request
    └─> Route calls get_db_connection()

2️⃣  Schema-Specific Function
    └─> get_ai_infrastructure_connection() 
        get_sessions_connection()
        get_synergy_sessions_connection()

3️⃣  Connection Pool Lookup
    └─> Check if pool exists for schema
        ├─ EXISTS: Reuse pool (FAST - 10ms)
        └─ NEW: Create pool (SLOW - 1200ms first time)

4️⃣  Get Connection from Pool
    └─> pool.getconn() with 5s timeout
        ├─ SUCCESS: Return connection
        └─ TIMEOUT: Detect leaked connections, raise error

5️⃣  Configure Connection
    └─> CREATE SCHEMA IF NOT EXISTS {schema}
        SET search_path TO {schema}, public
        SET statement_timeout = '60s'
        Apply RealDictCursor

6️⃣  Application Uses Connection
    └─> cursor.execute("SELECT * FROM users")
        # Resolves to {schema}.users via search_path
        
7️⃣  Return to Pool
    └─> conn.close() → pool.putconn()
        # Connection stays alive, returned to pool
        # Next request reuses same connection (FAST)

┌─────────────────────────────────────────────────────────────────────────┐
│                          QUERY RESOLUTION                                │
└─────────────────────────────────────────────────────────────────────────┘

🔍 Search Path: ai_infrastructure, public

Query: SELECT * FROM users

Resolution Steps:
1. Check ai_infrastructure.users → ✅ FOUND (use this)
2. Check public.users → (not checked)

Result: Executes against ai_infrastructure.users


🔍 Search Path: sessions, public

Query: SELECT * FROM users

Resolution Steps:
1. Check sessions.users → ✅ FOUND (use this)
2. Check public.users → (not checked)

Result: Executes against sessions.users


🔍 Search Path: synergy_sessions, public

Query: SELECT * FROM milestones

Resolution Steps:
1. Check synergy_sessions.milestones → ✅ FOUND (use this)
2. Check public.milestones → (not checked)

Result: Executes against synergy_sessions.milestones

┌─────────────────────────────────────────────────────────────────────────┐
│                       REALDICTCURSOR BEHAVIOR                            │
└─────────────────────────────────────────────────────────────────────────┘

Without RealDictCursor (Standard psycopg2):
cursor.execute("SELECT id, email FROM users WHERE id = 1")
row = cursor.fetchone()
# row = (1, 'user@example.com')  ← TUPLE
# row[0] = 1
# row[1] = 'user@example.com'
# row['email'] ← ERROR: tuples don't support string keys


With RealDictCursor (AI_infrastructure):
cursor.execute("SELECT id, email FROM users WHERE id = 1")
row = cursor.fetchone()
# row = RealDictRow(id=1, email='user@example.com')  ← DICT-LIKE
# row['id'] = 1         ✅ Works
# row['email'] = 'user@example.com'  ✅ Works
# row.get('email') = 'user@example.com'  ✅ Works
# dict(row) = {'id': 1, 'email': '...'}  ✅ Works

┌─────────────────────────────────────────────────────────────────────────┐
│                     CONNECTION POOL STATISTICS                           │
└─────────────────────────────────────────────────────────────────────────┘

Schema: ai_infrastructure
  Active: 0          (currently in use)
  Available: 4       (ready in pool)
  Max: 12           (burst capacity)
  Status: ✅ HEALTHY

Schema: sessions
  Active: 0
  Available: 4
  Max: 12
  Status: ✅ HEALTHY

Schema: synergy_sessions
  Active: 0
  Available: 4
  Max: 12
  Status: ✅ HEALTHY

Global:
  Total pools: 3
  Connections acquired: 3
  Connections returned: 3
  Leaked: 0          ✅ HEALTHY
  Avg wait: 1344ms   (initial pool creation only)

┌─────────────────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT VARIABLES                             │
└─────────────────────────────────────────────────────────────────────────┘

Required:
✅ SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
✅ SUPABASE_ANON_KEY=eyJhbGciOi...
✅ SUPABASE_DB_URL_POOLER=postgresql://postgres.ryoicrdifiqhqpsnjmdo:***@
   aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres

Optional:
✅ SUPABASE_DB_URL_SESSION=postgresql://...5432/postgres
✅ SUPABASE_SERVICE_KEY=eyJhbGciOi...
✅ SUPABASE_ACCESS_TOKEN=sbp_...

Configuration:
✅ USE_SUPABASE=true

┌─────────────────────────────────────────────────────────────────────────┐
│                            BEST PRACTICES                                │
└─────────────────────────────────────────────────────────────────────────┘

✅ DO: Use context managers
    with get_database_connection('sessions') as conn:
        cursor = conn.cursor()
        cursor.execute("...")
        # Auto-closes on exit

✅ DO: Always close connections
    conn = get_database_connection('sessions')
    try:
        # Use connection
    finally:
        conn.close()  # Returns to pool

✅ DO: Access rows as dicts
    user = cursor.fetchone()
    email = user['email']  # Dict-like access

❌ DON'T: Forget to close
    conn = get_database_connection('sessions')
    cursor.execute("...")
    # MISSING: conn.close() ← LEAK!

❌ DON'T: Use schema prefixes
    # BAD:
    cursor.execute("SELECT * FROM synergy_sessions.milestones")
    
    # GOOD:
    cursor.execute("SELECT * FROM milestones")
    # search_path resolves to synergy_sessions.milestones

❌ DON'T: Mix schemas in one connection
    # BAD:
    conn = get_ai_infrastructure_connection()
    cursor.execute("SELECT * FROM sessions.threads")  # Wrong schema!
    
    # GOOD:
    conn = get_sessions_connection()
    cursor.execute("SELECT * FROM threads")  # Correct

┌─────────────────────────────────────────────────────────────────────────┐
│                         VERIFICATION STATUS                              │
└─────────────────────────────────────────────────────────────────────────┘

Environment:       ✅ PASS
ai_infrastructure: ✅ PASS (20 tables)
sessions:          ✅ PASS (13 tables)
synergy_sessions:  ✅ PASS (9 tables)
Connection Pools:  ✅ PASS (0 leaks)
RealDictCursor:    ✅ PASS (dict-like rows)
Search Path:       ✅ PASS (schema isolation)

Overall: ✅ ALL SYSTEMS OPERATIONAL

Run Verification: python verify_supabase_connections.py
Documentation: SUPABASE_CONNECTION_VERIFICATION_DEC14.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      🎉 PRODUCTION READY 🎉
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
