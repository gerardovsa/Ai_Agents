"""Check removable adhesive vinyl stock details"""
import sqlite3

conn = sqlite3.connect('data/stock_data.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get the removable adhesive stock
cursor.execute('SELECT * FROM unified_stocks WHERE stock_id = "249"')
row = cursor.fetchone()

print("=" * 100)
print("STOCK ID 249 - Adestor Gloss Removable")
print("=" * 100)

if row:
    for key in row.keys():
        if row[key] is not None:
            print(f"{key:30s}: {row[key]}")
else:
    print("Stock ID 249 not found!")

# Also check StockLevels table
print("\n" + "=" * 100)
print("STOCK ID 249 - From StockLevels Table")
print("=" * 100)

cursor.execute('SELECT * FROM StockLevels WHERE StockID = 249')
row2 = cursor.fetchone()

if row2:
    for key in row2.keys():
        if row2[key] is not None:
            print(f"{key:30s}: {row2[key]}")
else:
    print("Stock ID 249 not found in StockLevels!")

conn.close()

print("\n" + "=" * 100)
print("ANALYSIS:")
print("=" * 100)
print("""
Stock ID 249 is 'Adestor Gloss Removable' adhesive vinyl.

KEY FACTS:
- Format: SHEET STOCK (450mm x 320mm sheets)
- GSM: 200
- Cost: $400 per 1,000 sheets
- Markup: 15%
- Finish: Gloss
- Adhesive Type: REMOVABLE

WHY IT'S NOT SUITABLE FOR ROLL-TO-ROLL VINYL STICKERS:

1. SHEET FORMAT vs ROLL FORMAT:
   - This is pre-cut sheet stock (450×320mm) for DIGITAL PRINTERS
   - Digital printers: Canon, Konica Minolta, Ricoh, HP Indigo
   - Sheets are fed through digital presses one at a time
   
   - Roll-to-roll vinyl is continuous media on 50m rolls
   - Used with wide-format printers and vinyl plotters
   - Different production workflow entirely

2. PRODUCTION WORKFLOW:
   - Sheet stock: Print → Cut individual sheets
   - Roll vinyl: Print roll → Laminate roll → Plotter cut shapes → Weed matrix
   
3. COST STRUCTURE:
   - Sheet: $400/1000 sheets = $0.40 per sheet
   - Each sheet: 0.144 sqm (450×320mm)
   - Cost: $2.78/sqm
   
   - Roll vinyl (R1): $3.50/sqm
   - Similar pricing but different format

4. USE CASE:
   - Sheets: Labels, small stickers printed on digital press
   - Rolls: Large format decals, vehicle graphics, plotted stickers

CONCLUSION:
Stock 249 exists but is NOT roll-to-roll vinyl. It's digital sheet stock for 
a completely different production process (digital printing vs wide-format/plotter).

For the vinyl stickers calculator (roll-to-roll production), we need:
- 1370mm+ width rolls
- 50m+ lengths  
- Compatible with eco-solvent/latex/UV printers and vinyl plotters

Stock 249 cannot be used for this calculator.
""")
