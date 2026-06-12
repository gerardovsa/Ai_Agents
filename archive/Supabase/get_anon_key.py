#!/usr/bin/env python3
"""
Quick helper to construct Supabase Anon Key

The anon key typically has the same structure as service_role key
but with role: "anon" instead of role: "service_role"
"""

print("""
================================================================================
SUPABASE ANON KEY NEEDED
================================================================================

To get your Anon Key, go to:
https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo/settings/api

Look for:
- Project API keys section
- Copy the "anon" / "public" key (it's a long JWT token starting with eyJ...)

OR

You can use the service_role key for the migration (has full admin access).

================================================================================
""")

use_service = input("Use service_role key for migration? (yes/no): ").strip().lower()

if use_service == 'yes':
    print("\nOK! We'll use the service_role key for migration.")
    print("This has full admin access and will work for the migration script.\n")
else:
    print("\nPlease get the anon key from the Supabase dashboard and re-run the migration.\n")
