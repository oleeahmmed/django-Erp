#!/usr/bin/env python
"""
ERP Complete Demo Data Import Script
=====================================
সব models এর জন্য demo data তৈরি করে।

Usage: python3 import_demo_data.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User

# Import all models
from erp.models import (
    Company, Warehouse, Category, Product, Customer, Supplier, SalesPerson,
    ProductWarehouseStock, StockTransaction,
    BillOfMaterials, BOMComponent,
    ProductionOrder, ProductionOrderComponent, ProductionReceipt, ProductionReceiptComponent,
    SalesQuotation, SalesQuotationItem,
    SalesOrder, SalesOrderItem,
    Invoice, InvoiceItem,
    Delivery, DeliveryItem,
    SalesReturn, SalesReturnItem,
    PurchaseQuotation, PurchaseQuotationItem,
    PurchaseOrder, PurchaseOrderItem,
    GoodsReceipt, GoodsReceiptItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    PurchaseReturn, PurchaseReturnItem,
    GoodsIssue, GoodsIssueItem,
    InventoryTransfer, InventoryTransferItem,
    StockAdjustment, StockAdjustmentItem,
    BankAccount, IncomingPayment, IncomingPaymentInvoice, OutgoingPayment, OutgoingPaymentInvoice,
    AccountType, ChartOfAccounts, CostCenter, Project, JournalEntry, JournalEntryLine,
    FiscalYear, Budget,
    Currency, ExchangeRate, TaxType, TaxRate, PaymentTerm,
    UnitOfMeasure, UOMConversion,
)

print("=" * 70)
print("ERP COMPLETE DEMO DATA IMPORT")
print("=" * 70)

# ==================== SUPERUSER ====================
print("\n[1/35] Creating Superuser...")
if not User.objects.filter(username='olee').exists():
    user = User.objects.create_superuser(
        username='olee',
        email='olee@example.com',
        password='501302aA',
        first_name='Olee',
        last_name='Admin'
    )
    print(f"   ✓ Superuser created: olee / 501302aA")
else:
    user = User.objects.get(username='olee')
    print(f"   ✓ Superuser already exists: olee")

# ==================== COMPANY ====================
print("\n[2/35] Creating Company...")
company, _ = Company.objects.get_or_create(
    name="ABC Trading Company Ltd",
    defaults={
        'address': '123 Gulshan Avenue, Gulshan-2',
        'city': 'Dhaka',
        'country': 'Bangladesh',
        'phone': '+880-2-9881234',
        'email': 'info@abctrading.com.bd',
        'website': 'https://abctrading.com.bd',
        'tax_number': 'TIN-123456789012',
    }
)
print(f"   ✓ Company: {company.name}")

# ==================== CURRENCIES ====================
print("\n[3/35] Creating Currencies...")
currencies_data = [
    {'code': 'BDT', 'name': 'Bangladeshi Taka', 'symbol': '৳', 'is_base_currency': True},
    {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_base_currency': False},
    {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_base_currency': False},
]
currencies = {}
for c in currencies_data:
    curr, _ = Currency.objects.get_or_create(code=c['code'], defaults=c)
    currencies[c['code']] = curr
    print(f"   ✓ Currency: {curr.code}")

# Exchange Rates
ExchangeRate.objects.get_or_create(from_currency=currencies['USD'], to_currency=currencies['BDT'], defaults={'rate': Decimal('110.50')})
ExchangeRate.objects.get_or_create(from_currency=currencies['EUR'], to_currency=currencies['BDT'], defaults={'rate': Decimal('120.75')})
print("   ✓ Exchange rates created")

# ==================== UNITS OF MEASURE ====================
print("\n[4/35] Creating Units of Measure...")
uom_data = [
    {'code': 'PCS', 'name': 'Pieces', 'uom_type': 'unit', 'is_base_unit': True},
    {'code': 'BOX', 'name': 'Box', 'uom_type': 'unit'},
    {'code': 'REAM', 'name': 'Ream', 'uom_type': 'unit'},
    {'code': 'KG', 'name': 'Kilogram', 'uom_type': 'weight', 'is_base_unit': True},
    {'code': 'GM', 'name': 'Gram', 'uom_type': 'weight'},
    {'code': 'LTR', 'name': 'Liter', 'uom_type': 'volume', 'is_base_unit': True},
    {'code': 'MTR', 'name': 'Meter', 'uom_type': 'length', 'is_base_unit': True},
    {'code': 'SQFT', 'name': 'Square Feet', 'uom_type': 'area', 'is_base_unit': True},
    {'code': 'SHEET', 'name': 'Sheet', 'uom_type': 'unit'},
]
uoms = {}
for u in uom_data:
    uom, _ = UnitOfMeasure.objects.get_or_create(code=u['code'], defaults=u)
    uoms[u['code']] = uom
print(f"   ✓ Created {len(uom_data)} UOMs")

# UOM Conversions
UOMConversion.objects.get_or_create(from_uom=uoms['KG'], to_uom=uoms['GM'], defaults={'conversion_factor': Decimal('1000')})
UOMConversion.objects.get_or_create(from_uom=uoms['BOX'], to_uom=uoms['PCS'], defaults={'conversion_factor': Decimal('12')})

# ==================== TAX TYPES ====================
print("\n[5/35] Creating Tax Types...")
tax_types_data = [
    {'code': 'VAT', 'name': 'Value Added Tax', 'category': 'both'},
    {'code': 'SD', 'name': 'Supplementary Duty', 'category': 'sales'},
    {'code': 'AIT', 'name': 'Advance Income Tax', 'category': 'purchase'},
]
tax_types = {}
for t in tax_types_data:
    tt, _ = TaxType.objects.get_or_create(code=t['code'], defaults=t)
    tax_types[t['code']] = tt
print(f"   ✓ Created {len(tax_types_data)} tax types")

# Tax Rates
TaxRate.objects.get_or_create(tax_type=tax_types['VAT'], name='Standard VAT', defaults={'rate': Decimal('15'), 'is_default': True})
TaxRate.objects.get_or_create(tax_type=tax_types['VAT'], name='Reduced VAT', defaults={'rate': Decimal('7.5')})
TaxRate.objects.get_or_create(tax_type=tax_types['SD'], name='Standard SD', defaults={'rate': Decimal('10'), 'is_default': True})
TaxRate.objects.get_or_create(tax_type=tax_types['AIT'], name='Standard AIT', defaults={'rate': Decimal('5'), 'is_default': True})

# ==================== PAYMENT TERMS ====================
print("\n[6/35] Creating Payment Terms...")
payment_terms_data = [
    {'code': 'CASH', 'name': 'Cash on Delivery', 'days': 0, 'is_default': True},
    {'code': 'NET15', 'name': 'Net 15 Days', 'days': 15},
    {'code': 'NET30', 'name': 'Net 30 Days', 'days': 30},
    {'code': 'NET45', 'name': 'Net 45 Days', 'days': 45},
    {'code': 'NET60', 'name': 'Net 60 Days', 'days': 60},
    {'code': '2/10N30', 'name': '2% 10 Net 30', 'days': 30, 'discount_days': 10, 'discount_percentage': Decimal('2')},
]
for pt in payment_terms_data:
    PaymentTerm.objects.get_or_create(code=pt['code'], defaults=pt)
print(f"   ✓ Created {len(payment_terms_data)} payment terms")

# ==================== WAREHOUSES ====================
print("\n[7/35] Creating Warehouses...")
warehouses_data = [
    {'name': 'Main Warehouse', 'code': 'WH-MAIN', 'city': 'Dhaka', 'address': 'Tejgaon Industrial Area', 'manager': 'Rahim Khan'},
    {'name': 'Chittagong Warehouse', 'code': 'WH-CTG', 'city': 'Chittagong', 'address': 'Port Area, Chittagong', 'manager': 'Karim Ahmed'},
    {'name': 'Showroom Stock', 'code': 'WH-SHOW', 'city': 'Dhaka', 'address': 'Gulshan-2', 'manager': 'Fatima Begum'},
    {'name': 'Raw Materials Store', 'code': 'WH-RAW', 'city': 'Gazipur', 'address': 'Gazipur Industrial Zone', 'manager': 'Abdul Haque'},
    {'name': 'Finished Goods Store', 'code': 'WH-FIN', 'city': 'Dhaka', 'address': 'Uttara Sector-10', 'manager': 'Nasir Uddin'},
]
warehouses = {}
for wh in warehouses_data:
    w, _ = Warehouse.objects.get_or_create(code=wh['code'], defaults=wh)
    warehouses[wh['code']] = w
    print(f"   ✓ Warehouse: {w.name}")

# ==================== CATEGORIES ====================
print("\n[8/35] Creating Categories...")
categories_data = ['Electronics', 'Furniture', 'Office Supplies', 'Raw Materials', 'Finished Goods', 'Packaging', 'Spare Parts']
categories = {}
for cat_name in categories_data:
    cat, _ = Category.objects.get_or_create(name=cat_name)
    categories[cat_name] = cat
print(f"   ✓ Created {len(categories_data)} categories")


# ==================== PRODUCTS ====================
print("\n[9/35] Creating Products...")
products_data = [
    # Electronics
    {'name': 'Laptop Dell Inspiron 15', 'sku': 'ELEC-001', 'category': 'Electronics', 'purchase_price': 45000, 'selling_price': 55000, 'unit': 'PCS'},
    {'name': 'Desktop Computer HP ProDesk', 'sku': 'ELEC-002', 'category': 'Electronics', 'purchase_price': 35000, 'selling_price': 42000, 'unit': 'PCS'},
    {'name': 'LED Monitor 24" Samsung', 'sku': 'ELEC-003', 'category': 'Electronics', 'purchase_price': 12000, 'selling_price': 15000, 'unit': 'PCS'},
    {'name': 'Wireless Mouse Logitech', 'sku': 'ELEC-004', 'category': 'Electronics', 'purchase_price': 500, 'selling_price': 750, 'unit': 'PCS'},
    {'name': 'USB Keyboard A4Tech', 'sku': 'ELEC-005', 'category': 'Electronics', 'purchase_price': 400, 'selling_price': 600, 'unit': 'PCS'},
    {'name': 'Printer HP LaserJet', 'sku': 'ELEC-006', 'category': 'Electronics', 'purchase_price': 18000, 'selling_price': 22000, 'unit': 'PCS'},
    {'name': 'UPS 1000VA', 'sku': 'ELEC-007', 'category': 'Electronics', 'purchase_price': 5000, 'selling_price': 6500, 'unit': 'PCS'},
    # Furniture
    {'name': 'Office Chair Executive', 'sku': 'FURN-001', 'category': 'Furniture', 'purchase_price': 8000, 'selling_price': 12000, 'unit': 'PCS'},
    {'name': 'Office Desk 5x3 ft', 'sku': 'FURN-002', 'category': 'Furniture', 'purchase_price': 15000, 'selling_price': 22000, 'unit': 'PCS'},
    {'name': 'Filing Cabinet 4 Drawer', 'sku': 'FURN-003', 'category': 'Furniture', 'purchase_price': 6000, 'selling_price': 9000, 'unit': 'PCS'},
    {'name': 'Conference Table 10 Seater', 'sku': 'FURN-004', 'category': 'Furniture', 'purchase_price': 35000, 'selling_price': 50000, 'unit': 'PCS'},
    {'name': 'Bookshelf 5 Tier', 'sku': 'FURN-005', 'category': 'Furniture', 'purchase_price': 4000, 'selling_price': 6000, 'unit': 'PCS'},
    # Office Supplies
    {'name': 'A4 Paper (Ream 500 sheets)', 'sku': 'OFFC-001', 'category': 'Office Supplies', 'purchase_price': 350, 'selling_price': 450, 'unit': 'REAM'},
    {'name': 'Ballpoint Pen Box (50 pcs)', 'sku': 'OFFC-002', 'category': 'Office Supplies', 'purchase_price': 150, 'selling_price': 220, 'unit': 'BOX'},
    {'name': 'Stapler Heavy Duty', 'sku': 'OFFC-003', 'category': 'Office Supplies', 'purchase_price': 200, 'selling_price': 300, 'unit': 'PCS'},
    {'name': 'Whiteboard 4x3 ft', 'sku': 'OFFC-004', 'category': 'Office Supplies', 'purchase_price': 1500, 'selling_price': 2200, 'unit': 'PCS'},
    {'name': 'Marker Pen Set (12 colors)', 'sku': 'OFFC-005', 'category': 'Office Supplies', 'purchase_price': 250, 'selling_price': 380, 'unit': 'SET'},
    # Raw Materials
    {'name': 'Steel Sheet 4x8 ft', 'sku': 'RAW-001', 'category': 'Raw Materials', 'purchase_price': 2500, 'selling_price': 3000, 'unit': 'SHEET'},
    {'name': 'Aluminum Rod 10mm', 'sku': 'RAW-002', 'category': 'Raw Materials', 'purchase_price': 800, 'selling_price': 1000, 'unit': 'KG'},
    {'name': 'Plastic Granules ABS', 'sku': 'RAW-003', 'category': 'Raw Materials', 'purchase_price': 120, 'selling_price': 150, 'unit': 'KG'},
    {'name': 'Wood Plywood 8x4 ft', 'sku': 'RAW-004', 'category': 'Raw Materials', 'purchase_price': 1800, 'selling_price': 2200, 'unit': 'SHEET'},
    {'name': 'Screw Set (100 pcs)', 'sku': 'RAW-005', 'category': 'Raw Materials', 'purchase_price': 80, 'selling_price': 120, 'unit': 'BOX'},
    # Finished Goods
    {'name': 'Computer Table Assembled', 'sku': 'FIN-001', 'category': 'Finished Goods', 'purchase_price': 5000, 'selling_price': 8000, 'unit': 'PCS'},
    {'name': 'Office Workstation Complete', 'sku': 'FIN-002', 'category': 'Finished Goods', 'purchase_price': 25000, 'selling_price': 35000, 'unit': 'SET'},
    # Packaging
    {'name': 'Carton Box Large', 'sku': 'PKG-001', 'category': 'Packaging', 'purchase_price': 50, 'selling_price': 80, 'unit': 'PCS'},
    {'name': 'Bubble Wrap Roll', 'sku': 'PKG-002', 'category': 'Packaging', 'purchase_price': 300, 'selling_price': 450, 'unit': 'ROLL'},
    # Spare Parts
    {'name': 'Laptop Battery Universal', 'sku': 'SPR-001', 'category': 'Spare Parts', 'purchase_price': 2000, 'selling_price': 3000, 'unit': 'PCS'},
    {'name': 'Laptop Charger 65W', 'sku': 'SPR-002', 'category': 'Spare Parts', 'purchase_price': 800, 'selling_price': 1200, 'unit': 'PCS'},
]
products = {}
for p in products_data:
    product, _ = Product.objects.get_or_create(
        sku=p['sku'],
        defaults={
            'name': p['name'],
            'category': categories[p['category']],
            'purchase_price': Decimal(str(p['purchase_price'])),
            'selling_price': Decimal(str(p['selling_price'])),
            'unit': p['unit'],
            'default_warehouse': warehouses['WH-MAIN'],
            'min_stock_level': Decimal('10'),
        }
    )
    products[p['sku']] = product
print(f"   ✓ Created {len(products_data)} products")

# ==================== INITIAL STOCK ====================
print("\n[10/35] Creating Initial Stock...")
initial_stock = [
    # Main Warehouse
    ('ELEC-001', 'WH-MAIN', 50), ('ELEC-002', 'WH-MAIN', 30), ('ELEC-003', 'WH-MAIN', 100),
    ('ELEC-004', 'WH-MAIN', 200), ('ELEC-005', 'WH-MAIN', 150), ('ELEC-006', 'WH-MAIN', 25),
    ('ELEC-007', 'WH-MAIN', 40), ('FURN-001', 'WH-MAIN', 25), ('FURN-002', 'WH-MAIN', 15),
    ('FURN-003', 'WH-MAIN', 20), ('FURN-004', 'WH-MAIN', 5), ('FURN-005', 'WH-MAIN', 30),
    ('OFFC-001', 'WH-MAIN', 500), ('OFFC-002', 'WH-MAIN', 100), ('OFFC-003', 'WH-MAIN', 50),
    ('OFFC-004', 'WH-MAIN', 20), ('OFFC-005', 'WH-MAIN', 40),
    ('FIN-001', 'WH-MAIN', 40), ('FIN-002', 'WH-MAIN', 10),
    ('PKG-001', 'WH-MAIN', 500), ('PKG-002', 'WH-MAIN', 50),
    ('SPR-001', 'WH-MAIN', 30), ('SPR-002', 'WH-MAIN', 50),
    # Raw Materials Store
    ('RAW-001', 'WH-RAW', 200), ('RAW-002', 'WH-RAW', 500), ('RAW-003', 'WH-RAW', 1000),
    ('RAW-004', 'WH-RAW', 150), ('RAW-005', 'WH-RAW', 200),
    # Chittagong Warehouse
    ('ELEC-001', 'WH-CTG', 20), ('ELEC-003', 'WH-CTG', 50), ('FURN-001', 'WH-CTG', 10),
    ('OFFC-001', 'WH-CTG', 200),
    # Showroom
    ('ELEC-001', 'WH-SHOW', 5), ('ELEC-002', 'WH-SHOW', 3), ('ELEC-003', 'WH-SHOW', 10),
    ('FURN-001', 'WH-SHOW', 5), ('FURN-002', 'WH-SHOW', 3),
    # Finished Goods Store
    ('FIN-001', 'WH-FIN', 50), ('FIN-002', 'WH-FIN', 20),
]
for sku, wh_code, qty in initial_stock:
    if sku in products and wh_code in warehouses:
        stock, created = ProductWarehouseStock.objects.get_or_create(
            product=products[sku], warehouse=warehouses[wh_code],
            defaults={'quantity': Decimal(str(qty))}
        )
        if not created:
            stock.quantity = Decimal(str(qty))
            stock.save()
print(f"   ✓ Created {len(initial_stock)} stock records")


# ==================== CUSTOMERS ====================
print("\n[11/35] Creating Customers...")
customers_data = [
    {'name': 'Tech Solutions Ltd', 'phone': '01711111111', 'email': 'info@techsolutions.com', 'city': 'Dhaka', 'address': 'Banani, Road 11, House 45'},
    {'name': 'Office World Bangladesh', 'phone': '01722222222', 'email': 'sales@officeworld.com.bd', 'city': 'Dhaka', 'address': 'Motijheel C/A'},
    {'name': 'Furniture House CTG', 'phone': '01733333333', 'email': 'contact@furniturehouse.com', 'city': 'Chittagong', 'address': 'GEC Circle'},
    {'name': 'ABC Corporation', 'phone': '01744444444', 'email': 'purchase@abccorp.com', 'city': 'Dhaka', 'address': 'Gulshan-2, Road 45'},
    {'name': 'XYZ Enterprises', 'phone': '01755555555', 'email': 'info@xyzent.com', 'city': 'Sylhet', 'address': 'Zindabazar'},
    {'name': 'Global Traders BD', 'phone': '01766666666', 'email': 'trade@globaltraders.com.bd', 'city': 'Dhaka', 'address': 'Uttara Sector-7'},
    {'name': 'Smart Office Solutions', 'phone': '01777777777', 'email': 'hello@smartoffice.com', 'city': 'Dhaka', 'address': 'Dhanmondi Road 27'},
    {'name': 'Digital Zone Rajshahi', 'phone': '01788888888', 'email': 'sales@digitalzone.com', 'city': 'Rajshahi', 'address': 'Shaheb Bazar'},
    {'name': 'IT Hub Khulna', 'phone': '01799999999', 'email': 'info@ithub.com', 'city': 'Khulna', 'address': 'KDA Avenue'},
    {'name': 'Corporate Solutions', 'phone': '01611111111', 'email': 'corp@solutions.com', 'city': 'Dhaka', 'address': 'Bashundhara R/A'},
]
customers = {}
for c in customers_data:
    customer, _ = Customer.objects.get_or_create(
        name=c['name'],
        defaults={**c, 'country': 'Bangladesh', 'credit_limit': Decimal('500000')}
    )
    customers[c['name']] = customer
print(f"   ✓ Created {len(customers_data)} customers")

# ==================== SUPPLIERS ====================
print("\n[12/35] Creating Suppliers...")
suppliers_data = [
    {'name': 'Dell Bangladesh Ltd', 'phone': '01811111111', 'email': 'sales@dell.com.bd', 'city': 'Dhaka', 'address': 'Gulshan-1'},
    {'name': 'HP Authorized Distributor', 'phone': '01822222222', 'email': 'order@hpbd.com', 'city': 'Dhaka', 'address': 'Banani DOHS'},
    {'name': 'Furniture Factory Ltd', 'phone': '01833333333', 'email': 'supply@furniturefactory.com', 'city': 'Gazipur', 'address': 'Tongi Industrial Area'},
    {'name': 'Paper & Stationery Co', 'phone': '01844444444', 'email': 'sales@paperco.com', 'city': 'Dhaka', 'address': 'Nawabpur'},
    {'name': 'Steel Industries BD', 'phone': '01855555555', 'email': 'order@steelindustries.com', 'city': 'Chittagong', 'address': 'CEPZ'},
    {'name': 'Plastic Raw Materials', 'phone': '01866666666', 'email': 'supply@plasticraw.com', 'city': 'Dhaka', 'address': 'Tejgaon'},
    {'name': 'Samsung Electronics BD', 'phone': '01877777777', 'email': 'b2b@samsung.com.bd', 'city': 'Dhaka', 'address': 'Gulshan-2'},
    {'name': 'Logitech Distributor', 'phone': '01888888888', 'email': 'sales@logitech.com.bd', 'city': 'Dhaka', 'address': 'Uttara'},
]
suppliers = {}
for s in suppliers_data:
    supplier, _ = Supplier.objects.get_or_create(
        name=s['name'],
        defaults={**s, 'country': 'Bangladesh'}
    )
    suppliers[s['name']] = supplier
print(f"   ✓ Created {len(suppliers_data)} suppliers")

# ==================== SALES PERSONS ====================
print("\n[13/35] Creating Sales Persons...")
salespersons_data = [
    {'name': 'Rahim Ahmed', 'phone': '01911111111', 'email': 'rahim@company.com', 'employee_id': 'EMP-001', 'commission_rate': Decimal('2.5')},
    {'name': 'Karim Khan', 'phone': '01922222222', 'email': 'karim@company.com', 'employee_id': 'EMP-002', 'commission_rate': Decimal('3.0')},
    {'name': 'Fatima Begum', 'phone': '01933333333', 'email': 'fatima@company.com', 'employee_id': 'EMP-003', 'commission_rate': Decimal('2.0')},
    {'name': 'Nasir Uddin', 'phone': '01944444444', 'email': 'nasir@company.com', 'employee_id': 'EMP-004', 'commission_rate': Decimal('2.5')},
    {'name': 'Salma Akter', 'phone': '01955555555', 'email': 'salma@company.com', 'employee_id': 'EMP-005', 'commission_rate': Decimal('3.5')},
]
salespersons = {}
for sp in salespersons_data:
    person, _ = SalesPerson.objects.get_or_create(name=sp['name'], defaults=sp)
    salespersons[sp['name']] = person
print(f"   ✓ Created {len(salespersons_data)} sales persons")

# ==================== BANK ACCOUNTS ====================
print("\n[14/35] Creating Bank Accounts...")
banks_data = [
    {'account_name': 'Main Operating Account', 'account_number': '1234567890123', 'bank_name': 'Dutch Bangla Bank Ltd', 'branch': 'Gulshan', 'account_type': 'checking', 'opening_balance': Decimal('5000000')},
    {'account_name': 'Savings Account', 'account_number': '9876543210987', 'bank_name': 'BRAC Bank Ltd', 'branch': 'Banani', 'account_type': 'savings', 'opening_balance': Decimal('2000000')},
    {'account_name': 'Petty Cash', 'account_number': 'CASH-001', 'bank_name': 'Office Cash Box', 'branch': 'Head Office', 'account_type': 'cash', 'opening_balance': Decimal('100000')},
    {'account_name': 'Foreign Currency Account', 'account_number': 'FC-USD-001', 'bank_name': 'Standard Chartered', 'branch': 'Gulshan', 'account_type': 'checking', 'opening_balance': Decimal('500000'), 'currency': 'USD'},
]
bank_accounts = {}
for b in banks_data:
    bank, _ = BankAccount.objects.get_or_create(
        account_number=b['account_number'],
        defaults={**b, 'current_balance': b['opening_balance']}
    )
    bank_accounts[b['account_name']] = bank
print(f"   ✓ Created {len(banks_data)} bank accounts")

# ==================== ACCOUNT TYPES ====================
print("\n[15/35] Creating Account Types...")
account_types_data = [
    {'name': 'Current Assets', 'type_category': 'asset'},
    {'name': 'Fixed Assets', 'type_category': 'asset'},
    {'name': 'Current Liabilities', 'type_category': 'liability'},
    {'name': 'Long Term Liabilities', 'type_category': 'liability'},
    {'name': 'Share Capital', 'type_category': 'equity'},
    {'name': 'Retained Earnings', 'type_category': 'equity'},
    {'name': 'Sales Revenue', 'type_category': 'revenue'},
    {'name': 'Other Income', 'type_category': 'revenue'},
    {'name': 'Cost of Goods Sold', 'type_category': 'expense'},
    {'name': 'Operating Expenses', 'type_category': 'expense'},
    {'name': 'Administrative Expenses', 'type_category': 'expense'},
]
account_types = {}
for at in account_types_data:
    acc_type, _ = AccountType.objects.get_or_create(name=at['name'], defaults=at)
    account_types[at['name']] = acc_type
print(f"   ✓ Created {len(account_types_data)} account types")

# ==================== CHART OF ACCOUNTS ====================
print("\n[16/35] Creating Chart of Accounts...")
coa_data = [
    {'account_code': '1000', 'account_name': 'Cash and Bank', 'account_type': 'Current Assets'},
    {'account_code': '1100', 'account_name': 'Accounts Receivable', 'account_type': 'Current Assets'},
    {'account_code': '1200', 'account_name': 'Inventory', 'account_type': 'Current Assets'},
    {'account_code': '1500', 'account_name': 'Fixed Assets', 'account_type': 'Fixed Assets'},
    {'account_code': '2000', 'account_name': 'Accounts Payable', 'account_type': 'Current Liabilities'},
    {'account_code': '2100', 'account_name': 'VAT Payable', 'account_type': 'Current Liabilities'},
    {'account_code': '3000', 'account_name': 'Share Capital', 'account_type': 'Share Capital'},
    {'account_code': '3100', 'account_name': 'Retained Earnings', 'account_type': 'Retained Earnings'},
    {'account_code': '4000', 'account_name': 'Sales Revenue', 'account_type': 'Sales Revenue'},
    {'account_code': '4100', 'account_name': 'Sales Returns', 'account_type': 'Sales Revenue'},
    {'account_code': '5000', 'account_name': 'Cost of Goods Sold', 'account_type': 'Cost of Goods Sold'},
    {'account_code': '6000', 'account_name': 'Salaries Expense', 'account_type': 'Operating Expenses'},
    {'account_code': '6100', 'account_name': 'Rent Expense', 'account_type': 'Operating Expenses'},
    {'account_code': '6200', 'account_name': 'Utilities Expense', 'account_type': 'Operating Expenses'},
]
chart_accounts = {}
for coa in coa_data:
    acc, _ = ChartOfAccounts.objects.get_or_create(
        account_code=coa['account_code'],
        defaults={'account_name': coa['account_name'], 'account_type': account_types[coa['account_type']]}
    )
    chart_accounts[coa['account_code']] = acc
print(f"   ✓ Created {len(coa_data)} GL accounts")


# ==================== COST CENTERS ====================
print("\n[17/35] Creating Cost Centers...")
cost_centers_data = [
    {'code': 'CC-ADMIN', 'name': 'Administration', 'manager': 'CEO'},
    {'code': 'CC-SALES', 'name': 'Sales Department', 'manager': 'Sales Manager'},
    {'code': 'CC-PURCH', 'name': 'Procurement', 'manager': 'Purchase Manager'},
    {'code': 'CC-PROD', 'name': 'Production', 'manager': 'Production Manager'},
    {'code': 'CC-WH', 'name': 'Warehouse Operations', 'manager': 'Warehouse Manager'},
]
cost_centers = {}
for cc in cost_centers_data:
    center, _ = CostCenter.objects.get_or_create(code=cc['code'], defaults=cc)
    cost_centers[cc['code']] = center
print(f"   ✓ Created {len(cost_centers_data)} cost centers")

# ==================== PROJECTS ====================
print("\n[18/35] Creating Projects...")
projects_data = [
    {'project_code': 'PRJ-001', 'project_name': 'Office Setup - ABC Corp', 'customer': 'ABC Corporation', 'status': 'active', 'budget_amount': Decimal('500000')},
    {'project_code': 'PRJ-002', 'project_name': 'IT Infrastructure - Tech Solutions', 'customer': 'Tech Solutions Ltd', 'status': 'active', 'budget_amount': Decimal('1000000')},
    {'project_code': 'PRJ-003', 'project_name': 'Furniture Supply - Office World', 'customer': 'Office World Bangladesh', 'status': 'planning', 'budget_amount': Decimal('300000')},
]
projects = {}
for p in projects_data:
    proj, _ = Project.objects.get_or_create(
        project_code=p['project_code'],
        defaults={
            'project_name': p['project_name'],
            'customer': customers.get(p['customer']),
            'status': p['status'],
            'budget_amount': p['budget_amount'],
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=90),
        }
    )
    projects[p['project_code']] = proj
print(f"   ✓ Created {len(projects_data)} projects")

# ==================== FISCAL YEAR ====================
print("\n[19/35] Creating Fiscal Year...")
fy, _ = FiscalYear.objects.get_or_create(
    year_name='FY 2025-2026',
    defaults={
        'start_date': date(2025, 7, 1),
        'end_date': date(2026, 6, 30),
    }
)
print(f"   ✓ Fiscal Year: {fy.year_name}")

# ==================== BILL OF MATERIALS ====================
print("\n[20/35] Creating Bill of Materials...")
# BOM 1: Computer Table
bom1, created = BillOfMaterials.objects.get_or_create(
    product=products['FIN-001'],
    name='Computer Table Assembly',
    defaults={'version': '1.0', 'quantity': Decimal('1'), 'status': 'active', 'labor_cost': Decimal('500'), 'overhead_cost': Decimal('200')}
)
if created:
    BOMComponent.objects.create(bom=bom1, product=products['RAW-004'], quantity=Decimal('2'), scrap_percentage=Decimal('5'))
    BOMComponent.objects.create(bom=bom1, product=products['RAW-005'], quantity=Decimal('1'), scrap_percentage=Decimal('2'))
print(f"   ✓ BOM: {bom1.name}")

# BOM 2: Office Workstation
bom2, created = BillOfMaterials.objects.get_or_create(
    product=products['FIN-002'],
    name='Office Workstation Complete',
    defaults={'version': '1.0', 'quantity': Decimal('1'), 'status': 'active', 'labor_cost': Decimal('2000'), 'overhead_cost': Decimal('500')}
)
if created:
    BOMComponent.objects.create(bom=bom2, product=products['FURN-002'], quantity=Decimal('1'))
    BOMComponent.objects.create(bom=bom2, product=products['FURN-001'], quantity=Decimal('1'))
    BOMComponent.objects.create(bom=bom2, product=products['FIN-001'], quantity=Decimal('1'))
print(f"   ✓ BOM: {bom2.name}")

# ==================== SALES QUOTATIONS ====================
print("\n[21/35] Creating Sales Quotations...")
if not SalesQuotation.objects.exists():
    # Quotation 1
    sq1 = SalesQuotation.objects.create(
        customer=customers['Tech Solutions Ltd'],
        salesperson=salespersons['Rahim Ahmed'],
        status='sent',
        valid_until=date.today() + timedelta(days=30),
        payment_terms='Net 30',
        tax_rate=Decimal('15'),
    )
    SalesQuotationItem.objects.create(sales_quotation=sq1, product=products['ELEC-001'], quantity=Decimal('10'), unit_price=products['ELEC-001'].selling_price)
    SalesQuotationItem.objects.create(sales_quotation=sq1, product=products['ELEC-003'], quantity=Decimal('10'), unit_price=products['ELEC-003'].selling_price)
    SalesQuotationItem.objects.create(sales_quotation=sq1, product=products['ELEC-004'], quantity=Decimal('20'), unit_price=products['ELEC-004'].selling_price)
    print(f"   ✓ Sales Quotation: {sq1.quotation_number}")
    
    # Quotation 2
    sq2 = SalesQuotation.objects.create(
        customer=customers['ABC Corporation'],
        salesperson=salespersons['Karim Khan'],
        status='draft',
        valid_until=date.today() + timedelta(days=15),
        payment_terms='Net 15',
    )
    SalesQuotationItem.objects.create(sales_quotation=sq2, product=products['FURN-001'], quantity=Decimal('20'), unit_price=products['FURN-001'].selling_price)
    SalesQuotationItem.objects.create(sales_quotation=sq2, product=products['FURN-002'], quantity=Decimal('10'), unit_price=products['FURN-002'].selling_price)
    print(f"   ✓ Sales Quotation: {sq2.quotation_number}")
else:
    print("   ✓ Sales Quotations already exist")

# ==================== SALES ORDERS ====================
print("\n[22/35] Creating Sales Orders...")
if not SalesOrder.objects.exists():
    # SO 1 - Confirmed
    so1 = SalesOrder.objects.create(
        customer=customers['Office World Bangladesh'],
        salesperson=salespersons['Fatima Begum'],
        status='confirmed',
        payment_terms='Net 30',
        delivery_date=date.today() + timedelta(days=7),
    )
    SalesOrderItem.objects.create(sales_order=so1, product=products['FURN-001'], quantity=Decimal('15'), unit_price=products['FURN-001'].selling_price)
    SalesOrderItem.objects.create(sales_order=so1, product=products['FURN-002'], quantity=Decimal('8'), unit_price=products['FURN-002'].selling_price)
    SalesOrderItem.objects.create(sales_order=so1, product=products['FURN-003'], quantity=Decimal('10'), unit_price=products['FURN-003'].selling_price)
    print(f"   ✓ Sales Order: {so1.order_number}")
    
    # SO 2 - Confirmed
    so2 = SalesOrder.objects.create(
        customer=customers['Tech Solutions Ltd'],
        salesperson=salespersons['Rahim Ahmed'],
        status='confirmed',
        payment_terms='Net 15',
    )
    SalesOrderItem.objects.create(sales_order=so2, product=products['ELEC-001'], quantity=Decimal('25'), unit_price=products['ELEC-001'].selling_price)
    SalesOrderItem.objects.create(sales_order=so2, product=products['ELEC-002'], quantity=Decimal('15'), unit_price=products['ELEC-002'].selling_price)
    SalesOrderItem.objects.create(sales_order=so2, product=products['ELEC-003'], quantity=Decimal('40'), unit_price=products['ELEC-003'].selling_price)
    print(f"   ✓ Sales Order: {so2.order_number}")
    
    # SO 3 - Draft
    so3 = SalesOrder.objects.create(
        customer=customers['Global Traders BD'],
        salesperson=salespersons['Nasir Uddin'],
        status='draft',
    )
    SalesOrderItem.objects.create(sales_order=so3, product=products['OFFC-001'], quantity=Decimal('100'), unit_price=products['OFFC-001'].selling_price)
    SalesOrderItem.objects.create(sales_order=so3, product=products['OFFC-002'], quantity=Decimal('50'), unit_price=products['OFFC-002'].selling_price)
    print(f"   ✓ Sales Order: {so3.order_number}")
else:
    print("   ✓ Sales Orders already exist")


# ==================== PURCHASE QUOTATIONS ====================
print("\n[23/35] Creating Purchase Quotations...")
if not PurchaseQuotation.objects.exists():
    pq1 = PurchaseQuotation.objects.create(
        supplier=suppliers['Dell Bangladesh Ltd'],
        status='received',
        valid_until=date.today() + timedelta(days=30),
    )
    PurchaseQuotationItem.objects.create(purchase_quotation=pq1, product=products['ELEC-001'], quantity=Decimal('100'), unit_price=products['ELEC-001'].purchase_price)
    PurchaseQuotationItem.objects.create(purchase_quotation=pq1, product=products['ELEC-006'], quantity=Decimal('50'), unit_price=products['ELEC-006'].purchase_price)
    print(f"   ✓ Purchase Quotation: {pq1.quotation_number}")
else:
    print("   ✓ Purchase Quotations already exist")

# ==================== PURCHASE ORDERS ====================
print("\n[24/35] Creating Purchase Orders...")
if not PurchaseOrder.objects.exists():
    # PO 1
    po1 = PurchaseOrder.objects.create(
        supplier=suppliers['Dell Bangladesh Ltd'],
        status='confirmed',
        expected_date=date.today() + timedelta(days=14),
    )
    PurchaseOrderItem.objects.create(purchase_order=po1, product=products['ELEC-001'], quantity=Decimal('50'), unit_price=products['ELEC-001'].purchase_price)
    PurchaseOrderItem.objects.create(purchase_order=po1, product=products['ELEC-003'], quantity=Decimal('100'), unit_price=products['ELEC-003'].purchase_price)
    print(f"   ✓ Purchase Order: {po1.order_number}")
    
    # PO 2
    po2 = PurchaseOrder.objects.create(
        supplier=suppliers['Furniture Factory Ltd'],
        status='sent',
    )
    PurchaseOrderItem.objects.create(purchase_order=po2, product=products['FURN-001'], quantity=Decimal('30'), unit_price=products['FURN-001'].purchase_price)
    PurchaseOrderItem.objects.create(purchase_order=po2, product=products['FURN-002'], quantity=Decimal('20'), unit_price=products['FURN-002'].purchase_price)
    print(f"   ✓ Purchase Order: {po2.order_number}")
    
    # PO 3 - Raw Materials
    po3 = PurchaseOrder.objects.create(
        supplier=suppliers['Steel Industries BD'],
        status='confirmed',
    )
    PurchaseOrderItem.objects.create(purchase_order=po3, product=products['RAW-001'], quantity=Decimal('100'), unit_price=products['RAW-001'].purchase_price)
    PurchaseOrderItem.objects.create(purchase_order=po3, product=products['RAW-002'], quantity=Decimal('200'), unit_price=products['RAW-002'].purchase_price)
    print(f"   ✓ Purchase Order: {po3.order_number}")
else:
    print("   ✓ Purchase Orders already exist")

# ==================== GOODS RECEIPTS ====================
print("\n[25/35] Creating Goods Receipts...")
if not GoodsReceipt.objects.exists():
    po = PurchaseOrder.objects.filter(status='confirmed').first()
    if po:
        grn = GoodsReceipt.objects.create(
            purchase_order=po,
            supplier=po.supplier,
            warehouse=warehouses['WH-MAIN'],
            status='pending',
            receipt_type='purchase',
            received_by='Warehouse Staff',
        )
        for po_item in po.items.all():
            GoodsReceiptItem.objects.create(
                goods_receipt=grn,
                product=po_item.product,
                quantity=po_item.quantity,
                received_quantity=po_item.quantity,
                unit_price=po_item.unit_price,
            )
        print(f"   ✓ Goods Receipt: {grn.receipt_number}")
else:
    print("   ✓ Goods Receipts already exist")

# ==================== DELIVERIES ====================
print("\n[26/35] Creating Deliveries...")
if not Delivery.objects.exists():
    so = SalesOrder.objects.filter(status='confirmed').first()
    if so:
        delivery = Delivery.objects.create(
            sales_order=so,
            customer=so.customer,
            salesperson=so.salesperson,
            warehouse=warehouses['WH-MAIN'],
            status='pending',
            delivery_address=so.customer.address,
            carrier='ABC Logistics',
        )
        for so_item in so.items.all():
            DeliveryItem.objects.create(
                delivery=delivery,
                product=so_item.product,
                quantity=so_item.quantity,
                unit_price=so_item.unit_price,
            )
        print(f"   ✓ Delivery: {delivery.delivery_number}")
else:
    print("   ✓ Deliveries already exist")

# ==================== INVOICES ====================
print("\n[27/35] Creating Invoices...")
if not Invoice.objects.exists():
    so = SalesOrder.objects.filter(status='confirmed').first()
    if so:
        invoice = Invoice.objects.create(
            sales_order=so,
            customer=so.customer,
            salesperson=so.salesperson,
            status='draft',
            due_date=date.today() + timedelta(days=30),
        )
        for so_item in so.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                product=so_item.product,
                quantity=so_item.quantity,
                unit_price=so_item.unit_price,
            )
        print(f"   ✓ Invoice: {invoice.invoice_number}")
else:
    print("   ✓ Invoices already exist")

# ==================== PURCHASE INVOICES ====================
print("\n[28/35] Creating Purchase Invoices...")
if not PurchaseInvoice.objects.exists():
    po = PurchaseOrder.objects.filter(status='confirmed').first()
    if po:
        pinv = PurchaseInvoice.objects.create(
            purchase_order=po,
            supplier=po.supplier,
            status='draft',
            due_date=date.today() + timedelta(days=30),
        )
        for po_item in po.items.all():
            PurchaseInvoiceItem.objects.create(
                purchase_invoice=pinv,
                product=po_item.product,
                quantity=po_item.quantity,
                unit_price=po_item.unit_price,
            )
        print(f"   ✓ Purchase Invoice: {pinv.invoice_number}")
else:
    print("   ✓ Purchase Invoices already exist")


# ==================== INVENTORY TRANSFERS ====================
print("\n[29/35] Creating Inventory Transfers...")
if not InventoryTransfer.objects.exists():
    transfer = InventoryTransfer.objects.create(
        from_warehouse=warehouses['WH-MAIN'],
        to_warehouse=warehouses['WH-SHOW'],
        status='pending',
        transferred_by='Warehouse Manager',
        reference='Monthly Showroom Replenishment',
    )
    InventoryTransferItem.objects.create(inventory_transfer=transfer, product=products['ELEC-001'], quantity=Decimal('5'), unit_price=products['ELEC-001'].purchase_price)
    InventoryTransferItem.objects.create(inventory_transfer=transfer, product=products['ELEC-003'], quantity=Decimal('10'), unit_price=products['ELEC-003'].purchase_price)
    InventoryTransferItem.objects.create(inventory_transfer=transfer, product=products['FURN-001'], quantity=Decimal('3'), unit_price=products['FURN-001'].purchase_price)
    print(f"   ✓ Inventory Transfer: {transfer.transfer_number}")
else:
    print("   ✓ Inventory Transfers already exist")

# ==================== GOODS ISSUES ====================
print("\n[30/35] Creating Goods Issues...")
if not GoodsIssue.objects.exists():
    gi = GoodsIssue.objects.create(
        warehouse=warehouses['WH-MAIN'],
        issue_type='internal',
        status='pending',
        issued_by='Admin',
        issued_to='IT Department',
        reference='Internal IT Setup',
    )
    GoodsIssueItem.objects.create(goods_issue=gi, product=products['ELEC-004'], quantity=Decimal('5'), unit_price=products['ELEC-004'].selling_price)
    GoodsIssueItem.objects.create(goods_issue=gi, product=products['ELEC-005'], quantity=Decimal('5'), unit_price=products['ELEC-005'].selling_price)
    print(f"   ✓ Goods Issue: {gi.issue_number}")
else:
    print("   ✓ Goods Issues already exist")

# ==================== STOCK ADJUSTMENTS ====================
print("\n[31/35] Creating Stock Adjustments...")
if not StockAdjustment.objects.exists():
    adj = StockAdjustment.objects.create(
        warehouse=warehouses['WH-MAIN'],
        adjustment_type='physical_count',
        status='draft',
        reason='Monthly Physical Count',
        requested_by='Warehouse Manager',
    )
    # Get current stock and adjust
    stock1 = ProductWarehouseStock.objects.filter(product=products['OFFC-001'], warehouse=warehouses['WH-MAIN']).first()
    if stock1:
        StockAdjustmentItem.objects.create(
            stock_adjustment=adj,
            product=products['OFFC-001'],
            actual_quantity=stock1.quantity + Decimal('10'),  # Found 10 extra
            unit_cost=products['OFFC-001'].purchase_price,
            reason='Found extra stock during count',
        )
    stock2 = ProductWarehouseStock.objects.filter(product=products['ELEC-004'], warehouse=warehouses['WH-MAIN']).first()
    if stock2:
        StockAdjustmentItem.objects.create(
            stock_adjustment=adj,
            product=products['ELEC-004'],
            actual_quantity=stock2.quantity - Decimal('5'),  # 5 missing
            unit_cost=products['ELEC-004'].purchase_price,
            reason='Damaged items written off',
        )
    print(f"   ✓ Stock Adjustment: {adj.adjustment_number}")
else:
    print("   ✓ Stock Adjustments already exist")

# ==================== PRODUCTION ORDERS ====================
print("\n[32/35] Creating Production Orders...")
if not ProductionOrder.objects.exists():
    bom = BillOfMaterials.objects.filter(status='active').first()
    if bom:
        prod_order = ProductionOrder.objects.create(
            bom=bom,
            product=bom.product,
            warehouse=warehouses['WH-FIN'],
            quantity_to_produce=Decimal('20'),
            status='planned',
            planned_start_date=date.today() + timedelta(days=3),
            planned_end_date=date.today() + timedelta(days=10),
        )
        # Copy BOM components
        for comp in bom.components.all():
            ProductionOrderComponent.objects.create(
                production_order=prod_order,
                product=comp.product,
                quantity_required=comp.quantity * prod_order.quantity_to_produce,
                unit_cost=comp.unit_cost,
            )
        print(f"   ✓ Production Order: {prod_order.order_number}")
else:
    print("   ✓ Production Orders already exist")

# ==================== JOURNAL ENTRIES ====================
print("\n[33/35] Creating Journal Entries...")
if not JournalEntry.objects.exists():
    je = JournalEntry.objects.create(
        status='draft',
        reference='Opening Balance Entry',
    )
    JournalEntryLine.objects.create(journal_entry=je, account=chart_accounts['1000'], description='Cash Opening Balance', debit=Decimal('5000000'))
    JournalEntryLine.objects.create(journal_entry=je, account=chart_accounts['3000'], description='Share Capital', credit=Decimal('5000000'))
    print(f"   ✓ Journal Entry: {je.entry_number}")
else:
    print("   ✓ Journal Entries already exist")

# ==================== BUDGETS ====================
print("\n[34/35] Creating Budgets...")
if not Budget.objects.exists():
    Budget.objects.create(
        budget_name='Sales Revenue Budget FY25-26',
        fiscal_year=fy,
        account=chart_accounts['4000'],
        budget_amount=Decimal('50000000'),
    )
    Budget.objects.create(
        budget_name='Operating Expenses Budget FY25-26',
        fiscal_year=fy,
        account=chart_accounts['6000'],
        budget_amount=Decimal('5000000'),
    )
    print("   ✓ Created 2 budgets")
else:
    print("   ✓ Budgets already exist")

# ==================== INCOMING/OUTGOING PAYMENTS ====================
print("\n[35/35] Creating Sample Payments...")
if not IncomingPayment.objects.exists():
    ip = IncomingPayment.objects.create(
        customer=customers['Tech Solutions Ltd'],
        bank_account=bank_accounts['Main Operating Account'],
        payment_method='bank_transfer',
        status='draft',
        amount=Decimal('100000'),
        reference='Advance Payment',
    )
    print(f"   ✓ Incoming Payment: {ip.payment_number}")

if not OutgoingPayment.objects.exists():
    op = OutgoingPayment.objects.create(
        supplier=suppliers['Dell Bangladesh Ltd'],
        bank_account=bank_accounts['Main Operating Account'],
        payment_method='bank_transfer',
        status='draft',
        amount=Decimal('500000'),
        reference='Advance to Supplier',
    )
    print(f"   ✓ Outgoing Payment: {op.payment_number}")


# ==================== SUMMARY ====================
print("\n" + "=" * 70)
print("✅ IMPORT COMPLETE!")
print("=" * 70)
print(f"""
LOGIN CREDENTIALS:
------------------
Username: olee
Password: 501302aA

SUMMARY:
--------
• Company: {Company.objects.count()}
• Warehouses: {Warehouse.objects.count()}
• Categories: {Category.objects.count()}
• Products: {Product.objects.count()}
• Stock Records: {ProductWarehouseStock.objects.count()}
• Customers: {Customer.objects.count()}
• Suppliers: {Supplier.objects.count()}
• Sales Persons: {SalesPerson.objects.count()}
• Bank Accounts: {BankAccount.objects.count()}
• Currencies: {Currency.objects.count()}
• Tax Types: {TaxType.objects.count()}
• Payment Terms: {PaymentTerm.objects.count()}
• UOMs: {UnitOfMeasure.objects.count()}
• Account Types: {AccountType.objects.count()}
• Chart of Accounts: {ChartOfAccounts.objects.count()}
• Cost Centers: {CostCenter.objects.count()}
• Projects: {Project.objects.count()}
• BOMs: {BillOfMaterials.objects.count()}
• Sales Quotations: {SalesQuotation.objects.count()}
• Sales Orders: {SalesOrder.objects.count()}
• Invoices: {Invoice.objects.count()}
• Deliveries: {Delivery.objects.count()}
• Purchase Quotations: {PurchaseQuotation.objects.count()}
• Purchase Orders: {PurchaseOrder.objects.count()}
• Goods Receipts: {GoodsReceipt.objects.count()}
• Purchase Invoices: {PurchaseInvoice.objects.count()}
• Inventory Transfers: {InventoryTransfer.objects.count()}
• Goods Issues: {GoodsIssue.objects.count()}
• Stock Adjustments: {StockAdjustment.objects.count()}
• Production Orders: {ProductionOrder.objects.count()}
• Journal Entries: {JournalEntry.objects.count()}
• Budgets: {Budget.objects.count()}
• Incoming Payments: {IncomingPayment.objects.count()}
• Outgoing Payments: {OutgoingPayment.objects.count()}

Now run: python3 manage.py runserver
Then go to: http://127.0.0.1:8000/admin/
""")
