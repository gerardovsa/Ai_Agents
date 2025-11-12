"""
Calculate AI Costs - Analyze token usage and estimate costs
Tracks Anthropic Claude, OpenAI, and DeepSeek API usage

GitHub Copilot costs are separate - check at https://github.com/settings/copilot
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Pricing (as of Nov 2025)
PRICING = {
    'anthropic': {
        'claude-3-5-sonnet-20241022': {
            'input': 3.00 / 1_000_000,  # $3 per 1M tokens
            'output': 15.00 / 1_000_000  # $15 per 1M tokens
        },
        'claude-3-5-haiku-20241022': {
            'input': 0.80 / 1_000_000,
            'output': 4.00 / 1_000_000
        }
    },
    'openai': {
        'gpt-4-turbo': {
            'input': 10.00 / 1_000_000,
            'output': 30.00 / 1_000_000
        },
        'gpt-3.5-turbo': {
            'input': 0.50 / 1_000_000,
            'output': 1.50 / 1_000_000
        }
    },
    'deepseek': {
        'deepseek-chat': {
            'input': 0.14 / 1_000_000,
            'output': 0.28 / 1_000_000
        }
    },
    'github_copilot': {
        'individual': 10.00,  # per month
        'business': 19.00     # per user/month
    }
}

def get_db_path():
    """Get path to ai_infrastructure database"""
    root = Path(__file__).parent
    return root / 'data' / 'ai_infrastructure.db'

def analyze_token_usage():
    """Analyze token usage from database"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return None
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check available tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Available tables: {', '.join(tables)}\n")
    
    results = {
        'total_messages': 0,
        'by_provider': {},
        'by_model': {},
        'date_range': None
    }
    
    # Try to find message/conversation tables
    for table in ['messages', 'conversations', 'chat_messages', 'agent_messages']:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if columns:
                print(f"\n{table} table columns: {', '.join(columns)}")
                
                # Try to get token usage data
                token_columns = [col for col in columns if 'token' in col.lower()]
                if token_columns:
                    query = f"SELECT COUNT(*) as count, {', '.join(token_columns)} FROM {table}"
                    cursor.execute(query)
                    print(f"Sample data from {table}:")
                    for row in cursor.fetchall():
                        print(dict(row))
        except sqlite3.Error as e:
            print(f"Error querying {table}: {e}")
    
    conn.close()
    return results

def estimate_github_copilot_cost(months=3):
    """Estimate GitHub Copilot cost"""
    print("\n" + "="*60)
    print("GITHUB COPILOT COSTS")
    print("="*60)
    print("\nGitHub Copilot is billed separately through GitHub.")
    print("Check your actual billing at: https://github.com/settings/copilot")
    print("\nPricing:")
    print(f"  • Individual: ${PRICING['github_copilot']['individual']:.2f}/month (${PRICING['github_copilot']['individual']*12:.2f}/year)")
    print(f"  • Business: ${PRICING['github_copilot']['business']:.2f}/user/month")
    print(f"\nEstimated cost ({months} months): ${PRICING['github_copilot']['individual']*months:.2f}")
    
def display_api_pricing():
    """Display API pricing for reference"""
    print("\n" + "="*60)
    print("AI API PRICING (Your Agent Backend)")
    print("="*60)
    
    print("\nANTHROPIC CLAUDE:")
    for model, prices in PRICING['anthropic'].items():
        print(f"  {model}:")
        print(f"    Input:  ${prices['input']*1_000_000:.2f} per 1M tokens")
        print(f"    Output: ${prices['output']*1_000_000:.2f} per 1M tokens")
    
    print("\nOPENAI:")
    for model, prices in PRICING['openai'].items():
        print(f"  {model}:")
        print(f"    Input:  ${prices['input']*1_000_000:.2f} per 1M tokens")
        print(f"    Output: ${prices['output']*1_000_000:.2f} per 1M tokens")
    
    print("\nDEEPSEEK:")
    for model, prices in PRICING['deepseek'].items():
        print(f"  {model}:")
        print(f"    Input:  ${prices['input']*1_000_000:.2f} per 1M tokens")
        print(f"    Output: ${prices['output']*1_000_000:.2f} per 1M tokens")

def main():
    print("="*60)
    print("AI COST ANALYSIS")
    print("="*60)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Analyze token usage from database
    print("Analyzing database for token usage...")
    analyze_token_usage()
    
    # Display pricing
    display_api_pricing()
    
    # Estimate GitHub Copilot costs
    estimate_github_copilot_cost(months=3)
    
    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. GitHub Copilot: Check https://github.com/settings/copilot for actual billing")
    print("2. Anthropic: Check https://console.anthropic.com/settings/billing")
    print("3. OpenAI: Check https://platform.openai.com/usage")
    print("4. DeepSeek: Check DeepSeek dashboard for usage")
    print("\nNote: Token usage tracking may need to be implemented in your agent routes.")

if __name__ == '__main__':
    main()
