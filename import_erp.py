#!/usr/bin/env python3
"""
Standalone script to import ERP demo data
Usage: python3 import_erp.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

from erp.models import (
    Company, Category, Product, Customer, Supplier, SalesPerson, Warehouse,
    SalesQuotation, SalesQuotationItem,
    SalesOrder, SalesOrderItem, Delivery, DeliveryItem,
    Invoice, InvoiceItem, SalesReturn, SalesReturnItem,
    PurchaseQuotation, PurchaseQuotationItem,
    PurchaseOrder, PurchaseOrderItem, PurchaseReturn, PurchaseReturnItem,
    GoodsReceipt, GoodsReceiptItem, GoodsIssue, GoodsIssueItem,
    BillOfMaterials, BOMComponent,
    ProductionOrder, ProductionOrderComponent,
    ProductionReceipt, ProductionReceiptComponent,
    InventoryTransfer, InventoryTransferItem,
    ProductWarehouseStock, StockTransaction
)


def create_superuser():
    """Create or get superuser"""
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print('✓ Created superuser: admin / admin123')
    else:
        print('⚠ Superuser already exists')
    return user


def create_company():
    """Create company info"""
    company, created = Company.objects.get_or_create(
        name='Tech Solutions Ltd',
        defaults={
            'address': '123 Business Street, Gulshan-2',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'phone': '+880-1711-123456',
            'email': 'info@techsolutions.com',
            'website': 'https://techsolutions.com',
            'tax_number': 'TAX-123456789',
        }
    )
    if created:
        print('✓ Created company: Tech Solutions Ltd')
    else:
        print('⚠ Company already exists')
    return company


def create_warehouses():
    """Create demo warehouses"""
    warehouses_data = [
        {
            'name': 'Main Warehouse',
            'code': 'WH-001',
            'address': 'Plot 123, Tejgaon Industrial Area',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'phone': '+880-1700-111111',
            'manager': 'Kamal Hossain',
        },
        {
            'name': 'Branch Warehouse',
            'code': 'WH-002',
            'address': 'Sector 7, Uttara',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'phone': '+880-1700-222222',
            'manager': 'Rina Begum',
        },
        {
            'name': 'Chittagong Warehouse',
            'code': 'WH-003',
            'address': 'EPZ Area, Chittagong',
            'city': 'Chittagong',
            'country': 'Bangladesh',
            'phone': '+880-1700-333333',
            'manager': 'Jamal Ahmed',
        },
    ]
    
    warehouses = []
    for data in warehouses_data:
        warehouse, created = Warehouse.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        warehouses.append(warehouse)
    
    print(f'✓ Created {len(warehouses)} warehouses')
    return warehouses


def create_categories():
    """Create product categories"""
    categories_data = [
        {'name': 'Computers & Laptops', 'description': 'Desktop computers and laptops'},
        {'name': 'Computer Accessories', 'description': 'Mouse, keyboard, webcam, etc.'},
        {'name': 'Storage Devices', 'description': 'Hard drives, flash drives, SSDs'},
        {'name': 'Printers & Scanners', 'description': 'Printing and scanning equipment'},
        {'name': 'Monitors & Displays', 'description': 'Computer monitors and displays'},
    ]
    
    categories = []
    for data in categories_data:
        category, created = Category.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        categories.append(category)
    
    print(f'✓ Created {len(categories)} categories')
    return categories


def create_customers():
    """Create demo customers"""
    customers_data = [
        {
            'name': 'ABC Corporation',
            'phone': '+880-1711-123456',
            'email': 'contact@abccorp.com',
            'address': '123 Main Street, Gulshan',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'credit_limit': Decimal('100000.00'),
        },
        {
            'name': 'XYZ Enterprises',
            'phone': '+880-1712-234567',
            'email': 'info@xyzent.com',
            'address': '456 Park Avenue, Banani',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'credit_limit': Decimal('150000.00'),
        },
        {
            'name': 'Tech Solutions Ltd',
            'phone': '+880-1713-345678',
            'email': 'sales@techsol.com',
            'address': '789 Tech Park, Bashundhara',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'credit_limit': Decimal('200000.00'),
        },
        {
            'name': 'Global Trading Co',
            'phone': '+880-1714-456789',
            'email': 'orders@globaltrading.com',
            'address': '321 Business District, Motijheel',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'credit_limit': Decimal('80000.00'),
        },
        {
            'name': 'Retail Mart',
            'phone': '+880-1715-567890',
            'email': 'purchase@retailmart.com',
            'address': '654 Shopping Complex, Dhanmondi',
            'city': 'Dhaka',
            'country': 'Bangladesh',
            'credit_limit': Decimal('120000.00'),
        },
    ]
    
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        customers.append(customer)
    
    print(f'✓ Created {len(customers)} customers')
    return customers


def create_suppliers():
    """Create demo suppliers"""
    suppliers_data = [
        {
            'name': 'Tech Wholesale Ltd',
            'phone': '+880-1731-111111',
            'email': 'sales@techwholesale.com',
            'address': 'Tejgaon Industrial Area',
            'city': 'Dhaka',
            'country': 'Bangladesh',
        },
        {
            'name': 'Computer Parts BD',
            'phone': '+880-1732-222222',
            'email': 'info@computerparts.com',
            'address': 'Elephant Road',
            'city': 'Dhaka',
            'country': 'Bangladesh',
        },
        {
            'name': 'Electronics Supplier',
            'phone': '+880-1733-333333',
            'email': 'contact@electronicsupplier.com',
            'address': 'Bangla Motor',
            'city': 'Dhaka',
            'country': 'Bangladesh',
        },
    ]
    
    suppliers = []
    for data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        suppliers.append(supplier)
    
    print(f'✓ Created {len(suppliers)} suppliers')
    return suppliers


def create_sales_persons():
    """Create demo sales persons"""
    sales_persons_data = [
        {
            'name': 'Karim Ahmed',
            'phone': '+880-1721-111111',
            'email': 'karim@company.com',
            'employee_id': 'EMP001',
            'commission_rate': Decimal('2.50'),
        },
        {
            'name': 'Fatima Rahman',
            'phone': '+880-1722-222222',
            'email': 'fatima@company.com',
            'employee_id': 'EMP002',
            'commission_rate': Decimal('3.00'),
        },
        {
            'name': 'Rahim Hossain',
            'phone': '+880-1723-333333',
            'email': 'rahim@company.com',
            'employee_id': 'EMP003',
            'commission_rate': Decimal('2.00'),
        },
    ]
    
    sales_persons = []
    for data in sales_persons_data:
        sales_person, created = SalesPerson.objects.get_or_create(
            employee_id=data['employee_id'],
            defaults=data
        )
        sales_persons.append(sales_person)
    
    print(f'✓ Created {len(sales_persons)} sales persons')
    return sales_persons


def create_products(categories, warehouses):
    """Create demo products"""
    products_data = [
        {
            'name': 'Laptop Dell Inspiron 15',
            'sku': 'DELL-INS-15',
            'category': categories[0],
            'description': 'Intel Core i5, 8GB RAM, 512GB SSD',
            'purchase_price': Decimal('45000.00'),
            'selling_price': Decimal('55000.00'),
            'current_stock': Decimal('15.00'),
            'min_stock_level': Decimal('5.00'),
            'unit': 'PCS',
        },
        {
            'name': 'HP Laser Printer',
            'sku': 'HP-LASER-01',
            'category': categories[3],
            'description': 'Monochrome laser printer with WiFi',
            'purchase_price': Decimal('12000.00'),
            'selling_price': Decimal('15000.00'),
            'current_stock': Decimal('8.00'),
            'min_stock_level': Decimal('3.00'),
            'unit': 'PCS',
        },
        {
            'name': 'Wireless Mouse Logitech',
            'sku': 'LOG-MOUSE-01',
            'category': categories[1],
            'description': 'Ergonomic wireless mouse',
            'purchase_price': Decimal('800.00'),
            'selling_price': Decimal('1200.00'),
            'current_stock': Decimal('50.00'),
            'min_stock_level': Decimal('20.00'),
            'unit': 'PCS',
        },
        {
            'name': 'Mechanical Keyboard',
            'sku': 'MECH-KB-01',
            'category': categories[1],
            'description': 'RGB backlit mechanical keyboard',
            'purchase_price': Decimal('2500.00'),
            'selling_price': Decimal('3500.00'),
            'current_stock': Decimal('25.00'),
            'min_stock_level': Decimal('10.00'),
            'unit': 'PCS',
        },
        {
            'name': 'USB Flash Drive 64GB',
            'sku': 'USB-64GB',
            'category': categories[2],
            'description': 'High-speed USB 3.0 flash drive',
            'purchase_price': Decimal('400.00'),
            'selling_price': Decimal('600.00'),
            'current_stock': Decimal('100.00'),
            'min_stock_level': Decimal('50.00'),
            'unit': 'PCS',
        },
        {
            'name': 'External Hard Drive 1TB',
            'sku': 'HDD-EXT-1TB',
            'category': categories[2],
            'description': 'Portable external HDD',
            'purchase_price': Decimal('3500.00'),
            'selling_price': Decimal('4500.00'),
            'current_stock': Decimal('20.00'),
            'min_stock_level': Decimal('8.00'),
            'unit': 'PCS',
        },
        {
            'name': 'Webcam HD 1080p',
            'sku': 'WEBCAM-HD',
            'category': categories[1],
            'description': 'Full HD webcam with microphone',
            'purchase_price': Decimal('2000.00'),
            'selling_price': Decimal('2800.00'),
            'current_stock': Decimal('30.00'),
            'min_stock_level': Decimal('15.00'),
            'unit': 'PCS',
        },
        {
            'name': 'Monitor 24 inch LED',
            'sku': 'MON-24-LED',
            'category': categories[4],
            'description': 'Full HD LED monitor',
            'purchase_price': Decimal('9000.00'),
            'selling_price': Decimal('12000.00'),
            'current_stock': Decimal('12.00'),
            'min_stock_level': Decimal('5.00'),
            'unit': 'PCS',
        },
    ]
    
    products = []
    for data in products_data:
        # Set default warehouse to first warehouse
        data['default_warehouse'] = warehouses[0]
        product, created = Product.objects.get_or_create(
            sku=data['sku'],
            defaults=data
        )
        products.append(product)
        
        # Create initial warehouse stock for main warehouse
        if created:
            ProductWarehouseStock.objects.create(
                product=product,
                warehouse=warehouses[0],
                quantity=data['current_stock']
            )
    
    print(f'✓ Created {len(products)} products')
    return products


def create_sales_quotations(customers, sales_persons, products):
    """Create demo sales quotations"""
    quotations = []
    
    for i in range(5):
        customer = random.choice(customers)
        sales_person = random.choice(sales_persons) if random.random() > 0.3 else None
        
        sq = SalesQuotation.objects.create(
            quotation_date=timezone.now().date() - timedelta(days=random.randint(5, 30)),
            valid_until=timezone.now().date() + timedelta(days=random.randint(15, 45)),
            customer=customer,
            salesperson=sales_person,
            status=random.choice(['draft', 'sent', 'accepted']),
            payment_terms='Net 30',
            discount_amount=Decimal(str(random.randint(0, 500))),
            tax_rate=Decimal('5.00'),
        )
        
        # Add 2-4 items
        num_items = random.randint(2, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            SalesQuotationItem.objects.create(
                sales_quotation=sq,
                product=product,
                quantity=Decimal(str(random.randint(1, 10))),
                unit_price=product.selling_price,
            )
        
        sq.calculate_totals()
        quotations.append(sq)
    
    print(f'✓ Created {len(quotations)} sales quotations')
    return quotations


def create_purchase_quotations(suppliers, products):
    """Create demo purchase quotations"""
    quotations = []
    
    for i in range(3):
        supplier = suppliers[i % len(suppliers)]
        
        pq = PurchaseQuotation.objects.create(
            quotation_date=timezone.now().date() - timedelta(days=random.randint(10, 40)),
            valid_until=timezone.now().date() + timedelta(days=random.randint(20, 60)),
            supplier=supplier,
            status=random.choice(['draft', 'sent', 'received', 'accepted']),
            discount_amount=Decimal('300.00'),
            tax_amount=Decimal('500.00'),
        )
        
        # Add 2-3 items
        num_items = random.randint(2, 3)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            PurchaseQuotationItem.objects.create(
                purchase_quotation=pq,
                product=product,
                quantity=Decimal(str(random.randint(10, 30))),
                unit_price=product.purchase_price,
            )
        
        pq.calculate_totals()
        quotations.append(pq)
    
    print(f'✓ Created {len(quotations)} purchase quotations')
    return quotations


def create_purchase_orders(suppliers, products):
    """Create demo purchase orders"""
    purchase_orders = []
    
    for i in range(5):
        supplier = suppliers[i % len(suppliers)]
        
        po = PurchaseOrder.objects.create(
            order_date=timezone.now().date() - timedelta(days=random.randint(30, 90)),
            expected_date=timezone.now().date() - timedelta(days=random.randint(1, 20)),
            supplier=supplier,
            status='completed',
            discount_amount=Decimal('500.00'),
            tax_amount=Decimal('1000.00'),
        )
        
        # Add 2-4 items to each purchase order
        num_items = random.randint(2, 4)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                product=product,
                quantity=Decimal(str(random.randint(10, 50))),
                unit_price=product.purchase_price,
            )
        
        po.calculate_totals()
        purchase_orders.append(po)
    
    print(f'✓ Created {len(purchase_orders)} purchase orders')
    return purchase_orders


def create_sales_orders(customers, sales_persons, products):
    """Create demo sales orders"""
    sales_orders = []
    
    for i in range(10):
        customer = random.choice(customers)
        sales_person = random.choice(sales_persons) if random.random() > 0.3 else None
        
        so = SalesOrder.objects.create(
            order_date=timezone.now().date() - timedelta(days=random.randint(1, 60)),
            customer=customer,
            salesperson=sales_person,
            status=random.choice(['draft', 'confirmed', 'processing', 'completed']),
            delivery_date=timezone.now().date() + timedelta(days=random.randint(1, 14)),
            payment_terms='Net 30',
            discount_amount=Decimal(str(random.randint(0, 1000))),
            tax_rate=Decimal('5.00'),
            tax_amount=Decimal('0.00'),  # Will be calculated
        )
        
        # Add 1-5 items to each sales order
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            SalesOrderItem.objects.create(
                sales_order=so,
                product=product,
                quantity=Decimal(str(random.randint(1, 10))),
                unit_price=product.selling_price,
            )
        
        so.calculate_totals()
        sales_orders.append(so)
    
    print(f'✓ Created {len(sales_orders)} sales orders')
    return sales_orders


def create_deliveries(sales_orders):
    """Create demo deliveries from sales orders"""
    deliveries = []
    
    # Create deliveries for first 5 sales orders
    for so in sales_orders[:5]:
        delivery = Delivery.objects.create(
            delivery_date=so.order_date + timedelta(days=random.randint(1, 7)),
            sales_order=so,
            customer=so.customer,
            salesperson=so.salesperson,
            status=random.choice(['pending', 'in_transit', 'delivered']),
            delivery_address=so.customer.address,
        )
        
        # Deliver partial or full quantities
        for so_item in so.items.all():
            deliver_qty = so_item.quantity * Decimal(str(random.uniform(0.5, 1.0)))
            DeliveryItem.objects.create(
                delivery=delivery,
                product=so_item.product,
                quantity=deliver_qty,
                unit_price=so_item.unit_price,
            )
        
        deliveries.append(delivery)
    
    print(f'✓ Created {len(deliveries)} deliveries')
    return deliveries


def create_invoices(sales_orders):
    """Create demo invoices from sales orders"""
    invoices = []
    
    # Create invoices for first 6 sales orders
    for so in sales_orders[:6]:
        invoice = Invoice.objects.create(
            invoice_date=so.order_date + timedelta(days=random.randint(1, 5)),
            due_date=so.order_date + timedelta(days=30),
            sales_order=so,
            customer=so.customer,
            salesperson=so.salesperson,
            status=random.choice(['draft', 'sent', 'paid', 'partially_paid']),
            discount_amount=so.discount_amount,
            tax_amount=so.tax_amount,
            paid_amount=Decimal('0.00'),
        )
        
        # Invoice partial or full quantities
        for so_item in so.items.all():
            invoice_qty = so_item.quantity * Decimal(str(random.uniform(0.5, 1.0)))
            InvoiceItem.objects.create(
                invoice=invoice,
                product=so_item.product,
                quantity=invoice_qty,
                unit_price=so_item.unit_price,
            )
        
        invoice.calculate_totals()
        # Set paid amount
        invoice.paid_amount = invoice.total_amount * Decimal(str(random.uniform(0, 1)))
        invoice.save()
        
        invoices.append(invoice)
    
    print(f'✓ Created {len(invoices)} invoices')
    return invoices


def create_sales_returns(sales_orders):
    """Create demo sales returns"""
    returns = []
    
    # Create returns for 2 sales orders
    for so in sales_orders[:2]:
        sales_return = SalesReturn.objects.create(
            return_date=so.order_date + timedelta(days=random.randint(10, 20)),
            sales_order=so,
            customer=so.customer,
            salesperson=so.salesperson,
            status='pending',
            reason='Defective product',
        )
        
        # Return small quantities
        for so_item in so.items.all()[:2]:  # Only first 2 items
            return_qty = Decimal(str(random.randint(1, 3)))
            SalesReturnItem.objects.create(
                sales_return=sales_return,
                product=so_item.product,
                quantity=return_qty,
                unit_price=so_item.unit_price,
            )
        
        sales_return.calculate_totals()
        returns.append(sales_return)
    
    print(f'✓ Created {len(returns)} sales returns')
    return returns


def create_purchase_returns(purchase_orders):
    """Create demo purchase returns"""
    returns = []
    
    # Create returns for 1 purchase order
    for po in purchase_orders[:1]:
        purchase_return = PurchaseReturn.objects.create(
            return_date=po.order_date + timedelta(days=random.randint(5, 15)),
            purchase_order=po,
            supplier=po.supplier,
            status='pending',
            reason='Wrong items received',
        )
        
        # Return small quantities
        for po_item in po.items.all()[:2]:
            return_qty = Decimal(str(random.randint(1, 5)))
            PurchaseReturnItem.objects.create(
                purchase_return=purchase_return,
                product=po_item.product,
                quantity=return_qty,
                unit_price=po_item.unit_price,
            )
        
        purchase_return.calculate_totals()
        returns.append(purchase_return)
    
    print(f'✓ Created {len(returns)} purchase returns')
    return returns


def create_goods_receipts(purchase_orders, warehouses):
    """Create demo goods receipts"""
    receipts = []
    
    # Create receipts for first 3 purchase orders
    for po in purchase_orders[:3]:
        receipt = GoodsReceipt.objects.create(
            receipt_date=po.order_date + timedelta(days=random.randint(3, 10)),
            receipt_type='purchase',
            purchase_order=po,
            supplier=po.supplier,
            status=random.choice(['received', 'inspected', 'completed']),
            received_by='Warehouse Staff',
            warehouse_location=warehouses[0].name,
        )
        
        # Receive partial or full quantities
        for po_item in po.items.all():
            receive_qty = po_item.quantity * Decimal(str(random.uniform(0.7, 1.0)))
            GoodsReceiptItem.objects.create(
                goods_receipt=receipt,
                product=po_item.product,
                quantity=receive_qty,
                unit_price=po_item.unit_price,
            )
        
        receipts.append(receipt)
    
    print(f'✓ Created {len(receipts)} goods receipts')
    return receipts


def create_goods_issues(sales_orders, warehouses):
    """Create demo goods issues"""
    issues = []
    
    # Create issues for first 3 sales orders
    for so in sales_orders[:3]:
        issue = GoodsIssue.objects.create(
            issue_date=so.order_date + timedelta(days=random.randint(1, 5)),
            issue_type='sales',
            sales_order=so,
            customer=so.customer,
            status=random.choice(['issued', 'completed']),
            issued_by='Warehouse Staff',
            warehouse_location=warehouses[0].name,
        )
        
        # Issue partial or full quantities
        for so_item in so.items.all():
            issue_qty = so_item.quantity * Decimal(str(random.uniform(0.6, 1.0)))
            GoodsIssueItem.objects.create(
                goods_issue=issue,
                product=so_item.product,
                quantity=issue_qty,
                unit_price=so_item.unit_price,
            )
        
        issues.append(issue)
    
    print(f'✓ Created {len(issues)} goods issues')
    return issues


def create_inventory_transfers(products, warehouses):
    """Create demo inventory transfers"""
    transfers = []
    
    # Create 2 transfers between warehouses
    for i in range(2):
        transfer = InventoryTransfer.objects.create(
            transfer_date=timezone.now().date() - timedelta(days=random.randint(5, 20)),
            from_warehouse=warehouses[0],
            to_warehouse=warehouses[1],
            status=random.choice(['pending', 'in_transit', 'completed']),
            transferred_by='Transfer Staff',
            received_by='Branch Staff' if i == 0 else '',
        )
        
        # Transfer 2-3 products
        num_items = random.randint(2, 3)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            transfer_qty = Decimal(str(random.randint(5, 15)))
            InventoryTransferItem.objects.create(
                inventory_transfer=transfer,
                product=product,
                quantity=transfer_qty,
                unit_price=product.purchase_price,
            )
        
        transfers.append(transfer)
    
    print(f'✓ Created {len(transfers)} inventory transfers')
    return transfers


def create_bills_of_materials(products):
    """Create demo bills of materials"""
    boms = []
    
    # Create 3 BOMs for finished products
    # BOM 1: Custom Laptop Assembly
    bom1 = BillOfMaterials.objects.create(
        name='Custom Laptop Assembly',
        product=products[0],  # Laptop Dell Inspiron 15
        version='1.0',
        quantity=Decimal('1.00'),
        status='active',
        labor_cost=Decimal('5000.00'),
        overhead_cost=Decimal('2000.00'),
    )
    
    # Components for laptop (using other products as components)
    BOMComponent.objects.create(
        bom=bom1,
        product=products[2],  # Mouse
        quantity=Decimal('1.00'),
        scrap_percentage=Decimal('2.00'),
    )
    BOMComponent.objects.create(
        bom=bom1,
        product=products[3],  # Keyboard
        quantity=Decimal('1.00'),
        scrap_percentage=Decimal('2.00'),
    )
    BOMComponent.objects.create(
        bom=bom1,
        product=products[6],  # Webcam
        quantity=Decimal('1.00'),
        scrap_percentage=Decimal('1.00'),
    )
    
    bom1.calculate_costs()
    boms.append(bom1)
    
    # BOM 2: Computer Workstation Package
    bom2 = BillOfMaterials.objects.create(
        name='Computer Workstation Package',
        product=products[7],  # Monitor
        version='1.0',
        quantity=Decimal('1.00'),
        status='active',
        labor_cost=Decimal('1500.00'),
        overhead_cost=Decimal('500.00'),
    )
    
    BOMComponent.objects.create(
        bom=bom2,
        product=products[2],  # Mouse
        quantity=Decimal('1.00'),
        scrap_percentage=Decimal('1.00'),
    )
    BOMComponent.objects.create(
        bom=bom2,
        product=products[3],  # Keyboard
        quantity=Decimal('1.00'),
        scrap_percentage=Decimal('1.00'),
    )
    
    bom2.calculate_costs()
    boms.append(bom2)
    
    print(f'✓ Created {len(boms)} bills of materials')
    return boms


def create_production_orders(boms, warehouses, sales_orders):
    """Create demo production orders"""
    orders = []
    
    # Create 3 production orders
    for i, bom in enumerate(boms):
        po = ProductionOrder.objects.create(
            order_date=timezone.now().date() - timedelta(days=random.randint(10, 30)),
            planned_start_date=timezone.now().date() - timedelta(days=random.randint(5, 15)),
            planned_end_date=timezone.now().date() + timedelta(days=random.randint(1, 10)),
            bom=bom,
            warehouse=warehouses[0],
            quantity_to_produce=Decimal(str(random.randint(5, 15))),
            status=random.choice(['planned', 'in_progress', 'completed']),
            sales_order=sales_orders[i] if i < len(sales_orders) else None,
        )
        
        # Create components from BOM
        for bom_comp in bom.components.all():
            ProductionOrderComponent.objects.create(
                production_order=po,
                product=bom_comp.product,
                quantity_required=bom_comp.quantity * po.quantity_to_produce,
                quantity_consumed=Decimal('0.00'),
            )
        
        orders.append(po)
    
    print(f'✓ Created {len(orders)} production orders')
    return orders


def create_production_receipts(production_orders):
    """Create demo production receipts"""
    receipts = []
    
    # Create receipts for completed production orders
    for po in production_orders:
        if po.status in ['in_progress', 'completed']:
            # Produce 70-100% of planned quantity
            qty_received = po.quantity_to_produce * Decimal(str(random.uniform(0.7, 1.0)))
            qty_rejected = qty_received * Decimal(str(random.uniform(0, 0.05)))  # 0-5% rejection
            
            receipt = ProductionReceipt.objects.create(
                receipt_date=po.planned_start_date + timedelta(days=random.randint(3, 7)),
                production_order=po,
                quantity_received=qty_received,
                quantity_rejected=qty_rejected,
                status=random.choice(['received', 'inspected', 'completed']),
                received_by='Production Staff',
                inspected_by='QC Inspector',
            )
            
            # Record material consumption
            for po_comp in po.components.all():
                consumed_qty = po_comp.quantity_required * Decimal(str(random.uniform(0.9, 1.1)))
                ProductionReceiptComponent.objects.create(
                    production_receipt=receipt,
                    product=po_comp.product,
                    quantity_consumed=consumed_qty,
                )
                
                # Update production order component
                po_comp.quantity_consumed = consumed_qty
                po_comp.save()
            
            # Update production order quantity produced
            po.quantity_produced = receipt.quantity_accepted
            if po.quantity_produced >= po.quantity_to_produce:
                po.status = 'completed'
                po.actual_end_date = receipt.receipt_date
            po.save()
            
            receipts.append(receipt)
    
    print(f'✓ Created {len(receipts)} production receipts')
    return receipts


def main():
    """Main import function"""
    print('🚀 Starting ERP demo data import...\n')
    
    try:
        # Create data
        user = create_superuser()
        company = create_company()
        warehouses = create_warehouses()
        categories = create_categories()
        customers = create_customers()
        suppliers = create_suppliers()
        sales_persons = create_sales_persons()
        products = create_products(categories, warehouses)
        
        # Quotations
        sales_quotations = create_sales_quotations(customers, sales_persons, products)
        purchase_quotations = create_purchase_quotations(suppliers, products)
        
        # Orders
        purchase_orders = create_purchase_orders(suppliers, products)
        sales_orders = create_sales_orders(customers, sales_persons, products)
        
        # Deliveries and Invoices
        deliveries = create_deliveries(sales_orders)
        invoices = create_invoices(sales_orders)
        
        # Returns
        sales_returns = create_sales_returns(sales_orders)
        purchase_returns = create_purchase_returns(purchase_orders)
        
        # Inventory Operations
        goods_receipts = create_goods_receipts(purchase_orders, warehouses)
        goods_issues = create_goods_issues(sales_orders, warehouses)
        inventory_transfers = create_inventory_transfers(products, warehouses)
        
        # Production Operations
        boms = create_bills_of_materials(products)
        production_orders = create_production_orders(boms, warehouses, sales_orders)
        production_receipts = create_production_receipts(production_orders)
        
        print('\n🎉 Demo data import completed successfully!')
        print('\n' + '='*60)
        print('LOGIN CREDENTIALS:')
        print('='*60)
        print('Username: admin')
        print('Password: admin123')
        print('='*60)
        print('\nRun: python3 manage.py runserver')
        print('Then go to: http://127.0.0.1:8000/admin/')
        print('='*60)
        print('\nDemo Data Summary:')
        print(f'  - {len(warehouses)} Warehouses')
        print(f'  - {len(categories)} Categories')
        print(f'  - {len(products)} Products')
        print(f'  - {len(customers)} Customers')
        print(f'  - {len(suppliers)} Suppliers')
        print(f'  - {len(sales_persons)} Sales Persons')
        print(f'  - {len(sales_quotations)} Sales Quotations')
        print(f'  - {len(purchase_quotations)} Purchase Quotations')
        print(f'  - {len(purchase_orders)} Purchase Orders')
        print(f'  - {len(sales_orders)} Sales Orders')
        print(f'  - {len(deliveries)} Deliveries')
        print(f'  - {len(invoices)} Invoices')
        print(f'  - {len(sales_returns)} Sales Returns')
        print(f'  - {len(purchase_returns)} Purchase Returns')
        print(f'  - {len(goods_receipts)} Goods Receipts')
        print(f'  - {len(goods_issues)} Goods Issues')
        print(f'  - {len(inventory_transfers)} Inventory Transfers')
        print(f'  - {len(boms)} Bills of Materials')
        print(f'  - {len(production_orders)} Production Orders')
        print(f'  - {len(production_receipts)} Production Receipts')
        print('='*60)
        
    except Exception as e:
        print(f'\n❌ Error during import: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
