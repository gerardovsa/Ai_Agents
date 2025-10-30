"""
Test Current Connections - Baseline
====================================

Before we rebuild, let's verify what's currently working/broken.
No modifications - just testing current state.
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("TESTING CURRENT TOOL CONNECTIONS")
print("="*80)

# ============================================================
# TEST 1: Registry Loading
# ============================================================
print("\n[TEST 1] Registry Loading - Current State")
print("-" * 80)

try:
    from tools.registry import ToolRegistry
    registry = ToolRegistry()
    print(f"✅ Registry initialized: {len(registry.tools)} tools loaded")
    
    # Check for Gmail tools
    gmail_tools = [t for t in registry.tools.keys() if 'gmail' in t.lower()]
    print(f"   Gmail tools found: {len(gmail_tools)}")
    if gmail_tools:
        print(f"   Examples: {gmail_tools[:3]}")
    
    # Check for Google Docs tools
    docs_tools = [t for t in registry.tools.keys() if 'google_docs' in t.lower()]
    print(f"   Google Docs tools found: {len(docs_tools)}")
    if docs_tools:
        print(f"   Examples: {docs_tools[:3]}")
        
except Exception as e:
    print(f"❌ Registry loading failed: {e}")

# ============================================================
# TEST 2: Implementations Loading
# ============================================================
print("\n[TEST 2] Implementations Loading - Current State")
print("-" * 80)

try:
    # Try importing from tools/implementations directly
    print("Loading from tools/implementations/:")
    
    # Try gmail
    try:
        from tools.implementations import gmail
        print(f"  ✅ tools.implementations.gmail loaded")
        print(f"     Functions: {[x for x in dir(gmail) if 'gmail_' in x][:3]}")
    except Exception as e:
        print(f"  ❌ tools.implementations.gmail failed: {e}")
    
    # Try google_docs
    try:
        from tools.implementations import google_docs
        print(f"  ✅ tools.implementations.google_docs loaded")
        print(f"     Functions: {[x for x in dir(google_docs) if 'google_docs_' in x][:3]}")
    except Exception as e:
        print(f"  ❌ tools.implementations.google_docs failed: {e}")
        
except Exception as e:
    print(f"❌ Implementation loading failed: {e}")

# ============================================================
# TEST 3: google_workspace Direct Loading
# ============================================================
print("\n[TEST 3] google_workspace Direct Loading")
print("-" * 80)

try:
    print("Loading from google_workspace/:")
    
    # Try gmail
    try:
        from google_workspace import gmail as gw_gmail
        print(f"  ✅ google_workspace.gmail loaded")
        print(f"     Functions: {[x for x in dir(gw_gmail) if 'gmail_' in x and not x.startswith('_')][:3]}")
    except Exception as e:
        print(f"  ❌ google_workspace.gmail failed: {e}")
    
    # Try google_docs
    try:
        from google_workspace import google_docs as gw_docs
        print(f"  ✅ google_workspace.google_docs loaded")
        print(f"     Functions: {[x for x in dir(gw_docs) if 'google_docs_' in x and not x.startswith('_')][:3]}")
    except Exception as e:
        print(f"  ❌ google_workspace.google_docs failed: {e}")
        
except Exception as e:
    print(f"❌ google_workspace loading failed: {e}")

# ============================================================
# TEST 4: Schema Loading
# ============================================================
print("\n[TEST 4] Schema Loading")
print("-" * 80)

try:
    import json
    from pathlib import Path
    
    schemas_dir = Path(__file__).parent / "tools" / "schemas"
    
    # Check Gmail schema
    gmail_schema = schemas_dir / "gmail_tools.json"
    if gmail_schema.exists():
        with open(gmail_schema) as f:
            gmail_data = json.load(f)
            print(f"✅ Gmail schema loaded: {len(gmail_data.get('tools', []))} tools defined")
            print(f"   Examples: {[t['name'] for t in gmail_data.get('tools', [])[:3]]}")
    else:
        print(f"❌ Gmail schema not found: {gmail_schema}")
    
    # Check Google Docs schema
    docs_schema = schemas_dir / "google_docs_tools.json"
    if docs_schema.exists():
        with open(docs_schema) as f:
            docs_data = json.load(f)
            print(f"✅ Google Docs schema loaded: {len(docs_data.get('tools', []))} tools defined")
            print(f"   Examples: {[t['name'] for t in docs_data.get('tools', [])[:3]]}")
    else:
        print(f"❌ Google Docs schema not found: {docs_schema}")
        
except Exception as e:
    print(f"❌ Schema loading failed: {e}")

# ============================================================
# TEST 5: Credential Injection Check
# ============================================================
print("\n[TEST 5] Credential Injection Support")
print("-" * 80)

try:
    import inspect
    from google_workspace import gmail as gw_gmail
    
    # Check gmail_send_email signature
    sig = inspect.signature(gw_gmail.gmail_send_email)
    params = list(sig.parameters.keys())
    print(f"gmail_send_email parameters: {params}")
    
    if '_user_id' in params or '_injected_credentials' in params:
        print("✅ Credential injection parameters found!")
    else:
        print("⚠️  Credential injection parameters NOT found in signature")
        print("   But they may be in **kwargs")
        
except Exception as e:
    print(f"❌ Signature check failed: {e}")

# ============================================================
# TEST 6: File Size Comparison
# ============================================================
print("\n[TEST 6] File Size Comparison")
print("-" * 80)

try:
    from pathlib import Path
    
    # google_workspace
    gw_gmail = Path(__file__).parent / "google_workspace" / "gmail.py"
    if gw_gmail.exists():
        size_gw = gw_gmail.stat().st_size / 1024
        print(f"google_workspace/gmail.py: {size_gw:.1f} KB")
    
    # tools/implementations redirect
    impl_gmail = Path(__file__).parent / "tools" / "implementations" / "gmail.py"
    if impl_gmail.exists():
        size_impl = impl_gmail.stat().st_size / 1024
        print(f"tools/implementations/gmail.py: {size_impl:.1f} KB")
        
        if size_impl < 1:
            print("⚠️  REDIRECT FILE DETECTED (< 1 KB)")
    
    # Ratio
    if gw_gmail.exists() and impl_gmail.exists():
        ratio = size_gw / size_impl
        print(f"Ratio: {ratio:.0f}x difference (google_workspace is larger)")
        
except Exception as e:
    print(f"⚠️  File comparison failed: {e}")

# ============================================================
# Summary
# ============================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
Current State:
  • Registry loads tools from: tools/implementations/ ✅
  • But most are redirects (0.3-0.4 KB files) ❌
  • Real code in: google_workspace/ (60-173 KB files) ✅
  • Schemas loaded from: tools/schemas/ ✅
  
Problem:
  • Credential injection broken through redirect layer
  • Missing tools: google_slides.py, google_meet.py
  
Solution:
  • Update registry to load directly from google_workspace/
  • Bypass redirect layer
  • Proper credential injection flows through
  
Next: Build registry_v3.py to test direct loading
""")
print("="*80 + "\n")
