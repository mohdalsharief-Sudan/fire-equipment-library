# app/check_simplex.py
"""
التحقق من بنود Simplex في قاعدة البيانات
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import EquipmentDatabase


def main():
    db = EquipmentDatabase()
    cursor = db.conn.cursor()
    
    # كل بنود Simplex
    cursor.execute("""
        SELECT model, type, price_sar 
        FROM equipment 
        WHERE model LIKE 'SIMPLEX%'
        ORDER BY model
    """)
    models = cursor.fetchall()
    
    print("=" * 70)
    print(f"[*] بنود Simplex في قاعدة البيانات: {len(models)}")
    print("=" * 70)
    
    for r in models:
        price = r[2] if r[2] else 0
        print(f"  - {r[0]:40} | {r[1]:30} | {price:>10,.0f} ريال")
    
    # البحث عن البند الناقص
    expected = [
        "SIMPLEX-4100-9701",
        "SIMPLEX-4098-9714",
        "SIMPLEX-4098-9733",
        "SIMPLEX-4099-9005",
        "SIMPLEX-2099-9139",
        "SIMPLEX-2975-9211",
        "SIMPLEX-4090-9001",
        "SIMPLEX-49AV-WRF",
        "SIMPLEX-49AV-WRFO",
        "SIMPLEX-49WPBB-AVVOWR",
        "SIMPLEX-4100-6078",
        "SIMPLEX-4098-9755",
        "SIMPLEX-2098-9808",
        "SIMPLEX-4603-9101",
    ]
    
    print("\n" + "=" * 70)
    print("[!] البنود الناقصة:")
    print("=" * 70)
    
    existing_models = [r[0] for r in models]
    missing = []
    for exp in expected:
        if exp not in existing_models:
            missing.append(exp)
            print(f"  [X] {exp}")
    
    if not missing:
        print("  [OK] لا توجد بنود ناقصة!")
    
    # عدد الفئات
    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    print(f"\n[*] عدد الفئات الإجمالي: {cat_count}")
    
    # عرض الفئات المكررة
    cursor.execute("""
        SELECT name, COUNT(*) as cnt 
        FROM categories 
        GROUP BY name 
        HAVING cnt > 1
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print("\n[!] فئات مكررة:")
        for d in duplicates:
            print(f"  - {d[0]}: {d[1]} مرة")
    
    db.close()


if __name__ == "__main__":
    main()