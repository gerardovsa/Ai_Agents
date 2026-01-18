import sys
sys.path.insert(0, 'UI/modules_external/inhouse-print')
from db_connector import InHousePrintDB

db = InHousePrintDB()
result = db.execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'GSM'")
print('GSM table columns:')
for col in result['COLUMN_NAME'].tolist():
    print(f"  • {col}")
