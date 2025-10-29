"""
Deploy AI_agents to Render.com
Automated deployment script using Render API
"""

import os
import sys
from dotenv import load_dotenv
from Render_backend.render_api_client import RenderAPIClient

# Load environment variables
load_dotenv('.env.master')

def deploy_ai_agents():
    """Deploy AI_agents Flask backend to Render.com"""
    
    print("=" * 80)
    print("🚀 DEPLOYING AI AGENTS TO RENDER.COM")
    print("=" * 80)
    
    # Initialize Render client
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key:
        print("❌ ERROR: RENDER_API_KEY not found in .env.master")
        print("   Get your API key from: https://dashboard.render.com/u/settings#api-keys")
        return False
    
    client = RenderAPIClient(api_key)
    print("✅ Render API client initialized")
    
    # Step 1: List existing services
    print("\n📋 Step 1: Checking existing services...")
    try:
        services = client.list_services(limit=100)
        print(f"   Found {len(services)} existing services")
        
        # Check if ai-agents-v2 already exists
        for item in services:
            service = item.get('service', {})
            if service.get('name') == 'ai-agents-v2':
                print(f"   ⚠️  Service 'ai-agents-v2' already exists!")
                print(f"   Service ID: {service.get('id')}")
                print(f"   URL: https://{service.get('slug')}.onrender.com")
                return True
    except Exception as e:
        print(f"   ❌ Error listing services: {e}")
        return False
    
    # Step 2: Create new web service
    print("\n🏗️  Step 2: Creating new web service...")
    
    service_config = {
        "name": "ai-agents-v2",
        "type": "web_service",
        "ownerId": None,  # Will use default owner
        "repo": "https://github.com/gerardovsa/AI_agents",
        "branch": "V2",
        "rootDir": "AI_infrastructure",
        "region": "oregon",
        "plan": "free",
        "runtime": "python3",
        "buildCommand": "pip install -r requirements.txt",
        "startCommand": "python flask_app.py",
        "envVars": [
            {
                "key": "FLASK_ENV",
                "value": "production"
            },
            {
                "key": "PORT",
                "value": "10000"
            },
            {
                "key": "PYTHONPATH",
                "value": "/opt/render/project/src"
            }
        ],
        "healthCheckPath": "/health",
        "autoDeploy": True
    }
    
    try:
        print(f"   Creating service: {service_config['name']}")
        print(f"   Repository: {service_config['repo']}")
        print(f"   Branch: {service_config['branch']}")
        print(f"   Region: {service_config['region']}")
        
        # Note: Render API requires specific payload format
        # This will need to be adjusted based on actual API response
        response = client._make_request('POST', 'services', json=service_config)
        
        service_id = response.get('service', {}).get('id')
        service_url = response.get('service', {}).get('serviceDetails', {}).get('url')
        
        print(f"\n✅ Service created successfully!")
        print(f"   Service ID: {service_id}")
        print(f"   URL: {service_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error creating service: {e}")
        print("\n💡 ALTERNATIVE APPROACH:")
        print("   Since API creation has specific requirements, please:")
        print("   1. Go to: https://dashboard.render.com/select-repo")
        print("   2. Connect your GitHub account")
        print("   3. Select 'gerardovsa/AI_agents' repository")
        print("   4. Select 'V2' branch")
        print("   5. Use these settings:")
        print("      - Name: ai-agents-v2")
        print("      - Region: Oregon")
        print("      - Branch: V2")
        print("      - Root Directory: AI_infrastructure")
        print("      - Build Command: pip install -r requirements.txt")
        print("      - Start Command: python flask_app.py")
        print("      - Plan: Free")
        return False

def show_environment_variables():
    """Show required environment variables for Render dashboard"""
    
    print("\n" + "=" * 80)
    print("🔑 REQUIRED ENVIRONMENT VARIABLES")
    print("=" * 80)
    print("\nAdd these in Render Dashboard → Environment:")
    
    env_vars = {
        "REQUIRED - AI Providers": [
            "ANTHROPIC_API_KEY",
            "OPENAI_API_KEY", 
            "DEEPSEEK_API_KEY"
        ],
        "REQUIRED - Flask": [
            "SECRET_KEY=<generate-random-32-char-string>",
            "FLASK_ENV=production",
            "PORT=10000"
        ],
        "REQUIRED - Microsoft OAuth": [
            "MICROSOFT_CLIENT_ID",
            "MICROSOFT_CLIENT_SECRET",
            "MICROSOFT_TENANT_ID=common"
        ],
        "REQUIRED - Google OAuth": [
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET"
        ],
        "OPTIONAL - Other Tools": [
            "STRIPE_SECRET_KEY",
            "WOOCOMMERCE_URL",
            "WOOCOMMERCE_KEY",
            "WOOCOMMERCE_SECRET",
            "SLACK_BOT_TOKEN",
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN"
        ]
    }
    
    for category, vars_list in env_vars.items():
        print(f"\n{category}:")
        for var in vars_list:
            print(f"  • {var}")
    
    print("\n" + "=" * 80)

def show_next_steps():
    """Show post-deployment steps"""
    
    print("\n" + "=" * 80)
    print("📋 NEXT STEPS AFTER DEPLOYMENT")
    print("=" * 80)
    
    steps = [
        ("1. Wait for Build", [
            "Initial build takes 5-10 minutes",
            "Monitor at: https://dashboard.render.com"
        ]),
        ("2. Update OAuth Redirect URLs", [
            "Microsoft Azure: https://portal.azure.com",
            "  Add: https://ai-agents-v2.onrender.com/api/auth/microsoft/callback",
            "Google Console: https://console.cloud.google.com",
            "  Add: https://ai-agents-v2.onrender.com/api/auth/google/callback"
        ]),
        ("3. Test the Deployment", [
            "Visit: https://ai-agents-v2.onrender.com",
            "Check health: https://ai-agents-v2.onrender.com/health",
            "Test OAuth login via the UI"
        ]),
        ("4. Monitor Logs", [
            "Check logs in Render dashboard",
            "Look for '564 tools loaded'",
            "Verify Flask started on port 10000"
        ])
    ]
    
    for title, items in steps:
        print(f"\n{title}:")
        for item in items:
            print(f"  • {item}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    print("\n🚀 AI AGENTS RENDER DEPLOYMENT SCRIPT")
    print("   Version: 1.0.0")
    print("   Date: October 29, 2025\n")
    
    # Deploy
    success = deploy_ai_agents()
    
    # Show configuration needed
    show_environment_variables()
    
    # Show next steps
    show_next_steps()
    
    if success:
        print("\n✅ DEPLOYMENT INITIATED SUCCESSFULLY!")
    else:
        print("\n⚠️  MANUAL DEPLOYMENT REQUIRED")
        print("   Follow the alternative approach shown above")
    
    print("\n" + "=" * 80)
