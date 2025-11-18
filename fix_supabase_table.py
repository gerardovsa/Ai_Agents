"""Replace client.table with client.query in supabase.py"""

with open('tools/implementations/supabase.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('client.table(', 'client.query(')

with open('tools/implementations/supabase.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Replaced all client.table() with client.query()")
