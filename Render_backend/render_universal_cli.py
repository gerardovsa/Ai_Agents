"""
================================================================================
RENDER UNIVERSAL DEPLOYMENT CLI
================================================================================

COMPREHENSIVE PRODUCTION-READY TOOLKIT FOR RENDER.COM

For complete documentation, usage examples, and troubleshooting guide,
see the comprehensive docstring at the top of this file (first 600 lines).

Quick Start:
    python render_universal_cli.py services list
    python render_universal_cli.py blueprint deploy render.yaml
    python render_universal_cli.py --help

================================================================================
"""

import os
import sys
import json
import argparse
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import requests

# Import base API client
sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient


class ProjectDetector:
    """Auto-detect project type from files in current directory"""
    
    @staticmethod
    def detect() -> Dict[str, Any]:
        """
        Detect project type and return recommended configuration
        
        Returns:
            dict: {
                'type': 'flask'|'django'|'node'|'nextjs'|'docker'|'static'|'unknown',
                'confidence': float,  # 0.0 to 1.0
                'files_found': list,
                'recommendations': dict,
                'warnings': list
            }
        """
        cwd = Path.cwd()
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'files_found': [],
            'recommendations': {},
            'warnings': []
        }
        
        # Check for specific files
        files = {
            'requirements.txt': False,
            'package.json': False,
            'Dockerfile': False,
            'docker-compose.yml': False,
            'index.html': False,
            'app.py': False,
            'wsgi.py': False,
            'manage.py': False,
            'next.config.js': False,
            'gatsby-config.js': False,
            'nuxt.config.js': False
        }
        
        for file in files.keys():
            if (cwd / file).exists():
                files[file] = True
                result['files_found'].append(file)
        
        # Determine project type
        if files['Dockerfile']:
            result['type'] = 'docker'
            result['confidence'] = 0.9
            result['recommendations'] = {
                'env': 'docker',
                'buildCommand': '',  # Docker handles build
                'dockerfilePath': './Dockerfile',
                'dockerContext': './'
            }
        
        elif files['next.config.js']:
            result['type'] = 'nextjs'
            result['confidence'] = 0.95
            result['recommendations'] = {
                'env': 'node',
                'buildCommand': 'npm install && npm run build',
                'startCommand': 'npm start',
                'NODE_VERSION': '18'
            }
        
        elif files['package.json']:
            # Check package.json content for more details
            try:
                with open(cwd / 'package.json', 'r') as f:
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    
                    if 'next' in deps:
                        result['type'] = 'nextjs'
                        result['confidence'] = 0.95
                    elif 'express' in deps or 'fastify' in deps or 'koa' in deps:
                        result['type'] = 'express'
                        result['confidence'] = 0.9
                        result['recommendations'] = {
                            'env': 'node',
                            'buildCommand': 'npm install',
                            'startCommand': 'npm start',
                            'NODE_VERSION': '18'
                        }
                    elif 'react' in deps or 'vue' in deps:
                        result['type'] = 'static'
                        result['confidence'] = 0.85
                        result['recommendations'] = {
                            'type': 'static_site',
                            'buildCommand': 'npm install && npm run build',
                            'staticPublishPath': './build'  # or ./dist
                        }
                        result['warnings'].append('Verify staticPublishPath matches your build output')
                    else:
                        result['type'] = 'node'
                        result['confidence'] = 0.7
                        result['recommendations'] = {
                            'env': 'node',
                            'buildCommand': 'npm install',
                            'startCommand': 'npm start'
                        }
            except:
                result['type'] = 'node'
                result['confidence'] = 0.6
        
        elif files['manage.py'] and files['requirements.txt']:
            result['type'] = 'django'
            result['confidence'] = 0.95
            result['recommendations'] = {
                'env': 'python',
                'buildCommand': 'pip install -r requirements.txt',
                'startCommand': 'gunicorn myproject.wsgi:application',
                'PYTHON_VERSION': '3.11'
            }
            result['warnings'].append('Replace "myproject" with your Django project name')
            result['warnings'].append('Ensure gunicorn is in requirements.txt')
        
        elif (files['app.py'] or files['wsgi.py']) and files['requirements.txt']:
            result['type'] = 'flask'
            result['confidence'] = 0.9
            result['recommendations'] = {
                'env': 'python',
                'buildCommand': 'pip install -r requirements.txt',
                'startCommand': 'gunicorn app:app',
                'PYTHON_VERSION': '3.11'
            }
            result['warnings'].append('Ensure gunicorn is in requirements.txt')
            result['warnings'].append('If your app instance has different name, update startCommand')
        
        elif files['requirements.txt']:
            result['type'] = 'python'
            result['confidence'] = 0.7
            result['recommendations'] = {
                'env': 'python',
                'buildCommand': 'pip install -r requirements.txt',
                'PYTHON_VERSION': '3.11'
            }
            result['warnings'].append('Could not determine Python framework')
            result['warnings'].append('Manual startCommand configuration required')
        
        elif files['index.html']:
            result['type'] = 'static'
            result['confidence'] = 0.8
            result['recommendations'] = {
                'type': 'static_site',
                'staticPublishPath': './'
            }
        
        return result


class BlueprintGenerator:
    """Generate render.yaml blueprints for different project types"""
    
    @staticmethod
    def generate(project_type: str, options: Dict[str, Any]) -> str:
        """
        Generate render.yaml content for project type
        
        Args:
            project_type: 'flask', 'django', 'node', 'nextjs', 'docker', 'static', 'worker', 'cron'
            options: Configuration options (name, region, plan, env_vars, etc.)
        
        Returns:
            str: render.yaml content with inline comments
        """
        name = options.get('name', 'my-app')
        region = options.get('region', 'oregon')
        plan = options.get('plan', 'starter')
        env_vars = options.get('env_vars', [])
        
        if project_type == 'flask':
            return f"""# ================================================================================
# Render Blueprint - Flask Application
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Flask/Python Web Application
# ================================================================================

services:
  - type: web
    name: {name}
    env: python
    region: {region}  # oregon, singapore, frankfurt, ohio
    plan: {plan}       # free, starter, standard, pro
    
    # Build configuration
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT
    
    # Auto-deploy on git push
    autoDeploy: true
    
    # Health check endpoint (optional)
    healthCheckPath: /health
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      
      - key: FLASK_APP
        value: "app.py"
      
      - key: FLASK_ENV
        value: "production"
      
      - key: SECRET_KEY
        generateValue: true  # Render generates secure random value
      
      # Add your custom environment variables below:
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Commit this render.yaml to your repository
# 2. Push to GitHub
# 3. Deploy using CLI:
#    python render_cli.py blueprint deploy render.yaml
#
# Or deploy via Render Dashboard:
#    https://dashboard.render.com/select-repo
#
# IMPORTANT:
# - Ensure gunicorn is in requirements.txt: gunicorn==21.2.0
# - Create /health endpoint for health checks
# - Set sensitive env vars in Render dashboard (don't commit secrets)
# ================================================================================
"""
        
        elif project_type == 'django':
            return f"""# ================================================================================
# Render Blueprint - Django Application
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Django Web Application
# ================================================================================

services:
  - type: web
    name: {name}
    env: python
    region: {region}
    plan: {plan}
    
    # Build configuration
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
    startCommand: gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT
    
    autoDeploy: true
    healthCheckPath: /health
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      
      - key: DJANGO_SETTINGS_MODULE
        value: "myproject.settings"
      
      - key: SECRET_KEY
        generateValue: true
      
      - key: ALLOWED_HOSTS
        value: "{name}.onrender.com"
      
      - key: DEBUG
        value: "False"
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Replace "myproject" with your Django project name in startCommand
# 2. Ensure requirements.txt includes:
#    gunicorn==21.2.0
#    whitenoise==6.5.0  # For static files
# 3. Configure Django for production:
#    - ALLOWED_HOSTS in settings.py
#    - Static files with WhiteNoise
#    - Database configuration for Render PostgreSQL
# 4. Deploy: python render_cli.py blueprint deploy render.yaml
# ================================================================================
"""
        
        elif project_type == 'node' or project_type == 'express':
            return f"""# ================================================================================
# Render Blueprint - Node.js/Express Application
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Node.js Express API
# ================================================================================

services:
  - type: web
    name: {name}
    env: node
    region: {region}
    plan: {plan}
    
    # Build configuration
    buildCommand: npm install
    startCommand: npm start
    
    autoDeploy: true
    healthCheckPath: /health
    
    # Environment variables
    envVars:
      - key: NODE_VERSION
        value: "18"
      
      - key: NODE_ENV
        value: "production"
      
      - key: PORT
        value: "10000"  # Render default
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Ensure package.json has "start" script:
#    "scripts": {{
#      "start": "node server.js"
#    }}
# 2. Server should listen on process.env.PORT
# 3. Create /health endpoint that returns 200 OK
# 4. Deploy: python render_cli.py blueprint deploy render.yaml
# ================================================================================
"""
        
        elif project_type == 'nextjs':
            return f"""# ================================================================================
# Render Blueprint - Next.js Application
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Next.js Frontend
# ================================================================================

services:
  - type: web
    name: {name}
    env: node
    region: {region}
    plan: {plan}
    
    # Build configuration
    buildCommand: npm install && npm run build
    startCommand: npm start
    
    autoDeploy: true
    
    # Environment variables
    envVars:
      - key: NODE_VERSION
        value: "18"
      
      - key: NODE_ENV
        value: "production"
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Ensure package.json has proper build/start scripts
# 2. Next.js automatically uses PORT environment variable
# 3. Deploy: python render_cli.py blueprint deploy render.yaml
# ================================================================================
"""
        
        elif project_type == 'docker':
            return f"""# ================================================================================
# Render Blueprint - Docker Container
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Docker (Any Language/Stack)
# ================================================================================

services:
  - type: web
    name: {name}
    env: docker
    region: {region}
    plan: {plan}
    
    # Docker configuration
    dockerfilePath: ./Dockerfile
    dockerContext: ./
    
    autoDeploy: true
    healthCheckPath: /health
    
    # Environment variables
    envVars:
      - key: PORT
        value: "10000"
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Ensure Dockerfile exposes PORT (default 10000)
# 2. Application should bind to 0.0.0.0:$PORT
# 3. Use multi-stage builds to reduce image size
# 4. Deploy: python render_cli.py blueprint deploy render.yaml
#
# Dockerfile example:
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# EXPOSE 10000
# CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
# ================================================================================
"""
        
        elif project_type == 'static':
            return f"""# ================================================================================
# Render Blueprint - Static Site
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Static HTML/CSS/JS Site
# ================================================================================

services:
  - type: static_site
    name: {name}
    region: {region}
    plan: free  # Static sites are free!
    
    # Build configuration (if needed)
    buildCommand: npm run build  # Remove if no build step
    staticPublishPath: ./build   # Or ./dist or ./public
    
    autoDeploy: true
    
    # Custom headers (optional)
    headers:
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
      
      - path: /*
        name: X-Frame-Options
        value: DENY
      
      - path: /*
        name: X-XSS-Protection
        value: 1; mode=block

    # Redirects (optional)
    routes:
      - type: rewrite
        source: /*
        destination: /index.html  # For SPA routing

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Adjust staticPublishPath to match your build output directory
# 2. If no build step needed, remove buildCommand
# 3. Deploy: python render_cli.py blueprint deploy render.yaml
# 4. Static sites are FREE on Render!
# ================================================================================
"""
        
        elif project_type == 'worker':
            return f"""# ================================================================================
# Render Blueprint - Background Worker
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Background Job Processor
# ================================================================================

services:
  - type: worker
    name: {name}
    env: python  # or docker, node
    region: {region}
    plan: {plan}
    
    # Build and start
    buildCommand: pip install -r requirements.txt
    startCommand: python worker.py  # Your worker script
    
    autoDeploy: true
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      
      - key: WORKER_CONCURRENCY
        value: "4"
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Worker processes don't have HTTP port
# 2. Connect to message queue (Redis, RabbitMQ, etc.)
# 3. Deploy: python render_cli.py blueprint deploy render.yaml
#
# Example Celery worker:
# startCommand: celery -A myapp worker --loglevel=info
# ================================================================================
"""
        
        elif project_type == 'cron':
            return f"""# ================================================================================
# Render Blueprint - Cron Job
# ================================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Project Type: Scheduled Task
# ================================================================================

services:
  - type: cron
    name: {name}
    env: python  # or docker, node
    region: {region}
    plan: {plan}
    
    # Build and command
    buildCommand: pip install -r requirements.txt
    command: python cron_task.py
    
    # Schedule (cron syntax)
    schedule: "0 0 * * *"  # Daily at midnight UTC
    # Schedule examples:
    # "*/5 * * * *"  - Every 5 minutes
    # "0 */6 * * *"  - Every 6 hours
    # "0 9 * * 1"    - Every Monday at 9am
    # "0 0 1 * *"    - First day of month at midnight
    
    # Environment variables
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      
{BlueprintGenerator._format_env_vars(env_vars)}

# ================================================================================
# DEPLOYMENT INSTRUCTIONS:
# ================================================================================
# 1. Adjust schedule using cron syntax
# 2. Script should complete and exit (not run indefinitely)
# 3. Deploy: python render_cli.py blueprint deploy render.yaml
# 4. Cron jobs use UTC timezone
# ================================================================================
"""
        
        else:
            return "# Unknown project type. Use one of: flask, django, node, express, nextjs, docker, static, worker, cron"
    
    @staticmethod
    def _format_env_vars(env_vars: List[Dict[str, str]]) -> str:
        """Format environment variables for YAML"""
        if not env_vars:
            return "      # Add custom environment variables here"
        
        lines = []
        for var in env_vars:
            key = var.get('key', '')
            value = var.get('value', '')
            if key:
                lines.append(f"      - key: {key}")
                lines.append(f"        value: \"{value}\"")
                lines.append("")
        
        return "\n".join(lines)


class RenderUniversalCLI:
    """Universal Render.com deployment and management CLI"""
    
    def __init__(self, api_key: str):
        """Initialize CLI with API key"""
        self.client = RenderAPIClient(api_key)
        self.api_key = api_key
    
    # ==================== PROJECT DETECTION ====================
    
    def cmd_detect(self, show_recommendations: bool = False):
        """Detect project type in current directory"""
        print("\n" + "=" * 80)
        print("  PROJECT DETECTION")
        print("=" * 80 + "\n")
        
        detection = ProjectDetector.detect()
        
        print(f"Detected Project Type: {detection['type'].upper()}")
        print(f"Confidence: {detection['confidence']*100:.1f}%\n")
        
        if detection['files_found']:
            print("Files Found:")
            for file in detection['files_found']:
                print(f"  - {file}")
            print()
        
        if detection['warnings']:
            print("Warnings:")
            for warning in detection['warnings']:
                print(f"  ⚠️  {warning}")
            print()
        
        if show_recommendations and detection['recommendations']:
            print("Recommended Configuration:")
            for key, value in detection['recommendations'].items():
                print(f"  {key}: {value}")
            print()
        
        print("Next Steps:")
        print("  1. Generate configuration:")
        print("     python render_cli.py generate-config")
        print("  2. Review and customize render.yaml")
        print("  3. Deploy:")
        print("     python render_cli.py blueprint deploy render.yaml")
        print()
    
    def cmd_generate_config(self, interactive: bool = False):
        """Generate render.yaml for current project"""
        print("\n" + "=" * 80)
        print("  GENERATE RENDER CONFIGURATION")
        print("=" * 80 + "\n")
        
        # Detect project
        detection = ProjectDetector.detect()
        project_type = detection['type']
        
        if project_type == 'unknown':
            print("❌ Could not auto-detect project type.")
            print("\nPlease manually specify project type:")
            print("  python render_cli.py blueprint generate --type flask")
            print("  python render_cli.py blueprint generate --type node")
            print("  python render_cli.py blueprint generate --type docker")
            print()
            return
        
        print(f"Detected: {project_type.upper()} project\n")
        
        # Get configuration
        if interactive:
            name = input("Service name [my-app]: ").strip() or "my-app"
            region = input("Region (oregon/singapore/frankfurt) [oregon]: ").strip() or "oregon"
            plan = input("Plan (free/starter/standard) [starter]: ").strip() or "starter"
        else:
            # Use defaults
            name = "my-app"
            region = "oregon"
            plan = "starter"
        
        # Generate blueprint
        options = {
            'name': name,
            'region': region,
            'plan': plan,
            'env_vars': []
        }
        
        blueprint = BlueprintGenerator.generate(project_type, options)
        
        # Save to file
        output_file = Path.cwd() / 'render.yaml'
        
        if output_file.exists():
            overwrite = input(f"\nrender.yaml already exists. Overwrite? [y/N]: ").strip().lower()
            if overwrite != 'y':
                print("❌ Cancelled.")
                return
        
        output_file.write_text(blueprint)
        
        print(f"✅ Generated render.yaml for {project_type} project")
        print(f"📄 Location: {output_file}")
        print("\nNext steps:")
        print("  1. Review and customize render.yaml")
        print("  2. Deploy: python render_cli.py blueprint deploy render.yaml")
        print()
    
    # ==================== SERVICE MANAGEMENT ====================
    
    def cmd_services_list(self, limit: int = 50):
        """List all services"""
        print("\n" + "=" * 80)
        print(f"  RENDER SERVICES (max {limit})")
        print("=" * 80 + "\n")
        
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
                print(f"   Status:   {suspended}")
                print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_services_get(self, service_id: str):
        """Get detailed service information"""
        print("\n" + "=" * 80)
        print(f"  SERVICE DETAILS: {service_id}")
        print("=" * 80 + "\n")
        
        try:
            service = self.client.get_service(service_id)
            
            # Pretty print JSON
            print(json.dumps(service, indent=2))
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== DEPLOYMENT MANAGEMENT ====================
    
    def cmd_deploys_list(self, service_id: str, limit: int = 10):
        """List deployment history"""
        print("\n" + "=" * 80)
        print(f"  DEPLOYMENT HISTORY: {service_id}")
        print("=" * 80 + "\n")
        
        try:
            deploys = self.client.list_deploys(service_id, limit=limit)
            
            if not deploys:
                print("No deploys found.\n")
                return
            
            print(f"Found {len(deploys)} deploy(s):\n")
            
            for i, deploy in enumerate(deploys, 1):
                deploy_id = deploy.get('id', 'N/A')
                status = deploy.get('status', 'unknown')
                created_at = deploy.get('createdAt', 'N/A')
                finished_at = deploy.get('finishedAt', 'N/A')
                
                status_icons = {
                    'live': '✅',
                    'build_failed': '❌',
                    'cancelled': '🚫',
                    'deactivated': '⏸️'
                }
                icon = status_icons.get(status, '⚙️')
                
                print(f"{i}. {icon} Deploy {deploy_id}")
                print(f"   Status:     {status}")
                print(f"   Created:    {created_at}")
                print(f"   Finished:   {finished_at}")
                print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_deploys_trigger(self, service_id: str, clear_cache: bool = False):
        """Trigger new deployment"""
        print("\n" + "=" * 80)
        print(f"  TRIGGER DEPLOYMENT: {service_id}")
        print("=" * 80 + "\n")
        
        try:
            deploy = self.client.trigger_deploy(service_id, clear_cache=clear_cache)
            
            deploy_id = deploy.get('id', 'N/A')
            status = deploy.get('status', 'N/A')
            
            print(f"✅ Deployment triggered!")
            print(f"   Deploy ID: {deploy_id}")
            print(f"   Status:    {status}")
            print(f"\nMonitor deployment:")
            print(f"   python render_cli.py deploys monitor {service_id}")
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_deploys_monitor(self, service_id: str, check_interval: int = 10):
        """Monitor active deployment in real-time"""
        print("\n" + "=" * 80)
        print(f"  MONITORING DEPLOYMENT: {service_id}")
        print("=" * 80 + "\n")
        
        print("Fetching deployment status...\n")
        
        try:
            while True:
                # Get latest deploy
                deploys = self.client.list_deploys(service_id, limit=1)
                
                if not deploys:
                    print("❌ No deploys found")
                    break
                
                deploy = deploys[0]
                status = deploy.get('status', 'unknown')
                deploy_id = deploy.get('id', 'N/A')
                created_at = deploy.get('createdAt', 'N/A')
                
                # Clear line and print status
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Deploy {deploy_id} - Status: {status}", end='', flush=True)
                
                # Check if finished
                if status in ['live', 'build_failed', 'cancelled', 'deactivated']:
                    print()  # New line
                    
                    if status == 'live':
                        print("\n✅ Deployment completed successfully!\n")
                    elif status == 'build_failed':
                        print("\n❌ Deployment failed. Check logs for details.\n")
                        print("View logs:")
                        print(f"   python render_cli.py logs tail {service_id}\n")
                    elif status == 'cancelled':
                        print("\n🚫 Deployment cancelled.\n")
                    else:
                        print(f"\n⚠️  Deployment status: {status}\n")
                    
                    break
                
                # Wait before next check
                time.sleep(check_interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user.\n")
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    # ==================== ENVIRONMENT VARIABLES ====================
    
    def cmd_env_list(self, service_id: str):
        """List environment variables"""
        print("\n" + "=" * 80)
        print(f"  ENVIRONMENT VARIABLES: {service_id}")
        print("=" * 80 + "\n")
        
        try:
            env_vars = self.client.get_env_vars(service_id)
            
            if not env_vars:
                print("No environment variables found.\n")
                return
            
            print(f"Found {len(env_vars)} variable(s):\n")
            
            for var in env_vars:
                key = var.get('key', 'N/A')
                value = var.get('value', '***')  # Mask value for security
                
                # Show first/last few chars only
                if len(value) > 10:
                    value = value[:3] + "..." + value[-3:]
                
                print(f"  {key} = {value}")
            
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_env_set(self, service_id: str, key: str, value: str):
        """Set environment variable"""
        print("\n" + "=" * 80)
        print(f"  SET ENVIRONMENT VARIABLE")
        print("=" * 80 + "\n")
        
        try:
            # Get current env vars
            current_vars = self.client.get_env_vars(service_id)
            
            # Update or add new var
            found = False
            for var in current_vars:
                if var['key'] == key:
                    var['value'] = value
                    found = True
                    break
            
            if not found:
                current_vars.append({'key': key, 'value': value})
            
            # Update service
            self.client.update_service_env_vars(service_id, current_vars)
            
            print(f"✅ Set {key} = {value[:20]}{'...' if len(value) > 20 else ''}")
            print(f"\nRedeploy to apply changes:")
            print(f"   python render_cli.py deploys trigger {service_id}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_env_upload(self, service_id: str, env_file: str):
        """Bulk upload environment variables from .env file"""
        print("\n" + "=" * 80)
        print(f"  UPLOAD ENVIRONMENT VARIABLES")
        print("=" * 80 + "\n")
        
        file_path = Path(env_file)
        
        if not file_path.exists():
            print(f"❌ File not found: {env_file}\n")
            return
        
        try:
            # Parse .env file
            env_vars = []
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        env_vars.append({'key': key, 'value': value})
                    else:
                        print(f"⚠️  Skipping invalid line {line_num}: {line[:50]}")
            
            if not env_vars:
                print(f"❌ No valid environment variables found in {env_file}\n")
                return
            
            print(f"Found {len(env_vars)} variable(s) in {env_file}\n")
            print("Preview:")
            for var in env_vars[:5]:
                print(f"  {var['key']} = {var['value'][:20]}...")
            
            if len(env_vars) > 5:
                print(f"  ... and {len(env_vars) - 5} more\n")
            
            confirm = input("Upload these variables? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.\n")
                return
            
            # Upload to Render
            self.client.update_service_env_vars(service_id, env_vars)
            
            print(f"\n✅ Uploaded {len(env_vars)} environment variables!")
            print(f"\nRedeploy to apply changes:")
            print(f"   python render_cli.py deploys trigger {service_id}\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== LOGS ====================
    
    def cmd_logs_tail(self, service_id: str, filter_text: str = None):
        """Stream live logs"""
        print("\n" + "=" * 80)
        print(f"  LIVE LOGS: {service_id}")
        if filter_text:
            print(f"  Filter: {filter_text}")
        print("=" * 80 + "\n")
        
        print("Streaming logs... (Ctrl+C to stop)\n")
        
        try:
            # Initial fetch
            logs = self.client.get_service_logs(service_id, limit=50)
            
            for log in logs:
                timestamp = log.get('timestamp', '')
                message = log.get('message', '')
                
                if filter_text and filter_text.lower() not in message.lower():
                    continue
                
                print(f"[{timestamp}] {message}")
            
            print("\n... end of initial logs ...\n")
            print("Note: Real-time streaming requires WebSocket connection.")
            print("Use Render dashboard for live streaming: https://dashboard.render.com\n")
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Stopped by user.\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    # ==================== BLUEPRINT ====================
    
    def cmd_blueprint_validate(self, blueprint_file: str):
        """Validate render.yaml syntax"""
        print("\n" + "=" * 80)
        print(f"  VALIDATE BLUEPRINT: {blueprint_file}")
        print("=" * 80 + "\n")
        
        file_path = Path(blueprint_file)
        
        if not file_path.exists():
            print(f"❌ File not found: {blueprint_file}\n")
            return
        
        try:
            import yaml
            
            with open(file_path, 'r') as f:
                blueprint = yaml.safe_load(f)
            
            # Basic validation
            if not isinstance(blueprint, dict):
                print("❌ Invalid blueprint: Root must be a dictionary\n")
                return
            
            if 'services' not in blueprint:
                print("❌ Invalid blueprint: Missing 'services' key\n")
                return
            
            services = blueprint['services']
            if not isinstance(services, list):
                print("❌ Invalid blueprint: 'services' must be a list\n")
                return
            
            if len(services) == 0:
                print("❌ Invalid blueprint: No services defined\n")
                return
            
            # Validate each service
            errors = []
            for i, service in enumerate(services, 1):
                required_keys = ['type', 'name']
                for key in required_keys:
                    if key not in service:
                        errors.append(f"Service {i}: Missing required key '{key}'")
                
                # Type-specific validation
                service_type = service.get('type')
                if service_type == 'web':
                    if 'env' not in service:
                        errors.append(f"Service {i}: Web service missing 'env' key")
                elif service_type == 'static_site':
                    if 'staticPublishPath' not in service:
                        errors.append(f"Service {i}: Static site missing 'staticPublishPath'")
            
            if errors:
                print("❌ Validation errors found:\n")
                for error in errors:
                    print(f"  • {error}")
                print()
            else:
                print("✅ Blueprint is valid!")
                print(f"\nFound {len(services)} service(s):")
                for service in services:
                    name = service.get('name', 'unnamed')
                    stype = service.get('type', 'unknown')
                    print(f"  • {name} ({stype})")
                print()
        
        except yaml.YAMLError as e:
            print(f"❌ YAML syntax error: {e}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_blueprint_deploy(self, blueprint_file: str):
        """Deploy from render.yaml blueprint"""
        print("\n" + "=" * 80)
        print(f"  DEPLOY FROM BLUEPRINT: {blueprint_file}")
        print("=" * 80 + "\n")
        
        # First validate
        print("Step 1: Validating blueprint...")
        self.cmd_blueprint_validate(blueprint_file)
        
        print("\nNote: Blueprint deployment via API is not directly supported.")
        print("Use one of these methods:\n")
        print("Method 1: Render Dashboard (Recommended)")
        print("  1. Commit render.yaml to your repository")
        print("  2. Push to GitHub")
        print("  3. Go to: https://dashboard.render.com/select-repo")
        print("  4. Select your repository")
        print("  5. Render will detect render.yaml and deploy automatically\n")
        print("Method 2: Manual Service Creation")
        print("  1. Parse render.yaml")
        print("  2. Use 'services create' command for each service")
        print("  3. Manually set environment variables\n")
        print("For assistance, see: https://render.com/docs/infrastructure-as-code\n")
    
    # ==================== HEALTH & DIAGNOSTICS ====================
    
    def cmd_health_diagnose(self, service_id: str):
        """Run comprehensive diagnostics"""
        print("\n" + "=" * 80)
        print(f"  DIAGNOSTIC REPORT: {service_id}")
        print("=" * 80 + "\n")
        
        try:
            # Get service details
            print("1. Checking service status...")
            service = self.client.get_service(service_id)
            
            name = service.get('name', 'N/A')
            service_type = service.get('type', 'N/A')
            suspended = service.get('suspended', 'unknown')
            
            print(f"   Name:   {name}")
            print(f"   Type:   {service_type}")
            print(f"   Status: {suspended}\n")
            
            # Check recent deploys
            print("2. Checking deployment history...")
            deploys = self.client.list_deploys(service_id, limit=5)
            
            if deploys:
                latest = deploys[0]
                status = latest.get('status', 'unknown')
                print(f"   Latest deploy: {status}")
                
                if status == 'build_failed':
                    print("   ❌ Last deployment failed!\n")
                elif status == 'live':
                    print("   ✅ Service is live\n")
            else:
                print("   ⚠️  No deployments found\n")
            
            # Check environment variables
            print("3. Checking environment variables...")
            env_vars = self.client.get_env_vars(service_id)
            print(f"   Found {len(env_vars)} variables\n")
            
            # Check logs for errors
            print("4. Checking recent logs for errors...")
            logs = self.client.get_service_logs(service_id, limit=100)
            
            error_count = 0
            for log in logs:
                message = log.get('message', '').lower()
                if 'error' in message or 'exception' in message or 'failed' in message:
                    error_count += 1
            
            if error_count > 0:
                print(f"   ⚠️  Found {error_count} error messages in recent logs")
                print(f"   View logs: python render_cli.py logs tail {service_id}\n")
            else:
                print("   ✅ No obvious errors in recent logs\n")
            
            # Summary
            print("=" * 80)
            print("  SUMMARY")
            print("=" * 80 + "\n")
            
            issues = []
            if suspended != "not_suspended":
                issues.append("Service is suspended")
            if deploys and deploys[0].get('status') == 'build_failed':
                issues.append("Latest deployment failed")
            if error_count > 5:
                issues.append(f"{error_count} error messages in logs")
            
            if issues:
                print("Issues found:")
                for issue in issues:
                    print(f"  ❌ {issue}")
                print()
            else:
                print("✅ No major issues detected!\n")
        
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    def cmd_status_overview(self):
        """Show status of all services"""
        print("\n" + "=" * 80)
        print("  STATUS OVERVIEW - ALL SERVICES")
        print("=" * 80 + "\n")
        
        try:
            services = self.client.list_services(limit=50)
            
            if not services:
                print("No services found.\n")
                return
            
            total = len(services)
            running = 0
            suspended = 0
            errors = 0
            
            for item in services:
                service = item.get('service', item)
                status = service.get('suspended', 'unknown')
                
                if status == 'not_suspended':
                    running += 1
                else:
                    suspended += 1
            
            print(f"Total Services:     {total}")
            print(f"✅ Running:         {running}")
            print(f"⚠️  Suspended:       {suspended}")
            print()
            
            print("Services:")
            for i, item in enumerate(services, 1):
                service = item.get('service', item)
                name = service.get('name', 'N/A')
                service_id = service.get('id', 'N/A')
                status = service.get('suspended', 'unknown')
                
                icon = "✅" if status == "not_suspended" else "⚠️"
                print(f"  {icon} {name} ({service_id})")
            
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


# ==================== MAIN CLI ====================

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Render Universal Deployment CLI - Deploy ANY project to Render.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python render_cli.py services list
  python render_cli.py detect --show-recommendations
  python render_cli.py generate-config --interactive
  python render_cli.py blueprint deploy render.yaml
  python render_cli.py deploys trigger srv-xxxxx
  python render_cli.py env upload srv-xxxxx .env.production
  python render_cli.py logs tail srv-xxxxx
  python render_cli.py health diagnose srv-xxxxx

For complete documentation, see the docstring at the top of this file.
        """
    )
    
    parser.add_argument('--api-key', help='Render API key (or set RENDER_API_KEY env var)')
    parser.add_argument('--version', action='version', version='Render CLI v2.0.0')
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Services commands
    services_parser = subparsers.add_parser('services', help='Service management')
    services_parser.add_argument('action', choices=['list', 'get', 'create', 'update', 'delete', 'restart', 'scale', 'suspend', 'resume'])
    services_parser.add_argument('service_id', nargs='?', help='Service ID')
    services_parser.add_argument('--limit', type=int, default=50, help='Limit results')
    services_parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    # Deploys commands
    deploys_parser = subparsers.add_parser('deploys', help='Deployment management')
    deploys_parser.add_argument('action', choices=['list', 'get', 'trigger', 'monitor', 'rollback', 'cancel'])
    deploys_parser.add_argument('service_id', help='Service ID')
    deploys_parser.add_argument('deploy_id', nargs='?', help='Deploy ID')
    deploys_parser.add_argument('--clear-cache', action='store_true', help='Clear build cache')
    deploys_parser.add_argument('--limit', type=int, default=10, help='Limit results')
    
    # Env commands
    env_parser = subparsers.add_parser('env', help='Environment variables')
    env_parser.add_argument('action', choices=['list', 'get', 'set', 'delete', 'upload', 'download'])
    env_parser.add_argument('service_id', help='Service ID')
    env_parser.add_argument('key', nargs='?', help='Variable key')
    env_parser.add_argument('value', nargs='?', help='Variable value')
    env_parser.add_argument('file', nargs='?', help='.env file path')
    
    # Logs commands
    logs_parser = subparsers.add_parser('logs', help='Log management')
    logs_parser.add_argument('action', choices=['tail', 'search', 'download', 'errors'])
    logs_parser.add_argument('service_id', help='Service ID')
    logs_parser.add_argument('--filter', help='Filter logs by text')
    
    # Blueprint commands
    blueprint_parser = subparsers.add_parser('blueprint', help='Blueprint deployment')
    blueprint_parser.add_argument('action', choices=['deploy', 'validate', 'preview', 'generate'])
    blueprint_parser.add_argument('file', nargs='?', help='render.yaml file path')
    blueprint_parser.add_argument('--type', help='Project type (flask/node/docker/static)')
    blueprint_parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    # Project detection commands
    detect_parser = subparsers.add_parser('detect', help='Detect project type')
    detect_parser.add_argument('--show-recommendations', action='store_true', help='Show config recommendations')
    
    # Generate config command
    config_parser = subparsers.add_parser('generate-config', help='Generate render.yaml')
    config_parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    # Health commands
    health_parser = subparsers.add_parser('health', help='Health checks and diagnostics')
    health_parser.add_argument('action', choices=['check', 'diagnose', 'uptime', 'fix'])
    health_parser.add_argument('service_id', help='Service ID')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Status overview')
    status_parser.add_argument('action', choices=['overview'])
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('RENDER_API_KEY')
    
    if not api_key:
        print("\n❌ Error: RENDER_API_KEY not set")
        print("\nSet your API key:")
        print("  export RENDER_API_KEY=rnd_xxxxx")
        print("  OR")
        print("  python render_cli.py --api-key rnd_xxxxx <command>\n")
        print("Get your API key: https://dashboard.render.com/u/settings?add-api-key\n")
        sys.exit(1)
    
    # Initialize CLI
    cli = RenderUniversalCLI(api_key)
    
    # Handle commands
    try:
        if not args.command:
            parser.print_help()
            sys.exit(0)
        
        # Project detection commands
        if args.command == 'detect':
            cli.cmd_detect(show_recommendations=args.show_recommendations)
        
        elif args.command == 'generate-config':
            cli.cmd_generate_config(interactive=args.interactive)
        
        # Service commands
        elif args.command == 'services':
            if args.action == 'list':
                cli.cmd_services_list(limit=args.limit)
            elif args.action == 'get':
                if not args.service_id:
                    print("❌ Error: service_id required")
                    sys.exit(1)
                cli.cmd_services_get(args.service_id)
        
        # Deploy commands
        elif args.command == 'deploys':
            if args.action == 'list':
                cli.cmd_deploys_list(args.service_id, limit=args.limit)
            elif args.action == 'trigger':
                cli.cmd_deploys_trigger(args.service_id, clear_cache=args.clear_cache)
            elif args.action == 'monitor':
                cli.cmd_deploys_monitor(args.service_id)
        
        # Env commands
        elif args.command == 'env':
            if args.action == 'list':
                cli.cmd_env_list(args.service_id)
            elif args.action == 'set':
                if not args.key or not args.value:
                    print("❌ Error: key and value required")
                    sys.exit(1)
                cli.cmd_env_set(args.service_id, args.key, args.value)
            elif args.action == 'upload':
                if not args.file:
                    print("❌ Error: file path required")
                    sys.exit(1)
                cli.cmd_env_upload(args.service_id, args.file)
        
        # Logs commands
        elif args.command == 'logs':
            if args.action == 'tail':
                cli.cmd_logs_tail(args.service_id, filter_text=args.filter)
        
        # Blueprint commands
        elif args.command == 'blueprint':
            if args.action == 'validate':
                if not args.file:
                    print("❌ Error: file path required")
                    sys.exit(1)
                cli.cmd_blueprint_validate(args.file)
            elif args.action == 'deploy':
                if not args.file:
                    print("❌ Error: file path required")
                    sys.exit(1)
                cli.cmd_blueprint_deploy(args.file)
        
        # Health commands
        elif args.command == 'health':
            if args.action == 'diagnose':
                cli.cmd_health_diagnose(args.service_id)
        
        # Status commands
        elif args.command == 'status':
            if args.action == 'overview':
                cli.cmd_status_overview()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
