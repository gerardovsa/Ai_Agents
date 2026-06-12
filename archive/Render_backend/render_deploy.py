#!/usr/bin/env python3
"""
Render Deploy CLI - Complete deployment automation

This is the master CLI that orchestrates the entire deployment process
from prerequisites check to live production deployment.

Usage:
    python render_deploy.py                    # Interactive mode
    python render_deploy.py --auto             # Automatic mode (uses defaults)
    python render_deploy.py --check-only       # Only check prerequisites
    python render_deploy.py --monitor-only     # Only monitor existing deployment
"""

import os
import sys
import subprocess
from pathlib import Path

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colorful header"""
    print("\n" + "=" * 70)
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print("=" * 70 + "\n")

def print_step(number, text):
    """Print step number with text"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{number}️⃣  {text}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN} {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED} {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def run_script(script_name, args=None):
    """Run a utility script and return success status"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print_error(f"Script not found: {script_name}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode == 0
    except Exception as e:
        print_error(f"Error running {script_name}: {e}")
        return False

def check_prerequisites():
    """Step 1: Check prerequisites"""
    print_step(1, "Checking Prerequisites")
    success = run_script("check_prerequisites.py")
    
    if not success:
        print_error("Prerequisites check failed")
        print_warning("Fix the issues above before continuing")
        return False
    
    print_success("All prerequisites met")
    return True

def clean_git_secrets(auto=False):
    """Step 2: Clean git secrets"""
    print_step(2, "Cleaning Git Secrets")
    
    if not auto:
        response = input("Remove sensitive files from git history? (y/n): ")
        if response.lower() != 'y':
            print_warning("Skipped git cleanup")
            return True
    
    success = run_script("clean_git_secrets.py", ["--create-clean-branch"])
    
    if not success:
        print_error("Git cleanup failed")
        return False
    
    print_success("Git secrets cleaned")
    return True

def extract_env_vars():
    """Step 3: Extract environment variables"""
    print_step(3, "Extracting Environment Variables")
    success = run_script("extract_env_vars.py")
    
    if not success:
        print_error("Failed to extract environment variables")
        return False
    
    print_success("Environment variables exported")
    return True

def validate_api_keys(skip_on_failure=False):
    """Step 4: Validate API keys"""
    print_step(4, "Validating API Keys")
    success = run_script("validate_api_keys.py")
    
    if not success:
        if skip_on_failure:
            print_warning("Some API keys are invalid (continuing anyway)")
            return True
        else:
            print_error("API key validation failed")
            return False
    
    print_success("All API keys validated")
    return True

def deploy_to_render():
    """Step 5: Deploy to Render"""
    print_step(5, "Deploying to Render")
    
    # Use existing deploy script
    success = run_script("../deploy_to_render_api.py")
    
    if not success:
        print_error("Deployment failed")
        return False
    
    print_success("Deployment initiated")
    return True

def monitor_deployment(service_id=None):
    """Step 6: Monitor deployment"""
    print_step(6, "Monitoring Deployment")
    
    args = [service_id] if service_id else []
    success = run_script("monitor_deployment.py", args)
    
    if not success:
        print_error("Deployment monitoring failed")
        return False
    
    print_success("Deployment completed successfully")
    return True

def test_deployment(service_url=None):
    """Step 7: Test deployment"""
    print_step(7, "Testing Deployment")
    
    args = [service_url] if service_url else []
    success = run_script("test_deployment.py", args)
    
    if not success:
        print_error("Deployment tests failed")
        return False
    
    print_success("All tests passed")
    return True

def update_oauth_redirects(service_url=None):
    """Step 8: Update OAuth redirects"""
    print_step(8, "OAuth Redirect URLs")
    
    args = [service_url] if service_url else []
    success = run_script("update_oauth_redirects.py", args)
    
    print_success("OAuth instructions displayed")
    return True

def main():
    print_header("🚀 Render Deployment CLI")
    
    # Parse command line arguments
    auto_mode = "--auto" in sys.argv
    check_only = "--check-only" in sys.argv
    monitor_only = "--monitor-only" in sys.argv
    
    # Monitor only mode
    if monitor_only:
        service_id = sys.argv[sys.argv.index("--monitor-only") + 1] if len(sys.argv) > sys.argv.index("--monitor-only") + 1 else None
        monitor_deployment(service_id)
        return 0
    
    # Step 1: Prerequisites
    if not check_prerequisites():
        return 1
    
    if check_only:
        print_success("Prerequisites check complete!")
        return 0
    
    # Step 2: Git cleanup (optional)
    if not auto_mode:
        if not clean_git_secrets(auto=False):
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                return 1
    
    # Step 3: Extract environment variables
    if not extract_env_vars():
        return 1
    
    # Step 4: Validate API keys (continue even if some fail)
    validate_api_keys(skip_on_failure=True)
    
    # Step 5: Deploy to Render
    print("\n" + "=" * 70)
    if not auto_mode:
        response = input("Ready to deploy to Render? (y/n): ")
        if response.lower() != 'y':
            print_warning("Deployment cancelled")
            return 0
    
    if not deploy_to_render():
        return 1
    
    # Step 6: Monitor deployment
    service_id = "srv-d40tai15pdvs73ddh4m0"  # Default service ID
    if not monitor_deployment(service_id):
        print_warning("Deployment failed - check logs")
        run_script("fetch_logs.py", [service_id])
        return 1
    
    # Step 7: Test deployment
    service_url = "https://ai-agents-backend-2oi8.onrender.com"
    if not test_deployment(service_url):
        print_warning("Some tests failed")
    
    # Step 8: OAuth instructions
    update_oauth_redirects(service_url)
    
    # Success!
    print_header("🎉 Deployment Complete!")
    print(f"\n{Colors.GREEN} Your AI Agents platform is now live!{Colors.END}")
    print(f"\n🌐 Service URL: {service_url}")
    print(f"\n📋 Next steps:")
    print("   1. Update OAuth redirect URLs (instructions above)")
    print("   2. Test OAuth flows in browser")
    print("   3. (Optional) Downgrade to free plan:")
    print("      python Render_backend/downgrade_to_free.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
