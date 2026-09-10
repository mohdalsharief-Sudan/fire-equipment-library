# app/database.py
"""
إدارة قاعدة بيانات SQLite لمكتبة المعدات
"""

import sqlite3
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class EquipmentDatabase:
    """إدارة قاعدة بيانات المعدات"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'fire_equipment.db')
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()
    
    def _create_schema(self):
        """إنشاء الجداول"""
        cursor = self.conn.cursor()
        
        # المصنعون
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manufacturers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_ar TEXT,
                country TEXT,
                website TEXT,
                certifications TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # الفئات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                name_ar TEXT,
                parent_id INTEGER,
                description TEXT,
                FOREIGN KEY (parent_id) REFERENCES categories(id)
            )
        """)
        
        # المعدات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manufacturer_id INTEGER,
                category_id INTEGER,
                model TEXT NOT NULL,
                model_ar TEXT,
                type TEXT,
                description TEXT,
                specs TEXT,
                price_sar REAL,
                currency TEXT DEFAULT 'SAR',
                datasheet_path TEXT,
                curve_path TEXT,
                certificate_path TEXT,
                certifications TEXT,
                applications TEXT,
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        """)
        
        # سجل الأسعار
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id INTEGER,
                price_sar REAL,
                source TEXT,
                changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (equipment_id) REFERENCES equipment(id)
            )
        """)
        
        # فهارس
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_model ON equipment(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_type ON equipment(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_mfr ON equipment(manufacturer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_cat ON equipment(category_id)")
        
        self.conn.commit()
        logger.info(f"✅ تم إنشاء قاعدة البيانات: {self.db_path}")
    
    def add_manufacturer(self, name: str, name_ar: str = "", country: str = "",
                        website: str = "", certifications: List[str] = None) -> int:
        """إضافة مصنع"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO manufacturers (name, name_ar, country, website, certifications)
                VALUES (?, ?, ?, ?, ?)
            """, (name, name_ar, country, website, json.dumps(certifications or [])))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # موجود بالفعل
            cursor.execute("SELECT id FROM manufacturers WHERE name = ?", (name,))
            return cursor.fetchone()[0]
    
    def get_manufacturer(self, name: str) -> Optional[Dict]:
        """الحصول على مصنع بالاسم"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM manufacturers WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def add_category(self, name: str, name_ar: str = "", parent_id: int = None,
                    description: str = "") -> int:
        """إضافة فئة"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO categories (name, name_ar, parent_id, description)
            VALUES (?, ?, ?, ?)
        """, (name, name_ar, parent_id, description))
        self.conn.commit()
        return cursor.lastrowid
    
    def add_equipment(self, manufacturer_id: int, category_id: int,
                     model: str, type_: str, specs: Dict,
                     price_sar: float = 0, certifications: List[str] = None,
                     applications: List[str] = None, notes: str = "") -> int:
        """إضافة معدة"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO equipment 
            (manufacturer_id, category_id, model, type, specs, price_sar, 
             certifications, applications, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            manufacturer_id, category_id, model, type_,
            json.dumps(specs),
            price_sar,
            json.dumps(certifications or []),
            json.dumps(applications or []),
            notes
        ))
        equipment_id = cursor.lastrowid
        
        # تسجيل السعر
        if price_sar > 0:
            cursor.execute("""
                INSERT INTO price_history (equipment_id, price_sar, source)
                VALUES (?, ?, ?)
            """, (equipment_id, price_sar, "إدخال أولي"))
        
        self.conn.commit()
        return equipment_id
    
    def get_equipment_count(self) -> int:
        """عدد المعدات"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM equipment")
        return cursor.fetchone()[0]
    
    def close(self):
        """إغلاق الاتصال"""
        self.conn.close()