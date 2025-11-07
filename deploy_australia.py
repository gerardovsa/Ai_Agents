"""
AI Agents Platform - Australia Docker Deployment Wizard
Guides through deployment to Render.com (Singapore region)

Usage:
    python deploy_australia.py
"""

import os
import sys
import json
from pathlib import Path

# ANSI color codes
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
    print("\n" + "=" * 80)
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print("=" * 80 + "\n")

def print_step(number, text):
    """Print step number with text"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Step {number}: {text}{Colors.END}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {filepath}")
        return False

def check_prerequisites():
    """Check all deployment prerequisites"""
    print_step(1, "Checking Prerequisites")
    
    all_good = True
    
    # Check required files
    print("\n📁 Checking required files...")
    all_good &= check_file_exists("Dockerfile", "Dockerfile")
    all_good &= check_file_exists(".dockerignore", "Docker ignore file")
    all_good &= check_file_exists("render.yaml", "Render configuration")
    all_good &= check_file_exists("requirements.txt", "Python requirements")
    all_good &= check_file_exists("AI_infrastructure/flask_app.py", "Flask application")
    all_good &= check_file_exists(".env.master", "Environment variables")
    
    # Check git status
    print("\n🔧 Checking Git repository...")
    if os.path.exists(".git"):
        print_success("Git repository initialized")
        
        # Check current branch
        try:
            import subprocess
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip()
            
            if current_branch == 'V2_clean':
                print_success(f"On correct branch: {current_branch}")
            else:
                print_warning(f"Current branch: {current_branch} (should be V2_clean)")
                all_good = False
        except:
            print_warning("Could not determine current branch")
    else:
        print_error("Not a Git repository")
        all_good = False
    
    # Check render.yaml region
    print("\n🌏 Checking deployment region...")
    try:
        with open('render.yaml', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'region: singapore' in content:
                print_success("Region set to Singapore (optimal for Australia)")
            elif 'region: oregon' in content:
                print_error("Region set to Oregon (high latency from Australia)")
                print_info("Update render.yaml: Change 'oregon' to 'singapore'")
                all_good = False
            else:
                print_warning("Region not specified in render.yaml")
    except Exception as e:
        print_error(f"Could not check render.yaml: {e}")
        all_good = False
    
    return all_good

def extract_env_vars():
    """Extract environment variables from .env.master"""
    print_step(2, "Extracting Environment Variables")
    
    if not Path('.env.master').exists():
        print_error(".env.master not found")
        return False
    
    # Read .env.master with UTF-8 encoding
    env_vars = {}
    with open('.env.master', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Filter important keys for Render
    render_keys = {
        'ANTHROPIC_API_KEY': env_vars.get('ANTHROPIC_API_KEY', ''),
        'OPENAI_API_KEY': env_vars.get('OPENAI_API_KEY', ''),
        'DEEPSEEK_API_KEY_1': env_vars.get('DEEPSEEK_API_KEY_1', ''),
        'MICROSOFT_CLIENT_ID': env_vars.get('MICROSOFT_CLIENT_ID', ''),
        'MICROSOFT_CLIENT_SECRET': env_vars.get('MICROSOFT_CLIENT_SECRET', ''),
        'GOOGLE_OAUTH_CLIENT_ID': env_vars.get('GOOGLE_OAUTH_CLIENT_ID', ''),
        'GOOGLE_OAUTH_CLIENT_SECRET': env_vars.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
    }
    
    # Save to JSON file
    output_file = 'render_env_vars.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(render_keys, f, indent=2)
    
    print_success(f"Environment variables extracted to: {output_file}")
    print_info(f"Found {len(render_keys)} keys to configure in Render dashboard")
    
    return True

def show_deployment_instructions():
    """Show deployment instructions"""
    print_step(3, "Deployment Instructions")
    
    print(f"\n{Colors.BOLD}🚀 Ready to Deploy!{Colors.END}\n")
    
    print("Choose your deployment method:\n")
    
    print(f"{Colors.BOLD}Option 1: Automated Deployment (Recommended){Colors.END}")
    print("  Run: python Render_backend/render_deploy.py")
    print("  This will:")
    print("    ✅ Push to GitHub")
    print("    ✅ Create Render service in Singapore")
    print("    ✅ Upload environment variables")
    print("    ✅ Monitor deployment progress\n")
    
    print(f"{Colors.BOLD}Option 2: Manual Dashboard Deployment{Colors.END}")
    print("  1. Push to GitHub:")
    print("     git add Dockerfile .dockerignore render.yaml")
    print("     git commit -m 'feat: Add Docker deployment for Singapore'")
    print("     git push origin V2_clean")
    print("\n  2. Go to: https://dashboard.render.com")
    print("     - Click 'New +' → 'Web Service'")
    print("     - Connect repository: gerardovsa/AI_agents")
    print("     - Branch: V2_clean")
    print("     - Region: Singapore ⭐ IMPORTANT")
    print("     - Environment: Docker")
    print("     - Plan: Starter ($7/month)")
    print("\n  3. Add environment variables from: render_env_vars.json")
    print("\n  4. Click 'Create Web Service'\n")
    
    print(f"{Colors.BOLD}📊 Expected Build Time:{Colors.END} 5-8 minutes")
    print(f"{Colors.BOLD}🌏 Expected Latency from Australia:{Colors.END} 100-150ms\n")

def show_post_deployment_steps():
    """Show post-deployment steps"""
    print_step(4, "Post-Deployment Steps")
    
    print("\nAfter deployment completes:\n")
    
    print(f"{Colors.BOLD}1. Test Deployment{Colors.END}")
    print("   python Render_backend/test_deployment.py https://ai-agents-backend-xxxx.onrender.com\n")
    
    print(f"{Colors.BOLD}2. Update OAuth Redirect URLs{Colors.END}")
    print("   python Render_backend/update_oauth_redirects.py https://ai-agents-backend-xxxx.onrender.com\n")
    
    print(f"{Colors.BOLD}3. Test Latency from Australia{Colors.END}")
    print("   curl -w '\\nTime: %{time_total}s\\n' https://ai-agents-backend-xxxx.onrender.com/health")
    print("   Expected: 0.1-0.15 seconds (100-150ms)\n")
    
    print(f"{Colors.BOLD}4. Monitor Service{Colors.END}")
    print("   python Render_backend/monitor_deployment.py srv-xxxxx\n")
    
    print(f"{Colors.BOLD}5. (Optional) Downgrade to Free Plan{Colors.END}")
    print("   python Render_backend/downgrade_to_free.py srv-xxxxx")
    print("   Note: Free plan spins down after 15 min inactivity\n")

def main():
    """Main deployment wizard"""
    print_header("🇦🇺 AI Agents Platform - Australia Docker Deployment Wizard")
    
    print(f"{Colors.CYAN}This wizard will guide you through deploying the AI Agents Platform")
    print(f"to Render.com in the Singapore region (optimized for Australia).{Colors.END}\n")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_error("\n❌ Prerequisites check failed!")
        print_info("Fix the issues above and run this script again.")
        sys.exit(1)
    
    print_success("\n✅ All prerequisites met!")
    
    # Step 2: Extract environment variables
    if not extract_env_vars():
        print_error("\n❌ Failed to extract environment variables!")
        sys.exit(1)
    
    # Step 3: Show deployment instructions
    show_deployment_instructions()
    
    # Step 4: Show post-deployment steps
    show_post_deployment_steps()
    
    # Summary
    print_header("📝 Quick Reference")
    print(f"{Colors.BOLD}Deployment Region:{Colors.END} Singapore (🇸🇬)")
    print(f"{Colors.BOLD}Expected Latency:{Colors.END} 100-150ms from Australia")
    print(f"{Colors.BOLD}Build Time:{Colors.END} 5-8 minutes")
    print(f"{Colors.BOLD}Plan:{Colors.END} Starter ($7/month, can downgrade to Free)")
    print(f"{Colors.BOLD}Environment Variables:{Colors.END} render_env_vars.json")
    print(f"{Colors.BOLD}Documentation:{Colors.END} Render_backend/AUSTRALIA_DOCKER_DEPLOYMENT.md")
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎯 Ready to deploy!{Colors.END}\n")
    
    # Ask if user wants to start deployment
    response = input(f"{Colors.BOLD}Start automated deployment now? (y/n): {Colors.END}")
    if response.lower() == 'y':
        print("\nStarting automated deployment...\n")
        import subprocess
        try:
            subprocess.run([sys.executable, "Render_backend/render_deploy.py"])
        except Exception as e:
            print_error(f"Deployment failed: {e}")
            print_info("Try manual deployment via Render dashboard")
    else:
        print_info("\nDeployment skipped. Use the instructions above to deploy manually.")

if __name__ == "__main__":
    main()
