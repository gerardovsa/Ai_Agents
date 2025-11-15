#!/usr/bin/env python3
"""
Render Deployment Readiness Checker
===================================
Verifies all requirements for Render deployment with Supabase database

Usage:
    python check_render_deployment.py
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if required file exists"""
    path = Path(filepath)
    if path.exists():
        return True, f"{GREEN}✓{RESET} Found: {filepath}"
    else:
        return False, f"{RED}✗{RESET} Missing: {filepath}"

def check_file_content(filepath: str, search_term: str) -> Tuple[bool, str]:
    """Check if file contains specific content"""
    path = Path(filepath)
    if not path.exists():
        return False, f"{RED}✗{RESET} File not found: {filepath}"
    
    try:
        content = path.read_text(encoding='utf-8')
        if search_term in content:
            return True, f"{GREEN}✓{RESET} Found '{search_term}' in {filepath}"
        else:
            return False, f"{YELLOW}⚠{RESET} Missing '{search_term}' in {filepath}"
    except Exception as e:
        return False, f"{RED}✗{RESET} Error reading {filepath}: {e}"

def check_env_var_example(var_name: str) -> Tuple[bool, str]:
    """Check if environment variable is documented in render.yaml"""
    result = check_file_content('render.yaml', var_name)
    if result[0]:
        return True, f"{GREEN}✓{RESET} {var_name} documented in render.yaml"
    else:
        return False, f"{RED}✗{RESET} {var_name} missing from render.yaml"

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Render Deployment Readiness Check{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    checks = []
    issues = []
    warnings = []
    
    # ==================== CORE FILES ====================
    print(f"{BLUE}[1] Core Deployment Files{RESET}")
    print("-" * 60)
    
    core_files = [
        'render.yaml',
        'Dockerfile',
        'startup.sh',
        'requirements.txt',
        'AI_infrastructure/flask_app.py',
        'AI_infrastructure/shared/database_utils.py',
    ]
    
    for file in core_files:
        success, msg = check_file_exists(file)
        checks.append((success, msg))
        if not success:
            issues.append(msg)
        print(msg)
    
    print()
    
    # ==================== SUPABASE CONFIGURATION ====================
    print(f"{BLUE}[2] Supabase Configuration{RESET}")
    print("-" * 60)
    
    # Check database_utils.py has Supabase support
    success, msg = check_file_content(
        'AI_infrastructure/shared/database_utils.py',
        'USE_SUPABASE'
    )
    checks.append((success, msg))
    if not success:
        issues.append("database_utils.py missing USE_SUPABASE support")
    print(msg)
    
    success, msg = check_file_content(
        'AI_infrastructure/shared/database_utils.py',
        'psycopg2'
    )
    checks.append((success, msg))
    if not success:
        issues.append("database_utils.py missing psycopg2 import")
    print(msg)
    
    # Check requirements.txt has psycopg2
    success, msg = check_file_content('requirements.txt', 'psycopg2-binary')
    checks.append((success, msg))
    if not success:
        issues.append("requirements.txt missing psycopg2-binary")
    print(msg)
    
    print()
    
    # ==================== ENVIRONMENT VARIABLES ====================
    print(f"{BLUE}[3] Environment Variables (render.yaml){RESET}")
    print("-" * 60)
    
    env_vars = [
        'USE_SUPABASE',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY',
        'SUPABASE_DB_URL',
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'DEEPSEEK_API_KEY_1',
        'MICROSOFT_CLIENT_ID',
        'MICROSOFT_CLIENT_SECRET',
        'GOOGLE_OAUTH_CLIENT_ID',
        'GOOGLE_OAUTH_CLIENT_SECRET',
        'SECRET_KEY',
    ]
    
    for var in env_vars:
        success, msg = check_env_var_example(var)
        checks.append((success, msg))
        if not success:
            issues.append(f"render.yaml missing {var}")
        print(msg)
    
    print()
    
    # ==================== RENDER.YAML CONFIGURATION ====================
    print(f"{BLUE}[4] Render.yaml Configuration{RESET}")
    print("-" * 60)
    
    # Check USE_SUPABASE is set to true
    success, msg = check_file_content('render.yaml', 'USE_SUPABASE')
    if success:
        success2, msg2 = check_file_content('render.yaml', 'value: "true"')
        if success2:
            print(f"{GREEN}✓{RESET} USE_SUPABASE enabled in render.yaml")
            checks.append((True, "USE_SUPABASE enabled"))
        else:
            print(f"{YELLOW}⚠{RESET} USE_SUPABASE found but may not be set to 'true'")
            warnings.append("Verify USE_SUPABASE is set to 'true' in render.yaml")
            checks.append((False, "USE_SUPABASE not set to true"))
    else:
        print(msg)
        issues.append("USE_SUPABASE not found in render.yaml")
        checks.append((False, msg))
    
    # Check disk configuration
    success, msg = check_file_content('render.yaml', 'disk:')
    checks.append((success, msg))
    if success:
        print(f"{GREEN}✓{RESET} Persistent disk configured")
    else:
        print(f"{RED}✗{RESET} Persistent disk not configured")
        issues.append("No persistent disk in render.yaml")
    
    # Check region is Singapore
    success, msg = check_file_content('render.yaml', 'region: singapore')
    checks.append((success, msg))
    if success:
        print(f"{GREEN}✓{RESET} Region set to Singapore (optimal for Australia)")
    else:
        print(f"{YELLOW}⚠{RESET} Region not set to Singapore")
        warnings.append("Consider setting region to Singapore for Australia")
    
    print()
    
    # ==================== DOCKERFILE ====================
    print(f"{BLUE}[5] Dockerfile Configuration{RESET}")
    print("-" * 60)
    
    dockerfile_checks = [
        ('FROM python:3.11-slim', 'Python 3.11 base image'),
        ('libpq-dev', 'PostgreSQL driver support (libpq-dev)'),
        ('HEALTHCHECK', 'Health check endpoint'),
        ('./startup.sh', 'Startup script'),
    ]
    
    for search, description in dockerfile_checks:
        success, msg = check_file_content('Dockerfile', search)
        checks.append((success, f"{description}: {msg}"))
        if success:
            print(f"{GREEN}✓{RESET} {description}")
        else:
            print(f"{RED}✗{RESET} {description}")
            issues.append(f"Dockerfile missing: {description}")
    
    print()
    
    # ==================== STARTUP SCRIPT ====================
    print(f"{BLUE}[6] Startup Script{RESET}")
    print("-" * 60)
    
    startup_checks = [
        ('gunicorn', 'Gunicorn production server'),
        ('geventwebsocket', 'WebSocket support'),
        ('/data', 'Persistent disk mount'),
    ]
    
    for search, description in startup_checks:
        success, msg = check_file_content('startup.sh', search)
        checks.append((success, f"{description}: {msg}"))
        if success:
            print(f"{GREEN}✓{RESET} {description}")
        else:
            print(f"{RED}✗{RESET} {description}")
            issues.append(f"startup.sh missing: {description}")
    
    print()
    
    # ==================== FLASK APP ====================
    print(f"{BLUE}[7] Flask Application{RESET}")
    print("-" * 60)
    
    # Check Flask app uses database_utils
    success, msg = check_file_content(
        'AI_infrastructure/flask_app.py',
        'from shared.database_utils import get_database_connection'
    )
    checks.append((success, msg))
    if success:
        print(f"{GREEN}✓{RESET} Flask app uses centralized database utilities")
    else:
        print(f"{RED}✗{RESET} Flask app not using database_utils")
        issues.append("Flask app must import from shared.database_utils")
    
    print()
    
    # ==================== SUMMARY ====================
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    total_checks = len(checks)
    passed_checks = sum(1 for success, _ in checks if success)
    failed_checks = total_checks - passed_checks
    
    print(f"Total Checks: {total_checks}")
    print(f"{GREEN}Passed: {passed_checks}{RESET}")
    if failed_checks > 0:
        print(f"{RED}Failed: {failed_checks}{RESET}")
    else:
        print(f"Failed: {failed_checks}")
    
    if warnings:
        print(f"{YELLOW}Warnings: {len(warnings)}{RESET}")
    
    print()
    
    if issues:
        print(f"{RED}Issues Found:{RESET}")
        for issue in issues:
            print(f"  • {issue}")
        print()
    
    if warnings:
        print(f"{YELLOW}Warnings:{RESET}")
        for warning in warnings:
            print(f"  • {warning}")
        print()
    
    # ==================== DEPLOYMENT READY ====================
    if failed_checks == 0:
        print(f"{GREEN}✓ DEPLOYMENT READY!{RESET}")
        print(f"\n{BLUE}Next Steps:{RESET}")
        print(f"1. Push to GitHub branch 'v6'")
        print(f"2. Add environment variables in Render dashboard:")
        print(f"   - SUPABASE_URL")
        print(f"   - SUPABASE_SERVICE_KEY")
        print(f"   - SUPABASE_DB_URL (connection pooler, port 6543)")
        print(f"   - ANTHROPIC_API_KEY")
        print(f"   - OPENAI_API_KEY")
        print(f"   - SECRET_KEY")
        print(f"3. Deploy to Render")
        print(f"4. Test: curl https://your-app.onrender.com/health")
        print(f"\n{GREEN}Supabase will be automatically used in production!{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ DEPLOYMENT NOT READY{RESET}")
        print(f"Fix the issues above before deploying.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
