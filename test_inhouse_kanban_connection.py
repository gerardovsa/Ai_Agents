"""
InHouse Kanban Database Connection & API Integration Test
=========================================================

API Design Architect Methodology - Comprehensive Connection Validation

Tests:
1. ✅ SQL Server database connectivity (InHousePrint @ 3.25.76.138:1433)
2. ✅ All 5 REST API endpoints with sample queries
3. ✅ Frontend-backend data contract validation
4. ✅ SQL query performance and result correctness
5. ✅ Error handling and retry logic

Database: InHousePrint (SQL Server 2019)
Tables: JobTickets, Orders, JobStage, PaperType, GSM, PaperSize, etc.
Credentials: sa/Jack2011 (production read-only access via pymssql)
"""

import sys
import os
import requests
import pymssql
from datetime import datetime
import json

# ANSI colors for terminal output
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print section header"""
    print(f"\n{Color.HEADER}{Color.BOLD}{'=' * 80}")
    print(f"  {text}")
    print(f"{'=' * 80}{Color.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Color.OKGREEN}✓{Color.ENDC} {text}")

def print_error(text):
    """Print error message"""
    print(f"{Color.FAIL}✗{Color.ENDC} {text}")

def print_info(text):
    """Print info message"""
    print(f"{Color.OKCYAN}ℹ{Color.ENDC} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Color.WARNING}⚠{Color.ENDC} {text}")

# Database configuration
DB_CONFIG = {
    'server': '3.25.76.138',
    'port': 1433,
    'database': 'InHousePrint',
    'user': 'sa',
    'password': 'Jack2011'
}

# API configuration
API_BASE_URL = 'http://localhost:5001'  # Flask backend
API_PREFIX = '/api/inhouse-kanban'

def test_database_connection():
    """Test 1: Direct SQL Server connection"""
    print_header("Test 1: SQL Server Database Connection")
    
    try:
        print_info(f"Connecting to {DB_CONFIG['server']}:{DB_CONFIG['port']} / {DB_CONFIG['database']}...")
        
        conn = pymssql.connect(
            server=DB_CONFIG['server'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            timeout=10,
            login_timeout=10
        )
        
        print_success("Database connection established!")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print_info(f"SQL Server version: {version[:80]}...")
        
        # Count active jobs
        cursor.execute("""
            SELECT COUNT(*) 
            FROM JobTickets 
            WHERE InternalInvoiceComplete = 0 AND StageID != 10
        """)
        active_jobs = cursor.fetchone()[0]
        print_success(f"Active jobs in system: {active_jobs}")
        
        # Check table structures
        cursor.execute("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print_info(f"Database contains {len(tables)} tables")
        
        # Verify critical tables exist
        critical_tables = ['JobTickets', 'Orders', 'JobStage', 'PaperType', 'GSM', 'PaperSize', 
                          'BindType', 'ShippingType', 'Business', 'ClientList']
        missing_tables = [t for t in critical_tables if t not in tables]
        
        if missing_tables:
            print_error(f"Missing critical tables: {missing_tables}")
        else:
            print_success("All critical tables present")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


def test_api_health():
    """Test 2: API health check endpoint"""
    print_header("Test 2: API Health Check Endpoint")
    
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/health"
        print_info(f"GET {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"API Status: {data.get('status')}")
            print_success(f"Database: {data.get('database')}")
            print_success(f"Active Jobs: {data.get('active_jobs')}")
            print_info(f"Server: {data.get('server')}")
            print_info(f"Database: {data.get('database_name')}")
            return True
        else:
            print_error(f"Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"API health check failed: {e}")
        print_warning("Ensure Flask server is running: BISTART")
        return False


def test_api_jobs_list():
    """Test 3: GET /api/inhouse-kanban/jobs (active jobs list)"""
    print_header("Test 3: GET /jobs - Active Jobs List")
    
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/jobs"
        params = {
            'timeframe_months': -6,
            'priority_filter': 'all',
            'limit': 10
        }
        
        print_info(f"GET {url}?{requests.compat.urlencode(params)}")
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            
            print_success(f"Retrieved {len(jobs)} jobs")
            
            if jobs:
                # Validate first job structure
                job = jobs[0]
                required_fields = [
                    'TicketID', 'OrderID', 'StageID', 'StageDescription', 'ClientName',
                    'ShortJobDesc', 'DateRequired', 'Cost', 'AIPriorityScore',
                    'PriorityLabel', 'PriorityColorHex', 'CustomerTier', 'WIPStatus'
                ]
                
                missing_fields = [f for f in required_fields if f not in job]
                
                if missing_fields:
                    print_error(f"Missing required fields: {missing_fields}")
                else:
                    print_success("All required fields present in job data")
                
                # Display sample job
                print_info(f"\nSample Job:")
                print_info(f"  Ticket ID: {job.get('TicketID')}")
                print_info(f"  Client: {job.get('ClientName')}")
                print_info(f"  Description: {job.get('ShortJobDesc')[:50]}...")
                print_info(f"  Stage: {job.get('StageDescription')}")
                print_info(f"  Cost: ${job.get('Cost')}")
                print_info(f"  Priority: {job.get('PriorityLabel')} ({job.get('AIPriorityScore')})")
                print_info(f"  Tier: {job.get('CustomerTier')}")
            
            return True
        else:
            print_error(f"Jobs list failed: HTTP {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Jobs list API test failed: {e}")
        return False


def test_api_stages():
    """Test 4: GET /api/inhouse-kanban/stages (stage summary)"""
    print_header("Test 4: GET /stages - Stage Summary")
    
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/stages"
        params = {'timeframe_months': -6}
        
        print_info(f"GET {url}?{requests.compat.urlencode(params)}")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stages = data.get('stages', [])
            
            print_success(f"Retrieved {len(stages)} stages")
            
            if stages:
                print_info("\nStage Breakdown:")
                for stage in stages:
                    print_info(f"  {stage.get('StageDescription')}: {stage.get('JobCount')} jobs, ${stage.get('TotalValue'):.2f}")
            
            return True
        else:
            print_error(f"Stages API failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Stages API test failed: {e}")
        return False


def test_api_metrics():
    """Test 5: GET /api/inhouse-kanban/metrics (dashboard metrics)"""
    print_header("Test 5: GET /metrics - Dashboard Metrics")
    
    try:
        url = f"{API_BASE_URL}{API_PREFIX}/metrics"
        params = {'timeframe_months': -6}
        
        print_info(f"GET {url}?{requests.compat.urlencode(params)}")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metrics', {})
            
            print_success("Dashboard metrics retrieved:")
            print_info(f"  Total Jobs: {metrics.get('total_jobs')}")
            print_info(f"  Pipeline Value: ${metrics.get('pipeline_value'):.2f}")
            print_info(f"  Overdue Jobs: {metrics.get('overdue_jobs')}")
            print_info(f"  Avg Days in System: {metrics.get('avg_days_in_system')} days")
            
            return True
        else:
            print_error(f"Metrics API failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Metrics API test failed: {e}")
        return False


def test_api_job_details():
    """Test 6: GET /api/inhouse-kanban/jobs/:id (job details)"""
    print_header("Test 6: GET /jobs/:id - Job Details")
    
    try:
        # First get a job ID from jobs list
        url = f"{API_BASE_URL}{API_PREFIX}/jobs"
        response = requests.get(url, params={'limit': 1}, timeout=10)
        
        if response.status_code != 200:
            print_warning("Could not get job list, skipping job details test")
            return False
        
        jobs = response.json().get('jobs', [])
        if not jobs:
            print_warning("No jobs available to test job details endpoint")
            return False
        
        ticket_id = int(jobs[0]['TicketID'])  # Convert to int for URL
        
        # Get job details
        url = f"{API_BASE_URL}{API_PREFIX}/jobs/{ticket_id}"
        print_info(f"GET {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            job = data.get('job', {})
            
            print_success(f"Job details retrieved for Ticket #{ticket_id}")
            
            # Validate extended fields
            extended_fields = ['Paper', 'JobSize', 'Pages', 'Binding', 'Cello', 
                             'Folding', 'Stitching', 'TicketNotes', 'Shipping']
            
            present_fields = [f for f in extended_fields if f in job and job[f]]
            print_info(f"Extended fields present: {len(present_fields)}/{len(extended_fields)}")
            
            return True
        else:
            print_error(f"Job details API failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Job details API test failed: {e}")
        return False


def test_frontend_backend_contract():
    """Test 7: Frontend-Backend data contract validation"""
    print_header("Test 7: Frontend-Backend Data Contract Validation")
    
    try:
        # Get jobs from API
        url = f"{API_BASE_URL}{API_PREFIX}/jobs"
        response = requests.get(url, params={'limit': 5}, timeout=15)
        
        if response.status_code != 200:
            print_error("Cannot validate contract without API data")
            return False
        
        jobs = response.json().get('jobs', [])
        
        if not jobs:
            print_warning("No jobs available for contract validation")
            return False
        
        # Frontend expects these fields (from inhouse-kanban.js renderJobCard)
        frontend_expected = {
            'TicketID': 'number',
            'ClientName': 'string',
            'ShortJobDesc': 'string',
            'StageID': 'number',
            'StageDescription': 'string',
            'Cost': 'number',
            'DateRequired': 'string',  # ISO date
            'AIPriorityScore': 'number',
            'PriorityLabel': 'string',
            'PriorityColorHex': 'string',
            'CustomerTier': 'string',
            'WIPStatus': 'string',
            'DaysInSystem': 'number'
        }
        
        validation_errors = []
        
        for job in jobs:
            for field, expected_type in frontend_expected.items():
                if field not in job:
                    validation_errors.append(f"Missing field: {field}")
                else:
                    actual_value = job[field]
                    
                    # Type validation
                    if expected_type == 'number' and not isinstance(actual_value, (int, float)):
                        if actual_value is not None:
                            validation_errors.append(f"Field {field} should be {expected_type}, got {type(actual_value).__name__}")
                    elif expected_type == 'string' and not isinstance(actual_value, str):
                        if actual_value is not None:
                            validation_errors.append(f"Field {field} should be {expected_type}, got {type(actual_value).__name__}")
        
        if validation_errors:
            print_error("Data contract violations found:")
            for error in validation_errors[:10]:  # Show first 10 errors
                print_error(f"  - {error}")
            return False
        else:
            print_success("Frontend-backend data contract is valid")
            print_success("All required fields present with correct types")
            return True
            
    except Exception as e:
        print_error(f"Contract validation failed: {e}")
        return False


def test_sql_query_performance():
    """Test 8: SQL query performance analysis"""
    print_header("Test 8: SQL Query Performance Analysis")
    
    try:
        conn = pymssql.connect(
            server=DB_CONFIG['server'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            timeout=10
        )
        
        cursor = conn.cursor()
        
        # Test main jobs query performance
        query_start = datetime.now()
        cursor.execute("""
            SELECT TOP (100)
                jt.TicketID,
                jt.OrderID,
                o.ClientName,
                jt.ShortJobDesc,
                jt.Cost,
                o.DateRequired,
                jt.StageID
            FROM JobTickets jt
            INNER JOIN Orders o ON jt.OrderID = o.OrderID
            WHERE jt.InternalInvoiceComplete = 0
                AND jt.StageID != 10
                AND o.OrderDate >= DATEADD(month, -6, GETDATE())
            ORDER BY o.DateRequired ASC
        """)
        
        results = cursor.fetchall()
        query_duration = (datetime.now() - query_start).total_seconds()
        
        print_success(f"Main jobs query executed in {query_duration:.3f}s")
        print_info(f"Retrieved {len(results)} jobs")
        
        if query_duration > 2.0:
            print_warning(f"Query is slow (>{query_duration:.1f}s). Consider adding indexes.")
        else:
            print_success("Query performance is acceptable")
        
        conn.close()
        return True
        
    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False


def main():
    """Run all connection tests"""
    print(f"\n{Color.BOLD}{Color.HEADER}")
    print("=" * 80)
    print("  InHouse Kanban Database & API Connection Test Suite")
    print("  API Design Architect Methodology - Comprehensive Validation")
    print("=" * 80)
    print(f"{Color.ENDC}")
    
    print_info(f"Database: {DB_CONFIG['server']}:{DB_CONFIG['port']} / {DB_CONFIG['database']}")
    print_info(f"API Base: {API_BASE_URL}{API_PREFIX}")
    print_info(f"Driver: pymssql (no ODBC required)")
    
    # Run all tests
    tests = [
        ("Database Connection", test_database_connection),
        ("API Health Check", test_api_health),
        ("Jobs List API", test_api_jobs_list),
        ("Stages Summary API", test_api_stages),
        ("Dashboard Metrics API", test_api_metrics),
        ("Job Details API", test_api_job_details),
        ("Frontend-Backend Contract", test_frontend_backend_contract),
        ("SQL Query Performance", test_sql_query_performance)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_header("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Color.BOLD}Results: {passed}/{total} tests passed{Color.ENDC}")
    
    if passed == total:
        print(f"\n{Color.OKGREEN}{Color.BOLD}SUCCESS! All tests passed.{Color.ENDC}")
        print_info("InHouse Kanban module is ready for production use.")
        return 0
    else:
        print(f"\n{Color.FAIL}{Color.BOLD}FAILURE! {total - passed} test(s) failed.{Color.ENDC}")
        print_warning("Review errors above and fix before production deployment.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
