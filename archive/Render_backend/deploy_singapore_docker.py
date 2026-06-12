"""
Deploy AI Agents Platform to Render.com - Singapore Region with Docker
=======================================================================

This script deploys a NEW Render service in Singapore region with Docker support,
replacing the old Oregon python-based deployment.

WHAT THIS DOES:
1. Creates new Render web service in Singapore region
2. Uses Docker environment (enables code execution sandbox)
3. Configures all environment variables from render.yaml
4. Sets up auto-deploy from GitHub (V2_clean branch)
5. Provides monitoring and testing utilities

PREREQUISITES:
- Render API key in .env.master (RENDER_API_KEY=rnd_...)
- GitHub repo: gerardovsa/AI_agents (branch: V2_clean)
- All local changes committed and pushed
- render.yaml and Dockerfile in root directory

AFTER DEPLOYMENT:
- Service will deploy to Singapore region (~100-150ms from Australia)
- Docker environment enables sandboxed code execution
- Auto-deploy watches V2_clean branch
- Need to manually add API keys in Render dashboard

CLEANUP:
After verifying new service works:
- Delete old Oregon service: srv-d40tai15pdvs73ddh4m0
- Update OAuth redirect URLs (Google/Microsoft)
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from render_api_client import RenderAPIClient


class SingaporeDockerDeployer:
    """Deploy AI Agents to Singapore with Docker"""
    
    def __init__(self):
        """Initialize deployer with API client"""
        # Get API key from environment with fallback to hardcoded value
        api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
        
        self.client = RenderAPIClient(api_key)
        self.service_id = None
        self.service_url = None
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def print_step(self, step_num, text):
        """Print step number and description"""
        print(f"\n[STEP {step_num}] {text}")
        print("-" * 80)
    
    def check_prerequisites(self):
        """Check all prerequisites before deployment"""
        self.print_step(1, "Checking Prerequisites")
        
        checks = []
        
        # Check 1: Render API key (use same fallback as __init__)
        api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
        if api_key and api_key.startswith('rnd_'):
            checks.append(("Render API Key", True, f"Found: {api_key[:10]}..."))
        else:
            checks.append(("Render API Key", False, "Not found or invalid"))
        
        # Check 2: render.yaml exists
        render_yaml = Path(__file__).parent.parent / 'render.yaml'
        if render_yaml.exists():
            checks.append(("render.yaml", True, str(render_yaml)))
        else:
            checks.append(("render.yaml", False, "Not found in root"))
        
        # Check 3: Dockerfile exists
        dockerfile = Path(__file__).parent.parent / 'Dockerfile'
        if dockerfile.exists():
            checks.append(("Dockerfile", True, str(dockerfile)))
        else:
            checks.append(("Dockerfile", False, "Not found in root"))
        
        # Check 4: Git status (optional - just warn)
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            if result.returncode == 0:
                if result.stdout.strip():
                    checks.append(("Git Status", True, "Uncommitted changes detected (WARNING)"))
                else:
                    checks.append(("Git Status", True, "Clean working tree"))
            else:
                checks.append(("Git Status", True, "Could not check (optional)"))
        except Exception:
            checks.append(("Git Status", True, "Could not check (optional)"))
        
        # Print results
        all_passed = True
        for name, passed, message in checks:
            status = "PASS" if passed else "FAIL"
            icon = "✅" if passed else "❌"
            print(f"  {icon} {status:4} | {name:20} | {message}")
            if not passed:
                all_passed = False
        
        if not all_passed:
            print("\n❌ Prerequisites check FAILED. Please fix issues above.")
            return False
        
        print("\n✅ All prerequisites passed!")
        return True
    
    def create_service(self):
        """Create new Render web service in Singapore"""
        self.print_step(2, "Creating Render Service in Singapore")
        
        service_config = {
            "type": "web_service",
            "name": "ai-agents-backend-singapore",
            "ownerId": "tea-d1bv56p5pdvs73e9iobg",  # Vet Success team
            "repo": "https://github.com/gerardovsa/Ai_Agents",  # Note: Ai_Agents (capital A)
            "autoDeploy": "yes",
            "branch": "v3",
            "buildFilter": {
                "paths": [],
                "ignoredPaths": []
            },
            "envSpecificDetails": {
                "docker": {
                    "dockerfilePath": "./Dockerfile",
                    "dockerContext": "./"
                }
            },
            "serviceDetails": {
                "env": "docker",
                "region": "singapore",
                "plan": "starter",
                "healthCheckPath": "/health",
                "envVars": [
                    {"key": "PYTHONUNBUFFERED", "value": "1"},
                    {"key": "RENDER", "value": "true"},
                    {"key": "ENVIRONMENT", "value": "production"},
                    {"key": "PORT", "value": "10000"}
                ]
            }
        }
        
        print("Service Configuration:")
        print(f"  Name:       {service_config['name']}")
        print(f"  Region:     {service_config['serviceDetails']['region']} 🇸🇬")
        print(f"  Env:        {service_config['serviceDetails']['env']}")
        print(f"  Plan:       {service_config['serviceDetails']['plan']}")
        print(f"  Repository: {service_config['repo']}")
        print(f"  Branch:     {service_config['branch']}")
        print(f"  Dockerfile: {service_config['envSpecificDetails']['docker']['dockerfilePath']}")
        
        print("\n⏳ Creating service... (this may take a few moments)")
        
        try:
            response = self.client.create_service(service_config)
            
            if 'service' in response:
                service = response['service']
                self.service_id = service.get('id')
                self.service_url = service.get('serviceDetails', {}).get('url')
                
                print(f"\n✅ Service created successfully!")
                print(f"  Service ID:  {self.service_id}")
                print(f"  Service URL: {self.service_url}")
                return True
            else:
                print(f"\n❌ Failed to create service")
                print(f"Response: {json.dumps(response, indent=2)}")
                return False
                
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error creating service: {e}")
            if hasattr(e.response, 'text'):
                print(f"Error details: {e.response.text}")
            return False
        except Exception as e:
            print(f"\n❌ Error creating service: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def wait_for_deployment(self, timeout=600):
        """Wait for initial deployment to complete"""
        self.print_step(3, "Waiting for Initial Deployment")
        
        if not self.service_id:
            print("❌ No service ID available")
            return False
        
        print(f"Monitoring deployment of {self.service_id}...")
        print("This typically takes 5-10 minutes for Docker builds.\n")
        
        start_time = time.time()
        last_status = None
        
        while (time.time() - start_time) < timeout:
            try:
                # Get latest deploy
                deploys = self.client.list_deploys(self.service_id, limit=1)
                
                if deploys:
                    deploy = deploys[0]
                    deploy_id = deploy.get('id', 'unknown')
                    status = deploy.get('status', 'unknown')
                    created_at = deploy.get('createdAt', 'unknown')
                    
                    if status != last_status:
                        elapsed = int(time.time() - start_time)
                        print(f"[{elapsed:3}s] Deploy {deploy_id[:8]}... | Status: {status.upper()}")
                        last_status = status
                    
                    if status == 'live':
                        print(f"\n✅ Deployment LIVE! Total time: {int(time.time() - start_time)}s")
                        return True
                    elif status in ['build_failed', 'failed']:
                        print(f"\n❌ Deployment FAILED")
                        return False
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"⚠️  Error checking deployment: {e}")
                time.sleep(10)
        
        print(f"\n⚠️  Deployment timeout after {timeout}s")
        return False
    
    def test_deployment(self):
        """Test the deployed service"""
        self.print_step(4, "Testing Deployment")
        
        if not self.service_url:
            print("❌ No service URL available")
            return False
        
        print(f"Testing service at: {self.service_url}")
        
        import requests
        
        # Test 1: Health endpoint
        try:
            print("\n1️⃣  Testing /health endpoint...")
            response = requests.get(f"{self.service_url}/health", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Tools loaded: {data.get('tools_loaded', 0)}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Health check error: {e}")
            return False
        
        # Test 2: Root endpoint
        try:
            print("\n2️⃣  Testing / (root) endpoint...")
            response = requests.get(self.service_url, timeout=30)
            
            if response.status_code == 200:
                print(f"   ✅ Root endpoint accessible")
            else:
                print(f"   ⚠️  Root returned: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Root endpoint error: {e}")
        
        print("\n✅ Basic tests passed!")
        return True
    
    def print_next_steps(self):
        """Print instructions for next steps"""
        self.print_header("DEPLOYMENT COMPLETE - NEXT STEPS")
        
        print("🎉 Your AI Agents platform is now deployed to Singapore!")
        print(f"\n📍 Service URL: {self.service_url}")
        print(f"🆔 Service ID:  {self.service_id}")
        
        print("\n" + "="*80)
        print("IMPORTANT: Manual Configuration Required")
        print("="*80)
        
        print("\n1️⃣  ADD API KEYS in Render Dashboard:")
        print(f"   https://dashboard.render.com/web/{self.service_id}/env")
        print("\n   Required environment variables:")
        print("   - ANTHROPIC_API_KEY")
        print("   - OPENAI_API_KEY")
        print("   - DEEPSEEK_API_KEY_1")
        print("   - MICROSOFT_CLIENT_ID")
        print("   - MICROSOFT_CLIENT_SECRET")
        print("   - MICROSOFT_TENANT_ID")
        print("   - GOOGLE_CLIENT_ID (if using OAuth)")
        print("   - GOOGLE_CLIENT_SECRET (if using OAuth)")
        
        print("\n2️⃣  UPDATE OAUTH REDIRECT URLs:")
        print(f"   New redirect URL: {self.service_url}/api/auth/google/callback")
        print(f"   New redirect URL: {self.service_url}/api/auth/microsoft/callback")
        print("\n   Google Cloud Console:")
        print("   https://console.cloud.google.com/apis/credentials")
        print("\n   Microsoft Azure Portal:")
        print("   https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps")
        
        print("\n3️⃣  DELETE OLD OREGON SERVICE:")
        print("   After verifying this works, delete the old service:")
        print("   Service ID: srv-d40tai15pdvs73ddh4m0")
        print("   Command: python render_cli.py delete srv-d40tai15pdvs73ddh4m0")
        
        print("\n4️⃣  MONITOR DEPLOYMENT:")
        print(f"   Logs:    python render_cli.py logs {self.service_id}")
        print(f"   Status:  python render_cli.py status {self.service_id}")
        print(f"   Deploys: python render_cli.py deploys {self.service_id}")
        
        print("\n" + "="*80)
        print("Performance Improvement")
        print("="*80)
        print("\n🚀 Latency reduction: Oregon (200-250ms) → Singapore (100-150ms)")
        print("📊 50% faster response times for Australian users!")
        print("🐳 Docker enables sandboxed code execution")
        
        print("\n" + "="*80)
    
    def run(self):
        """Run full deployment process"""
        self.print_header("AI Agents Platform - Singapore Docker Deployment")
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Create service
        if not self.create_service():
            return False
        
        # Step 3: Wait for deployment
        if not self.wait_for_deployment():
            print("\n⚠️  Initial deployment not completed within timeout.")
            print("You can monitor deployment manually:")
            print(f"  python render_cli.py logs {self.service_id}")
            return False
        
        # Step 4: Test deployment
        if not self.test_deployment():
            print("\n⚠️  Some tests failed, but service may still work.")
        
        # Step 5: Print next steps
        self.print_next_steps()
        
        return True


def main():
    """Main entry point"""
    deployer = SingaporeDockerDeployer()
    
    # Confirm before proceeding
    print("\n" + "="*80)
    print("  AI AGENTS PLATFORM - SINGAPORE DOCKER DEPLOYMENT")
    print("="*80)
    print("\nThis will create a NEW Render service with:")
    print("  • Region: Singapore 🇸🇬")
    print("  • Environment: Docker 🐳")
    print("  • Plan: Starter ($7/month)")
    print("  • Auto-deploy: Enabled")
    print("\nThe old Oregon service will NOT be deleted automatically.")
    print("You must delete it manually after verifying this works.\n")
    
    response = input("Continue with deployment? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n❌ Deployment cancelled.")
        return
    
    # Run deployment
    success = deployer.run()
    
    if success:
        print("\n✅ Deployment script completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Deployment encountered errors.")
        sys.exit(1)


if __name__ == '__main__':
    main()
