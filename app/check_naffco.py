# app/check_naffco.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import EquipmentDatabase

db = EquipmentDatabase()
cursor = db.conn.cursor()
cursor.execute("""
    SELECT model, supplier_price, price_sar, price_type 
    FROM equipment 
    WHERE model LIKE 'NAFFCO-HSC%'
""")

print("=" * 70)
for r in cursor.fetchall():
    print(f"Model:          {r[0]}")
    print(f"Supplier Price: {r[1]:,.2f} ريال")
    print(f"Final Price:    {r[2]:,.2f} ريال")
    print(f"Price Type:     {r[3]}")
    print(f"Expected:       {r[1]:,.0f} × 1.075 = {r[1] * 1.075:,.2f}")
    print("=" * 70)

db.close()