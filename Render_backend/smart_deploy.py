"""
Smart Deployment Tool - Analyzes capabilities and deploys to Render.com
=========================================================================

This tool:
1. Scans all available deployment tools and APIs
2. Analyzes Render API capabilities
3. Checks MCP (Model Context Protocol) tools
4. Creates optimized deployment strategy
5. Executes deployment to Singapore region with Docker

Usage:
    python smart_deploy.py --analyze    # Show all deployment capabilities
    python smart_deploy.py --deploy     # Deploy to Render Singapore
    python smart_deploy.py --status     # Check deployment status
    python smart_deploy.py --delete     # Delete old Oregon service
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from render_api_client import RenderAPIClient


class SmartDeploymentTool:
    """Intelligent deployment tool with capability analysis"""
    
    def __init__(self):
        """Initialize smart deployment tool"""
        self.api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
        self.render_client = RenderAPIClient(self.api_key)
        self.capabilities = {}
        self.deployment_tools = []
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def analyze_tool_registry(self):
        """Analyze all available deployment tools in the system"""
        self.print_header("ANALYZING TOOL REGISTRY")
        
        try:
            # Import registry
            from tools.registry_v3 import RegistryV3
            registry = RegistryV3()
            
            # Find deployment-related tools
            keywords = ['deploy', 'render', 'service', 'docker', 'cloud', 'container']
            self.deployment_tools = [
                name for name in registry.tools.keys()
                if any(keyword in name.lower() for keyword in keywords)
            ]
            
            print(f"Found {len(self.deployment_tools)} deployment-related tools:")
            for tool in sorted(self.deployment_tools):
                tool_def = registry.get_tool(tool)
                print(f"  - {tool}")
                print(f"    Description: {tool_def.get('description', 'N/A')[:80]}...")
            
            self.capabilities['tool_registry'] = {
                'total_tools': len(registry.tools),
                'deployment_tools': len(self.deployment_tools),
                'tools': self.deployment_tools
            }
            
            return True
            
        except Exception as e:
            print(f"Error analyzing tool registry: {e}")
            return False
    
    def analyze_render_api(self):
        """Analyze Render API capabilities"""
        self.print_header("ANALYZING RENDER API")
        
        try:
            # List current services
            services = self.render_client.list_services(limit=100)
            
            print(f"Found {len(services)} Render services:")
            
            regions = {}
            envs = {}
            plans = {}
            
            for item in services:
                service = item.get('service', {})
                name = service.get('name', 'Unknown')
                region = service.get('region', 'unknown')
                env = service.get('env', 'unknown')
                plan = service.get('plan', 'unknown')
                status = service.get('suspendedReason', 'active') == 'active'
                
                regions[region] = regions.get(region, 0) + 1
                envs[env] = envs.get(env, 0) + 1
                plans[plan] = plans.get(plan, 0) + 1
                
                status_icon = "✅" if status else "⚠️"
                print(f"  {status_icon} {name}")
                print(f"      Region: {region} | Env: {env} | Plan: {plan}")
            
            print(f"\nRegion Distribution:")
            for region, count in sorted(regions.items(), key=lambda x: x[1], reverse=True):
                print(f"  {region}: {count} services")
            
            print(f"\nEnvironment Distribution:")
            for env, count in sorted(envs.items(), key=lambda x: x[1], reverse=True):
                print(f"  {env}: {count} services")
            
            print(f"\nPlan Distribution:")
            for plan, count in sorted(plans.items(), key=lambda x: x[1], reverse=True):
                print(f"  {plan}: {count} services")
            
            self.capabilities['render_api'] = {
                'total_services': len(services),
                'regions': regions,
                'environments': envs,
                'plans': plans
            }
            
            return True
            
        except Exception as e:
            print(f"Error analyzing Render API: {e}")
            return False
    
    def analyze_docker_capabilities(self):
        """Analyze Docker and containerization capabilities"""
        self.print_header("ANALYZING DOCKER CAPABILITIES")
        
        # Check Dockerfile
        dockerfile = Path(__file__).parent.parent / 'Dockerfile'
        if dockerfile.exists():
            print("✅ Dockerfile found")
            with open(dockerfile, 'r') as f:
                content = f.read()
                print(f"   Size: {len(content)} bytes")
                if 'python:3.11' in content:
                    print("   Base: Python 3.11 ✅")
                if 'HEALTHCHECK' in content:
                    print("   Health check: Configured ✅")
        else:
            print("❌ Dockerfile not found")
        
        # Check docker-compose
        compose = Path(__file__).parent.parent / 'docker-compose.yml'
        if compose.exists():
            print("✅ docker-compose.yml found")
        
        # Check render.yaml
        render_yaml = Path(__file__).parent.parent / 'render.yaml'
        if render_yaml.exists():
            print("✅ render.yaml found")
            with open(render_yaml, 'r') as f:
                content = f.read()
                if 'singapore' in content.lower():
                    print("   Region: Singapore ✅")
                if 'docker' in content.lower():
                    print("   Environment: Docker ✅")
        
        self.capabilities['docker'] = {
            'dockerfile': dockerfile.exists(),
            'compose': compose.exists(),
            'render_yaml': render_yaml.exists()
        }
        
        return True
    
    def analyze_cloud_run_capabilities(self):
        """Analyze Google Cloud Run deployment capabilities"""
        self.print_header("ANALYZING GOOGLE CLOUD RUN")
        
        try:
            from tools.registry_v3 import RegistryV3
            registry = RegistryV3()
            
            cloud_run_tools = [
                name for name in registry.tools.keys()
                if 'google_cloud_run' in name
            ]
            
            print(f"Found {len(cloud_run_tools)} Google Cloud Run tools:")
            for tool in sorted(cloud_run_tools):
                print(f"  - {tool}")
            
            self.capabilities['google_cloud_run'] = {
                'available': len(cloud_run_tools) > 0,
                'tool_count': len(cloud_run_tools),
                'tools': cloud_run_tools
            }
            
            return True
            
        except Exception as e:
            print(f"Error analyzing Cloud Run: {e}")
            return False
    
    def analyze_all(self):
        """Run all analysis"""
        self.print_header("SMART DEPLOYMENT CAPABILITY ANALYSIS")
        
        print("Scanning all deployment capabilities...")
        
        # Run all analyses
        self.analyze_tool_registry()
        self.analyze_render_api()
        self.analyze_docker_capabilities()
        self.analyze_cloud_run_capabilities()
        
        # Save capabilities report
        report_path = Path(__file__).parent / 'deployment_capabilities.json'
        with open(report_path, 'w') as f:
            json.dump(self.capabilities, f, indent=2)
        
        self.print_header("ANALYSIS COMPLETE")
        print(f"Full report saved to: {report_path}")
        print(f"\nCapabilities Summary:")
        print(f"  Total Tools: {self.capabilities.get('tool_registry', {}).get('total_tools', 0)}")
        print(f"  Deployment Tools: {len(self.deployment_tools)}")
        print(f"  Render Services: {self.capabilities.get('render_api', {}).get('total_services', 0)}")
        print(f"  Docker Ready: {'✅' if self.capabilities.get('docker', {}).get('dockerfile') else '❌'}")
        print(f"  Cloud Run Tools: {self.capabilities.get('google_cloud_run', {}).get('tool_count', 0)}")
    
    def deploy_to_singapore(self):
        """Deploy AI Agents to Render Singapore with Docker"""
        self.print_header("DEPLOYING TO RENDER SINGAPORE")
        
        print("⚠️  This feature uses the Render Dashboard due to API complexity.")
        print("\nRecommended deployment method:")
        print("1. Open https://dashboard.render.com")
        print("2. Click 'New +' → 'Web Service'")
        print("3. Select 'gerardovsa/Ai_Agents' repository")
        print("4. Use these settings:")
        print("   - Region: Singapore")
        print("   - Environment: Docker")
        print("   - Branch: V2_clean")
        print("   - Plan: Starter ($7/month)")
        print("\nFor detailed instructions, see:")
        print("  Render_backend/DEPLOY_VIA_DASHBOARD.md")
        
        print("\nAlternative: Use render.yaml blueprint:")
        print("1. Go to https://dashboard.render.com/select-repo")
        print("2. Select 'gerardovsa/Ai_Agents'")
        print("3. Render will detect render.yaml")
        print("4. Click 'Apply' - automatic deployment!")
    
    def check_status(self):
        """Check deployment status"""
        self.print_header("CHECKING DEPLOYMENT STATUS")
        
        try:
            services = self.render_client.list_services(limit=20)
            
            # Find AI Agents services
            ai_services = [
                item.get('service', {})
                for item in services
                if 'ai-agents' in item.get('service', {}).get('name', '').lower()
            ]
            
            if not ai_services:
                print("❌ No AI Agents services found")
                return
            
            print(f"Found {len(ai_services)} AI Agents service(s):\n")
            
            for service in ai_services:
                name = service.get('name', 'Unknown')
                service_id = service.get('id', 'N/A')
                region = service.get('region', 'unknown')
                env = service.get('env', 'unknown')
                url = service.get('serviceDetails', {}).get('url', 'N/A')
                suspended = service.get('suspendedReason')
                
                print(f"📦 {name}")
                print(f"   ID: {service_id}")
                print(f"   Region: {region}")
                print(f"   Environment: {env}")
                print(f"   URL: {url}")
                print(f"   Status: {'Active ✅' if not suspended else f'Suspended ⚠️ ({suspended})'}")
                
                # Get latest deploy
                try:
                    deploys = self.render_client.list_deploys(service_id, limit=1)
                    if deploys:
                        deploy = deploys[0]
                        status = deploy.get('status', 'unknown')
                        created = deploy.get('createdAt', 'N/A')
                        print(f"   Latest Deploy: {status} at {created}")
                except:
                    pass
                
                print()
            
        except Exception as e:
            print(f"Error checking status: {e}")
    
    def delete_oregon_service(self):
        """Delete old Oregon service"""
        self.print_header("DELETE OREGON SERVICE")
        
        OREGON_SERVICE_ID = "srv-d40tai15pdvs73ddh4m0"
        
        print("⚠️  WARNING: This will delete the Oregon AI Agents service!")
        print(f"   Service ID: {OREGON_SERVICE_ID}")
        print(f"   Region: Oregon")
        print(f"   URL: https://ai-agents-backend-2oi8.onrender.com")
        
        print("\nBefore proceeding, ensure:")
        print("  ✅ New Singapore service is deployed and working")
        print("  ✅ OAuth redirect URLs updated to new service")
        print("  ✅ All users redirected to new URL")
        
        confirm = input("\nType 'DELETE OREGON' to proceed: ")
        
        if confirm != 'DELETE OREGON':
            print("❌ Deletion cancelled")
            return
        
        try:
            print(f"\n⏳ Deleting service {OREGON_SERVICE_ID}...")
            result = self.render_client.delete_service(OREGON_SERVICE_ID)
            print("✅ Service deleted successfully!")
            print(f"   {result}")
        except Exception as e:
            print(f"❌ Error deleting service: {e}")
            print("\nYou can delete manually at:")
            print(f"  https://dashboard.render.com/web/{OREGON_SERVICE_ID}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Smart Deployment Tool for AI Agents Platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smart_deploy.py --analyze    # Analyze all deployment capabilities
  python smart_deploy.py --deploy     # Deploy to Render Singapore
  python smart_deploy.py --status     # Check current deployment status
  python smart_deploy.py --delete     # Delete old Oregon service
        """
    )
    
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze all deployment capabilities')
    parser.add_argument('--deploy', action='store_true',
                       help='Deploy to Render Singapore (with guide)')
    parser.add_argument('--status', action='store_true',
                       help='Check deployment status')
    parser.add_argument('--delete', action='store_true',
                       help='Delete old Oregon service')
    
    args = parser.parse_args()
    
    # If no args, show help
    if not any([args.analyze, args.deploy, args.status, args.delete]):
        parser.print_help()
        return
    
    # Create tool instance
    tool = SmartDeploymentTool()
    
    # Execute requested action
    if args.analyze:
        tool.analyze_all()
    
    if args.deploy:
        tool.deploy_to_singapore()
    
    if args.status:
        tool.check_status()
    
    if args.delete:
        tool.delete_oregon_service()


if __name__ == '__main__':
    main()
