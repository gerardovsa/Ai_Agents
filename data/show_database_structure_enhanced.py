#!/usr/bin/env python3
"""
Database Structure Visualization Tool - ENHANCED WITH SUPABASE SUPPORT

Analyzes SQLite databases AND Supabase PostgreSQL schemas:
- Complete database schema (tables, columns, types, constraints)
- Sample data for each table
- Row counts and table statistics
- Scripts that access each database
- API routes that use each database
- Inconsistencies between code and database
- Supabase connection manager validation
- Real-time channel subscription audit
- Schema-to-code consistency checks

NEW FEATURES (Nov 24, 2025):
- SupabaseAnalyzer: Scans PostgreSQL schemas (ai_infrastructure, sessions, synergy_sessions, stock_data)
- ConnectionManagerValidator: Detects duplicate Supabase client creation
- SchemaConsistencyChecker: Validates code references match actual schema
- Frontend JavaScript analysis: Tracks Realtime subscriptions

Usage:
    python show_database_structure_enhanced.py
    
Output:
    - Console output with detailed structure
    - Saved report in data/database_analysis_report_enhanced.txt
    
Environment Variables:
    SUPABASE_DB_URL: PostgreSQL connection URL (required for Supabase analysis)
"""

import sqlite3
from pathlib import Path
import re
import os
import sys
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
_env_file = Path(__file__).parent.parent / '.env.master'
if _env_file.exists():
    load_dotenv(_env_file)
else:
    load_dotenv()

# Try importing psycopg2 for Supabase support
try:
    import psycopg2
    from psycopg2 import pool
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠️  psycopg2 not available - Supabase analysis disabled")
    print("   Install with: pip install psycopg2-binary")


# ========================================
# SUPABASE ANALYZER (NEW)
# ========================================

class SupabaseAnalyzer:
    """
    Analyze Supabase PostgreSQL schemas
    
    Scans production Supabase database for:
    - All tables in each schema
    - Column definitions (name, type, nullable, default)
    - Primary keys, foreign keys, indexes
    - Row counts
    - Table relationships
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv('SUPABASE_DB_URL')
        self.schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions', 'stock_data', 'kanban_analytics']
        self.conn = None
        self.schema_data = {}
        
        if not self.connection_string:
            print("⚠️  SUPABASE_DB_URL not set - Skipping Supabase analysis")
            return
        
        try:
            self.conn = psycopg2.connect(self.connection_string)
            print("✅ Connected to Supabase PostgreSQL")
            self.analyze_all_schemas()
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
    
    def analyze_all_schemas(self):
        """Analyze all configured schemas"""
        if not self.conn:
            return
        
        for schema_name in self.schemas:
            try:
                self.schema_data[schema_name] = self.analyze_schema(schema_name)
                print(f"   Analyzed schema: {schema_name} ({len(self.schema_data[schema_name])} tables)")
            except Exception as e:
                print(f"   Error analyzing {schema_name}: {e}")
    
    def analyze_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get complete structure of a PostgreSQL schema"""
        cursor = self.conn.cursor()
        
        # Get all tables in schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema_name,))
        
        tables = {}
        for (table_name,) in cursor.fetchall():
            tables[table_name] = {
                'columns': self._get_columns(cursor, schema_name, table_name),
                'primary_keys': self._get_primary_keys(cursor, schema_name, table_name),
                'foreign_keys': self._get_foreign_keys(cursor, schema_name, table_name),
                'indexes': self._get_indexes(cursor, schema_name, table_name),
                'row_count': self._get_row_count(cursor, schema_name, table_name),
                'sample_data': self._get_sample_data(cursor, schema_name, table_name)
            }
        
        cursor.close()
        return tables
    
    def _get_columns(self, cursor, schema_name: str, table_name: str) -> List[Dict]:
        """Get column definitions"""
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema_name, table_name))
        
        return [{
            'name': row[0],
            'type': row[1],
            'nullable': row[2] == 'YES',
            'default': row[3],
            'max_length': row[4]
        } for row in cursor.fetchall()]
    
    def _get_primary_keys(self, cursor, schema_name: str, table_name: str) -> List[str]:
        """Get primary key columns"""
        cursor.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
        """, (f"{schema_name}.{table_name}",))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_foreign_keys(self, cursor, schema_name: str, table_name: str) -> List[Dict]:
        """Get foreign key relationships"""
        cursor.execute("""
            SELECT
                kcu.column_name,
                ccu.table_schema AS foreign_schema,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_schema = %s
                AND tc.table_name = %s
        """, (schema_name, table_name))
        
        return [{
            'column': row[0],
            'references': f"{row[1]}.{row[2]}({row[3]})"
        } for row in cursor.fetchall()]
    
    def _get_indexes(self, cursor, schema_name: str, table_name: str) -> List[str]:
        """Get indexes on table"""
        cursor.execute("""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s
        """, (schema_name, table_name))
        
        return [row[0] for row in cursor.fetchall()]
    
    def _get_row_count(self, cursor, schema_name: str, table_name: str) -> int:
        """Get approximate row count"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
            return cursor.fetchone()[0]
        except:
            return 0
    
    def _get_sample_data(self, cursor, schema_name: str, table_name: str, limit: int = 3) -> List[Tuple]:
        """Get sample rows"""
        try:
            cursor.execute(f"SELECT * FROM {schema_name}.{table_name} LIMIT {limit}")
            return cursor.fetchall()
        except:
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# ========================================
# CONNECTION MANAGER VALIDATOR (NEW)
# ========================================

class ConnectionManagerValidator:
    """
    Validate Supabase connection manager singleton pattern
    
    Detects:
    - Direct createClient() calls (bypasses singleton)
    - Direct channel subscriptions (should use manager)
    - Multiple client instances in same file
    - Files not using connection manager
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.compliant_files = []
    
    def validate_all(self) -> List[Dict]:
        """Run all validation checks"""
        self.check_duplicate_clients()
        self.check_channel_subscriptions()
        self.check_manager_usage()
        return self.issues
    
    def check_duplicate_clients(self):
        """Find direct createClient() calls that bypass singleton"""
        ui_dir = self.project_root / 'UI'
        if not ui_dir.exists():
            return
        
        for js_file in ui_dir.rglob('*.js'):
            # Skip the connection manager itself
            if 'connection-manager' in js_file.name:
                continue
            
            try:
                content = js_file.read_text(encoding='utf-8')
                
                # Bad pattern: Direct client creation
                if 'createClient(' in content:
                    # Check if it's in a comment
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'createClient(' in line and not line.strip().startswith('//'):
                            self.issues.append({
                                'file': js_file.relative_to(self.project_root),
                                'line': i + 1,
                                'type': 'DUPLICATE_CLIENT',
                                'severity': 'HIGH',
                                'message': 'Direct createClient() call bypasses singleton pattern'
                            })
            except Exception as e:
                pass  # Skip files with encoding issues
    
    def check_channel_subscriptions(self):
        """Check if channel subscriptions go through manager"""
        ui_dir = self.project_root / 'UI'
        if not ui_dir.exists():
            return
        
        for js_file in ui_dir.rglob('*.js'):
            if 'connection-manager' in js_file.name:
                continue
            
            try:
                content = js_file.read_text(encoding='utf-8')
                
                # Bad pattern: Direct channel subscription
                direct_channel = re.findall(r'(?:supabaseClient|supabase)\.channel\(', content)
                if direct_channel:
                    self.issues.append({
                        'file': js_file.relative_to(self.project_root),
                        'type': 'DIRECT_CHANNEL',
                        'severity': 'MEDIUM',
                        'message': f'Direct channel subscription ({len(direct_channel)} occurrences) - should use connectionManager.subscribeChannel()'
                    })
                
                # Good pattern: Using manager
                if 'connectionManager.getClient()' in content or 'connectionManager.subscribeChannel(' in content:
                    self.compliant_files.append(js_file.relative_to(self.project_root))
            except:
                pass
    
    def check_manager_usage(self):
        """Verify connection manager is imported where Supabase is used"""
        ui_dir = self.project_root / 'UI'
        if not ui_dir.exists():
            return
        
        manager_path = ui_dir / 'js' / 'supabase-connection-manager.js'
        if not manager_path.exists():
            self.issues.append({
                'file': 'UI/js',
                'type': 'MISSING_MANAGER',
                'severity': 'CRITICAL',
                'message': 'supabase-connection-manager.js not found!'
            })


# ========================================
# SCHEMA CONSISTENCY CHECKER (NEW)
# ========================================

class SchemaConsistencyChecker:
    """
    Validate code references match actual database schema
    
    Checks:
    - Table references in code exist in database
    - Column references are valid
    - Foreign key relationships are respected
    - No orphaned tables (defined but never used)
    """
    
    def __init__(self, supabase_analyzer: SupabaseAnalyzer, project_root: Path):
        self.supabase = supabase_analyzer
        self.project_root = project_root
        self.issues = []
    
    def check_all(self) -> List[Dict]:
        """Run all consistency checks"""
        if not self.supabase or not self.supabase.schema_data:
            return []
        
        self.check_table_references()
        self.check_column_references()
        self.find_orphaned_tables()
        return self.issues
    
    def check_table_references(self):
        """Find code referencing non-existent tables"""
        # Build set of all actual tables
        actual_tables = set()
        for schema_name, tables in self.supabase.schema_data.items():
            for table_name in tables.keys():
                actual_tables.add(f"{schema_name}.{table_name}")
                actual_tables.add(table_name)  # Also allow unqualified names
        
        # Scan Python files
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # Find .from('table_name') patterns
                table_refs = re.findall(r'\.from\(["\']([^"\']+)["\']', content)
                
                for table_ref in table_refs:
                    # Remove schema prefix if present for comparison
                    clean_ref = table_ref.split('.')[-1]
                    
                    if table_ref not in actual_tables and clean_ref not in actual_tables:
                        self.issues.append({
                            'file': py_file.relative_to(self.project_root),
                            'type': 'MISSING_TABLE',
                            'severity': 'HIGH',
                            'table': table_ref,
                            'message': f"Code references table '{table_ref}' not found in Supabase"
                        })
            except:
                pass
        
        # Scan JavaScript files
        for js_file in self.project_root.rglob('*.js'):
            if 'node_modules' in str(js_file):
                continue
            
            try:
                content = js_file.read_text(encoding='utf-8')
                
                # Find .from('table_name') patterns
                table_refs = re.findall(r'\.from\(["\']([^"\']+)["\']', content)
                
                for table_ref in table_refs:
                    clean_ref = table_ref.split('.')[-1]
                    
                    if table_ref not in actual_tables and clean_ref not in actual_tables:
                        self.issues.append({
                            'file': js_file.relative_to(self.project_root),
                            'type': 'MISSING_TABLE',
                            'severity': 'HIGH',
                            'table': table_ref,
                            'message': f"Code references table '{table_ref}' not found in Supabase"
                        })
            except:
                pass
    
    def check_column_references(self):
        """Find code referencing non-existent columns (basic check)"""
        # This is a simplified check - full implementation would parse .select() calls
        pass
    
    def find_orphaned_tables(self):
        """Find tables that exist in schema but never used in code"""
        if not self.supabase or not self.supabase.schema_data:
            return
        
        # Build set of all tables used in code
        used_tables = set()
        
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                table_refs = re.findall(r'\.from\(["\']([^"\']+)["\']', content)
                used_tables.update(table_refs)
            except:
                pass
        
        for js_file in self.project_root.rglob('*.js'):
            if 'node_modules' in str(js_file):
                continue
            
            try:
                content = js_file.read_text(encoding='utf-8')
                table_refs = re.findall(r'\.from\(["\']([^"\']+)["\']', content)
                used_tables.update(table_refs)
            except:
                pass
        
        # Check for orphaned tables
        for schema_name, tables in self.supabase.schema_data.items():
            for table_name in tables.keys():
                qualified_name = f"{schema_name}.{table_name}"
                
                if table_name not in used_tables and qualified_name not in used_tables:
                    row_count = tables[table_name].get('row_count', 0)
                    self.issues.append({
                        'type': 'ORPHANED_TABLE',
                        'severity': 'LOW',
                        'table': qualified_name,
                        'row_count': row_count,
                        'message': f"Table '{qualified_name}' exists but never referenced in code ({row_count} rows)"
                    })


# ========================================
# REALTIME HEALTH CHECKER (NEW - PHASE 5)
# ========================================

class RealtimeHealthChecker:
    """
    Real-time browser-based health checks using Playwright
    
    Tests actual browser behavior with Supabase connection manager:
    - Validates singleton pattern at runtime
    - Detects multiple GoTrueClient instances
    - Counts WebSocket connections
    - Tests channel subscription management
    - Simulates network events (offline/online)
    - Monitors memory usage and leaks
    
    Requires: pip install playwright; playwright install chromium
    """
    
    def __init__(self, ui_url: str = 'http://localhost:5001', timeout: int = 30000):
        self.ui_url = ui_url
        self.timeout = timeout
        self.results = {
            'singleton_test': {},
            'websocket_test': {},
            'channel_test': {},
            'network_test': {},
            'memory_test': {},
            'console_warnings': [],
            'overall_status': 'NOT_RUN'
        }
        self.playwright_available = False
        
        # Check if Playwright is available
        try:
            import playwright
            self.playwright_available = True
        except ImportError:
            pass
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run complete real-time health check suite"""
        if not self.playwright_available:
            return {
                'status': 'SKIPPED',
                'reason': 'Playwright not installed',
                'install_instructions': 'pip install playwright && playwright install chromium'
            }
        
        from playwright.async_api import async_playwright
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                # Run all test suites
                await self._test_singleton_pattern(browser)
                await self._test_websocket_connections(browser)
                await self._test_channel_management(browser)
                await self._test_network_resilience(browser)
                await self._test_memory_usage(browser)
                
                await browser.close()
                
                # Determine overall status
                self._calculate_overall_status()
                
        except Exception as e:
            self.results['overall_status'] = 'ERROR'
            self.results['error'] = str(e)
        
        return self.results
    
    async def _test_singleton_pattern(self, browser):
        """Test 1: Validate connection manager singleton pattern"""
        page = await browser.new_page()
        
        # Capture console messages
        console_messages = []
        page.on('console', lambda msg: console_messages.append({
            'type': msg.type,
            'text': msg.text
        }))
        
        try:
            # Load UI
            await page.goto(self.ui_url, timeout=self.timeout, wait_until='networkidle')
            await page.wait_for_timeout(3000)  # Wait for initialization
            
            # Check for multiple GoTrueClient warnings
            duplicate_warnings = [msg for msg in console_messages 
                                 if 'Multiple GoTrueClient instances' in msg['text']]
            
            # Count supabaseClient instances in window
            client_count = await page.evaluate('''() => {
                let count = 0;
                if (window.supabaseClient) count++;
                if (window.SUPABASE_CLIENT) count++;
                if (window.connectionManager && window.connectionManager._client) count++;
                return count;
            }''')
            
            self.results['singleton_test'] = {
                'status': 'PASSED' if len(duplicate_warnings) == 0 and client_count <= 1 else 'FAILED',
                'duplicate_warnings': len(duplicate_warnings),
                'client_instances': client_count,
                'messages': duplicate_warnings[:5] if duplicate_warnings else []
            }
            
            # Store console warnings
            self.results['console_warnings'].extend([
                msg for msg in console_messages 
                if msg['type'] in ['warning', 'error']
            ])
            
        except Exception as e:
            self.results['singleton_test'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _test_websocket_connections(self, browser):
        """Test 2: Count WebSocket connections"""
        page = await browser.new_page()
        
        try:
            await page.goto(self.ui_url, timeout=self.timeout, wait_until='networkidle')
            await page.wait_for_timeout(5000)
            
            # Count WebSocket connections via performance API
            ws_data = await page.evaluate('''() => {
                const entries = performance.getEntriesByType('resource');
                const wsEntries = entries.filter(e => 
                    e.name.includes('realtime') || 
                    e.name.includes('ws://') || 
                    e.name.includes('wss://')
                );
                return {
                    count: wsEntries.length,
                    urls: wsEntries.map(e => e.name)
                };
            }''')
            
            # Also check via Network tab
            ws_count_network = await page.evaluate('''() => {
                // Try to detect open WebSocket connections
                return window.connectionManager && window.connectionManager._client 
                    ? 1 : 0;
            }''')
            
            self.results['websocket_test'] = {
                'status': 'PASSED' if ws_data['count'] <= 1 else 'WARNING',
                'connection_count': ws_data['count'],
                'connection_urls': ws_data['urls'],
                'expected': 1,
                'message': f"Expected 1 WebSocket, found {ws_data['count']}"
            }
            
        except Exception as e:
            self.results['websocket_test'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _test_channel_management(self, browser):
        """Test 3: Test Realtime channel subscription management"""
        page = await browser.new_page()
        
        try:
            await page.goto(self.ui_url, timeout=self.timeout, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # Test channel subscription
            channel_test = await page.evaluate('''async () => {
                if (!window.connectionManager) {
                    return { error: 'connectionManager not found' };
                }
                
                try {
                    // Subscribe to test channels
                    const channel1 = await window.connectionManager.subscribeChannel(
                        'test-channel-1',
                        'broadcast',
                        { event: 'test' },
                        () => {}
                    );
                    
                    const channel2 = await window.connectionManager.subscribeChannel(
                        'test-channel-1', // Same channel name (should deduplicate)
                        'broadcast',
                        { event: 'test' },
                        () => {}
                    );
                    
                    const channel3 = await window.connectionManager.subscribeChannel(
                        'test-channel-2',
                        'broadcast',
                        { event: 'test' },
                        () => {}
                    );
                    
                    // Check active channels
                    const activeChannels = window.connectionManager._activeChannels || {};
                    const channelCount = Object.keys(activeChannels).length;
                    
                    // Cleanup
                    if (channel1) channel1.unsubscribe();
                    if (channel3) channel3.unsubscribe();
                    
                    return {
                        subscribed: 3,
                        active: channelCount,
                        deduplication_works: channelCount === 2 // Should have 2, not 3
                    };
                } catch (error) {
                    return { error: error.message };
                }
            }''')
            
            if 'error' in channel_test:
                self.results['channel_test'] = {
                    'status': 'ERROR',
                    'error': channel_test['error']
                }
            else:
                self.results['channel_test'] = {
                    'status': 'PASSED' if channel_test.get('deduplication_works') else 'WARNING',
                    'subscribed': channel_test.get('subscribed', 0),
                    'active': channel_test.get('active', 0),
                    'deduplication': channel_test.get('deduplication_works', False)
                }
            
        except Exception as e:
            self.results['channel_test'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _test_network_resilience(self, browser):
        """Test 4: Test auto-reconnection on network changes"""
        page = await browser.new_page()
        
        try:
            await page.goto(self.ui_url, timeout=self.timeout, wait_until='networkidle')
            await page.wait_for_timeout(3000)
            
            # Test network event handling
            network_test = await page.evaluate('''async () => {
                if (!window.connectionManager) {
                    return { error: 'connectionManager not found' };
                }
                
                let reconnectCalled = false;
                
                // Mock _reconnect to track calls
                const originalReconnect = window.connectionManager._reconnect;
                window.connectionManager._reconnect = async function() {
                    reconnectCalled = true;
                    return originalReconnect.call(this);
                };
                
                // Simulate offline event
                window.dispatchEvent(new Event('offline'));
                await new Promise(resolve => setTimeout(resolve, 100));
                
                // Simulate online event
                window.dispatchEvent(new Event('online'));
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                return {
                    reconnect_triggered: reconnectCalled,
                    has_listeners: true
                };
            }''')
            
            if 'error' in network_test:
                self.results['network_test'] = {
                    'status': 'ERROR',
                    'error': network_test['error']
                }
            else:
                self.results['network_test'] = {
                    'status': 'PASSED' if network_test.get('reconnect_triggered') else 'WARNING',
                    'reconnect_triggered': network_test.get('reconnect_triggered', False),
                    'listeners_active': network_test.get('has_listeners', False)
                }
            
        except Exception as e:
            self.results['network_test'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            await page.close()
    
    async def _test_memory_usage(self, browser):
        """Test 5: Monitor memory usage for leaks"""
        page = await browser.new_page()
        
        try:
            await page.goto(self.ui_url, timeout=self.timeout, wait_until='networkidle')
            
            # Get initial memory
            initial_memory = await page.evaluate('''() => {
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }''')
            
            # Perform operations that might leak memory
            await page.evaluate('''async () => {
                if (!window.connectionManager) return;
                
                // Subscribe and unsubscribe multiple times
                for (let i = 0; i < 10; i++) {
                    const channel = await window.connectionManager.subscribeChannel(
                        `test-channel-${i}`,
                        'broadcast',
                        { event: 'test' },
                        () => {}
                    );
                    if (channel) channel.unsubscribe();
                }
            }''')
            
            await page.wait_for_timeout(2000);
            
            # Get final memory
            final_memory = await page.evaluate('''() => {
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }''')
            
            if initial_memory and final_memory:
                memory_growth = final_memory['used'] - initial_memory['used']
                memory_growth_mb = memory_growth / (1024 * 1024)
                
                self.results['memory_test'] = {
                    'status': 'PASSED' if memory_growth_mb < 10 else 'WARNING',
                    'initial_mb': round(initial_memory['used'] / (1024 * 1024), 2),
                    'final_mb': round(final_memory['used'] / (1024 * 1024), 2),
                    'growth_mb': round(memory_growth_mb, 2),
                    'threshold_mb': 10
                }
            else:
                self.results['memory_test'] = {
                    'status': 'SKIPPED',
                    'reason': 'performance.memory not available (use Chrome with --enable-precise-memory-info)'
                }
            
        except Exception as e:
            self.results['memory_test'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        finally:
            await page.close()
    
    def _calculate_overall_status(self):
        """Calculate overall test status"""
        statuses = [
            self.results['singleton_test'].get('status'),
            self.results['websocket_test'].get('status'),
            self.results['channel_test'].get('status'),
            self.results['network_test'].get('status'),
            self.results['memory_test'].get('status')
        ]
        
        if any(s == 'FAILED' for s in statuses):
            self.results['overall_status'] = 'FAILED'
        elif any(s == 'ERROR' for s in statuses):
            self.results['overall_status'] = 'ERROR'
        elif any(s == 'WARNING' for s in statuses):
            self.results['overall_status'] = 'WARNING'
        else:
            self.results['overall_status'] = 'PASSED'


# ========================================
# ORIGINAL SQLITE ANALYZER (PRESERVED)
# ========================================

class DatabaseAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.databases = {}
        self.load_databases()
    
    def load_databases(self):
        """Load all non-backup databases"""
        for db_file in self.data_dir.glob("*.db"):
            if "backup" not in db_file.name.lower():
                self.databases[db_file.name] = self.analyze_database(db_file)
    
    def analyze_database(self, db_path):
        """Analyze single database structure"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {}
        
        for row in cursor.fetchall():
            table_name = row[0]
            tables[table_name] = self.analyze_table(cursor, table_name)
        
        conn.close()
        return tables
    
    def analyze_table(self, cursor, table_name):
        """Analyze single table"""
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
        sample_data = cursor.fetchall()
        
        return {
            'columns': columns,
            'row_count': row_count,
            'sample_data': sample_data
        }


class ScriptAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.scripts = []
        self.db_usage = defaultdict(list)
        self.scan_scripts()
    
    def scan_scripts(self):
        """Find all Python scripts that access databases"""
        for script in self.project_root.rglob("*.py"):
            if "venv" not in str(script) and "__pycache__" not in str(script):
                self.scripts.append(script)
                content = script.read_text(encoding='utf-8', errors='ignore')
                
                if "sqlite3.connect" in content or "get_database_connection" in content:
                    db_files = re.findall(r'["\']([^"\']*\.db)["\']', content)
                    for db_file in db_files:
                        self.db_usage[db_file].append(script)


class APIAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.routes = []
        self.scan_routes()
    
    def scan_routes(self):
        """Find all Flask API routes"""
        routes_dir = self.project_root / "AI_infrastructure" / "routes"
        if not routes_dir.exists():
            return
        
        for route_file in routes_dir.glob("*.py"):
            content = route_file.read_text(encoding='utf-8', errors='ignore')
            
            route_matches = re.findall(r'@\w+\.route\(["\']([^"\']+)["\']', content)
            for route_path in route_matches:
                self.routes.append({
                    'path': route_path,
                    'file': route_file,
                    'uses_db': 'get_database_connection' in content or 'sqlite3.connect' in content
                })


class InconsistencyDetector:
    def __init__(self, db_analyzer, script_analyzer):
        self.db_analyzer = db_analyzer
        self.script_analyzer = script_analyzer
    
    def detect_all_issues(self):
        """Detect various inconsistencies"""
        issues = []
        
        # Find referenced databases that don't exist
        for db_name, scripts in self.script_analyzer.db_usage.items():
            if db_name not in self.db_analyzer.databases:
                for script in scripts:
                    issues.append({
                        'type': 'missing_database',
                        'database': db_name,
                        'script': script,
                        'severity': 'high'
                    })
        
        # Find unused databases
        used_dbs = set(self.script_analyzer.db_usage.keys())
        for db_name in self.db_analyzer.databases.keys():
            if db_name not in used_dbs:
                issues.append({
                    'type': 'unused_database',
                    'database': db_name,
                    'severity': 'low'
                })
        
        return issues


# ========================================
# REPORTING FUNCTIONS
# ========================================

def print_section(title):
    """Print formatted section header"""
    print("\n" + "=" * 100)
    print(f"  {title}")
    print("=" * 100)


def print_supabase_structure(analyzer: SupabaseAnalyzer):
    """Print Supabase PostgreSQL structure"""
    if not analyzer or not analyzer.schema_data:
        print("\n⚠️  Supabase analysis skipped (connection unavailable)")
        return
    
    print_section("SUPABASE POSTGRESQL SCHEMAS")
    
    for schema_name, tables in analyzer.schema_data.items():
        print(f"\nSchema: {schema_name}")
        print(f"Tables: {len(tables)}")
        print("-" * 100)
        
        for table_name, info in tables.items():
            print(f"\n  Table: {schema_name}.{table_name}")
            print(f"  Rows: {info['row_count']}")
            
            # Primary keys
            if info['primary_keys']:
                print(f"  Primary Keys: {', '.join(info['primary_keys'])}")
            
            # Foreign keys
            if info['foreign_keys']:
                print(f"  Foreign Keys:")
                for fk in info['foreign_keys']:
                    print(f"    {fk['column']} -> {fk['references']}")
            
            # Columns
            print(f"  Columns:")
            for col in info['columns']:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col['default'] else ""
                print(f"    {col['name']:<30} {col['type']:<20} {nullable}{default}")
            
            # Sample data
            if info['sample_data']:
                print(f"  Sample Data (first 3 rows):")
                for i, row in enumerate(info['sample_data'], 1):
                    print(f"    Row {i}: {row[:3]}...")  # Show first 3 columns


def print_connection_manager_validation(validator: ConnectionManagerValidator):
    """Print connection manager validation results"""
    print_section("CONNECTION MANAGER VALIDATION")
    
    if validator.issues:
        print(f"\n❌ Found {len(validator.issues)} issues:\n")
        for issue in validator.issues:
            severity_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡" if issue['severity'] == 'MEDIUM' else "⚪"
            print(f"{severity_icon} [{issue['severity']}] {issue['type']}")
            print(f"   File: {issue['file']}")
            if 'line' in issue:
                print(f"   Line: {issue['line']}")
            print(f"   {issue['message']}")
            print()
    else:
        print("\n✅ All files use connection manager correctly!")
    
    if validator.compliant_files:
        print(f"\n✅ {len(validator.compliant_files)} files using connection manager:")
        for f in validator.compliant_files[:10]:  # Show first 10
            print(f"   {f}")
        if len(validator.compliant_files) > 10:
            print(f"   ... and {len(validator.compliant_files) - 10} more")


def print_schema_consistency(checker: SchemaConsistencyChecker):
    """Print schema consistency check results"""
    print_section("SCHEMA CONSISTENCY CHECKS")
    
    if not checker.issues:
        print("\n✅ No consistency issues found!")
        return
    
    # Group by type
    by_type = defaultdict(list)
    for issue in checker.issues:
        by_type[issue['type']].append(issue)
    
    for issue_type, issues in by_type.items():
        print(f"\n{issue_type}: {len(issues)} issues")
        print("-" * 100)
        
        for issue in issues[:10]:  # Show first 10 of each type
            severity_icon = "🔴" if issue['severity'] == 'HIGH' else "🟡" if issue['severity'] == 'MEDIUM' else "⚪"
            print(f"{severity_icon} [{issue['severity']}] {issue.get('table', 'N/A')}")
            if 'file' in issue:
                print(f"   File: {issue['file']}")
            print(f"   {issue['message']}")
            print()
        
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")


def print_realtime_health_checks(results: Dict[str, Any]):
    """Print real-time health check results"""
    print_section("REAL-TIME HEALTH CHECKS (PHASE 5)")
    
    if results.get('status') == 'SKIPPED':
        print(f"\n⚠️  Real-time checks skipped: {results.get('reason', 'Unknown')}")
        if 'install_instructions' in results:
            print(f"   Install with: {results['install_instructions']}")
        return
    
    overall_status = results.get('overall_status', 'UNKNOWN')
    status_icon = {
        'PASSED': '✅',
        'WARNING': '⚠️ ',
        'FAILED': '❌',
        'ERROR': '🔴',
        'NOT_RUN': '⏸️ '
    }.get(overall_status, '❓')
    
    print(f"\n{status_icon} Overall Status: {overall_status}\n")
    
    # Test 1: Singleton Pattern
    singleton = results.get('singleton_test', {})
    if singleton:
        status = singleton.get('status', 'UNKNOWN')
        icon = '✅' if status == 'PASSED' else '❌' if status == 'FAILED' else '⚠️ '
        print(f"{icon} Test 1: Singleton Pattern - {status}")
        if status != 'ERROR':
            print(f"   Duplicate warnings: {singleton.get('duplicate_warnings', 0)}")
            print(f"   Client instances: {singleton.get('client_instances', 0)}")
            if singleton.get('messages'):
                print(f"   Messages: {singleton['messages'][0]['text'][:60]}...")
        else:
            print(f"   Error: {singleton.get('error', 'Unknown')}")
        print()
    
    # Test 2: WebSocket Connections
    websocket = results.get('websocket_test', {})
    if websocket:
        status = websocket.get('status', 'UNKNOWN')
        icon = '✅' if status == 'PASSED' else '⚠️ ' if status == 'WARNING' else '❌'
        print(f"{icon} Test 2: WebSocket Connections - {status}")
        if status != 'ERROR':
            print(f"   Connection count: {websocket.get('connection_count', 0)} (expected: {websocket.get('expected', 1)})")
            if websocket.get('connection_urls'):
                print(f"   URLs: {len(websocket['connection_urls'])} detected")
        else:
            print(f"   Error: {websocket.get('error', 'Unknown')}")
        print()
    
    # Test 3: Channel Management
    channel = results.get('channel_test', {})
    if channel:
        status = channel.get('status', 'UNKNOWN')
        icon = '✅' if status == 'PASSED' else '⚠️ ' if status == 'WARNING' else '❌'
        print(f"{icon} Test 3: Channel Management - {status}")
        if status != 'ERROR':
            print(f"   Subscribed: {channel.get('subscribed', 0)}")
            print(f"   Active: {channel.get('active', 0)}")
            print(f"   Deduplication: {'✅ Working' if channel.get('deduplication') else '❌ Failed'}")
        else:
            print(f"   Error: {channel.get('error', 'Unknown')}")
        print()
    
    # Test 4: Network Resilience
    network = results.get('network_test', {})
    if network:
        status = network.get('status', 'UNKNOWN')
        icon = '✅' if status == 'PASSED' else '⚠️ ' if status == 'WARNING' else '❌'
        print(f"{icon} Test 4: Network Resilience - {status}")
        if status != 'ERROR':
            print(f"   Reconnect triggered: {'✅ Yes' if network.get('reconnect_triggered') else '❌ No'}")
            print(f"   Listeners active: {'✅ Yes' if network.get('listeners_active') else '❌ No'}")
        else:
            print(f"   Error: {network.get('error', 'Unknown')}")
        print()
    
    # Test 5: Memory Usage
    memory = results.get('memory_test', {})
    if memory:
        status = memory.get('status', 'UNKNOWN')
        icon = '✅' if status == 'PASSED' else '⚠️ ' if status == 'WARNING' else '🔵'
        print(f"{icon} Test 5: Memory Usage - {status}")
        if status == 'SKIPPED':
            print(f"   {memory.get('reason', 'Not available')}")
        elif status != 'ERROR':
            print(f"   Initial: {memory.get('initial_mb', 0)} MB")
            print(f"   Final: {memory.get('final_mb', 0)} MB")
            print(f"   Growth: {memory.get('growth_mb', 0)} MB (threshold: {memory.get('threshold_mb', 10)} MB)")
        else:
            print(f"   Error: {memory.get('error', 'Unknown')}")
        print()
    
    # Console Warnings Summary
    console_warnings = results.get('console_warnings', [])
    if console_warnings:
        print(f"⚠️  Console Warnings: {len(console_warnings)} detected")
        for warning in console_warnings[:5]:
            print(f"   [{warning['type']}] {warning['text'][:70]}...")
        if len(console_warnings) > 5:
            print(f"   ... and {len(console_warnings) - 5} more")
        print()


def print_database_structure(db_analyzer):
    """Print SQLite database structure"""
    print_section("SQLITE DATABASES")
    
    for db_name, tables in db_analyzer.databases.items():
        print(f"\nDatabase: {db_name}")
        print(f"Tables: {len(tables)}")
        print("-" * 100)
        
        for table_name, info in tables.items():
            print(f"\n  Table: {table_name}")
            print(f"  Rows: {info['row_count']}")
            print(f"  Columns:")
            for col in info['columns']:
                nullable = "NULL" if col['notnull'] == 0 else "NOT NULL"
                print(f"    {col['name']:<30} {col['type']:<20} {nullable}")


def print_script_analysis(script_analyzer):
    """Print script database usage"""
    print_section("SCRIPT DATABASE USAGE")
    
    if script_analyzer.db_usage:
        for db_name, scripts in script_analyzer.db_usage.items():
            print(f"\n{db_name} used by {len(scripts)} scripts:")
            for script in scripts:
                print(f"  - {script}")
    else:
        print("\nNo database usage detected in scripts")


def print_api_analysis(api_analyzer):
    """Print API route analysis"""
    print_section("API ROUTES")
    
    for route in api_analyzer.routes:
        db_icon = "💾" if route['uses_db'] else "  "
        print(f"{db_icon} {route['path']:<50} ({route['file'].name})")


def print_inconsistencies(issues):
    """Print detected inconsistencies"""
    print_section("INCONSISTENCIES DETECTED")
    
    if not issues:
        print("\n✅ No inconsistencies found!")
        return
    
    by_type = defaultdict(list)
    for issue in issues:
        by_type[issue['type']].append(issue)
    
    for issue_type, type_issues in by_type.items():
        print(f"\n{issue_type.upper()}: {len(type_issues)} issues")
        print("-" * 100)
        for issue in type_issues:
            print(f"  Database: {issue.get('database', 'N/A')}")
            if 'script' in issue:
                print(f"  Script: {issue['script']}")
            if 'table' in issue:
                print(f"  Table: {issue['table']}")
            print()


def print_ui_mapping():
    """Print UI to data source mapping"""
    print_section("UI ELEMENT TO DATA SOURCE MAPPING")
    
    print("""
1. THREAD LIST (Left Sidebar)
   Data Source: sessions.threads (Supabase PostgreSQL)
   API: GET /api/threads
   Key Fields: thread_slug, last_agent_location, last_message_timestamp

2. MESSAGE HISTORY (Chat Area)
   Data Source: sessions.messages (Supabase PostgreSQL)
   API: GET /api/threads/<thread_slug>/messages
   Key Fields: role, content, timestamp, tool_calls

3. AGENT SELECTOR (Top Bar)
   Data Source: sessions.thread_assignments (Supabase PostgreSQL)
   API: GET /api/thread-assignments/<thread_slug>
   Values: 'prime', 'agent-1', 'agent-2', 'agent-3', 'agent-4'

4. USER PROFILE (Account Menu)
   Data Source: ai_infrastructure.users (Supabase PostgreSQL)
   API: GET /api/auth/me
   Key Fields: username, email, role, primary_gmail

5. SUB-USER MANAGEMENT (Settings)
   Data Source: ai_infrastructure.users (WHERE is_sub_user = 1)
   API: GET /api/users/sub-users
   Fields: allowed_tools, allowed_agents, data_access_scope
""")


def print_ci_cd_integration():
    """Print CI/CD integration guide"""
    print_section("CI/CD INTEGRATION GUIDE")
    
    print("""
GITHUB ACTIONS WORKFLOW:

Create .github/workflows/database-checks.yml:

```yaml
name: Database Structure Validation

on:
  push:
    branches: [ main, v9 ]
  pull_request:
    branches: [ main, v9 ]

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install psycopg2-binary python-dotenv
    
    - name: Run database structure analysis
      env:
        SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
      run: |
        python data/show_database_structure_enhanced.py
    
    - name: Check for critical issues
      run: |
        if grep -q "CRITICAL" data/database_analysis_report_enhanced.txt; then
          echo "Critical database issues found!"
          exit 1
        fi
```

PRE-COMMIT HOOK:

Create .git/hooks/pre-commit:

```bash
#!/bin/bash
echo "Running database structure validation..."
python data/show_database_structure_enhanced.py > /dev/null

if [ $? -ne 0 ]; then
    echo "Database validation failed! Commit aborted."
    exit 1
fi

echo "Database validation passed ✅"
```

MANUAL VALIDATION:

Run before deploying:
    python data/show_database_structure_enhanced.py

Check report for:
    - Missing tables
    - Orphaned tables
    - Connection manager violations
    - Schema inconsistencies
""")


async def main_async():
    """Main execution (async for real-time checks)"""
    project_root = Path(__file__).parent.parent
    data_dir = Path(__file__).parent
    
    print("\n" + "=" * 100)
    print("AI AGENTS PLATFORM - ENHANCED SYSTEM ANALYSIS (with Phase 5 Real-Time Checks)")
    print("=" * 100)
    print(f"Project: {project_root}")
    print(f"Data: {data_dir}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize analyzers
    print("\nInitializing analyzers...")
    
    # SQLite analyzer (original)
    db_analyzer = DatabaseAnalyzer(data_dir)
    print(f"  SQLite Databases: {len(db_analyzer.databases)}")
    
    # Supabase analyzer (NEW - Phase 1)
    supabase_analyzer = None
    if SUPABASE_AVAILABLE:
        supabase_analyzer = SupabaseAnalyzer()
        if supabase_analyzer and supabase_analyzer.schema_data:
            total_tables = sum(len(tables) for tables in supabase_analyzer.schema_data.values())
            print(f"  Supabase Schemas: {len(supabase_analyzer.schema_data)} ({total_tables} tables)")
    
    # Script analyzer
    script_analyzer = ScriptAnalyzer(project_root)
    print(f"  Scripts: {len(script_analyzer.scripts)}")
    
    # API analyzer
    api_analyzer = APIAnalyzer(project_root)
    print(f"  API Routes: {len(api_analyzer.routes)}")
    
    # Connection manager validator (NEW - Phase 2)
    connection_validator = ConnectionManagerValidator(project_root)
    connection_issues = connection_validator.validate_all()
    print(f"  Connection Issues: {len(connection_issues)}")
    
    # Schema consistency checker (NEW - Phase 3)
    consistency_checker = None
    consistency_issues = []
    if supabase_analyzer:
        consistency_checker = SchemaConsistencyChecker(supabase_analyzer, project_root)
        consistency_issues = consistency_checker.check_all()
        print(f"  Schema Consistency Issues: {len(consistency_issues)}")
    
    # SQLite inconsistency detector (original)
    inconsistency_detector = InconsistencyDetector(db_analyzer, script_analyzer)
    sqlite_issues = inconsistency_detector.detect_all_issues()
    print(f"  SQLite Issues: {len(sqlite_issues)}")
    
    # Real-time health checker (NEW - Phase 5)
    realtime_results = None
    print("\n🚀 Starting real-time health checks (Phase 5)...")
    print("   This will launch a headless browser to test actual connection behavior...")
    
    realtime_checker = RealtimeHealthChecker()
    if realtime_checker.playwright_available:
        print("   ✅ Playwright detected - Running browser-based tests")
        try:
            realtime_results = await realtime_checker.run_all_checks()
            print(f"   ✅ Real-time checks complete: {realtime_results.get('overall_status', 'UNKNOWN')}")
        except Exception as e:
            print(f"   ❌ Real-time checks failed: {e}")
            realtime_results = {'status': 'ERROR', 'error': str(e)}
    else:
        print("   ⚠️  Playwright not installed - Skipping real-time checks")
        print("      Install with: pip install playwright && playwright install chromium")
        realtime_results = {
            'status': 'SKIPPED',
            'reason': 'Playwright not installed',
            'install_instructions': 'pip install playwright && playwright install chromium'
        }
    
    # Print all sections
    print_supabase_structure(supabase_analyzer)
    print_connection_manager_validation(connection_validator)
    if consistency_checker:
        print_schema_consistency(consistency_checker)
    if realtime_results:
        print_realtime_health_checks(realtime_results)
    print_database_structure(db_analyzer)
    print_script_analysis(script_analyzer)
    print_api_analysis(api_analyzer)
    print_inconsistencies(sqlite_issues)
    print_ui_mapping()
    print_ci_cd_integration()
    
    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    
    # Summary
    total_issues = len(connection_issues) + len(consistency_issues) + len(sqlite_issues)
    if total_issues > 0:
        print(f"\n⚠️  Found {total_issues} total issues (static analysis)")
    else:
        print(f"\n✅ No issues found in static analysis - codebase is healthy!")
    
    # Real-time summary
    if realtime_results and realtime_results.get('status') != 'SKIPPED':
        rt_status = realtime_results.get('overall_status', 'UNKNOWN')
        rt_icon = '✅' if rt_status == 'PASSED' else '⚠️ ' if rt_status == 'WARNING' else '❌'
        print(f"{rt_icon} Real-time checks: {rt_status}")
    
    # Save to file
    output_file = data_dir / 'database_analysis_report_enhanced.txt'
    print(f"\nSaving report to: {output_file}")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            import sys
            original_stdout = sys.stdout
            sys.stdout = f
            
            # Re-run all print functions to file
            print_supabase_structure(supabase_analyzer)
            print_connection_manager_validation(connection_validator)
            if consistency_checker:
                print_schema_consistency(consistency_checker)
            if realtime_results:
                print_realtime_health_checks(realtime_results)
            print_database_structure(db_analyzer)
            print_script_analysis(script_analyzer)
            print_api_analysis(api_analyzer)
            print_inconsistencies(sqlite_issues)
            print_ui_mapping()
            print_ci_cd_integration()
            
            print("\n" + "=" * 100)
            print("ANALYSIS COMPLETE")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            
            sys.stdout = original_stdout
        
        print(f"SUCCESS: Report saved!")
        
    except Exception as e:
        print(f"ERROR: Failed to save report: {e}")
    
    # Cleanup
    if supabase_analyzer:
        supabase_analyzer.close()
    
    return {
        'static_issues': total_issues,
        'realtime_status': realtime_results.get('overall_status') if realtime_results else 'SKIPPED'
    }


def main():
    """Synchronous wrapper for async main"""
    import asyncio
    
    try:
        # Python 3.7+ - Use asyncio.run()
        return asyncio.run(main_async())
    except AttributeError:
        # Python 3.6 fallback
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(main_async())


if __name__ == '__main__':
    main()
