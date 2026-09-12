# app/load_projects.py
"""
تحميل المشاريع من Excel
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import EquipmentDatabase
from app.projects_loader import ProjectsLoader

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """تحميل المشاريع"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    db = EquipmentDatabase()
    loader = ProjectsLoader(db)
    
    # ملف Excel
    excel_file = os.path.join(
        base_dir, 'data', 'projects',
        'مقارنة_تكاليف_أنظمة_السلامة_والمكافحة.xlsx'
    )
    
    if not os.path.exists(excel_file):
        logger.error(f"❌ الملف غير موجود: {excel_file}")
        return
    
    print("📊 تحميل المشاريع من Excel...")
    result = loader.load_from_excel(excel_file)
    
    # الإحصائيات
    print("\n" + "=" * 60)
    print("📊 إحصائيات المشاريع")
    print("=" * 60)
    print(f"✅ عدد المشاريع: {db.get_projects_count()}")
    print(f"✅ عدد العملاء: {db.get_clients_count()}")
    
    stats = db.get_projects_stats()
    if stats:
        print(f"\n💰 إجمالي التكاليف:")
        print(f"   • أنظمة الإطفاء: {stats.get('fire_total') or 0:,.2f} ريال")
        print(f"   • أنظمة الإنذار: {stats.get('alarm_total') or 0:,.2f} ريال")
        print(f"   • التهوية: {stats.get('ventilation_total') or 0:,.2f} ريال")
        print(f"   • أنظمة أخرى: {stats.get('other_total') or 0:,.2f} ريال")
        print(f"   • الإجمالي: {stats.get('total') or 0:,.2f} ريال")
    db.close()
    print("\n🎉 اكتمل التحميل!")


if __name__ == "__main__":
    main()