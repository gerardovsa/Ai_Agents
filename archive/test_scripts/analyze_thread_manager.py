"""Analyze thread_manager.py structure"""

with open('AI_infrastructure/thread_manager.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

print("=" * 80)
print("THREAD_MANAGER.PY ANALYSIS")
print("=" * 80)
print(f"\nTotal lines: {len(lines)}")
print(f"File size: {len(content)} bytes ({len(content) / 1024:.1f} KB)")

# Find class definitions
classes = [line for line in lines if line.strip().startswith('class ')]
print(f"\nClasses ({len(classes)}):")
for cls in classes:
    print(f"  - {cls.strip()}")

# Find method definitions
methods = [line for line in lines if 'def ' in line and not line.strip().startswith('#')]
print(f"\nMethods ({len(methods)}):")

workspace_methods = [m for m in methods if 'workspace' in m.lower()]
thread_methods = [m for m in methods if 'thread' in m.lower() and 'workspace' not in m.lower()]
message_methods = [m for m in methods if 'message' in m.lower()]
api_methods = [m for m in methods if 'api' in m.lower() or '@app.route' in m]

print(f"\n  Workspace methods: {len(workspace_methods)}")
for m in workspace_methods[:5]:
    print(f"    - {m.strip()[:80]}")

print(f"\n  Thread methods: {len(thread_methods)}")
for m in thread_methods[:5]:
    print(f"    - {m.strip()[:80]}")

print(f"\n  Message methods: {len(message_methods)}")
for m in message_methods[:5]:
    print(f"    - {m.strip()[:80]}")

# Check for API routes
has_api_routes = 'create_thread_api_routes' in content or '@app.route' in content
print(f"\n  Has API routes: {has_api_routes}")

# Check for workspace table operations
has_workspace_crud = all(x in content for x in ['create_workspace', 'get_workspace', 'delete_workspace'])
has_thread_crud = all(x in content for x in ['create_thread', 'get_thread', 'delete_thread'])
has_message_crud = all(x in content for x in ['add_message', 'get_messages'])

print(f"\n" + "=" * 80)
print("FEATURE ANALYSIS:")
print("=" * 80)
print(f"  Workspace CRUD: {has_workspace_crud}")
print(f"  Thread CRUD: {has_thread_crud}")
print(f"  Message CRUD: {has_message_crud}")
print(f"  API Routes: {has_api_routes}")

# Check database connections
db_connections = content.count('sqlite3.connect')
print(f"\n  Database connection calls: {db_connections}")

# Check imports
import_section = '\n'.join(lines[:30])
print(f"\n" + "=" * 80)
print("IMPORTS:")
print("=" * 80)
print(import_section)

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("""
CURRENT STATE:
- Single 729-line file with everything
- Workspace, thread, and message operations mixed
- API routes included in same file
- Helper functions at top

RECOMMENDED STRUCTURE:
AI_infrastructure/
├── threads/                         # NEW MODULE
│   ├── __init__.py
│   ├── thread_manager.py           # Thread CRUD only
│   ├── message_manager.py          # Message operations only
│   ├── thread_helpers.py           # Helper functions
│   └── constants.py                # Thread-specific constants
│
├── workspace/                       # EXISTING (created)
│   ├── workspace_manager.py        # Workspace CRUD
│   └── ...
│
└── routes/
    ├── thread_routes.py            # Thread API routes (already exists)
    └── workspace_routes.py         # Workspace API routes (to create)

BENEFITS:
✅ Separation of concerns (threads vs workspaces)
✅ Easier to maintain (smaller files)
✅ Better testability (isolated modules)
✅ Cleaner imports
✅ Follows existing workspace module pattern

MIGRATION PLAN:
1. Create threads/ module
2. Move workspace methods → workspace/workspace_manager.py
3. Move thread methods → threads/thread_manager.py
4. Move message methods → threads/message_manager.py
5. Move helper functions → threads/thread_helpers.py
6. Update imports in thread_routes.py
7. Remove old thread_manager.py
""")
