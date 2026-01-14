"""
Get GitHub Copilot AI fees from GitHub API

This script fetches your GitHub Copilot billing information
"""

import requests
import json
from datetime import datetime, timedelta
import os

def get_github_copilot_usage():
    """
    Fetch GitHub Copilot usage and billing information
    
    You need a GitHub Personal Access Token with 'read:user' and 'read:org' scopes
    Create one at: https://github.com/settings/tokens
    """
    
    # Check for token in environment or config
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("=" * 80)
        print("GITHUB TOKEN REQUIRED")
        print("=" * 80)
        print("\nTo get your GitHub Copilot billing information, you need a Personal Access Token.")
        print("\nSteps:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scopes: 'read:user', 'read:org', 'admin:billing' (if available)")
        print("4. Generate token and copy it")
        print("5. Set environment variable: $env:GITHUB_TOKEN='your_token_here'")
        print("6. Run this script again")
        print("\nOr provide token directly when prompted.")
        print("=" * 80)
        
        token = input("\nEnter your GitHub token (or press Enter to exit): ").strip()
        if not token:
            return
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print("\n" + "=" * 80)
    print("GITHUB COPILOT BILLING ANALYSIS")
    print("=" * 80)
    
    # Get user info
    try:
        user_response = requests.get('https://api.github.com/user', headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()
        username = user_data.get('login', 'Unknown')
        print(f"\nUser: {username}")
        print(f"Account: {user_data.get('type', 'Unknown')}")
    except Exception as e:
        print(f"\nError fetching user info: {e}")
        username = "Unknown"
    
    # Try to get Copilot seat information
    print("\n" + "-" * 80)
    print("COPILOT SEAT INFORMATION")
    print("-" * 80)
    
    try:
        # Check Copilot subscription status
        copilot_url = f'https://api.github.com/users/{username}/copilot/billing'
        copilot_response = requests.get(copilot_url, headers=headers)
        
        if copilot_response.status_code == 200:
            copilot_data = copilot_response.json()
            print(f"Copilot Status: Active")
            print(f"Plan: {copilot_data.get('plan', 'Unknown')}")
            print(f"Seat Cost: ${copilot_data.get('seat_cost', 'Unknown')}/month")
        else:
            print(f"Status Code: {copilot_response.status_code}")
            print("Unable to fetch Copilot billing directly from API")
    except Exception as e:
        print(f"Note: {e}")
    
    # Try organization billing (if applicable)
    print("\n" + "-" * 80)
    print("ORGANIZATION BILLING INFORMATION")
    print("-" * 80)
    
    try:
        orgs_response = requests.get('https://api.github.com/user/orgs', headers=headers)
        orgs_response.raise_for_status()
        orgs = orgs_response.json()
        
        if orgs:
            print(f"\nFound {len(orgs)} organization(s):")
            for org in orgs:
                org_name = org.get('login')
                print(f"\n  Organization: {org_name}")
                
                # Try to get billing info
                try:
                    billing_url = f'https://api.github.com/orgs/{org_name}/copilot/billing'
                    billing_response = requests.get(billing_url, headers=headers)
                    if billing_response.status_code == 200:
                        billing_data = billing_response.json()
                        print(f"  Total Seats: {billing_data.get('total_seats', 'Unknown')}")
                        print(f"  Seat Cost: ${billing_data.get('seat_cost', 'Unknown')}/month")
                except:
                    print(f"  (Billing details not accessible)")
        else:
            print("No organizations found")
    except Exception as e:
        print(f"Unable to fetch organization info: {e}")
    
    # GitHub Copilot pricing information
    print("\n" + "=" * 80)
    print("GITHUB COPILOT PRICING (Standard Rates)")
    print("=" * 80)
    print("\nIndividual Plans:")
    print("  - Copilot Individual: $10/month or $100/year")
    print("  - Copilot Business: $19/user/month")
    print("  - Copilot Enterprise: $39/user/month")
    
    print("\nCopilot Chat (included in above plans)")
    print("  - Web interface, IDE integration, mobile apps")
    
    # Calculate potential costs
    print("\n" + "=" * 80)
    print("ESTIMATED COSTS FOR YOUR USAGE")
    print("=" * 80)
    
    # You can manually update these based on your usage
    months_used = input("\nHow many months have you been using Copilot? (default: 6): ").strip()
    months_used = int(months_used) if months_used else 6
    
    plan_type = input("Which plan? (1=Individual $10/mo, 2=Business $19/mo, 3=Enterprise $39/mo): ").strip()
    if plan_type == '2':
        monthly_cost = 19
        plan_name = "Business"
    elif plan_type == '3':
        monthly_cost = 39
        plan_name = "Enterprise"
    else:
        monthly_cost = 10
        plan_name = "Individual"
    
    total_cost = monthly_cost * months_used
    
    print(f"\nPlan: GitHub Copilot {plan_name}")
    print(f"Monthly Cost: ${monthly_cost}")
    print(f"Duration: {months_used} months")
    print(f"Total Cost: ${total_cost}")
    
    # Additional AI costs if you're using other services
    print("\n" + "=" * 80)
    print("OTHER AI SERVICES")
    print("=" * 80)
    print("\nIf you're also using:")
    print("  - Claude API (Anthropic): Check Anthropic console")
    print("  - OpenAI API: Check OpenAI usage dashboard")
    print("  - Azure OpenAI: Check Azure billing")
    
    # Export to JSON
    output = {
        "username": username,
        "copilot_plan": plan_name,
        "monthly_cost": monthly_cost,
        "months_used": months_used,
        "total_cost": total_cost,
        "date_generated": datetime.now().isoformat()
    }
    
    output_file = "github_copilot_fees.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Report saved to: {output_file}")
    
    # Create a markdown summary
    md_content = f"""# GitHub Copilot Fees Summary

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

## Account Information
- **Username:** {username}
- **Plan:** GitHub Copilot {plan_name}

## Cost Breakdown
- **Monthly Cost:** ${monthly_cost}/month
- **Duration:** {months_used} months
- **Total Cost:** ${total_cost}

## Additional Information

### GitHub Copilot Features Included:
- Code completion in IDE
- Copilot Chat (conversational AI)
- Code explanation and refactoring
- Unit test generation
- Documentation writing

### Usage Recommendations:
To get detailed usage statistics:
1. Visit: https://github.com/settings/copilot
2. Check your activity dashboard
3. Review billing at: https://github.com/settings/billing

### API Access:
For detailed billing via API, you need:
- Personal Access Token with `admin:billing` scope
- Access to organization billing (if applicable)

---

*Note: This is an estimate based on standard GitHub pricing. Actual charges may vary based on your specific plan and usage.*
"""
    
    md_file = "github_copilot_fees.md"
    with open(md_file, 'w') as f:
        f.write(md_content)
    
    print(f"✅ Markdown report saved to: {md_file}")
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("\n1. Visit https://github.com/settings/billing to see exact charges")
    print("2. Check https://github.com/settings/copilot for usage details")
    print("3. For organizations: Visit org settings -> Billing -> Copilot")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    get_github_copilot_usage()
