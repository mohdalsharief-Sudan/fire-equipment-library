# app/search.py
"""
البحث والاستعلام في مكتبة المعدات
"""

import sqlite3
import json
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class EquipmentSearch:
    """البحث في مكتبة المعدات"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'fire_equipment.db')
        
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def find_pumps(self, 
                   flow_gpm: float = None,
                   pressure_bar: float = None,
                   manufacturer: str = None,
                   min_price: float = None,
                   max_price: float = None,
                   certifications: List[str] = None) -> List[Dict]:
        """
        البحث عن مضخات
        
        Args:
            flow_gpm: الحد الأدنى للتدفق
            pressure_bar: الحد الأدنى للضغط
            manufacturer: اسم المصنع
            min_price: الحد الأدنى للسعر
            max_price: الحد الأقصى للسعر
            certifications: قائمة الاعتمادات المطلوبة
        """
        query = """
            SELECT e.*, m.name as manufacturer_name, c.name as category_name
            FROM equipment e
            JOIN manufacturers m ON e.manufacturer_id = m.id
            JOIN categories c ON e.category_id = c.id
            WHERE e.is_active = 1
        """
        params = []
        
        if manufacturer:
            query += " AND m.name = ?"
            params.append(manufacturer)
        
        if min_price is not None:
            query += " AND e.price_sar >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND e.price_sar <= ?"
            params.append(max_price)
        
        query += " ORDER BY e.price_sar"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            item = dict(row)
            item['specs'] = json.loads(item['specs']) if item['specs'] else {}
            item['certifications'] = json.loads(item['certifications']) if item['certifications'] else []
            item['applications'] = json.loads(item['applications']) if item['applications'] else []
            
            # فلترة حسب التدفق والضغط
            specs = item['specs']
            flow = specs.get('flow_gpm', 0)
            pressure = specs.get('pressure_bar', 0)
            
            if flow_gpm and flow < flow_gpm * 0.9:
                continue
            if pressure_bar and pressure < pressure_bar:
                continue
            
            # فلترة حسب الاعتمادات
            if certifications:
                pump_certs = item['certifications']
                if not all(c in pump_certs for c in certifications):
                    continue
            
            results.append(item)
        
        return results
    
    def get_by_model(self, model: str) -> Optional[Dict]:
        """الحصول على معدة بالموديل"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, m.name as manufacturer_name, c.name as category_name
            FROM equipment e
            JOIN manufacturers m ON e.manufacturer_id = m.id
            JOIN categories c ON e.category_id = c.id
            WHERE e.model = ?
        """, (model,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        item = dict(row)
        item['specs'] = json.loads(item['specs']) if item['specs'] else {}
        item['certifications'] = json.loads(item['certifications']) if item['certifications'] else []
        item['applications'] = json.loads(item['applications']) if item['applications'] else []
        return item
    
    def list_all(self) -> List[Dict]:
        """عرض كل المعدات"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, m.name as manufacturer_name, c.name as category_name
            FROM equipment e
            JOIN manufacturers m ON e.manufacturer_id = m.id
            JOIN categories c ON e.category_id = c.id
            WHERE e.is_active = 1
            ORDER BY m.name, e.model
        """)
        
        results = []
        for row in cursor.fetchall():
            item = dict(row)
            item['specs'] = json.loads(item['specs']) if item['specs'] else {}
            item['certifications'] = json.loads(item['certifications']) if item['certifications'] else []
            results.append(item)
        
        return results
    
    def print_pump(self, pump: Dict):
        """طباعة تفاصيل معدة"""
        specs = pump.get('specs', {})
        certs = " / ".join(pump.get('certifications', []))
        
        print(f"\n{'=' * 60}")
        print(f"🔧 {pump['manufacturer_name']} - {pump['model']}")
        print('=' * 60)
        print(f"النوع: {pump.get('type', '')}")
        
        # المواصفات الأساسية
        if specs.get('flow_gpm'):
            print(f"التدفق: {specs.get('flow_gpm')} GPM")
        if specs.get('pressure_bar'):
            print(f"الضغط: {specs.get('pressure_bar')} bar")
        
        # القدرات
        if specs.get('electric_hp'):
            print(f"مضخة كهربائية: {specs.get('electric_hp')} HP")
        elif specs.get('power_hp') and specs.get('driver') == 'electric':
            print(f"مضخة كهربائية: {specs.get('power_hp')} HP")
        
        if specs.get('diesel_hp'):
            print(f"مضخة ديزل: {specs.get('diesel_hp')} HP")
        
        if specs.get('jockey_hp'):
            print(f"مضخة جوكي: {specs.get('jockey_hp')} HP")
        
        if specs.get('weight_kg'):
            print(f"الوزن: {specs.get('weight_kg')} kg")
        
        if specs.get('header_pipe'):
            print(f"الهيدر: {specs.get('header_pipe')}")
        
        # ← جديد: عرض الحزمة
        print(f"\n📦 محتويات الحزمة:")
        
        if specs.get('is_complete_package'):
            print(f"   ✅ حزمة كاملة جاهزة")
        
        if specs.get('includes_jockey'):
            print(f"   ✅ تشمل مضخة جوكي")
        
        if specs.get('includes_controller'):
            print(f"   ✅ تشمل لوحة تحكم")
        
        if specs.get('includes_diesel'):
            print(f"   ✅ تشمل مضخة ديزل")
        
        # تحذيرات
        if specs.get('requires_jockey') and not specs.get('includes_jockey'):
            print(f"   ⚠️ يتطلب مضخة جوكي (غير مشمولة)")
        
        # الاعتمادات
        print(f"\n🏆 الاعتمادات: {certs}")
        
        # السعر
        print(f"\n💰 السعر: {pump.get('price_sar', 0):,.0f} ريال")
        
        # التطبيقات
        if pump.get('applications'):
            print(f"\n📋 التطبيقات:")
            for app in pump['applications']:
                print(f"   • {app}")
        
        # ملاحظات
        if pump.get('notes'):
            print(f"\n📝 ملاحظات: {pump['notes']}")
    
    def print_results(self, results: List[Dict]):
        """طباعة نتائج البحث"""
        if not results:
            print("\n❌ لا توجد نتائج")
            return
        
        print(f"\n{'=' * 60}")
        print(f"🔍 نتائج البحث ({len(results)} نتيجة)")
        print('=' * 60)
        
        for i, pump in enumerate(results, 1):
            specs = pump['specs']
            print(f"\n{i}. {pump['manufacturer_name']} - {pump['model']}")
            print(f"   التدفق: {specs.get('flow_gpm', 0)} GPM @ {specs.get('pressure_bar', 0)} bar")
            print(f"   السعر: {pump.get('price_sar', 0):,.0f} ريال")
    
    def close(self):
        self.conn.close()