#!/usr/bin/env python3
"""
Automated Render Deployment Issue Fixer

Fixes:
1. Duplicate API_BASE_URL declarations
2. Missing loadSupabaseConfig function
3. Script load order issues

Usage:
    python scripts/maintenance/fix_render_deployment_issues.py
"""

import re
from pathlib import Path
from typing import List, Tuple

class RenderDeploymentFixer:
    """Automated fixer for common Render deployment issues"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.ui_dir = project_root / 'UI'
        self.fixes_applied = []
        self.issues_found = []
    
    def run_all_fixes(self):
        """Run all automated fixes"""
        print("\n" + "="*80)
        print("RENDER DEPLOYMENT ISSUE FIXER")
        print("="*80 + "\n")
        
        self.fix_duplicate_api_base_url()
        self.check_load_supabase_config()
        self.verify_script_load_order()
        
        self.print_summary()
    
    def fix_duplicate_api_base_url(self):
        """Find and fix duplicate API_BASE_URL declarations"""
        print("🔍 Checking for duplicate API_BASE_URL declarations...\n")
        
        declarations_found = []
        
        # Search all JS files
        for js_file in self.ui_dir.rglob('*.js'):
            try:
                content = js_file.read_text(encoding='utf-8')
                
                # Find declarations
                patterns = [
                    r'const\s+API_BASE_URL\s*=',
                    r'var\s+API_BASE_URL\s*=',
                    r'let\s+API_BASE_URL\s*='
                ]
                
                for pattern in patterns:
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            declarations_found.append({
                                'file': js_file,
                                'line': line_num,
                                'declaration': match.group()
                            })
            except:
                pass
        
        # Search HTML files
        for html_file in [self.project_root / 'UI' / 'business-ai-platform-v2.html']:
            if html_file.exists():
                content = html_file.read_text(encoding='utf-8')
                
                for pattern in [r'const\s+API_BASE_URL\s*=', r'var\s+API_BASE_URL\s*=']:
                    matches = list(re.finditer(pattern, content))
                    if matches:
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            declarations_found.append({
                                'file': html_file,
                                'line': line_num,
                                'declaration': match.group()
                            })
        
        if len(declarations_found) > 1:
            print(f"   ❌ Found {len(declarations_found)} API_BASE_URL declarations:")
            for decl in declarations_found:
                print(f"      • {decl['file'].name}:{decl['line']}")
            
            self.issues_found.append({
                'type': 'DUPLICATE_API_BASE_URL',
                'count': len(declarations_found),
                'locations': declarations_found
            })
            
            # Offer to fix
            print(f"\n   📝 Recommended fix:")
            print(f"      1. Keep ONE declaration in main HTML file")
            print(f"      2. In other files, use: const API_BASE_URL = window.API_BASE_URL || '/api';")
            
            # Auto-fix account_profile.js if it's the culprit
            account_profile = self.ui_dir / 'external' / 'modules' / 'account-profile' / 'account_profile.js'
            if account_profile.exists():
                content = account_profile.read_text(encoding='utf-8')
                if re.search(r'const\s+API_BASE_URL\s*=', content):
                    print(f"\n   🔧 Auto-fixing {account_profile.name}...")
                    
                    # Replace const API_BASE_URL = ... with reference to global
                    new_content = re.sub(
                        r'const\s+API_BASE_URL\s*=\s*[^;]+;',
                        "// Use global API_BASE_URL from main HTML\nconst API_BASE_URL = window.API_BASE_URL || window.location.origin + '/api';",
                        content,
                        count=1
                    )
                    
                    account_profile.write_text(new_content, encoding='utf-8')
                    print(f"      ✅ Fixed! Changed to use window.API_BASE_URL")
                    self.fixes_applied.append('Fixed account_profile.js API_BASE_URL')
        
        elif len(declarations_found) == 1:
            print(f"   ✅ Single API_BASE_URL declaration found (correct)")
            print(f"      Location: {declarations_found[0]['file'].name}:{declarations_found[0]['line']}")
        else:
            print(f"   ⚠️  No API_BASE_URL declarations found")
        
        print()
    
    def check_load_supabase_config(self):
        """Check if loadSupabaseConfig function exists"""
        print("🔍 Checking for loadSupabaseConfig function...\n")
        
        main_html = self.project_root / 'UI' / 'business-ai-platform-v2.html'
        
        if not main_html.exists():
            print(f"   ⚠️  Main HTML file not found: {main_html}")
            return
        
        content = main_html.read_text(encoding='utf-8')
        
        # Check if function exists
        has_function = 'window.loadSupabaseConfig' in content or 'loadSupabaseConfig' in content
        
        if has_function:
            print(f"   ✅ loadSupabaseConfig function found in HTML")
        else:
            print(f"   ❌ loadSupabaseConfig function NOT found")
            
            self.issues_found.append({
                'type': 'MISSING_LOAD_SUPABASE_CONFIG',
                'file': main_html
            })
            
            print(f"\n   📝 Recommended fix:")
            print(f"      Add this BEFORE supabase-connection-manager.js:")
            print(f"""
      <script>
      window.loadSupabaseConfig = async function() {{
          console.log('[Config] Loading Supabase config...');
          try {{
              const response = await fetch('/api/auth/google/config');
              const data = await response.json();
              
              if (data.supabase_url && data.supabase_anon_key) {{
                  window.SUPABASE_URL = data.supabase_url;
                  window.SUPABASE_ANON_KEY = data.supabase_anon_key;
                  console.log('[Config] Supabase config loaded');
                  return true;
              }}
              return false;
          }} catch (error) {{
              console.error('[Config] Failed to load config:', error);
              return false;
          }}
      }};
      </script>
            """)
        
        print()
    
    def verify_script_load_order(self):
        """Verify scripts load in correct order"""
        print("🔍 Checking script load order...\n")
        
        main_html = self.project_root / 'UI' / 'business-ai-platform-v2.html'
        
        if not main_html.exists():
            return
        
        content = main_html.read_text(encoding='utf-8')
        
        # Find script tags
        script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>'
        scripts = re.findall(script_pattern, content)
        
        # Key scripts to check order
        supabase_sdk_pos = next((i for i, s in enumerate(scripts) if 'supabase' in s.lower() and 'cdn' in s.lower()), None)
        connection_manager_pos = next((i for i, s in enumerate(scripts) if 'supabase-connection-manager' in s), None)
        
        issues = []
        
        if supabase_sdk_pos is None:
            issues.append("Supabase SDK not found")
        
        if connection_manager_pos is None:
            issues.append("Connection manager script not found")
        
        if supabase_sdk_pos and connection_manager_pos:
            if connection_manager_pos < supabase_sdk_pos:
                issues.append("Connection manager loads BEFORE Supabase SDK (wrong order)")
        
        if issues:
            print(f"   ❌ Script load order issues:")
            for issue in issues:
                print(f"      • {issue}")
            
            print(f"\n   📝 Correct order should be:")
            print(f"      1. Supabase SDK (CDN)")
            print(f"      2. loadSupabaseConfig function")
            print(f"      3. supabase-connection-manager.js")
            print(f"      4. Other modules")
        else:
            print(f"   ✅ Script load order looks correct")
            if supabase_sdk_pos is not None and connection_manager_pos is not None:
                print(f"      • Supabase SDK at position {supabase_sdk_pos}")
                print(f"      • Connection manager at position {connection_manager_pos}")
        
        print()
    
    def print_summary(self):
        """Print fix summary"""
        print("="*80)
        print("SUMMARY")
        print("="*80 + "\n")
        
        print(f"Issues Found: {len(self.issues_found)}")
        if self.issues_found:
            for issue in self.issues_found:
                print(f"   • {issue['type']}")
        else:
            print("   ✅ No issues found!")
        
        print(f"\nFixes Applied: {len(self.fixes_applied)}")
        if self.fixes_applied:
            for fix in self.fixes_applied:
                print(f"   ✅ {fix}")
        else:
            print("   ℹ️  No automatic fixes applied (manual intervention needed)")
        
        print("\n" + "="*80)
        
        if len(self.issues_found) > 0:
            print("\n🔧 NEXT STEPS:")
            print("1. Review the recommended fixes above")
            print("2. Apply manual fixes to main HTML file")
            print("3. Test locally: BISTART")
            print("4. Run validation: python scripts/testing/validate_render_deployment.py http://localhost:5001")
            print("5. Deploy to Render")
            print("6. Run validation: python scripts/testing/validate_render_deployment.py https://your-app.onrender.com")
        else:
            print("\n✅ All checks passed! Deployment should work correctly.")


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent.parent
    fixer = RenderDeploymentFixer(project_root)
    fixer.run_all_fixes()


if __name__ == '__main__':
    main()
