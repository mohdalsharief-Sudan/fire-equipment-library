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
        
        # ========== 1. المصنعون ==========
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
        
        # ========== 2. الفئات ==========
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
        
        # ========== 3. المعدات ==========
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
                price_type TEXT DEFAULT 'supply_and_install',
                supplier_price REAL DEFAULT 0,
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
        
        # ========== 4. سجل الأسعار ==========
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
        
        # ========== 5. العملاء ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                company TEXT,
                phone TEXT,
                email TEXT,
                city TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ========== 6. المشاريع ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                client_id INTEGER,
                service_provider TEXT,
                location TEXT,
                fire_suppression_cost REAL DEFAULT 0,
                fire_alarm_cost REAL DEFAULT 0,
                ventilation_cost REAL DEFAULT 0,
                other_systems_cost REAL DEFAULT 0,
                total_before_vat REAL DEFAULT 0,
                vat_15 REAL DEFAULT 0,
                total_with_vat REAL DEFAULT 0,
                reference_file TEXT,
                notes TEXT,
                status TEXT DEFAULT 'completed',
                project_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients(id)
            )
        """)
        
        # ========== 7. بنود المشاريع ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                sheet_name TEXT,
                division TEXT,
                section TEXT,
                description TEXT NOT NULL,
                unit TEXT,
                quantity REAL DEFAULT 0,
                selling_price REAL DEFAULT 0,
                supply_price REAL DEFAULT 0,
                labour_price REAL DEFAULT 0,
                accessories REAL DEFAULT 0,
                total_cost REAL DEFAULT 0,
                profit_per_unit REAL DEFAULT 0,
                category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        
        # ========== 8. الفهارس ==========
        # المعدات
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_model ON equipment(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_type ON equipment(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_mfr ON equipment(manufacturer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_eq_cat ON equipment(category_id)")
        
        # المشاريع
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_client ON projects(client_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_proj_name ON projects(project_name)")
        
        # بنود المشاريع
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pi_project ON project_items(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pi_category ON project_items(category)")
        
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
                     applications: List[str] = None, notes: str = "",
                     price_type: str = "supply_and_install",
                     supplier_price: float = 0) -> int:
        """إضافة معدة"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO equipment 
            (manufacturer_id, category_id, model, type, specs, price_sar, 
             price_type, supplier_price, certifications, applications, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            manufacturer_id, category_id, model, type_,
            json.dumps(specs),
            price_sar,
            price_type,
            supplier_price,
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
    
        # ========== العملاء ==========
    
    def add_client(self, name: str, company: str = "", phone: str = "",
                   email: str = "", city: str = "", notes: str = "") -> int:
        """إضافة عميل"""
        cursor = self.conn.cursor()
        
        # تحقق أولاً
        cursor.execute("SELECT id FROM clients WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        
        cursor.execute("""
            INSERT INTO clients (name, company, phone, email, city, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, company, phone, email, city, notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_client(self, name: str) -> Optional[Dict]:
        """الحصول على عميل"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE name = ?", (name,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_clients(self) -> List[Dict]:
        """قائمة العملاء"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    # ========== المشاريع ==========
    
    def add_project(self, project_data: Dict) -> int:
        """إضافة مشروع"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO projects 
            (project_name, client_id, service_provider, location,
             fire_suppression_cost, fire_alarm_cost, ventilation_cost, other_systems_cost,
             total_before_vat, vat_15, total_with_vat,
             reference_file, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_data.get('project_name', ''),
            project_data.get('client_id'),
            project_data.get('service_provider', ''),
            project_data.get('location', ''),
            project_data.get('fire_suppression_cost', 0),
            project_data.get('fire_alarm_cost', 0),
            project_data.get('ventilation_cost', 0),
            project_data.get('other_systems_cost', 0),
            project_data.get('total_before_vat', 0),
            project_data.get('vat_15', 0),
            project_data.get('total_with_vat', 0),
            project_data.get('reference_file', ''),
            project_data.get('notes', ''),
            project_data.get('status', 'completed')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def list_projects(self) -> List[Dict]:
        """قائمة المشاريع"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name as client_name
            FROM projects p
            LEFT JOIN clients c ON p.client_id = c.id
            ORDER BY p.total_with_vat DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """الحصول على مشروع"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name as client_name
            FROM projects p
            LEFT JOIN clients c ON p.client_id = c.id
            WHERE p.id = ?
        """, (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_projects_count(self) -> int:
        """عدد المشاريع"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM projects")
        return cursor.fetchone()[0]
    
    def get_clients_count(self) -> int:
        """عدد العملاء"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        return cursor.fetchone()[0]
    
    def get_projects_stats(self) -> Dict:
        """إحصائيات المشاريع"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(total_with_vat), 0) as total,
                COALESCE(SUM(fire_suppression_cost), 0) as fire_total,
                COALESCE(SUM(fire_alarm_cost), 0) as alarm_total,
                COALESCE(SUM(ventilation_cost), 0) as ventilation_total,
                COALESCE(SUM(other_systems_cost), 0) as other_total
            FROM projects
        """)
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def update_price(self, equipment_id: int, new_price: float, source: str = "تعديل يدوي"):
        """تحديث سعر معدة"""
        cursor = self.conn.cursor()
        
        # تحديث السعر
        cursor.execute("""
            UPDATE equipment 
            SET price_sar = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_price, equipment_id))
        
        # تسجيل في التاريخ
        cursor.execute("""
            INSERT INTO price_history (equipment_id, price_sar, source)
            VALUES (?, ?, ?)
        """, (equipment_id, new_price, source))
        
        self.conn.commit()
        logger.info(f"✅ تم تحديث السعر: {equipment_id} → {new_price}")
        return True
    
    def get_price_history(self, equipment_id: int) -> List[Dict]:
        """الحصول على تاريخ أسعار معدة"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT price_sar, source, changed_at
            FROM price_history
            WHERE equipment_id = ?
            ORDER BY changed_at DESC
        """, (equipment_id,))
        return [dict(row) for row in cursor.fetchall()]
        # ========== بنود المشاريع ==========
    
    def add_project_item(self, project_id: int, item_data: dict) -> int:
        """إضافة بند لمشروع"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO project_items 
            (project_id, sheet_name, division, section, description,
             unit, quantity, selling_price, supply_price, labour_price,
             accessories, total_cost, profit_per_unit, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            item_data.get('sheet_name', ''),
            item_data.get('division', ''),
            item_data.get('section', ''),
            item_data.get('description', ''),
            item_data.get('unit', ''),
            item_data.get('quantity', 0),
            item_data.get('selling_price', 0),
            item_data.get('supply_price', 0),
            item_data.get('labour_price', 0),
            item_data.get('accessories', 0),
            item_data.get('total_cost', 0),
            item_data.get('profit_per_unit', 0),
            item_data.get('category', ''),
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def list_project_items(self, project_id: int = None, category: str = None) -> List[Dict]:
        """قائمة بنود المشاريع"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM project_items WHERE 1=1"
        params = []
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY sheet_name, id"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_project_items_count(self) -> int:
        """عدد بنود المشاريع"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM project_items")
        return cursor.fetchone()[0]
    
    def get_project_items_stats(self, project_id: int = None) -> Dict:
        """إحصائيات بنود المشاريع"""
        cursor = self.conn.cursor()
        
        where = ""
        params = []
        if project_id:
            where = "WHERE project_id = ?"
            params.append(project_id)
        
        cursor.execute(f"""
            SELECT 
                COUNT(*) as count,
                COALESCE(SUM(quantity * selling_price), 0) as total_selling,
                COALESCE(SUM(quantity * total_cost), 0) as total_cost,
                COALESCE(SUM(quantity * profit_per_unit), 0) as total_profit
            FROM project_items
            {where}
        """, params)
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def get_project_items_categories(self, project_id: int = None) -> List[Dict]:
        """تصنيفات بنود المشاريع"""
        cursor = self.conn.cursor()
        
        where = ""
        params = []
        if project_id:
            where = "WHERE project_id = ?"
            params.append(project_id)
        
        cursor.execute(f"""
            SELECT category, COUNT(*) as count
            FROM project_items
            {where}
            GROUP BY category
            ORDER BY count DESC
        """, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """إغلاق الاتصال"""
        self.conn.close()