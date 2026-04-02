from shared.database_utils import execute_query

# Check oauth_tokens columns
cols = execute_query(
    "SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='oauth_tokens' ORDER BY ordinal_position",
    fetch_mode='all'
)
print('oauth_tokens columns:', [c['column_name'] for c in cols])

# Check all rows for user 12
rows = execute_query(
    "SELECT * FROM ai_infrastructure.oauth_tokens WHERE user_id = 12",
    fetch_mode='all'
)
print('User 12 tokens:', rows)

# Also check user_gmail_accounts columns
cols2 = execute_query(
    "SELECT column_name FROM information_schema.columns WHERE table_schema='ai_infrastructure' AND table_name='user_gmail_accounts' ORDER BY ordinal_position",
    fetch_mode='all'
)
print('user_gmail_accounts columns:', [c['column_name'] for c in cols2])

gmail = execute_query(
    "SELECT * FROM ai_infrastructure.user_gmail_accounts WHERE user_id = 12",
    fetch_mode='all'
)
print('Gmail accounts for user 12:', gmail)
