"""
Tabulator API Connection Test for Stock Management Module
==========================================================

This script tests that API endpoints return data correctly and that
the data structure matches what Tabulator expects.

Usage:
    python tabulator_api_connection_test.py
    
Or from another module:
    from tabulator_api_connection_test import TabulatorAPITester
    tester = TabulatorAPITester(base_url='http://localhost:5001')
    tester.run_all_tests()

Author: InHouse Print
Date: November 8, 2025
Version: 1.0.0
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys


class TabulatorAPITester:
    """
    Test API endpoints to verify they return data compatible with Tabulator
    """
    
    def __init__(self, base_url: str = 'http://localhost:5001'):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log(self, message: str, level: str = 'INFO'):
        """Log a message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        icon = {
            'INFO': '🔵',
            'SUCCESS': '✅',
            'ERROR': '❌',
            'WARNING': '⚠️'
        }.get(level, '📝')
        print(f"[{timestamp}] {icon} {message}")
        
    def test_endpoint(
        self,
        name: str,
        endpoint: str,
        method: str = 'GET',
        expected_keys: List[str] = None,
        data_key: str = 'data',
        post_data: Dict = None
    ) -> Dict[str, Any]:
        """
        Test a single API endpoint
        
        Args:
            name: Test name
            endpoint: API endpoint path
            method: HTTP method (GET or POST)
            expected_keys: Keys expected in response
            data_key: Key containing the data array
            post_data: Data to send with POST requests
            
        Returns:
            Test result dictionary
        """
        self.log(f"Testing {name}...", 'INFO')
        
        result = {
            'name': name,
            'endpoint': endpoint,
            'method': method,
            'passed': False,
            'error': None,
            'response_time': 0,
            'status_code': 0,
            'data_count': 0,
            'has_columns': False
        }
        
        try:
            # Make request
            start_time = datetime.now()
            
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elif method == 'POST':
                response = requests.post(
                    f"{self.base_url}{endpoint}",
                    json=post_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = (datetime.now() - start_time).total_seconds()
            result['response_time'] = response_time
            result['status_code'] = response.status_code
            
            # Check status code
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text[:100]}")
            
            # Parse JSON
            data = response.json()
            
            # Check expected keys
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    raise Exception(f"Missing keys: {missing_keys}")
            
            # Check data array
            if data_key in data:
                data_array = data[data_key]
                result['data_count'] = len(data_array) if isinstance(data_array, list) else 0
                
                # Check if first item has structure (for Tabulator compatibility)
                if isinstance(data_array, list) and len(data_array) > 0:
                    first_item = data_array[0]
                    if isinstance(first_item, dict):
                        result['sample_fields'] = list(first_item.keys())[:5]
            
            # Check for columns (dynamic Tabulator cases)
            if 'columns' in data:
                result['has_columns'] = True
                result['column_count'] = len(data['columns'])
            
            # Success
            result['passed'] = True
            self.passed += 1
            self.log(
                f"{name}: {result['data_count']} records in {response_time:.2f}s",
                'SUCCESS'
            )
            
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection refused - Backend not running'
            self.failed += 1
            self.log(f"{name}: Connection refused", 'ERROR')
            
        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout (>10s)'
            self.failed += 1
            self.log(f"{name}: Timeout", 'ERROR')
            
        except Exception as e:
            result['error'] = str(e)
            self.failed += 1
            self.log(f"{name}: {str(e)}", 'ERROR')
        
        self.results.append(result)
        return result
    
    def test_tabulator_compatibility(self, result: Dict) -> bool:
        """
        Check if API response is compatible with Tabulator
        
        Tabulator needs:
        - Array of objects
        - Each object has consistent keys
        - Data can be empty but must be an array
        """
        if not result['passed']:
            return False
        
        # Must have data
        if result['data_count'] == 0 and not result['has_columns']:
            self.log(f"  ⚠️  {result['name']}: No data (may be expected)", 'WARNING')
            return True  # Empty data is OK
        
        # Check structure
        if 'sample_fields' in result:
            self.log(f"  ✅ {result['name']}: Compatible structure", 'SUCCESS')
            return True
        
        if result['has_columns']:
            self.log(f"  ✅ {result['name']}: Dynamic columns detected", 'SUCCESS')
            return True
        
        return False
    
    def run_all_tests(self) -> bool:
        """
        Run all Stock Management API tests
        
        Returns:
            True if all tests passed
        """
        print("\n" + "="*70)
        print("TABULATOR API CONNECTION TEST".center(70))
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
        print(f"Base URL: {self.base_url}".center(70))
        print("="*70 + "\n")
        
        # Test 1: Health Check
        self.test_endpoint(
            name='Health Check',
            endpoint='/health',
            expected_keys=['app', 'providers']
        )
        
        # Test 2: Usage Analytics
        self.test_endpoint(
            name='Usage Analytics',
            endpoint='/api/stock-management/usage-analytics?days=90',
            expected_keys=['data', 'database', 'status'],
            data_key='data'
        )
        
        # Test 3: Reorder Dashboard
        self.test_endpoint(
            name='Reorder Dashboard',
            endpoint='/api/stock-management/reorder-dashboard',
            expected_keys=['data', 'database', 'status'],
            data_key='data'
        )
        
        # Test 4: Profit Analysis
        self.test_endpoint(
            name='Profit Analysis',
            endpoint='/api/stock-management/profit-analysis?days=90',
            expected_keys=['data', 'database', 'status'],
            data_key='data'
        )
        
        # Test 5: AI Analytics
        self.test_endpoint(
            name='AI Analytics',
            endpoint='/api/stock/ai-analytics',
            expected_keys=['status', 'queries'],
            data_key='queries'
        )
        
        # Test 6: SQL Query (POST)
        self.test_endpoint(
            name='SQL Query',
            endpoint='/api/stock-management/sql-query',
            method='POST',
            expected_keys=['status', 'columns', 'data'],
            data_key='data',
            post_data={'query': 'SELECT * FROM unified_stocks LIMIT 5'}
        )
        
        # Print summary
        self.print_summary()
        
        # Check Tabulator compatibility
        print("\n" + "="*70)
        print("TABULATOR COMPATIBILITY CHECK".center(70))
        print("="*70 + "\n")
        
        for result in self.results:
            self.test_tabulator_compatibility(result)
        
        return self.failed == 0
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print("TEST SUMMARY".center(70))
        print("="*70)
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Pass Rate: {pass_rate:.1f}%\n")
        
        # Detailed results table
        print(f"{'Test':<25} {'Status':<10} {'Records':<10} {'Time':<10}")
        print("-"*70)
        
        for result in self.results:
            status = '✅ PASS' if result['passed'] else '❌ FAIL'
            records = str(result['data_count']) if result['data_count'] > 0 else '-'
            time = f"{result['response_time']:.2f}s" if result['response_time'] > 0 else '-'
            
            print(f"{result['name']:<25} {status:<10} {records:<10} {time:<10}")
            
            if not result['passed'] and result['error']:
                print(f"  └─ Error: {result['error']}")
        
        print("\n" + "="*70)
        
        if self.failed == 0:
            print("\n🎉 All tests passed! APIs are ready for Tabulator.\n")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Check backend and database.\n")
    
    def export_json(self, filename: str = 'test_results.json'):
        """Export test results to JSON file"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_tests': len(self.results),
            'passed': self.passed,
            'failed': self.failed,
            'pass_rate': (self.passed / len(self.results) * 100) if self.results else 0,
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        self.log(f"Results exported to {filename}", 'SUCCESS')


def main():
    """Main entry point"""
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5001'
    
    # Create tester and run tests
    tester = TabulatorAPITester(base_url=base_url)
    success = tester.run_all_tests()
    
    # Export results
    tester.export_json('tabulator_api_test_results.json')
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
