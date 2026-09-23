# app/check_other.py
"""
مراجعة البنود غير المصنفة (other)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.database import EquipmentDatabase


def main():
    db = EquipmentDatabase()
    cursor = db.conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT description, unit, supply_price
        FROM project_items 
        WHERE category = 'other'
        ORDER BY description
    """)
    
    items = cursor.fetchall()
    
    print("=" * 100)
    print(f"[*] بنود غير مصنفة: {len(items)}")
    print("=" * 100)
    print(f"{'#':<4} {'الوصف':<70} {'الوحدة':<8} {'التوريد':>10}")
    print("-" * 100)
    
    for i, item in enumerate(items, 1):
        desc = item[0] or ''
        unit = item[1] or ''
        price = item[2] or 0
        print(f"{i:<4} {desc[:68]:<70} {unit:<8} {price:>10,.2f}")
    
    db.close()


if __name__ == "__main__":
    main()