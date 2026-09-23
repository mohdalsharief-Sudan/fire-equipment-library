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
    
    # NAFFCO - Real Pumps (عروض حقيقية)
    naffco_real = os.path.join(base_dir, 'data', 'equipment', 'pumps', 'naffco_real_pumps.json')
    if os.path.exists(naffco_real):
            count = loader.load_equipment_file(naffco_real, 'pumps/package_units', naffco_id)
            logger.info(f"   ✅ NAFFCO Real Pumps: {count}")
    
    # ============ DFS / SMI ============
    print("\n📦 تحميل DFS / SMI (مضخات من Excel)...")
    
    dfs_file = os.path.join(base_dir, 'data', 'manufacturers', 'dfs_smi.json')
    if os.path.exists(dfs_file):
        dfs_id = loader.load_manufacturer(dfs_file)
        logger.info(f"✅ DFS/SMI ID: {dfs_id}")
        
        dfs_pumps = os.path.join(base_dir, 'data', 'equipment', 'pumps', 'dfs_smi_pumps.json')
        if os.path.exists(dfs_pumps):
            count = loader.load_equipment_file(dfs_pumps, 'pumps/package_units', dfs_id)
            logger.info(f"   ✅ DFS/SMI Pumps: {count}")        
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
    
    # ============ HI-TECH (FM-200) ============
    print("\n📦 تحميل HI-TECH (FM-200)...")
    
    hitech_file = os.path.join(base_dir, 'data', 'manufacturers', 'hi-tech.json')
    if os.path.exists(hitech_file):
        hitech_id = loader.load_manufacturer(hitech_file)
        logger.info(f"✅ HI-TECH ID: {hitech_id}")
        
        hitech_equipment = os.path.join(base_dir, 'data', 'equipment', 'gas_systems', 'hi-tech_fm200.json')
        if os.path.exists(hitech_equipment):
            count = loader.load_equipment_file(hitech_equipment, 'gas_systems', hitech_id)
            logger.info(f"   ✅ HI-TECH FM-200: {count} معدة")
    
    # ============ ANSUL / PYRO-CHEM ============
    print("\n📦 تحميل ANSUL / PYRO-CHEM...")
    
    ansul_file = os.path.join(base_dir, 'data', 'manufacturers', 'ansul_pyrochem.json')
    if os.path.exists(ansul_file):
        ansul_id = loader.load_manufacturer(ansul_file)
        logger.info(f"✅ ANSUL ID: {ansul_id}")
        
        ansul_equipment = os.path.join(base_dir, 'data', 'equipment', 'gas_systems', 'ansul_kitchen.json')
        if os.path.exists(ansul_equipment):
            count = loader.load_equipment_file(ansul_equipment, 'gas_systems', ansul_id)
            logger.info(f"   ✅ ANSUL Kitchen: {count} معدة")   
            
    # ============ TYCO ============
    print("\n📦 تحميل TYCO...")
    
    tyco_file = os.path.join(base_dir, 'data', 'manufacturers', 'tyco.json')
    if os.path.exists(tyco_file):
        tyco_id = loader.load_manufacturer(tyco_file)
        logger.info(f"✅ TYCO ID: {tyco_id}")
        
        # رشاشات TYCO
        tyco_sprinklers = os.path.join(base_dir, 'data', 'equipment', 'sprinklers', 'tyco_sprinklers.json')
        if os.path.exists(tyco_sprinklers):
            count = loader.load_equipment_file(tyco_sprinklers, 'sprinklers', tyco_id)
            logger.info(f"   ✅ TYCO Sprinklers: {count}")
        
        # محابس TYCO
        tyco_valves = os.path.join(base_dir, 'data', 'equipment', 'valves', 'tyco_alarm_valves.json')
        if os.path.exists(tyco_valves):
            count = loader.load_equipment_file(tyco_valves, 'valves', tyco_id)
            logger.info(f"   ✅ TYCO Valves: {count}")
    
    # ============ Rozenberg (Ventilation) ============
    print("\n📦 تحميل Rozenberg (التهوية)...")
    
    roz_file = os.path.join(base_dir, 'data', 'manufacturers', 'rozenberg.json')
    if os.path.exists(roz_file):
        roz_id = loader.load_manufacturer(roz_file)
        logger.info(f"✅ Rozenberg ID: {roz_id}")
        
        roz_equipment = os.path.join(base_dir, 'data', 'equipment', 'ventilation', 'rozenberg_fans.json')
        if os.path.exists(roz_equipment):
            count = loader.load_equipment_file(roz_equipment, 'ventilation', roz_id)
            logger.info(f"   ✅ Rozenberg Fans: {count}")
    
        # ============ KHIND ============
    print("\n📦 تحميل KHIND (إنارة طوارئ)...")
    
    khind_file = os.path.join(base_dir, 'data', 'manufacturers', 'khind.json')
    if os.path.exists(khind_file):
        khind_id = loader.load_manufacturer(khind_file)
        logger.info(f"✅ KHIND ID: {khind_id}")
        
        khind_equipment = os.path.join(base_dir, 'data', 'equipment', 'architectural', 'khind_emergency.json')
        if os.path.exists(khind_equipment):
            count = loader.load_equipment_file(khind_equipment, 'architectural_safety', khind_id)
            logger.info(f"   ✅ KHIND Emergency: {count}")
    
    # ============ Giacomini ============
    print("\n📦 تحميل Giacomini...")
    
    giacomini_file = os.path.join(base_dir, 'data', 'manufacturers', 'giacomini.json')
    if os.path.exists(giacomini_file):
        giacomini_id = loader.load_manufacturer(giacomini_file)
        logger.info(f"✅ Giacomini ID: {giacomini_id}")
        
        giacomini_equipment = os.path.join(base_dir, 'data', 'equipment', 'valves', 'giacomini_valves.json')
        if os.path.exists(giacomini_equipment):
            count = loader.load_equipment_file(giacomini_equipment, 'valves', giacomini_id)
            logger.info(f"   ✅ Giacomini Valves: {count}")
    
    # ============ Morris ============
    print("\n📦 تحميل Morris...")
    
    morris_file = os.path.join(base_dir, 'data', 'manufacturers', 'morris.json')
    if os.path.exists(morris_file):
        morris_id = loader.load_manufacturer(morris_file)
        logger.info(f"✅ Morris ID: {morris_id}")
        
        morris_equipment = os.path.join(base_dir, 'data', 'equipment', 'valves', 'morris_hydrants.json')
        if os.path.exists(morris_equipment):
            count = loader.load_equipment_file(morris_equipment, 'valves', morris_id)
            logger.info(f"   ✅ Morris Hydrants: {count}")
                                     
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