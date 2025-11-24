#!/usr/bin/env python3
"""
Render Deployment Validator - Real-Time Health Checks

Tests actual deployed application for:
1. JavaScript syntax errors (duplicate declarations)
2. Supabase connection manager initialization
3. API authentication (401 errors)
4. WebSocket connections
5. Console warnings/errors

Usage:
    python scripts/testing/validate_render_deployment.py https://your-app.onrender.com
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Try importing playwright
try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  playwright not installed")
    print("   Install with: pip install playwright")
    print("   Then run: playwright install chromium")
    sys.exit(1)


class RenderDeploymentValidator:
    """Validate deployed application health"""
    
    def __init__(self, url: str):
        self.url = url
        self.results = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'overall_status': 'UNKNOWN'
        }
    
    async def run_all_checks(self):
        """Run complete validation suite"""
        print(f"\n{'='*80}")
        print(f"RENDER DEPLOYMENT VALIDATION")
        print(f"{'='*80}")
        print(f"URL: {self.url}")
        print(f"Time: {self.results['timestamp']}")
        print(f"{'='*80}\n")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Non-headless to see what's happening
            context = await browser.new_context()
            page = await context.new_page()
            
            # Capture console messages
            console_messages = []
            page.on('console', lambda msg: console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'location': msg.location
            }))
            
            # Capture network requests
            network_requests = []
            page.on('request', lambda req: network_requests.append({
                'url': req.url,
                'method': req.method,
                'headers': dict(req.headers)
            }))
            
            # Capture responses
            network_responses = []
            page.on('response', lambda res: network_responses.append({
                'url': res.url,
                'status': res.status,
                'status_text': res.status_text
            }))
            
            try:
                # Load the page
                print("📡 Loading application...")
                await page.goto(self.url, timeout=30000, wait_until='networkidle')
                print("✅ Page loaded\n")
                
                # Wait for initialization
                print("⏳ Waiting for app initialization (10 seconds)...")
                await page.wait_for_timeout(10000)
                
                # Run checks
                await self.check_javascript_errors(console_messages)
                await self.check_supabase_connection(page, console_messages)
                await self.check_api_authentication(network_responses)
                await self.check_websocket_connections(page)
                await self.check_duplicate_declarations(console_messages)
                await self.check_critical_functions(page)
                
                # Calculate overall status
                self.calculate_overall_status()
                
                # Print summary
                self.print_summary()
                
            except PlaywrightTimeout:
                print("❌ Timeout loading page")
                self.results['overall_status'] = 'TIMEOUT'
            except Exception as e:
                print(f"❌ Error during validation: {e}")
                self.results['overall_status'] = 'ERROR'
            finally:
                await browser.close()
        
        return self.results
    
    async def check_javascript_errors(self, console_messages: List[Dict]):
        """Check for JavaScript errors in console"""
        print("🔍 Checking JavaScript errors...")
        
        errors = [msg for msg in console_messages if msg['type'] == 'error']
        syntax_errors = [msg for msg in errors if 'SyntaxError' in msg['text']]
        duplicate_declarations = [msg for msg in errors if 'already been declared' in msg['text']]
        
        self.results['checks']['javascript_errors'] = {
            'status': 'PASSED' if len(errors) == 0 else 'FAILED',
            'total_errors': len(errors),
            'syntax_errors': len(syntax_errors),
            'duplicate_declarations': len(duplicate_declarations),
            'details': duplicate_declarations[:5]  # First 5
        }
        
        if errors:
            print(f"   ❌ Found {len(errors)} JavaScript errors")
            if duplicate_declarations:
                print(f"   🔴 {len(duplicate_declarations)} duplicate declaration errors:")
                for err in duplicate_declarations[:3]:
                    print(f"      • {err['text'][:100]}...")
        else:
            print(f"   ✅ No JavaScript errors")
        print()
    
    async def check_supabase_connection(self, page, console_messages: List[Dict]):
        """Check Supabase connection manager status"""
        print("🔍 Checking Supabase connection...")
        
        # Check if connectionManager exists
        manager_exists = await page.evaluate('''() => {
            return typeof window.connectionManager !== 'undefined';
        }''')
        
        # Check if client was created
        client_exists = await page.evaluate('''() => {
            return window.connectionManager && window.connectionManager._client !== null;
        }''')
        
        # Check console for Supabase errors
        supabase_errors = [msg for msg in console_messages 
                          if 'Supabase' in msg['text'] and msg['type'] in ['error', 'warning']]
        
        # Check for specific error
        config_function_missing = any('loadSupabaseConfig is not a function' in msg['text'] 
                                     for msg in console_messages)
        
        # Check reconnection attempts
        reconnect_attempts = [msg for msg in console_messages 
                             if 'Reconnecting' in msg['text']]
        
        max_attempts_reached = any('Max reconnect attempts' in msg['text'] 
                                  for msg in console_messages)
        
        status = 'PASSED'
        if not manager_exists:
            status = 'CRITICAL'
        elif not client_exists or config_function_missing or max_attempts_reached:
            status = 'FAILED'
        elif len(supabase_errors) > 0:
            status = 'WARNING'
        
        self.results['checks']['supabase_connection'] = {
            'status': status,
            'manager_exists': manager_exists,
            'client_created': client_exists,
            'config_function_missing': config_function_missing,
            'reconnect_attempts': len(reconnect_attempts),
            'max_attempts_reached': max_attempts_reached,
            'errors': len(supabase_errors),
            'error_details': [msg['text'] for msg in supabase_errors[:5]]
        }
        
        if status == 'CRITICAL':
            print(f"   🔴 CRITICAL: Connection manager not found!")
        elif status == 'FAILED':
            print(f"   ❌ Supabase connection FAILED")
            if config_function_missing:
                print(f"      • window.loadSupabaseConfig is not a function")
            if max_attempts_reached:
                print(f"      • Max reconnection attempts reached ({len(reconnect_attempts)} attempts)")
            if not client_exists:
                print(f"      • Client not created")
        elif status == 'WARNING':
            print(f"   ⚠️  Supabase warnings: {len(supabase_errors)}")
        else:
            print(f"   ✅ Supabase connection working")
        print()
    
    async def check_api_authentication(self, responses: List[Dict]):
        """Check for 401 authentication errors"""
        print("🔍 Checking API authentication...")
        
        api_responses = [res for res in responses if '/api/' in res['url']]
        auth_errors = [res for res in api_responses if res['status'] == 401]
        failed_requests = [res for res in api_responses if res['status'] >= 400]
        
        self.results['checks']['api_authentication'] = {
            'status': 'PASSED' if len(auth_errors) == 0 else 'FAILED',
            'total_api_calls': len(api_responses),
            'auth_errors': len(auth_errors),
            'failed_requests': len(failed_requests),
            'details': auth_errors[:5]
        }
        
        if auth_errors:
            print(f"   ❌ Found {len(auth_errors)} authentication errors (401)")
            for err in auth_errors[:3]:
                print(f"      • {err['url']}")
        elif failed_requests:
            print(f"   ⚠️  Found {len(failed_requests)} failed API requests")
        else:
            print(f"   ✅ All API requests successful ({len(api_responses)} calls)")
        print()
    
    async def check_websocket_connections(self, page):
        """Check WebSocket connection count"""
        print("🔍 Checking WebSocket connections...")
        
        ws_count = await page.evaluate('''() => {
            const entries = performance.getEntriesByType('resource');
            return entries.filter(e => 
                e.name.includes('realtime') || 
                e.name.includes('ws://') || 
                e.name.includes('wss://')
            ).length;
        }''')
        
        self.results['checks']['websocket_connections'] = {
            'status': 'PASSED' if ws_count <= 1 else 'WARNING' if ws_count <= 3 else 'FAILED',
            'connection_count': ws_count,
            'expected': 1
        }
        
        if ws_count == 0:
            print(f"   ❌ No WebSocket connections found")
        elif ws_count == 1:
            print(f"   ✅ Single WebSocket connection (correct)")
        elif ws_count <= 3:
            print(f"   ⚠️  Multiple WebSocket connections: {ws_count}")
        else:
            print(f"   ❌ Too many WebSocket connections: {ws_count}")
        print()
    
    async def check_duplicate_declarations(self, console_messages: List[Dict]):
        """Check for duplicate variable declarations"""
        print("🔍 Checking duplicate declarations...")
        
        duplicates = [msg for msg in console_messages 
                     if 'already been declared' in msg['text']]
        
        api_base_url_duplicates = [msg for msg in duplicates 
                                  if 'API_BASE_URL' in msg['text']]
        
        self.results['checks']['duplicate_declarations'] = {
            'status': 'PASSED' if len(duplicates) == 0 else 'FAILED',
            'total_duplicates': len(duplicates),
            'api_base_url_duplicates': len(api_base_url_duplicates),
            'details': [msg['text'] for msg in duplicates]
        }
        
        if duplicates:
            print(f"   ❌ Found {len(duplicates)} duplicate declarations")
            if api_base_url_duplicates:
                print(f"      🔴 API_BASE_URL declared {len(api_base_url_duplicates)} times")
        else:
            print(f"   ✅ No duplicate declarations")
        print()
    
    async def check_critical_functions(self, page):
        """Check if critical functions exist"""
        print("🔍 Checking critical functions...")
        
        functions_to_check = [
            'window.loadSupabaseConfig',
            'window.connectionManager',
            'window.ThreadManager',
            'window.UserAuth',
            'window.ModuleManager'
        ]
        
        results = {}
        for func_name in functions_to_check:
            exists = await page.evaluate(f'''() => {{
                return typeof {func_name} !== 'undefined';
            }}''')
            results[func_name] = exists
        
        missing = [name for name, exists in results.items() if not exists]
        
        self.results['checks']['critical_functions'] = {
            'status': 'PASSED' if len(missing) == 0 else 'CRITICAL',
            'total_checked': len(functions_to_check),
            'missing_count': len(missing),
            'missing_functions': missing,
            'details': results
        }
        
        if missing:
            print(f"   🔴 CRITICAL: {len(missing)} functions missing:")
            for func in missing:
                print(f"      • {func}")
        else:
            print(f"   ✅ All critical functions present")
        print()
    
    def calculate_overall_status(self):
        """Calculate overall validation status"""
        statuses = [check['status'] for check in self.results['checks'].values()]
        
        if 'CRITICAL' in statuses:
            self.results['overall_status'] = 'CRITICAL'
        elif 'FAILED' in statuses:
            self.results['overall_status'] = 'FAILED'
        elif 'WARNING' in statuses:
            self.results['overall_status'] = 'WARNING'
        else:
            self.results['overall_status'] = 'PASSED'
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}\n")
        
        status_icon = {
            'PASSED': '✅',
            'WARNING': '⚠️',
            'FAILED': '❌',
            'CRITICAL': '🔴'
        }
        
        for check_name, check_data in self.results['checks'].items():
            status = check_data['status']
            icon = status_icon.get(status, '❓')
            print(f"{icon} {check_name.replace('_', ' ').title()}: {status}")
        
        print(f"\n{'='*80}")
        overall_icon = status_icon.get(self.results['overall_status'], '❓')
        print(f"{overall_icon} OVERALL STATUS: {self.results['overall_status']}")
        print(f"{'='*80}\n")
        
        # Recommendations
        if self.results['overall_status'] in ['CRITICAL', 'FAILED']:
            print("🔧 RECOMMENDED ACTIONS:\n")
            
            # Check specific issues
            if self.results['checks']['duplicate_declarations']['total_duplicates'] > 0:
                print("1. Fix duplicate API_BASE_URL declarations:")
                print("   • Search codebase for 'const API_BASE_URL'")
                print("   • Ensure it's declared only once globally")
                print("   • Check account_profile.js and main index file\n")
            
            if not self.results['checks']['critical_functions']['details'].get('window.loadSupabaseConfig', True):
                print("2. Fix missing loadSupabaseConfig function:")
                print("   • Ensure loadSupabaseConfig() is defined before connection manager loads")
                print("   • Check script load order in HTML")
                print("   • Verify function is exposed to window scope\n")
            
            if not self.results['checks']['supabase_connection']['client_created']:
                print("3. Fix Supabase client initialization:")
                print("   • Check SUPABASE_URL and SUPABASE_ANON_KEY are set")
                print("   • Verify connection manager initialization sequence")
                print("   • Check browser console for detailed errors\n")
            
            if self.results['checks']['api_authentication']['auth_errors'] > 0:
                print("4. Fix API authentication:")
                print("   • Check if user is logged in")
                print("   • Verify auth token is being sent with requests")
                print("   • Check /api/auth/status endpoint\n")


async def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("Usage: python validate_render_deployment.py <URL>")
        print("Example: python validate_render_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    url = sys.argv[1]
    if not url.startswith('http'):
        url = f'https://{url}'
    
    validator = RenderDeploymentValidator(url)
    results = await validator.run_all_checks()
    
    # Save results
    output_file = Path(__file__).parent.parent.parent / 'data' / 'render_validation_report.json'
    import json
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📄 Full report saved: {output_file}\n")
    
    # Exit with appropriate code
    if results['overall_status'] in ['CRITICAL', 'FAILED']:
        sys.exit(1)
    elif results['overall_status'] == 'WARNING':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
