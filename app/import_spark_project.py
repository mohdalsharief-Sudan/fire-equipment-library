# app/import_spark_project.py
"""
استيراد مشروع SPARK كاملاً من ملف Excel
- يقرأ كل الأوراق
- يستخرج البنود الفعلية
- يحفظ الأسعار الحقيقية (توريد + تركيب + ربح)
"""

import os
import sys
import re
import json
import logging
from openpyxl import load_workbook

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import EquipmentDatabase

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class SparkProjectImporter:
    """مستورد مشروع SPARK"""
    
    def __init__(self, db):
        self.db = db
        self.items = []  # كل البنود المستخرجة
    
    def extract_items(self, file_path):
        """استخراج البنود من كل الأوراق"""
        wb = load_workbook(file_path, data_only=True)
        
        # الأوراق التي تحتوي بنود
        relevant_sheets = [
            'JUN-T1 E', 'JUN-T1-EXT', 'JUN-T1',
            'JUN-T2 E', 'JUN-T2-EXT', 'JUN-T2',
            'SUPERVISOR -E', 'SUPERVISOR-EXT', 'SUPERVISOR',
            'ISOLATE - E', 'ISOLATED-EXT', 'ISOLATED',
            'SENIOR - E', 'SENIOR-EXT', 'SENIOR',
            'ADMIN -E', 'ADMIN-EXT', 'ADMIN',
            'RECREATION - E', 'RECREATION-EXT', 'RECREATION',
            'SERVICE - E', 'SERVICE-EXT', 'SERVICE',
            'PUMP RM-1', 'PUMP-R1-EXT',
            'PUMP RM-2', 'PUMP-R2-EXT',
            'PUMP RM-3', 'PUMP-R3-EXT',
            'PUMP02', 'GUARD RM', 'GUARD-RM-EXT',
        ]
        
        for sheet_name in relevant_sheets:
            if sheet_name not in wb.sheetnames:
                continue
            
            logger.info(f"📄 معالجة: {sheet_name}")
            self._process_sheet(wb[sheet_name], sheet_name)
        
        logger.info(f"\n✅ إجمالي البنود المستخرجة: {len(self.items)}")
        return self.items
    
    def _process_sheet(self, ws, sheet_name):
        """معالجة ورقة واحدة"""
        # البحث عن رؤوس الأعمدة
        header_row = None
        desc_col = None
        qty_col = None
        unit_col = None
        price_col = None
        actual_price_col = None
        labour_col = None
        accessories_col = None
        
        for row_idx in range(1, 15):
            row = ws[row_idx]
            for col_idx, cell in enumerate(row):
                if cell.value and isinstance(cell.value, str):
                    value = cell.value.strip()
                    if 'DESCRIPTION OF ITEM' in value.upper():
                        header_row = row_idx
                        desc_col = col_idx
                    elif value.upper().startswith('ESTIMATED QUANTITY'):
                        qty_col = col_idx
                    elif value.upper() == 'UNIT':
                        unit_col = col_idx
                    elif 'UNIT PRICE(SR)' in value.upper() and 'EXCL' in value.upper():
                        price_col = col_idx
                    elif 'ACTUAL PRICE' in value.upper():
                        actual_price_col = col_idx
                    elif 'ACTUAL LABOUR' in value.upper() or 'ACTUAL LABOR' in value.upper():
                        labour_col = col_idx
                    elif 'ACCESSORIES' in value.upper():
                        accessories_col = col_idx
        
        if header_row is None:
            return
        
        # استخراج البنود
        division = None
        section = None
        
        for row_idx in range(header_row + 1, ws.max_row + 1):
            row = ws[row_idx]
            
            # تجاهل الصفوف الفارغة
            if all(c.value is None for c in row):
                continue
            
            desc_cell = row[desc_col] if desc_col is not None and desc_col < len(row) else None
            desc = desc_cell.value if desc_cell else None
            
            if not desc or not isinstance(desc, str):
                continue
            
            desc = desc.strip()
            
            # تتبع الأقسام
            if 'DIVISION' in desc.upper():
                division = desc
                continue
            
            # تتبع العناوين الفرعية
            if desc.startswith(('1.0', '2.0', '3.0', '4.0')):
                section = desc
                continue
            
            # تجاهل الأسطر الوصفية
            if desc.startswith(('Supply', 'To include', 'Includes', 'Piping', 'Two way')):
                continue
            
            if desc.startswith('SUB-TOTAL'):
                continue
            
            # استخراج القيم
            qty = self._get_number(row, qty_col)
            unit = self._get_string(row, unit_col)
            price = self._get_number(row, price_col)
            actual_price = self._get_number(row, actual_price_col)
            labour = self._get_number(row, labour_col)
            accessories = self._get_number(row, accessories_col)
            
            if not qty or not price:
                continue
            
            item = {
                'sheet': sheet_name,
                'division': division,
                'section': section,
                'description': desc,
                'unit': unit,
                'quantity': qty,
                'selling_price': price,      # سعر البيع للعميل
                'supply_price': actual_price, # سعر التوريد الحقيقي
                'labour_price': labour,       # أجور التركيب
                'accessories': accessories,   # الملحقات
                'total_cost': (actual_price or 0) + (labour or 0) + (accessories or 0),
                'profit_per_unit': price - ((actual_price or 0) + (labour or 0) + (accessories or 0)),
            }
            
            self.items.append(item)
    
    def _get_number(self, row, col_idx):
        """استخراج رقم من خلية"""
        if col_idx is None or col_idx >= len(row):
            return None
        cell = row[col_idx]
        if cell.value is None:
            return None
        try:
            return float(cell.value)
        except (ValueError, TypeError):
            return None
    
    def _get_string(self, row, col_idx):
        """استخراج نص من خلية"""
        if col_idx is None or col_idx >= len(row):
            return ''
        cell = row[col_idx]
        if cell.value is None:
            return ''
        return str(cell.value).strip()
    
    def save_to_json(self, output_file):
        """حفظ البنود في ملف JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ تم حفظ {len(self.items)} بند في: {output_file}")
    
    def analyze(self):
        """تحليل البنود المستخرجة"""
        print("\n" + "=" * 80)
        print("📊 تحليل البنود المستخرجة")
        print("=" * 80)
        
        # تجميع حسب الوحدة
        units = {}
        for item in self.items:
            unit = item['unit'] or 'غير محدد'
            units[unit] = units.get(unit, 0) + 1
        
        print(f"\n📦 حسب الوحدة:")
        for unit, count in sorted(units.items(), key=lambda x: -x[1]):
            print(f"   • {unit}: {count} بند")
        
        # تجميع حسب القسم
        divisions = {}
        for item in self.items:
            div = item['division'] or 'غير محدد'
            divisions[div] = divisions.get(div, 0) + 1
        
        print(f"\n🏗️ حسب القسم:")
        for div, count in sorted(divisions.items(), key=lambda x: -x[1]):
            print(f"   • {div}: {count} بند")
        
        # إحصائيات
        total_selling = sum(i['quantity'] * i['selling_price'] for i in self.items)
        total_cost = sum(i['quantity'] * i['total_cost'] for i in self.items)
        total_profit = total_selling - total_cost
        
        print(f"\n💰 الإحصائيات:")
        print(f"   • عدد البنود: {len(self.items)}")
        print(f"   • إجمالي البيع: {total_selling:,.2f} ريال")
        print(f"   • إجمالي التكلفة: {total_cost:,.2f} ريال")
        print(f"   • إجمالي الربح: {total_profit:,.2f} ريال")
        if total_selling > 0:
            print(f"   • هامش الربح: {(total_profit / total_selling) * 100:.1f}%")

    def classify_item(self, item):
        """تصنيف البند"""
        desc = item['description'].lower()
        section = (item.get('section') or '').lower()
        division = (item.get('division') or '').upper()
        unit = item.get('unit', '')
        
        # ========== 1. كواشف ==========
        if 'detector' in desc or 'detection' in section:
            if 'smoke' in desc: return 'smoke_detector'
            if 'heat' in desc: return 'heat_detector'
            if 'beam' in desc: return 'beam_detector'
            if 'duct' in desc: return 'duct_detector'
            return 'detector'
        
        # ========== 2. لوحات ==========
        if 'facp' in desc or 'control panel' in desc:
            return 'control_panel'
        
        if 'workstation' in desc or 'work station' in desc:
            return 'workstation'
        
        if 'repeater' in desc or 'farp' in desc:
            return 'repeater_panel'
        
        # ========== 3. وحدات ==========
        if 'module' in desc or 'isolator' in desc:
            return 'module'
        
        # ========== 4. سارينات ==========
        if 'bell' in desc or 'strobe' in desc or 'sounder' in desc or 'beacon' in desc:
            return 'sounder'
        
        # ========== 5. محطات سحب ==========
        if 'pull station' in desc:
            return 'pull_station'
        
        # ========== 6. كوابل ==========
        if 'cable' in desc or 'mm²' in desc or 'conduit' in desc:
            return 'cable'
        
        # ========== 7. مواسير (بدون unit=Ea) ==========
        if 'diameter' in desc and unit == 'm':
            return 'pipe'
        
        # ========== 8. محابس ==========
        if 'valve' in desc:
            if 'gate' in desc: return 'gate_valve'
            if 'alarm check' in desc: return 'alarm_valve'
            if 'zone control' in desc: return 'zone_valve'
            if 'check' in desc: return 'check_valve'
            return 'valve'
        
        # ========== 9. محابس بأقطار (من السياق) ==========
        if 'diameter' in desc and unit == 'Ea':
            # من القسم - تحديد النوع
            if 'gate' in section or 'general-duty valve' in section:
                return 'gate_valve'
            if 'alarm' in section or 'check' in section:
                return 'alarm_valve'
            if 'zone' in section or 'control' in section:
                return 'zone_valve'
            if 'check valve' in section:
                return 'check_valve'
            if 'flexible' in section:
                return 'flexible_connection'
            if 'strainer' in section:
                return 'strainer'
            if 'flow meter' in section:
                return 'flow_meter'
            if 'fire department' in section:
                return 'fdc'
            # default
            return 'valve'
        
        # ========== 10. رشاشات ==========
        if 'sprinkler' in desc or 'pendent' in desc or 'upright' in desc or 'wall side' in desc:
            if 'pendent' in desc: return 'sprinkler_pendent'
            if 'upright' in desc: return 'sprinkler_upright'
            if 'wall side' in desc: return 'sprinkler_sidewall'
            return 'sprinkler'
        
        # ========== 11. طفايات ==========
        if 'extinguisher' in desc or 'fe-' in desc or 'afe-' in desc:
            return 'fire_extinguisher'
        
        # ========== 12. FHC ==========
        if 'fhc' in desc or 'hose cabinet' in desc or 'hose reel' in desc:
            return 'hose_cabinet'
        
        # ========== 13. أنظمة غاز ==========
        if 'clean agent' in desc or 'kg set' in desc:
            return 'clean_agent'
        
        if 'wet-chemical' in desc:
            return 'wet_chemical'
        
        # ========== 14. FDC ==========
        if 'fire department' in desc or 'swivel' in desc:
            return 'fdc'
        
        # ========== 15. بطاريات ==========
        if 'battery' in desc or 'power supply' in desc or 'charger' in desc:
            return 'power_supply'
        
        # ========== 16. مضخات ==========
        if 'gpm' in desc and 'psi' in desc:
            if '50 gpm' in desc: return 'jockey_pump'
            return 'fire_pump'
        
        # ========== 17. بطانية حريق ==========
        if 'fire blanket' in desc:
            return 'fire_blanket'
        
        return 'other'
    
    def save_to_database(self, project_id: int):
        """حفظ البنود في قاعدة البيانات"""
        saved = 0
        for item in self.items:
            # إضافة التصنيف
            item['category'] = self.classify_item(item)
            
            self.db.add_project_item(project_id, item)
            saved += 1
        
        logger.info(f"✅ تم حفظ {saved} بند في قاعدة البيانات")
        return saved

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # ملف SPARK
    spark_file = os.path.join(
        base_dir, 'documents', 'projects',
        'Spark-Profit-Calculation.xlsx'
    )
    
    if not os.path.exists(spark_file):
        logger.error(f"❌ الملف غير موجود: {spark_file}")
        return
    
    # استخراج البنود
    db = EquipmentDatabase()
    importer = SparkProjectImporter(db)
    
    logger.info(f"📂 قراءة: {spark_file}")
    items = importer.extract_items(spark_file)
    
    if not items:
        logger.warning("⚠️ لم يتم استخراج أي بنود")
        return
    
    # حفظ في JSON
    output_dir = os.path.join(base_dir, 'data', 'projects')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'spark_items.json')
    importer.save_to_json(output_file)
    
    # إنشاء المشروع في قاعدة البيانات
    project_id = db.add_project({
        'project_name': 'SPARK City - Workers Accommodation',
        'client_id': None,
        'service_provider': 'مؤسسة أسس السلامة',
        'location': 'الرياض',
        'total_before_vat': 6521039.74,
        'total_with_vat': 6493121.74,
        'notes': 'مشروع كامل - 41 ورقة',
    })
    logger.info(f"✅ تم إنشاء المشروع ID: {project_id}")
    
    # حفظ البنود في قاعدة البيانات
    importer.save_to_database(project_id)
    
    # تحليل
    importer.analyze()
    
    # إحصائيات التصنيف
    print("\n" + "=" * 80)
    print("📊 إحصائيات التصنيف:")
    print("=" * 80)
    categories = {}
    for item in items:
        cat = item.get('category', 'other')
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   • {cat}: {count}")
    
    # عدد بنود المشاريع
    print(f"\n✅ إجمالي بنود المشاريع في القاعدة: {db.get_project_items_count()}")
    
    db.close()
    print("\n🎉 اكتمل الاستيراد!")


if __name__ == "__main__":
    main()