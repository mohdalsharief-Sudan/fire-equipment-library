# app/check_prices.py
"""
التحقق من الأسعار المحسوبة تلقائياً
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import EquipmentDatabase


def main():
    db = EquipmentDatabase()
    cursor = db.conn.cursor()
    
    # البحث عن الرشاشات
    cursor.execute("""
        SELECT model, supplier_price, price_sar, price_type
        FROM equipment 
        WHERE model LIKE 'TYCO-CONCEALED%' 
           OR model LIKE 'SPR-K56%'
           OR model LIKE 'SPR-K8%'
           OR model LIKE 'TYCO-SIDEWALL%'
        ORDER BY model
    """)
    
    print("=" * 80)
    print(f"{'Model':<35} | {'Supplier':>10} | {'Final':>10} | {'Type':<20}")
    print("=" * 80)
    
    for r in cursor.fetchall():
        model, supplier, final, ptype = r
        supplier_str = f"{supplier:>10.2f}" if supplier else "N/A"
        final_str = f"{final:>10.2f}" if final else "N/A"
        
        # التحقق من صحة الحساب
        if supplier and final:
            expected = round(supplier * 1.35, 2)
            check = "OK" if abs(final - expected) < 0.01 else f"X (expected {expected})"
        else:
            check = ""
        
        print(f"{model:<35} | {supplier_str} | {final_str} | {check}")
    
    print("\n" + "=" * 80)
    print("التحقق من محابس TYCO:")
    print("=" * 80)
    
    cursor.execute("""
        SELECT model, price_sar, price_type
        FROM equipment 
        WHERE model LIKE 'TYCO-ALARM%'
    """)
    
    for r in cursor.fetchall():
        print(f"  {r[0]:<35} | {r[1]:>10,.2f} ريال | {r[2]}")
    
    db.close()


if __name__ == "__main__":
    main()