"""Fix tool_result message tagging"""
from AI_infrastructure.shared.database_utils import execute_query

print("Fixing tool_result message tagging...")
print("=" * 60)

# Update tool_result messages (better pattern)
print("\n[1/2] Updating tool_result messages...")
execute_query("""
    UPDATE sessions.messages 
    SET message_source = 'tool_result'
    WHERE role = 'user' 
      AND (content::text LIKE '%tool_result%' OR content::text LIKE '%tool_use_id%')
      AND message_source = 'user_input'
""", params=None, fetch_mode=None)
print("✅ Updated")

# Check distribution
print("\n[2/2] Checking distribution...")
result = execute_query("""
    SELECT message_source, COUNT(*) as count 
    FROM sessions.messages 
    GROUP BY message_source 
    ORDER BY count DESC
""", params=None, fetch_mode='all')

print("\n📊 Message Source Distribution:")
print("=" * 60)
total = 0
for row in result:
    count = row['count'] if isinstance(row, dict) else row[1]
    source = row['message_source'] if isinstance(row, dict) else row[0]
    total += count
    print(f"  {source:20s} {count:6,} messages")
print("=" * 60)
print(f"  {'TOTAL':20s} {total:6,} messages")

print("\n✅ Fix complete!")
