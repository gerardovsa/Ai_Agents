import sqlite3

conn = sqlite3.connect('c:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(synergy_internal_docs)')
columns = cursor.fetchall()

print('\nsynergy_internal_docs TABLE SCHEMA:')
print('-' * 80)
print(f'{"Column Name":<25} {"Type":<15} {"Not Null":<10} {"Primary Key"}')
print('-' * 80)

for col in columns:
    cid, name, dtype, notnull, dflt_value, pk = col
    print(f'{name:<25} {dtype:<15} {"YES" if notnull else "NO":<10} {"YES" if pk else "NO"}')

conn.close()
