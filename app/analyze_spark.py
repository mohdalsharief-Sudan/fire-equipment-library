# app/analyze_spark.py
"""
تحليل بنود SPARK المستخرجة
"""

import json
import os
from collections import Counter, defaultdict


def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    json_file = os.path.join(base_dir, 'data', 'projects', 'spark_items.json')
    
    with open(json_file, 'r', encoding='utf-8') as f:
        items = json.load(f)
    
    print("=" * 80)
    print(f"📊 تحليل {len(items)} بند من مشروع SPARK")
    print("=" * 80)
    
    # 1. البنود الفريدة (بدون تكرار)
    unique_descriptions = {}
    for item in items:
        desc = item['description'][:60]
        if desc not in unique_descriptions:
            unique_descriptions[desc] = item
        else:
            # الاحتفاظ بأقل سعر (الأفضل)
            existing = unique_descriptions[desc]
            if item['supply_price'] and (not existing['supply_price'] or item['supply_price'] < existing['supply_price']):
                unique_descriptions[desc] = item
    
    print(f"\n📦 البنود الفريدة: {len(unique_descriptions)}")
    
    # 2. عرض البنود الفريدة
    print("\n" + "=" * 80)
    print("📋 قائمة البنود الفريدة (أول 50):")
    print("=" * 80)
    print(f"{'#':<4} {'الوصف':<50} {'الوحدة':<8} {'البيع':>10} {'التوريد':>10}")
    print("-" * 80)
    
    for i, (desc, item) in enumerate(list(unique_descriptions.items())[:50], 1):
        selling = item['selling_price'] or 0
        supply = item['supply_price'] or 0
        print(f"{i:<4} {desc[:48]:<50} {item['unit'] or '':<8} {selling:>10,.2f} {supply:>10,.2f}")
    
    if len(unique_descriptions) > 50:
        print(f"\n... و {len(unique_descriptions) - 50} بند إضافي")
    
    # 3. تصنيف البنود
    print("\n" + "=" * 80)
    print("🏗️ تصنيف حسب النوع:")
    print("=" * 80)
    
    categories = {
        'Pipe': 0,
        'Cable': 0,
        'Valve': 0,
        'Detector': 0,
        'Module': 0,
        'Panel': 0,
        'Sprinkler': 0,
        'Extinguisher': 0,
        'FHC': 0,
        'Other': 0,
    }
    
    for desc in unique_descriptions:
        d = desc.lower()
        if 'pipe' in d or 'diameter' in d:
            categories['Pipe'] += 1
        elif 'cable' in d or 'mm²' in d:
            categories['Cable'] += 1
        elif 'valve' in d:
            categories['Valve'] += 1
        elif 'detector' in d:
            categories['Detector'] += 1
        elif 'module' in d:
            categories['Module'] += 1
        elif 'panel' in d or 'facp' in d:
            categories['Panel'] += 1
        elif 'sprinkler' in d or 'pendent' in d or 'upright' in d or 'sidewall' in d:
            categories['Sprinkler'] += 1
        elif 'extinguisher' in d:
            categories['Extinguisher'] += 1
        elif 'hose cabinet' in d or 'fhc' in d:
            categories['FHC'] += 1
        else:
            categories['Other'] += 1
    
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"   • {cat}: {count} بند")
    
    # 4. حفظ البنود الفريدة
    output_file = os.path.join(base_dir, 'data', 'projects', 'spark_unique_items.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(unique_descriptions.values()), f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ تم حفظ البنود الفريدة في: {output_file}")


if __name__ == "__main__":
    main()