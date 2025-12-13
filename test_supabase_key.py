import psycopg2
import requests

# Connect to Supabase
conn = psycopg2.connect('postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres')
cur = conn.cursor()

# Get key from database
cur.execute("SELECT credential_value FROM ai_infrastructure.user_platform_credentials WHERE platform='anthropic' AND user_id=1")
key = cur.fetchone()[0]

print(f"✅ Retrieved key from Supabase")
print(f"Key ends with: {key[-20:]}")
print(f"Key length: {len(key)}")

# Test the key
print("\n🧪 Testing key with Anthropic API...")
resp = requests.post(
    'https://api.anthropic.com/v1/messages',
    headers={
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json'
    },
    json={
        'model': 'claude-sonnet-4-20250514',
        'max_tokens': 10,
        'messages': [{'role': 'user', 'content': 'hi'}]
    }
)

print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print("✅ KEY IS VALID!")
else:
    print(f"❌ KEY IS INVALID: {resp.text[:200]}")
