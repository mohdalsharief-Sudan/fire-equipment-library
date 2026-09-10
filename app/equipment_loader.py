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
            self.db.add_equipment(
                manufacturer_id=manufacturer_id,
                category_id=category_id,
                model=item['model'],
                type_=item.get('type', ''),
                specs=item.get('specs', {}),
                price_sar=item.get('price_sar', 0),
                certifications=item.get('certifications', []),
                applications=item.get('applications', []),
                notes=item.get('notes', '')
            )
            count += 1
        
        logger.info(f"✅ تم تحميل {count} معدة من {json_file}")
        return count