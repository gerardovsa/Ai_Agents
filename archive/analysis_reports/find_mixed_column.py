import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Get column info
cursor.execute('PRAGMA table_info(extracted_jobs)')
columns = cursor.fetchall()

# Find rows with "mixed" in INTEGER columns
integer_cols = [(i, col[1], col[2]) for i, col in enumerate(columns) if col[2].upper() == 'INTEGER']

print("INTEGER columns in extracted_jobs:")
for i, name, dtype in integer_cols:
    print(f"  {i}: {name} ({dtype})")

print("\nSearching for 'mixed' values in INTEGER columns...")

for i, col_name, dtype in integer_cols:
    cursor.execute(f'SELECT id, "{col_name}" FROM extracted_jobs WHERE typeof("{col_name}") = "text" AND "{col_name}" = "mixed" LIMIT 3')
    rows = cursor.fetchall()
    if rows:
        print(f"\nFound 'mixed' in column '{col_name}' (defined as {dtype}):")
        for row in rows:
            print(f"  Job ID {row[0]}: value = '{row[1]}'")

conn.close()
