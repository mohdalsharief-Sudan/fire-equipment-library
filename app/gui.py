# app/gui.py
"""
واجهة رسومية لمكتبة معدات السلامة
مع تابات للمعدات والمشاريع والعملاء والإحصائيات
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.search import EquipmentSearch
from app.database import EquipmentDatabase


class EquipmentLibraryGUI:
    """الواجهة الرسومية لمكتبة المعدات"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fire Equipment Library - مكتبة معدات السلامة")
        self.root.geometry("1300x800")
        self.root.configure(bg="#0f1626")
        
        # الاتصال بقاعدة البيانات
        self.search = EquipmentSearch()
        self.db = EquipmentDatabase()
        
        # البيانات
        self.results = []
        self.projects = []
        
        self._build_ui()
        
        # تحميل البيانات الأولية
        self._load_equipment()
        self._load_projects()
    
    def _build_ui(self):
        """بناء الواجهة الرئيسية"""
        # ====== العنوان ======
        title_frame = tk.Frame(self.root, bg="#1B4F72")
        title_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text="🔥 Fire Equipment Library",
            font=("Arial", 22, "bold"),
            bg="#1B4F72", fg="white",
            padx=20, pady=10
        ).pack()
        
        tk.Label(
            title_frame,
            text="مكتبة معدات السلامة - SFFECO | NAFFCO | Sprinklers",
            font=("Arial", 11),
            bg="#1B4F72", fg="#A8D5E5",
        ).pack(pady=(0, 8))
        
        # ====== شريط التابات ======
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background="#0f1626", borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background="#2874A6", 
                       foreground="white",
                       padding=[20, 10],
                       font=("Arial", 11, "bold"))
        style.map('TNotebook.Tab',
                 background=[('selected', '#1B4F72')],
                 foreground=[('selected', 'white')])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ====== التاب 1: المعدات ======
        self.tab_equipment = tk.Frame(self.notebook, bg="#0f1626")
        self.notebook.add(self.tab_equipment, text="🔧 المعدات")
        self._build_equipment_tab()
        
        # ====== التاب 2: المشاريع ======
        self.tab_projects = tk.Frame(self.notebook, bg="#0f1626")
        self.notebook.add(self.tab_projects, text="📊 المشاريع")
        self._build_projects_tab()
        
        # ====== التاب 3: العملاء ======
        self.tab_clients = tk.Frame(self.notebook, bg="#0f1626")
        self.notebook.add(self.tab_clients, text="👥 العملاء")
        self._build_clients_tab()
        
        # ====== التاب 4: الإحصائيات ======
        self.tab_stats = tk.Frame(self.notebook, bg="#0f1626")
        self.notebook.add(self.tab_stats, text="📈 الإحصائيات")
        self._build_stats_tab()
        
        # ====== شريط الحالة ======
        status_frame = tk.Frame(self.root, bg="#1B4F72")
        status_frame.pack(fill="x", side="bottom")
        
        self.status_var = tk.StringVar(value="جاهز")
        tk.Label(
            status_frame, textvariable=self.status_var,
            font=("Arial", 10), bg="#1B4F72", fg="white",
            padx=10, pady=5
        ).pack(side="left")
        
        self.count_var = tk.StringVar(value="")
        tk.Label(
            status_frame, textvariable=self.count_var,
            font=("Arial", 10, "bold"), bg="#1B4F72", fg="#A8D5E5",
            padx=10, pady=5
        ).pack(side="right")
    
    # ==================================================================
    # التاب 1: المعدات
    # ==================================================================
    
    def _build_equipment_tab(self):
        """بناء تاب المعدات"""
        # ====== إطار البحث ======
        search_frame = tk.Frame(self.tab_equipment, bg="#0f1626")
        search_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 بحث:", font=("Arial", 11, "bold"),
                bg="#0f1626", fg="white").pack(side="left", padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               width=25, font=("Arial", 11))
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda e: self._do_search())
        
        # المصنع
        tk.Label(search_frame, text="المصنع:", font=("Arial", 10),
                bg="#0f1626", fg="white").pack(side="left", padx=5)
        
        self.manufacturer_var = tk.StringVar(value="الكل")
        ttk.Combobox(search_frame, textvariable=self.manufacturer_var,
                    values=["الكل", "SFFECO", "NAFFCO", "Sprinkler Brands"],
                    width=15, state="readonly").pack(side="left", padx=5)
        
        # الفئة
        tk.Label(search_frame, text="الفئة:", font=("Arial", 10),
                bg="#0f1626", fg="white").pack(side="left", padx=5)
        
        self.category_var = tk.StringVar(value="الكل")
        ttk.Combobox(search_frame, textvariable=self.category_var,
                    values=["الكل", "package_units", "single_pumps", "split_case",
                           "jockey", "controllers", "valves", "tanks", "sprinklers"],
                    width=15, state="readonly").pack(side="left", padx=5)
        
        tk.Button(search_frame, text="🔍 بحث", command=self._do_search,
                 bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=3, cursor="hand2").pack(side="left", padx=10)
        
        tk.Button(search_frame, text="📋 عرض الكل", command=self._load_equipment,
                 bg="#2874A6", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=3, cursor="hand2").pack(side="left", padx=5)
        
        # ====== جدول المعدات ======
        table_frame = tk.Frame(self.tab_equipment, bg="#0f1626")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("#", "manufacturer", "model", "type", "flow", "pressure", "price", "package")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                 yscrollcommand=scroll_y.set)
        
        headers = {
            "#": "#",
            "manufacturer": "المصنع",
            "model": "الموديل",
            "type": "النوع",
            "flow": "التدفق (GPM)",
            "pressure": "الضغط (bar)",
            "price": "السعر (ريال)",
            "package": "الحزمة"
        }
        widths = {"#": 40, "manufacturer": 130, "model": 200, "type": 180,
                 "flow": 100, "pressure": 100, "price": 120, "package": 150}
        
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=widths[col], anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        
        self.tree.bind("<Double-1>", self._on_equipment_double_click)
        
        # ====== أزرار التصدير ======
        export_frame = tk.Frame(self.tab_equipment, bg="#0f1626")
        export_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(export_frame, text="📊 تصدير Excel", command=self._export_excel,
                 bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(export_frame, text="📄 تصدير JSON", command=self._export_json,
                 bg="#8E44AD", fg="white", font=("Arial", 10, "bold"),
                 padx=15, pady=5, cursor="hand2").pack(side="left", padx=5)
    
    # ==================================================================
    # التاب 2: المشاريع
    # ==================================================================
    
    def _build_projects_tab(self):
        """بناء تاب المشاريع"""
        # ====== إحصائيات سريعة ======
        stats_frame = tk.Frame(self.tab_projects, bg="#1B4F72")
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.projects_stats_var = tk.StringVar(value="جاري التحميل...")
        tk.Label(
            stats_frame, textvariable=self.projects_stats_var,
            font=("Arial", 12, "bold"),
            bg="#1B4F72", fg="white",
            pady=15
        ).pack()
        
        # ====== جدول المشاريع ======
        table_frame = tk.Frame(self.tab_projects, bg="#0f1626")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        scroll_x = tk.Scrollbar(table_frame, orient="horizontal")
        
        columns = ("#", "name", "client", "fire", "alarm", "vent", "other", "total")
        self.projects_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set
        )
        
        headers = {
            "#": "#",
            "name": "اسم المشروع",
            "client": "العميل",
            "fire": "إطفاء (ر.س)",
            "alarm": "إنذار (ر.س)",
            "vent": "تهوية (ر.س)",
            "other": "أخرى (ر.س)",
            "total": "الإجمالي (ر.س)"
        }
        widths = {"#": 40, "name": 280, "client": 200, "fire": 130,
                 "alarm": 130, "vent": 130, "other": 130, "total": 150}
        
        for col in columns:
            self.projects_tree.heading(col, text=headers[col])
            self.projects_tree.column(col, width=widths[col], anchor="center")
        
        self.projects_tree.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self.projects_tree.yview)
        scroll_x.config(command=self.projects_tree.xview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        self.projects_tree.bind("<Double-1>", self._on_project_double_click)
    
    # ==================================================================
    # التاب 3: العملاء
    # ==================================================================
    
    def _build_clients_tab(self):
        """بناء تاب العملاء"""
        table_frame = tk.Frame(self.tab_clients, bg="#0f1626")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scroll_y = tk.Scrollbar(table_frame, orient="vertical")
        
        columns = ("#", "name", "company", "phone", "email", "city")
        self.clients_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=scroll_y.set
        )
        
        headers = {
            "#": "#",
            "name": "اسم العميل",
            "company": "الشركة",
            "phone": "الهاتف",
            "email": "البريد",
            "city": "المدينة"
        }
        widths = {"#": 40, "name": 250, "company": 200,
                 "phone": 150, "email": 200, "city": 150}
        
        for col in columns:
            self.clients_tree.heading(col, text=headers[col])
            self.clients_tree.column(col, width=widths[col], anchor="center")
        
        self.clients_tree.pack(side="left", fill="both", expand=True)
        scroll_y.config(command=self.clients_tree.yview)
        scroll_y.pack(side="right", fill="y")
    
    # ==================================================================
    # التاب 4: الإحصائيات
    # ==================================================================
    
    def _build_stats_tab(self):
        """بناء تاب الإحصائيات"""
        container = tk.Frame(self.tab_stats, bg="#0f1626")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.stats_text = tk.Text(
            container,
            font=("Consolas", 12),
            bg="#1a1a2e", fg="#e0e0e0",
            wrap="word", padx=20, pady=20
        )
        self.stats_text.pack(fill="both", expand=True)
        
        # زر تحديث
        tk.Button(
            container,
            text="🔄 تحديث الإحصائيات",
            command=self._load_stats,
            bg="#27AE60", fg="white",
            font=("Arial", 11, "bold"),
            padx=20, pady=8, cursor="hand2"
        ).pack(pady=10)
    
    # ==================================================================
    # تحميل البيانات
    # ==================================================================
    
    def _load_equipment(self):
        """تحميل كل المعدات"""
        self.status_var.set("جاري التحميل...")
        self.results = self.search.list_all()
        self._display_results()
        self.count_var.set(f"{len(self.results)} معدة")
    
    def _load_projects(self):
        """تحميل المشاريع"""
        self.projects = self.db.list_projects()
        
        # مسح الجدول
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        # إضافة المشاريع
        for i, proj in enumerate(self.projects, 1):
            self.projects_tree.insert("", "end", values=(
                i,
                proj.get('project_name', '')[:60],
                (proj.get('client_name') or '')[:40],
                f"{proj.get('fire_suppression_cost', 0):,.0f}",
                f"{proj.get('fire_alarm_cost', 0):,.0f}",
                f"{proj.get('ventilation_cost', 0):,.0f}",
                f"{proj.get('other_systems_cost', 0):,.0f}",
                f"{proj.get('total_with_vat', 0):,.0f}"
            ))
        
        # إحصائيات
        stats = self.db.get_projects_stats()
        if stats:
            self.projects_stats_var.set(
                f"📊 {stats.get('count', 0)} مشروع | "
                f"الإجمالي: {stats.get('total', 0):,.0f} ريال"
            )
    
    def _load_clients(self):
        """تحميل العملاء"""
        clients = self.db.list_clients()
        
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        for i, client in enumerate(clients, 1):
            self.clients_tree.insert("", "end", values=(
                i,
                client.get('name', '')[:60],
                client.get('company', '') or '',
                client.get('phone', '') or '',
                client.get('email', '') or '',
                client.get('city', '') or ''
            ))
    
    def _load_stats(self):
        """عرض الإحصائيات"""
        eq_count = self.db.get_equipment_count()
        proj_count = self.db.get_projects_count()
        client_count = self.db.get_clients_count()
        stats = self.db.get_projects_stats()
        
        text = f"""
╔══════════════════════════════════════════════════════════╗
║              📊 إحصائيات المكتبة الشاملة                 ║
╚══════════════════════════════════════════════════════════╝

📦 المعدات:
   • إجمالي المعدات: {eq_count}
   • SFFECO: 33
   • NAFFCO: 4
   • الرشاشات: 10

📊 المشاريع:
   • إجمالي المشاريع: {proj_count}
   • إجمالي العملاء: {client_count}

💰 التكاليف الإجمالية للمشاريع:
   • أنظمة الإطفاء: {stats.get('fire_total', 0):,.2f} ريال
   • أنظمة الإنذار: {stats.get('alarm_total', 0):,.2f} ريال
   • التهوية: {stats.get('ventilation_total', 0):,.2f} ريال
   • أنظمة أخرى: {stats.get('other_total', 0):,.2f} ريال
   ─────────────────────────────────────────────
   • الإجمالي: {stats.get('total', 0):,.2f} ريال

📈 توزيع النسب:
   • أنظمة الإطفاء: {(stats.get('fire_total', 0) / max(stats.get('total', 1), 1)) * 100:.1f}%
   • أنظمة الإنذار: {(stats.get('alarm_total', 0) / max(stats.get('total', 1), 1)) * 100:.1f}%
   • التهوية: {(stats.get('ventilation_total', 0) / max(stats.get('total', 1), 1)) * 100:.1f}%
   • أنظمة أخرى: {(stats.get('other_total', 0) / max(stats.get('total', 1), 1)) * 100:.1f}%
"""
        
        self.stats_text.delete("1.0", tk.END)
        self.stats_text.insert("1.0", text)
    
    # ==================================================================
    # البحث والعرض
    # ==================================================================
    
    def _do_search(self):
        """تنفيذ البحث"""
        search_text = self.search_var.get().strip()
        manufacturer = self.manufacturer_var.get()
        category = self.category_var.get()
        
        self.results = self.search.list_all()
        
        if manufacturer != "الكل":
            self.results = [r for r in self.results if r.get('manufacturer_name') == manufacturer]
        
        if search_text:
            search_lower = search_text.lower()
            self.results = [
                r for r in self.results
                if search_lower in r.get('model', '').lower()
                or search_lower in r.get('type', '').lower()
            ]
        
        self._display_results()
        self.count_var.set(f"{len(self.results)} معدة")
    
    def _display_results(self):
        """عرض النتائج"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, eq in enumerate(self.results, 1):
            specs = eq.get('specs', {})
            
            package_info = ""
            if specs.get('is_complete_package'):
                package_info = "✅ كاملة"
            elif specs.get('includes_jockey'):
                package_info = "✅ مع جوكي"
            elif specs.get('requires_jockey'):
                package_info = "⚠️ تحتاج جوكي"
            
            self.tree.insert("", "end", values=(
                i,
                eq.get('manufacturer_name', ''),
                eq.get('model', ''),
                eq.get('type', ''),
                specs.get('flow_gpm', 0),
                specs.get('pressure_bar', 0),
                f"{eq.get('price_sar', 0):,.0f}",
                package_info
            ))
    
    # ==================================================================
    # الأحداث
    # ==================================================================
    
    def _on_equipment_double_click(self, event):
        """عرض تفاصيل معدة"""
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        index = int(item['values'][0]) - 1
        if 0 <= index < len(self.results):
            self._show_equipment_details(self.results[index])
    
    def _on_project_double_click(self, event):
        """عرض تفاصيل مشروع"""
        selection = self.projects_tree.selection()
        if not selection:
            return
        item = self.projects_tree.item(selection[0])
        index = int(item['values'][0]) - 1
        if 0 <= index < len(self.projects):
            self._show_project_details(self.projects[index])
    
    def _show_equipment_details(self, equipment):
        """عرض تفاصيل معدة"""
        window = tk.Toplevel(self.root)
        window.title(f"تفاصيل: {equipment['model']}")
        window.geometry("600x650")
        window.configure(bg="#0f1626")
        
        tk.Label(window, text=f"🔧 {equipment['manufacturer_name']} - {equipment['model']}",
                font=("Arial", 16, "bold"), bg="#0f1626", fg="#3498DB",
                pady=15).pack()
        
        text = tk.Text(window, font=("Arial", 11), bg="#1a1a2e", fg="#e0e0e0",
                      wrap="word", padx=15, pady=15)
        text.pack(fill="both", expand=True, padx=20, pady=10)
        
        specs = equipment.get('specs', {})
        content = []
        content.append(f"النوع: {equipment.get('type', '')}\n")
        if specs.get('flow_gpm'):
            content.append(f"التدفق: {specs['flow_gpm']} GPM\n")
        if specs.get('pressure_bar'):
            content.append(f"الضغط: {specs['pressure_bar']} bar\n")
        if specs.get('power_hp'):
            content.append(f"القدرة: {specs['power_hp']} HP\n")
        
        content.append(f"\n📦 محتويات الحزمة:\n")
        if specs.get('is_complete_package'):
            content.append("   ✅ حزمة كاملة جاهزة\n")
        if specs.get('includes_jockey'):
            content.append("   ✅ تشمل مضخة جوكي\n")
        if specs.get('includes_controller'):
            content.append("   ✅ تشمل لوحة تحكم\n")
        
        if equipment.get('certifications'):
            content.append(f"\n🏆 الاعتمادات: {' / '.join(equipment['certifications'])}\n")
        
        content.append(f"\n💰 السعر: {equipment.get('price_sar', 0):,.0f} ريال\n")
        
        text.insert("1.0", "".join(content))
        text.config(state="disabled")
        
        tk.Button(window, text="❌ إغلاق", command=window.destroy,
                 bg="#E74C3C", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=8, cursor="hand2").pack(pady=10)
    
    def _show_project_details(self, project):
        """عرض تفاصيل مشروع"""
        window = tk.Toplevel(self.root)
        window.title(f"تفاصيل: {project['project_name'][:50]}")
        window.geometry("700x600")
        window.configure(bg="#0f1626")
        
        tk.Label(window, text=f"📊 {project['project_name']}",
                font=("Arial", 14, "bold"), bg="#0f1626", fg="#3498DB",
                pady=15, wraplength=650).pack()
        
        text = tk.Text(window, font=("Consolas", 11), bg="#1a1a2e", fg="#e0e0e0",
                      wrap="word", padx=15, pady=15)
        text.pack(fill="both", expand=True, padx=20, pady=10)
        
        content = f"""
📋 معلومات المشروع:
   • الاسم: {project.get('project_name', '')}
   • العميل: {project.get('client_name') or 'غير محدد'}
   • الجهة المنفذة: {project.get('service_provider', '')}

💰 التكاليف:
   • أنظمة الإطفاء: {project.get('fire_suppression_cost', 0):,.2f} ريال
   • أنظمة الإنذار: {project.get('fire_alarm_cost', 0):,.2f} ريال
   • التهوية: {project.get('ventilation_cost', 0):,.2f} ريال
   • أنظمة أخرى: {project.get('other_systems_cost', 0):,.2f} ريال
   ─────────────────────────────────────
   • الإجمالي قبل الضريبة: {project.get('total_before_vat', 0):,.2f} ريال
   • ضريبة 15%: {project.get('vat_15', 0):,.2f} ريال
   • الإجمالي مع الضريبة: {project.get('total_with_vat', 0):,.2f} ريال

📝 ملاحظات:
   {project.get('notes', 'لا توجد ملاحظات')}
"""
        
        text.insert("1.0", content)
        text.config(state="disabled")
        
        tk.Button(window, text="❌ إغلاق", command=window.destroy,
                 bg="#E74C3C", fg="white", font=("Arial", 11, "bold"),
                 padx=30, pady=8, cursor="hand2").pack(pady=10)
    
    # ==================================================================
    # التصدير
    # ==================================================================
    
    def _export_excel(self):
        """تصدير Excel"""
        if not self.results:
            messagebox.showwarning("تنبيه", "لا توجد نتائج")
            return
        
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            messagebox.showerror("خطأ", "مكتبة openpyxl غير مثبتة")
            return
        
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        default_name = f"equipment_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = filedialog.asksaveasfilename(
            title="حفظ Excel",
            initialdir=exports_dir,
            initialfile=default_name,
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        if not filepath:
            return
        
        wb = Workbook()
        ws = wb.active
        ws.title = "المعدات"
        ws.sheet_view.rightToLeft = True
        
        headers = ["#", "المصنع", "الموديل", "النوع", "التدفق", "الضغط", "السعر", "الحزمة"]
        ws.append(headers)
        
        header_fill = PatternFill(start_color="1B4F72", end_color="1B4F72", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=12)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")
        
        for i, eq in enumerate(self.results, 1):
            specs = eq.get('specs', {})
            package = "كاملة" if specs.get('is_complete_package') else \
                     "مع جوكي" if specs.get('includes_jockey') else ""
            
            ws.append([
                i, eq.get('manufacturer_name', ''), eq.get('model', ''),
                eq.get('type', ''), specs.get('flow_gpm', 0),
                specs.get('pressure_bar', 0), eq.get('price_sar', 0), package
            ])
        
        for i, width in enumerate([5, 15, 25, 25, 15, 15, 18, 15], 1):
            ws.column_dimensions[chr(64 + i)].width = width
        
        wb.save(filepath)
        messagebox.showinfo("تم", f"تم الحفظ:\n{filepath}")
    
    def _export_json(self):
        """تصدير JSON"""
        if not self.results:
            messagebox.showwarning("تنبيه", "لا توجد نتائج")
            return
        
        exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        default_name = f"equipment_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = filedialog.asksaveasfilename(
            title="حفظ JSON",
            initialdir=exports_dir,
            initialfile=default_name,
            defaultextension=".json",
            filetypes=[("JSON", "*.json")]
        )
        if not filepath:
            return
        
        export_data = []
        for eq in self.results:
            export_data.append({
                'manufacturer': eq.get('manufacturer_name', ''),
                'model': eq.get('model', ''),
                'type': eq.get('type', ''),
                'specs': eq.get('specs', {}),
                'price_sar': eq.get('price_sar', 0),
                'certifications': eq.get('certifications', []),
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        messagebox.showinfo("تم", f"تم الحفظ:\n{filepath}")
    
    def run(self):
        """تشغيل الواجهة"""
        # تحميل العملاء والإحصائيات عند البدء
        self._load_clients()
        self._load_stats()
        self.root.mainloop()


def main():
    """الدالة الرئيسية"""
    gui = EquipmentLibraryGUI()
    gui.run()


if __name__ == "__main__":
    main()