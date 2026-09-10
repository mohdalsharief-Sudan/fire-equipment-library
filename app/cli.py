# app/cli.py
"""
واجهة سطر الأوامر لمكتبة المعدات
"""

import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.search import EquipmentSearch


def cmd_list(args):
    """عرض كل المعدات"""
    search = EquipmentSearch()
    results = search.list_all()
    search.print_results(results)
    search.close()


def cmd_find(args):
    """البحث عن مضخات"""
    search = EquipmentSearch()
    results = search.find_pumps(
        flow_gpm=args.flow,
        pressure_bar=args.pressure,
        manufacturer=args.manufacturer,
        max_price=args.max_price,
    )
    search.print_results(results)
    search.close()


def cmd_show(args):
    """عرض تفاصيل مضخة"""
    search = EquipmentSearch()
    pump = search.get_by_model(args.model)
    if pump:
        search.print_pump(pump)
    else:
        print(f"❌ لم يتم العثور على: {args.model}")
    search.close()


def main():
    parser = argparse.ArgumentParser(description='مكتبة معدات السلامة')
    subparsers = parser.add_subparsers(dest='command')
    
    # list
    subparsers.add_parser('list', help='عرض كل المعدات')
    
    # find
    find_parser = subparsers.add_parser('find', help='البحث عن مضخات')
    find_parser.add_argument('--flow', type=float, help='الحد الأدنى للتدفق (GPM)')
    find_parser.add_argument('--pressure', type=float, help='الحد الأدنى للضغط (bar)')
    find_parser.add_argument('--manufacturer', type=str, help='المصنع')
    find_parser.add_argument('--max-price', type=float, help='الحد الأقصى للسعر')
    
    # show
    show_parser = subparsers.add_parser('show', help='عرض تفاصيل معدة')
    show_parser.add_argument('model', help='موديل المعدة')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        cmd_list(args)
    elif args.command == 'find':
        cmd_find(args)
    elif args.command == 'show':
        cmd_show(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()