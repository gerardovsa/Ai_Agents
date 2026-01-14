import sqlite3

conn = sqlite3.connect('data/stock_data.db')
cursor = conn.cursor()

# Get INT columns
cursor.execute('PRAGMA table_info(unified_stocks)')
cols = cursor.fetchall()
int_cols = [(c[0], c[1], c[2]) for c in cols if c[2].upper() == 'INTEGER']

print("INTEGER columns in unified_stocks:")
for i, name, dtype in int_cols:
    print(f"  {i}: {name}")

# Find which column has "custom"
for i, col_name, dtype in int_cols:
    cursor.execute(f'SELECT stock_id, "{col_name}" FROM unified_stocks WHERE "{col_name}" = "custom" LIMIT 3')
    rows = cursor.fetchall()
    if rows:
        print(f"\nFound 'custom' in column '{col_name}':")
        for row in rows:
            print(f"  Stock ID {row[0]}: value = '{row[1]}'")

conn.close()
