# app/equipment_loader.py
"""
تحميل المعدات من ملفات JSON إلى قاعدة البيانات
"""

import json
import os
import logging
from typing import Dict, Any

from .database import EquipmentDatabase

logger = logging.getLogger(__name__)


class EquipmentLoader:
    """تحميل المعدات من ملفات JSON"""
    
    def __init__(self, db: EquipmentDatabase):
        self.db = db
    
    def load_manufacturer(self, json_file: str) -> int:
        """تحميل مصنع من ملف JSON"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mfr_id = self.db.add_manufacturer(
            name=data['name'],
            name_ar=data.get('name_ar', ''),
            country=data.get('country', ''),
            website=data.get('website', ''),
            certifications=data.get('certifications', [])
        )
        logger.info(f"✅ تم تحميل المصنع: {data['name']}")
        return mfr_id
    
    def load_equipment_file(self, json_file: str, category_name: str, 
                           manufacturer_id: int) -> int:
        """تحميل معدات من ملف JSON"""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # إنشاء الفئة
        category_id = self.db.add_category(
            name=category_name,
            name_ar=data.get('category_ar', category_name)
        )
        
        count = 0
        for item in data.get('equipment', []):
            # استخراج الحقول
            price_type = item.get('price_type', 'supply_and_install')
            supplier_price = item.get('supplier_price', 0)
            final_price = item.get('price_sar', 0)
            item_type = item.get('type', '').lower()  # ← السطر المفقود!
            
            # ========== قاعدة التسعير التلقائية ==========
            if supplier_price > 0:
                # رشاشات → × 1.35
                if 'sprinkler' in item_type:
                    final_price = round(supplier_price * 1.35, 2)
                    logger.debug(f"   [Sprinkler] {item['model']}: {supplier_price} × 1.35 = {final_price}")
                
                # مضخات توريد فقط → × 1.075
                elif 'pump' in item_type and price_type == 'supply_only':
                    final_price = round(supplier_price * 1.075, 2)
                    logger.debug(f"   [Pump] {item['model']}: {supplier_price} × 1.075 = {final_price}")
                
                # Simplex مع price_type=supply_only → +375 أو +5,000
                elif price_type == 'supply_only':
                    if 'panel' in item_type or 'repeater' in item_type:
                        final_price = supplier_price + 5000
                    else:
                        final_price = supplier_price + 375
                
                else:
                    final_price = supplier_price
            # ============================================
            
            self.db.add_equipment(
                manufacturer_id=manufacturer_id,
                category_id=category_id,
                model=item['model'],
                type_=item.get('type', ''),
                specs=item.get('specs', {}),
                price_sar=final_price,
                certifications=item.get('certifications', []),
                applications=item.get('applications', []),
                notes=item.get('notes', ''),
                price_type=price_type,
                supplier_price=supplier_price,
            )
            count += 1
        
        logger.info(f"✅ تم تحميل {count} معدة من {json_file}")
        return count