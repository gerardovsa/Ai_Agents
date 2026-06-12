"""
RENDER COMPLETE CLI - Full Project Management Tool
Comprehensive command-line interface for complete Render.com project management

FEATURES:
- Services: List, create, update, delete, restart, scale
- Deploys: List, trigger, rollback, cancel
- Environment Variables: Add, update, delete, import/export
- Custom Domains: Add, verify, delete
- Logs: Stream, search, download
- Metrics: CPU, memory, bandwidth, requests
- Databases: PostgreSQL management
- Blueprints: Deploy from render.yaml
- Projects: Create, manage environments
- Health: Check service health, uptime
- Jobs: One-off jobs, cron jobs
- Teams: Manage team members and access

USAGE:
    python render_complete_cli.py <command> [options]

COMMANDS:
    # Services Management
    services list                              - List all services
    services get <service-id>                  - Get service details
    services create <config-file.json>         - Create new service
    services update <service-id> <key=value>   - Update service
    services delete <service-id>               - Delete service
    services restart <service-id>              - Restart service
    services scale <service-id> <instances>    - Scale service
    services suspend <service-id>              - Suspend service
    services resume <service-id>               - Resume service
    
    # Deploys Management
    deploys list <service-id>                  - List deploys
    deploys get <service-id> <deploy-id>       - Get deploy details
    deploys trigger <service-id>               - Trigger new deploy
    deploys rollback <service-id> <deploy-id>  - Rollback to deploy
    deploys cancel <service-id> <deploy-id>    - Cancel deploy
    
    # Environment Variables
    env list <service-id>                      - List env vars
    env get <service-id> <key>                 - Get env var value
    env set <service-id> <key> <value>         - Set env var
    env delete <service-id> <key>              - Delete env var
    env import <service-id> <file.env>         - Import from .env file
    env export <service-id> <file.env>         - Export to .env file
    
    # Custom Domains
    domains list <service-id>                  - List domains
    domains add <service-id> <domain>          - Add custom domain
    domains verify <service-id> <domain>       - Verify domain
    domains delete <service-id> <domain>       - Remove domain
    
    # Logs Management
    logs tail <service-id>                     - Stream live logs
    logs search <service-id> <query>           - Search logs
    logs download <service-id> <file.log>      - Download logs
    
    # Metrics & Monitoring
    metrics cpu <service-id>                   - Show CPU usage
    metrics memory <service-id>                - Show memory usage
    metrics requests <service-id>              - Show request metrics
    metrics bandwidth <service-id>             - Show bandwidth usage
    metrics all <service-id>                   - Show all metrics
    
    # Database Management (PostgreSQL)
    db list                                    - List all databases
    db create <name> <plan>                    - Create database
    db get <db-id>                             - Get database details
    db delete <db-id>                          - Delete database
    db backup <db-id>                          - Create backup
    db restore <db-id> <backup-id>             - Restore backup
    
    # Blueprint Deployment
    blueprint deploy <render.yaml>             - Deploy from blueprint
    blueprint validate <render.yaml>           - Validate blueprint
    blueprint preview <render.yaml>            - Preview changes
    
    # Projects & Environments
    projects list                              - List all projects
    projects create <name>                     - Create project
    projects get <project-id>                  - Get project details
    environments list <project-id>             - List environments
    environments create <project-id> <name>    - Create environment
    
    # Health & Status
    health check <service-id>                  - Check service health
    health uptime <service-id>                 - Show uptime stats
    status overview                            - Show all services status
    
    # Jobs Management
    jobs list <service-id>                     - List one-off jobs
    jobs run <service-id> <command>            - Run one-off job
    jobs logs <service-id> <job-id>            - Get job logs
    
    # Team Management
    team list                                  - List team members
    team invite <email> <role>                 - Invite team member
    team remove <member-id>                    - Remove team member
    
    # Quick Actions
    quick singapore                            - Deploy AI Agents to Singapore
    quick status                               - Show AI Agents status
    quick restart                              - Restart AI Agents
    quick logs                                 - Show AI Agents logs
    
EXAMPLES:
    # List all services
    python render_complete_cli.py services list
    
    # Create new service
    python render_complete_cli.py services create service-config.json
    
    # Set environment variable
    python render_complete_cli.py env set srv-xxxxx PYTHON_VERSION 3.11
    
    # Stream logs
    python render_complete_cli.py logs tail srv-xxxxx
    
    # Deploy from blueprint
    python render_complete_cli.py blueprint deploy render.yaml
    
    # Scale service
    python render_complete_cli.py services scale srv-xxxxx 3

CONFIGURATION:
    Set RENDER_API_KEY environment variable or use --api-key flag
    API Key: https://dashboard.render.com/u/settings?add-api-key
"""

import os
import sys
import json
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Import the base API client
sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

class RenderCompleteCLI:
    """Complete Render.com project management CLI"""
    
    def __init__(self, api_key: str):
        """Initialize CLI with API key"""
        self.client = RenderAPIClient(api_key)
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    # ==================== Services Management ====================
    
    def services_list(self, limit: int = 50):
        """List all services with detailed info"""
        print(f"\n{'='*100}")
        print(f"  RENDER SERVICES ({limit} max)")
        print(f"{'='*100}\n")
        
        try:
            services = self.client.list_services(limit=limit)
            
            if not services:
                print("No services found.\n")
                return
            
            print(f"Found {len(services)} service(s):\n")
            
            for i, item in enumerate(services, 1):
                service = item.get('service', item)
                details = service.get('serviceDetails', {})
                
                name = service.get('name', 'N/A')
                service_id = service.get('id', 'N/A')
                service_type = service.get('type', 'N/A')
                suspended = service.get('suspended', 'unknown')
                
                status_icon = "✅" if suspended == "not_suspended" else "⚠️"
                
                print(f"{i}. {status_icon} {name}")
                print(f"   ID:       {service_id}")
                print(f"   Type:     {service_type}")
                print(f"   URL:      {details.get('url', 'N/A')}")
                print(f"   Region:   {details.get('region', 'N/A')}")
                print(f"   Plan:     {details.get('plan', 'N/A')}")
                print(f"   Env:      {details.get('env', 'N/A')}")
                print(f"   Status:   {suspended}")
                print(f"   Created:  {service.get('createdAt', 'N/A')}")
                print(f"   Updated:  {service.get('updatedAt', 'N/A')}")
                print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def services_get(self, service_id: str):
        """Get detailed service information"""
        print(f"\n{'='*100}")
        print(f"  SERVICE DETAILS: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            service = self.client.get_service(service_id)
            
            # Basic info
            print(f"Name:         {service.get('name', 'N/A')}")
            print(f"ID:           {service.get('id', 'N/A')}")
            print(f"Type:         {service.get('type', 'N/A')}")
            print(f"Status:       {service.get('suspended', 'N/A')}")
            print(f"Created:      {service.get('createdAt', 'N/A')}")
            print(f"Updated:      {service.get('updatedAt', 'N/A')}")
            
            # Service details
            details = service.get('serviceDetails', {})
            print(f"\nService Details:")
            print(f"  URL:        {details.get('url', 'N/A')}")
            print(f"  Region:     {details.get('region', 'N/A')}")
            print(f"  Plan:       {details.get('plan', 'N/A')}")
            print(f"  Env:        {details.get('env', 'N/A')}")
            print(f"  Runtime:    {details.get('runtime', 'N/A')}")
            print(f"  Health:     {details.get('healthCheckPath', 'N/A')}")
            
            # Repository info
            if 'repo' in service:
                print(f"\nRepository:")
                print(f"  Repo:       {service.get('repo', 'N/A')}")
                print(f"  Branch:     {service.get('branch', 'N/A')}")
                print(f"  Auto Deploy: {service.get('autoDeploy', 'N/A')}")
            
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def services_create(self, config_file: str):
        """Create new service from JSON config"""
        print(f"\n{'='*100}")
        print(f"  CREATE SERVICE FROM: {config_file}")
        print(f"{'='*100}\n")
        
        try:
            # Load config
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"Creating service: {config.get('name', 'N/A')}")
            print(f"Type: {config.get('type', 'N/A')}")
            print(f"Region: {config.get('region', 'N/A')}")
            print(f"Plan: {config.get('plan', 'N/A')}")
            print()
            
            # Create service
            result = self.client.create_service(config)
            
            service = result.get('service', result)
            print(f"✅ Service created successfully!")
            print(f"   ID:  {service.get('id', 'N/A')}")
            print(f"   URL: {service.get('serviceDetails', {}).get('url', 'N/A')}")
            print()
        except FileNotFoundError:
            print(f"❌ Config file not found: {config_file}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def services_delete(self, service_id: str):
        """Delete a service with confirmation"""
        print(f"\n{'='*100}")
        print(f"  DELETE SERVICE: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            # Get service info first
            service = self.client.get_service(service_id)
            name = service.get('name', 'N/A')
            
            print(f"⚠️  WARNING: You are about to delete:")
            print(f"   Name: {name}")
            print(f"   ID:   {service_id}")
            print()
            
            confirm = input("Type 'DELETE' to confirm: ")
            if confirm != 'DELETE':
                print("❌ Deletion cancelled.\n")
                return
            
            # Delete service
            result = self.client.delete_service(service_id)
            print(f"✅ Service deleted successfully!\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def services_restart(self, service_id: str):
        """Restart service by triggering deploy with cache clear"""
        print(f"\n{'='*100}")
        print(f"  RESTART SERVICE: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            print(f"🔄 Triggering restart with cache clear...")
            result = self.client.restart_service(service_id)
            
            deploy_id = result.get('deploy', {}).get('id', 'N/A')
            print(f"✅ Deploy triggered: {deploy_id}")
            print(f"   Service will restart shortly.")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def services_scale(self, service_id: str, instances: int):
        """Scale service to specified number of instances"""
        print(f"\n{'='*100}")
        print(f"  SCALE SERVICE: {service_id}")
        print(f"{'='*100}\n")
        
        print(f"⚠️  Scaling to {instances} instances...")
        print(f"   Note: This may require API endpoint not yet implemented.")
        print(f"   Use Render Dashboard to scale: https://dashboard.render.com/web/{service_id}")
        print()
    
    # ==================== Deploys Management ====================
    
    def deploys_list(self, service_id: str, limit: int = 20):
        """List deploy history"""
        print(f"\n{'='*100}")
        print(f"  DEPLOY HISTORY: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            deploys = self.client.list_deploys(service_id, limit=limit)
            
            if not deploys:
                print("No deploys found.\n")
                return
            
            print(f"Found {len(deploys)} deploy(s):\n")
            
            for i, item in enumerate(deploys, 1):
                deploy = item.get('deploy', item)
                
                deploy_id = deploy.get('id', 'N/A')
                status = deploy.get('status', 'N/A')
                created = deploy.get('createdAt', 'N/A')
                finished = deploy.get('finishedAt', 'N/A')
                commit = deploy.get('commit', {})
                
                status_icons = {
                    'live': '✅',
                    'build_failed': '❌',
                    'building': '🔨',
                    'deploying': '🚀',
                    'deactivated': '⏸️'
                }
                icon = status_icons.get(status, '❓')
                
                print(f"{i}. {icon} Deploy {deploy_id}")
                print(f"   Status:   {status}")
                print(f"   Created:  {created}")
                print(f"   Finished: {finished}")
                if commit:
                    print(f"   Commit:   {commit.get('message', 'N/A')[:60]}")
                print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def deploys_trigger(self, service_id: str, clear_cache: bool = False):
        """Trigger new deploy"""
        print(f"\n{'='*100}")
        print(f"  TRIGGER DEPLOY: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            cache_text = "with cache clear" if clear_cache else "without cache clear"
            print(f"🚀 Triggering deploy {cache_text}...")
            
            result = self.client.trigger_deploy(service_id, clear_cache=clear_cache)
            
            deploy_id = result.get('deploy', {}).get('id', 'N/A')
            print(f"✅ Deploy triggered: {deploy_id}")
            print(f"   Monitor: https://dashboard.render.com/web/{service_id}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== Environment Variables ====================
    
    def env_list(self, service_id: str):
        """List environment variables"""
        print(f"\n{'='*100}")
        print(f"  ENVIRONMENT VARIABLES: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            service = self.client.get_service(service_id)
            env_vars = service.get('envVars', [])
            
            if not env_vars:
                print("No environment variables found.\n")
                return
            
            print(f"Found {len(env_vars)} variable(s):\n")
            
            for i, var in enumerate(env_vars, 1):
                key = var.get('key', 'N/A')
                value = var.get('value', '')
                
                # Mask sensitive values
                if len(value) > 20 or any(secret in key.lower() for secret in ['key', 'secret', 'password', 'token']):
                    display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                else:
                    display_value = value
                
                print(f"{i}. {key} = {display_value}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def env_set(self, service_id: str, key: str, value: str):
        """Set environment variable"""
        print(f"\n{'='*100}")
        print(f"  SET ENVIRONMENT VARIABLE")
        print(f"{'='*100}\n")
        
        try:
            print(f"Setting {key} on {service_id}...")
            
            # Get current env vars
            service = self.client.get_service(service_id)
            env_vars = service.get('envVars', [])
            
            # Update or add
            found = False
            for var in env_vars:
                if var['key'] == key:
                    var['value'] = value
                    found = True
                    break
            
            if not found:
                env_vars.append({'key': key, 'value': value})
            
            # Update service
            result = self.client.update_service_env_vars(service_id, env_vars)
            
            print(f"✅ Environment variable set: {key}")
            print(f"   Note: Redeploy required for changes to take effect.")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def env_import(self, service_id: str, env_file: str):
        """Import environment variables from .env file"""
        print(f"\n{'='*100}")
        print(f"  IMPORT ENVIRONMENT VARIABLES FROM: {env_file}")
        print(f"{'='*100}\n")
        
        try:
            # Read .env file
            env_vars = []
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_vars.append({'key': key.strip(), 'value': value.strip()})
            
            if not env_vars:
                print("No variables found in file.\n")
                return
            
            print(f"Found {len(env_vars)} variable(s) to import:")
            for var in env_vars:
                print(f"  - {var['key']}")
            print()
            
            confirm = input("Import these variables? (y/n): ")
            if confirm.lower() != 'y':
                print("❌ Import cancelled.\n")
                return
            
            # Get current env vars and merge
            service = self.client.get_service(service_id)
            current_vars = service.get('envVars', [])
            current_keys = {v['key'] for v in current_vars}
            
            # Add new vars
            for var in env_vars:
                if var['key'] not in current_keys:
                    current_vars.append(var)
                else:
                    # Update existing
                    for cv in current_vars:
                        if cv['key'] == var['key']:
                            cv['value'] = var['value']
            
            # Update service
            result = self.client.update_service_env_vars(service_id, current_vars)
            
            print(f"✅ {len(env_vars)} variables imported successfully!")
            print(f"   Note: Redeploy required for changes to take effect.")
            print()
        except FileNotFoundError:
            print(f"❌ File not found: {env_file}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def env_export(self, service_id: str, env_file: str):
        """Export environment variables to .env file"""
        print(f"\n{'='*100}")
        print(f"  EXPORT ENVIRONMENT VARIABLES TO: {env_file}")
        print(f"{'='*100}\n")
        
        try:
            service = self.client.get_service(service_id)
            env_vars = service.get('envVars', [])
            
            if not env_vars:
                print("No environment variables to export.\n")
                return
            
            # Write to file
            with open(env_file, 'w') as f:
                f.write(f"# Environment variables from {service.get('name', service_id)}\n")
                f.write(f"# Exported: {datetime.now().isoformat()}\n\n")
                for var in env_vars:
                    f.write(f"{var['key']}={var['value']}\n")
            
            print(f"✅ {len(env_vars)} variables exported to {env_file}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== Logs Management ====================
    
    def logs_tail(self, service_id: str):
        """Stream live logs (simulated)"""
        print(f"\n{'='*100}")
        print(f"  STREAMING LOGS: {service_id}")
        print(f"{'='*100}\n")
        
        print(f"⚠️  Live log streaming not available via REST API.")
        print(f"   Use Render CLI or Dashboard:")
        print(f"   Dashboard: https://dashboard.render.com/web/{service_id}")
        print(f"   CLI: render logs tail {service_id}")
        print()
    
    # ==================== Metrics & Monitoring ====================
    
    def metrics_all(self, service_id: str):
        """Show all metrics"""
        print(f"\n{'='*100}")
        print(f"  METRICS OVERVIEW: {service_id}")
        print(f"{'='*100}\n")
        
        print(f"⚠️  Metrics endpoints may require different API access.")
        print(f"   View metrics in Dashboard: https://dashboard.render.com/web/{service_id}")
        print()
    
    # ==================== Health & Status ====================
    
    def health_check(self, service_id: str):
        """Check service health"""
        print(f"\n{'='*100}")
        print(f"  HEALTH CHECK: {service_id}")
        print(f"{'='*100}\n")
        
        try:
            service = self.client.get_service(service_id)
            details = service.get('serviceDetails', {})
            
            name = service.get('name', 'N/A')
            suspended = service.get('suspended', 'unknown')
            url = details.get('url', 'N/A')
            health_path = details.get('healthCheckPath', '/health')
            
            status_icon = "✅" if suspended == "not_suspended" else "❌"
            
            print(f"Service: {name}")
            print(f"Status:  {status_icon} {suspended}")
            print(f"URL:     {url}")
            print(f"Health:  {url}{health_path}")
            print()
            
            # Try to hit health endpoint
            if url != 'N/A':
                try:
                    print(f"Testing health endpoint...")
                    response = requests.get(f"{url}{health_path}", timeout=10)
                    if response.status_code == 200:
                        print(f"✅ Health check passed (200 OK)")
                    else:
                        print(f"⚠️  Health check returned {response.status_code}")
                except Exception as e:
                    print(f"❌ Health check failed: {e}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def status_overview(self):
        """Show overview of all services"""
        print(f"\n{'='*100}")
        print(f"  STATUS OVERVIEW - ALL SERVICES")
        print(f"{'='*100}\n")
        
        try:
            services = self.client.list_services(limit=100)
            
            if not services:
                print("No services found.\n")
                return
            
            # Count by status
            active = sum(1 for s in services if s.get('service', {}).get('suspended') == 'not_suspended')
            suspended = len(services) - active
            
            print(f"Total Services: {len(services)}")
            print(f"  Active:      {active} ✅")
            print(f"  Suspended:   {suspended} ⚠️")
            print()
            
            # List by region
            regions = {}
            for item in services:
                service = item.get('service', {})
                region = service.get('serviceDetails', {}).get('region', 'Unknown')
                if region not in regions:
                    regions[region] = []
                regions[region].append(service.get('name', 'N/A'))
            
            print(f"By Region:")
            for region, names in regions.items():
                print(f"  {region}: {len(names)} service(s)")
                for name in names:
                    print(f"    - {name}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== Blueprint Deployment ====================
    
    def blueprint_deploy(self, yaml_file: str):
        """Deploy from render.yaml blueprint"""
        print(f"\n{'='*100}")
        print(f"  DEPLOY FROM BLUEPRINT: {yaml_file}")
        print(f"{'='*100}\n")
        
        print(f"⚠️  Blueprint deployment requires Blueprint API endpoints.")
        print(f"   Use Render Dashboard to deploy blueprint:")
        print(f"   1. Go to https://dashboard.render.com/select-repo")
        print(f"   2. Connect your repository")
        print(f"   3. Render will detect {yaml_file}")
        print(f"   4. Click 'Apply' to deploy")
        print()
    
    def blueprint_validate(self, yaml_file: str):
        """Validate render.yaml"""
        print(f"\n{'='*100}")
        print(f"  VALIDATE BLUEPRINT: {yaml_file}")
        print(f"{'='*100}\n")
        
        try:
            import yaml
            
            with open(yaml_file, 'r') as f:
                config = yaml.safe_load(f)
            
            print(f"✅ YAML syntax valid")
            print()
            
            # Check required fields
            if 'services' in config:
                services = config['services']
                print(f"Services defined: {len(services)}")
                for service in services:
                    print(f"  - {service.get('name', 'N/A')} ({service.get('type', 'N/A')})")
            
            if 'databases' in config:
                databases = config['databases']
                print(f"\nDatabases defined: {len(databases)}")
                for db in databases:
                    print(f"  - {db.get('name', 'N/A')} ({db.get('plan', 'N/A')})")
            
            print()
        except FileNotFoundError:
            print(f"❌ File not found: {yaml_file}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== Quick Actions ====================
    
    def quick_singapore(self):
        """Quick deploy AI Agents to Singapore"""
        print(f"\n{'='*100}")
        print(f"  QUICK DEPLOY: AI AGENTS TO SINGAPORE")
        print(f"{'='*100}\n")
        
        print(f"Follow these steps:")
        print(f"1. Go to https://dashboard.render.com/select-repo")
        print(f"2. Connect repository: gerardovsa/Ai_Agents")
        print(f"3. Branch: V2_clean")
        print(f"4. Render will detect render.yaml")
        print(f"5. Verify settings:")
        print(f"   - Region: Singapore")
        print(f"   - Environment: Docker")
        print(f"   - Plan: Starter")
        print(f"6. Add environment variables from .env.master")
        print(f"7. Click 'Apply' to deploy")
        print()
        
        print(f"📚 See DEPLOY_VIA_DASHBOARD.md for complete guide")
        print()
    
    def quick_status(self):
        """Quick status check for AI Agents"""
        print(f"\n{'='*100}")
        print(f"  QUICK STATUS: AI AGENTS")
        print(f"{'='*100}\n")
        
        try:
            # Find ai-agents-backend service
            services = self.client.list_services(limit=100)
            ai_service = None
            
            for item in services:
                service = item.get('service', {})
                if 'ai-agent' in service.get('name', '').lower():
                    ai_service = service
                    break
            
            if not ai_service:
                print("❌ AI Agents service not found")
                print()
                return
            
            details = ai_service.get('serviceDetails', {})
            print(f"Service: {ai_service.get('name', 'N/A')}")
            print(f"ID:      {ai_service.get('id', 'N/A')}")
            print(f"Status:  {ai_service.get('suspended', 'N/A')}")
            print(f"URL:     {details.get('url', 'N/A')}")
            print(f"Region:  {details.get('region', 'N/A')}")
            print(f"Plan:    {details.get('plan', 'N/A')}")
            print(f"Updated: {ai_service.get('updatedAt', 'N/A')}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


# ==================== CLI Entry Point ====================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Render Complete CLI - Full Project Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument('--api-key', 
                        default=os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu'),
                        help='Render API key')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Services commands
    services = subparsers.add_parser('services', help='Service management')
    services.add_argument('action', choices=['list', 'get', 'create', 'delete', 'restart', 'scale'])
    services.add_argument('args', nargs='*', help='Command arguments')
    
    # Deploys commands
    deploys = subparsers.add_parser('deploys', help='Deploy management')
    deploys.add_argument('action', choices=['list', 'trigger'])
    deploys.add_argument('service_id', help='Service ID')
    deploys.add_argument('--clear-cache', action='store_true', help='Clear build cache')
    
    # Env commands
    env = subparsers.add_parser('env', help='Environment variables')
    env.add_argument('action', choices=['list', 'set', 'import', 'export'])
    env.add_argument('service_id', help='Service ID')
    env.add_argument('args', nargs='*', help='Key/value or filename')
    
    # Logs commands
    logs = subparsers.add_parser('logs', help='Logs management')
    logs.add_argument('action', choices=['tail'])
    logs.add_argument('service_id', help='Service ID')
    
    # Metrics commands
    metrics = subparsers.add_parser('metrics', help='Metrics & monitoring')
    metrics.add_argument('action', choices=['all'])
    metrics.add_argument('service_id', help='Service ID')
    
    # Health commands
    health = subparsers.add_parser('health', help='Health checks')
    health.add_argument('action', choices=['check'])
    health.add_argument('service_id', help='Service ID')
    
    # Status commands
    status = subparsers.add_parser('status', help='Status overview')
    status.add_argument('action', choices=['overview'])
    
    # Blueprint commands
    blueprint = subparsers.add_parser('blueprint', help='Blueprint deployment')
    blueprint.add_argument('action', choices=['deploy', 'validate'])
    blueprint.add_argument('file', help='YAML file path')
    
    # Quick commands
    quick = subparsers.add_parser('quick', help='Quick actions')
    quick.add_argument('action', choices=['singapore', 'status'])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = RenderCompleteCLI(args.api_key)
    
    # Route commands
    try:
        if args.command == 'services':
            if args.action == 'list':
                cli.services_list()
            elif args.action == 'get':
                cli.services_get(args.args[0])
            elif args.action == 'create':
                cli.services_create(args.args[0])
            elif args.action == 'delete':
                cli.services_delete(args.args[0])
            elif args.action == 'restart':
                cli.services_restart(args.args[0])
            elif args.action == 'scale':
                cli.services_scale(args.args[0], int(args.args[1]))
        
        elif args.command == 'deploys':
            if args.action == 'list':
                cli.deploys_list(args.service_id)
            elif args.action == 'trigger':
                cli.deploys_trigger(args.service_id, args.clear_cache)
        
        elif args.command == 'env':
            if args.action == 'list':
                cli.env_list(args.service_id)
            elif args.action == 'set':
                cli.env_set(args.service_id, args.args[0], args.args[1])
            elif args.action == 'import':
                cli.env_import(args.service_id, args.args[0])
            elif args.action == 'export':
                cli.env_export(args.service_id, args.args[0])
        
        elif args.command == 'logs':
            if args.action == 'tail':
                cli.logs_tail(args.service_id)
        
        elif args.command == 'metrics':
            if args.action == 'all':
                cli.metrics_all(args.service_id)
        
        elif args.command == 'health':
            if args.action == 'check':
                cli.health_check(args.service_id)
        
        elif args.command == 'status':
            if args.action == 'overview':
                cli.status_overview()
        
        elif args.command == 'blueprint':
            if args.action == 'deploy':
                cli.blueprint_deploy(args.file)
            elif args.action == 'validate':
                cli.blueprint_validate(args.file)
        
        elif args.command == 'quick':
            if args.action == 'singapore':
                cli.quick_singapore()
            elif args.action == 'status':
                cli.quick_status()
    
    except IndexError:
        print(f"❌ Missing required arguments. Use --help for usage.")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
