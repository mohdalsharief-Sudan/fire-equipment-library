# app/load_initial_data.py
"""
تحميل البيانات الأولية إلى قاعدة البيانات
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import EquipmentDatabase
from app.equipment_loader import EquipmentLoader

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """تحميل كل البيانات"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    db = EquipmentDatabase()
    loader = EquipmentLoader(db)
    
    # ============ SFFECO ============
    print("\n📦 تحميل SFFECO...")
    sffeco_file = os.path.join(base_dir, 'data', 'manufacturers', 'sffeco.json')
    sffeco_id = loader.load_manufacturer(sffeco_file)
    logger.info(f"✅ SFFECO ID: {sffeco_id}")
    
    sffeco_equipment = [
        ('data/equipment/pumps/sffeco_edj.json', 'pumps/package_units'),
        ('data/equipment/pumps/sffeco_single_pumps.json', 'pumps/single_pumps'),
        ('data/equipment/pumps/sffeco_split_case.json', 'pumps/split_case'),
        ('data/equipment/pumps/sffeco_jockey.json', 'pumps/jockey'),
        ('data/equipment/accessories/sffeco_controllers.json', 'accessories/controllers'),
        ('data/equipment/accessories/sffeco_tanks.json', 'accessories/tanks'),
        ('data/equipment/valves/sffeco_valves.json', 'valves'),
    ]
    
    for rel_path, category in sffeco_equipment:
        file_path = os.path.join(base_dir, rel_path)
        if os.path.exists(file_path):
            count = loader.load_equipment_file(file_path, category, sffeco_id)
            logger.info(f"   ✅ {rel_path}: {count}")
    
    # ============ NAFFCO ============
    print("\n📦 تحميل NAFFCO...")
    naffco_file = os.path.join(base_dir, 'data', 'manufacturers', 'naffco.json')
    if os.path.exists(naffco_file):
        naffco_id = loader.load_manufacturer(naffco_file)
        logger.info(f"✅ NAFFCO ID: {naffco_id}")
        
        naffco_equipment = [
            ('data/equipment/pumps/naffco_edj.json', 'pumps/package_units'),
        ]
        
        for rel_path, category in naffco_equipment:
            file_path = os.path.join(base_dir, rel_path)
            if os.path.exists(file_path):
                count = loader.load_equipment_file(file_path, category, naffco_id)
                logger.info(f"   ✅ {rel_path}: {count}")
    
    # ============ الرشاشات ============
    print("\n📦 تحميل الرشاشات...")
    
    sprinkler_brands_id = loader.db.add_manufacturer(
        name="Sprinkler Brands",
        name_ar="مصنعو الرشاشات المعتمدون",
        country="دولي",
        certifications=["UL", "FM"]
    )
    logger.info(f"✅ Sprinkler Brands ID: {sprinkler_brands_id}")
    
    sprinklers_file = os.path.join(base_dir, 'data', 'equipment', 'sprinklers', 'certified_sprinklers.json')
    if os.path.exists(sprinklers_file):
        count = loader.load_equipment_file(sprinklers_file, 'sprinklers', sprinkler_brands_id)
        logger.info(f"   ✅ {sprinklers_file}: {count}")
    
    # ============ Simplex ============
    print("\n📦 تحميل Simplex...")
    
    simplex_file = os.path.join(base_dir, 'data', 'manufacturers', 'simplex.json')
    if os.path.exists(simplex_file):
        simplex_id = loader.load_manufacturer(simplex_file)
        logger.info(f"✅ Simplex ID: {simplex_id}")
        
        simplex_alarm = os.path.join(base_dir, 'data', 'equipment', 'alarm', 'simplex_alarm.json')
        if os.path.exists(simplex_alarm):
            count = loader.load_equipment_file(simplex_alarm, 'alarm_systems', simplex_id)
            logger.info(f"   ✅ Simplex Alarm: {count} معدة")
    else:
        logger.warning(f"⚠️ ملف Simplex غير موجود: {simplex_file}")    
    
    # ============ GENT / ZETA ============
    print("\n📦 تحميل GENT / ZETA...")
    
    gent_zeta_file = os.path.join(base_dir, 'data', 'manufacturers', 'gent_zeta.json')
    if os.path.exists(gent_zeta_file):
        gent_zeta_id = loader.load_manufacturer(gent_zeta_file)
        logger.info(f"✅ GENT/ZETA ID: {gent_zeta_id}")
        
        gent_zeta_alarm = os.path.join(base_dir, 'data', 'equipment', 'alarm', 'gent_zeta_alarm.json')
        if os.path.exists(gent_zeta_alarm):
            count = loader.load_equipment_file(gent_zeta_alarm, 'alarm_systems', gent_zeta_id)
            logger.info(f"   ✅ GENT/ZETA Alarm: {count} معدة")
    else:
        logger.warning(f"⚠️ ملف GENT/ZETA غير موجود")
        
    # ============ الإحصائيات ============
    print("\n" + "=" * 60)
    print("📊 إحصائيات قاعدة البيانات")
    print("=" * 60)
    print(f"✅ عدد المعدات الإجمالي: {db.get_equipment_count()}")
    
    
    # عدد لكل مصنع
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT m.name, COUNT(e.id) as count
        FROM manufacturers m
        LEFT JOIN equipment e ON e.manufacturer_id = m.id
        GROUP BY m.id
    """)
    for row in cursor.fetchall():
        print(f"   • {row[0]}: {row[1]} معدة")
    
    print(f"\n📁 قاعدة البيانات: {db.db_path}")
    db.close()
    print("\n🎉 اكتمل التحميل!")


if __name__ == "__main__":
    main()