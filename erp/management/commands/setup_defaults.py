"""
Management command to setup default data for MUST HAVE modules
"""
from django.core.management.base import BaseCommand
from erp.models import (
    Currency, PaymentTerm, UnitOfMeasure, UOMConversion,
    TaxType, TaxRate, PriceList,
    DiscountType, NotificationType, ApprovalWorkflow, ApprovalLevel
)
from decimal import Decimal


class Command(BaseCommand):
    help = 'Setup default data for Currency, Tax, Payment Terms, UOM, and Price Lists'

    def handle(self, *args, **options):
        self.setup_currencies()
        self.setup_payment_terms()
        self.setup_uom()
        self.setup_tax()
        self.setup_price_lists()
        self.setup_discounts()
        self.setup_notifications()
        self.setup_approval_workflows()
        self.stdout.write(self.style.SUCCESS('✅ Default data setup completed!'))

    def setup_currencies(self):
        """Setup common currencies"""
        currencies = [
            {'code': 'USD', 'name': 'US Dollar', 'symbol': '$', 'is_base_currency': True},
            {'code': 'BDT', 'name': 'Bangladeshi Taka', 'symbol': '৳', 'is_base_currency': False},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€', 'is_base_currency': False},
            {'code': 'GBP', 'name': 'British Pound', 'symbol': '£', 'is_base_currency': False},
            {'code': 'INR', 'name': 'Indian Rupee', 'symbol': '₹', 'is_base_currency': False},
            {'code': 'SAR', 'name': 'Saudi Riyal', 'symbol': 'ر.س', 'is_base_currency': False},
            {'code': 'AED', 'name': 'UAE Dirham', 'symbol': 'د.إ', 'is_base_currency': False},
        ]
        for curr in currencies:
            Currency.objects.get_or_create(code=curr['code'], defaults=curr)
        self.stdout.write(f'  → Created {len(currencies)} currencies')

    def setup_payment_terms(self):
        """Setup common payment terms"""
        terms = [
            {'code': 'COD', 'name': 'Cash on Delivery', 'days': 0, 'is_default': True},
            {'code': 'NET7', 'name': 'Net 7 Days', 'days': 7},
            {'code': 'NET15', 'name': 'Net 15 Days', 'days': 15},
            {'code': 'NET30', 'name': 'Net 30 Days', 'days': 30},
            {'code': 'NET45', 'name': 'Net 45 Days', 'days': 45},
            {'code': 'NET60', 'name': 'Net 60 Days', 'days': 60},
            {'code': 'NET90', 'name': 'Net 90 Days', 'days': 90},
            {'code': '2/10NET30', 'name': '2% 10 Net 30', 'days': 30, 'discount_days': 10, 'discount_percentage': Decimal('2.00')},
        ]
        for term in terms:
            PaymentTerm.objects.get_or_create(code=term['code'], defaults=term)
        self.stdout.write(f'  → Created {len(terms)} payment terms')

    def setup_uom(self):
        """Setup common units of measure"""
        uoms = [
            # Unit type
            {'code': 'PCS', 'name': 'Pieces', 'uom_type': 'unit', 'is_base_unit': True},
            {'code': 'EA', 'name': 'Each', 'uom_type': 'unit'},
            {'code': 'SET', 'name': 'Set', 'uom_type': 'unit'},
            {'code': 'PAIR', 'name': 'Pair', 'uom_type': 'unit'},
            {'code': 'DOZ', 'name': 'Dozen', 'uom_type': 'unit'},
            {'code': 'BOX', 'name': 'Box', 'uom_type': 'unit'},
            {'code': 'CTN', 'name': 'Carton', 'uom_type': 'unit'},
            {'code': 'PKT', 'name': 'Packet', 'uom_type': 'unit'},
            # Weight type
            {'code': 'KG', 'name': 'Kilogram', 'uom_type': 'weight', 'is_base_unit': True},
            {'code': 'G', 'name': 'Gram', 'uom_type': 'weight'},
            {'code': 'MG', 'name': 'Milligram', 'uom_type': 'weight'},
            {'code': 'LB', 'name': 'Pound', 'uom_type': 'weight'},
            {'code': 'OZ', 'name': 'Ounce', 'uom_type': 'weight'},
            {'code': 'TON', 'name': 'Metric Ton', 'uom_type': 'weight'},
            # Volume type
            {'code': 'LTR', 'name': 'Liter', 'uom_type': 'volume', 'is_base_unit': True},
            {'code': 'ML', 'name': 'Milliliter', 'uom_type': 'volume'},
            {'code': 'GAL', 'name': 'Gallon', 'uom_type': 'volume'},
            # Length type
            {'code': 'M', 'name': 'Meter', 'uom_type': 'length', 'is_base_unit': True},
            {'code': 'CM', 'name': 'Centimeter', 'uom_type': 'length'},
            {'code': 'MM', 'name': 'Millimeter', 'uom_type': 'length'},
            {'code': 'FT', 'name': 'Feet', 'uom_type': 'length'},
            {'code': 'IN', 'name': 'Inch', 'uom_type': 'length'},
            {'code': 'YD', 'name': 'Yard', 'uom_type': 'length'},
            # Area type
            {'code': 'SQM', 'name': 'Square Meter', 'uom_type': 'area', 'is_base_unit': True},
            {'code': 'SQFT', 'name': 'Square Feet', 'uom_type': 'area'},
        ]
        for uom in uoms:
            UnitOfMeasure.objects.get_or_create(code=uom['code'], defaults=uom)
        self.stdout.write(f'  → Created {len(uoms)} units of measure')
        
        # Setup conversions
        conversions = [
            ('DOZ', 'PCS', Decimal('12')),
            ('G', 'KG', Decimal('0.001')),
            ('MG', 'G', Decimal('0.001')),
            ('KG', 'G', Decimal('1000')),
            ('TON', 'KG', Decimal('1000')),
            ('LB', 'KG', Decimal('0.453592')),
            ('OZ', 'LB', Decimal('0.0625')),
            ('ML', 'LTR', Decimal('0.001')),
            ('LTR', 'ML', Decimal('1000')),
            ('GAL', 'LTR', Decimal('3.78541')),
            ('CM', 'M', Decimal('0.01')),
            ('MM', 'CM', Decimal('0.1')),
            ('M', 'CM', Decimal('100')),
            ('FT', 'M', Decimal('0.3048')),
            ('IN', 'FT', Decimal('0.0833333')),
            ('YD', 'M', Decimal('0.9144')),
            ('SQFT', 'SQM', Decimal('0.092903')),
        ]
        for from_code, to_code, factor in conversions:
            try:
                from_uom = UnitOfMeasure.objects.get(code=from_code)
                to_uom = UnitOfMeasure.objects.get(code=to_code)
                UOMConversion.objects.get_or_create(
                    from_uom=from_uom, to_uom=to_uom,
                    defaults={'conversion_factor': factor}
                )
            except UnitOfMeasure.DoesNotExist:
                pass
        self.stdout.write(f'  → Created {len(conversions)} UOM conversions')

    def setup_tax(self):
        """Setup common tax types and rates"""
        tax_types = [
            {'code': 'VAT', 'name': 'Value Added Tax', 'category': 'both'},
            {'code': 'GST', 'name': 'Goods and Services Tax', 'category': 'both'},
            {'code': 'ST', 'name': 'Sales Tax', 'category': 'sales'},
            {'code': 'PT', 'name': 'Purchase Tax', 'category': 'purchase'},
            {'code': 'WHT', 'name': 'Withholding Tax', 'category': 'both'},
        ]
        for tt in tax_types:
            TaxType.objects.get_or_create(code=tt['code'], defaults=tt)
        self.stdout.write(f'  → Created {len(tax_types)} tax types')
        
        # Setup tax rates
        try:
            vat = TaxType.objects.get(code='VAT')
            rates = [
                {'tax_type': vat, 'name': 'Standard Rate', 'rate': Decimal('15.00'), 'is_default': True},
                {'tax_type': vat, 'name': 'Reduced Rate', 'rate': Decimal('7.50')},
                {'tax_type': vat, 'name': 'Zero Rate', 'rate': Decimal('0.00')},
                {'tax_type': vat, 'name': 'Exempt', 'rate': Decimal('0.00')},
            ]
            for rate in rates:
                TaxRate.objects.get_or_create(
                    tax_type=rate['tax_type'], name=rate['name'],
                    defaults=rate
                )
            self.stdout.write(f'  → Created {len(rates)} tax rates for VAT')
        except TaxType.DoesNotExist:
            pass

    def setup_price_lists(self):
        """Setup default price lists"""
        price_lists = [
            {'code': 'RETAIL', 'name': 'Retail Price List', 'price_type': 'sales', 'is_default': True},
            {'code': 'WHOLESALE', 'name': 'Wholesale Price List', 'price_type': 'sales'},
            {'code': 'VIP', 'name': 'VIP Customer Price List', 'price_type': 'sales'},
            {'code': 'PURCHASE', 'name': 'Standard Purchase Price', 'price_type': 'purchase', 'is_default': True},
        ]
        for pl in price_lists:
            PriceList.objects.get_or_create(code=pl['code'], defaults=pl)
        self.stdout.write(f'  → Created {len(price_lists)} price lists')


    def setup_discounts(self):
        """Setup common discount types"""
        discounts = [
            {'code': 'BULK10', 'name': 'Bulk Order 10%', 'discount_method': 'percentage', 'apply_on': 'order', 'value': Decimal('10.00'), 'min_order_amount': Decimal('10000.00')},
            {'code': 'BULK15', 'name': 'Bulk Order 15%', 'discount_method': 'percentage', 'apply_on': 'order', 'value': Decimal('15.00'), 'min_order_amount': Decimal('25000.00')},
            {'code': 'VIP20', 'name': 'VIP Customer 20%', 'discount_method': 'percentage', 'apply_on': 'customer', 'value': Decimal('20.00')},
            {'code': 'FLAT500', 'name': 'Flat 500 Off', 'discount_method': 'fixed', 'apply_on': 'order', 'value': Decimal('500.00'), 'min_order_amount': Decimal('5000.00')},
            {'code': 'SEASONAL', 'name': 'Seasonal Discount', 'discount_method': 'percentage', 'apply_on': 'product', 'value': Decimal('25.00')},
        ]
        for disc in discounts:
            DiscountType.objects.get_or_create(code=disc['code'], defaults=disc)
        self.stdout.write(f'  → Created {len(discounts)} discount types')

    def setup_notifications(self):
        """Setup notification types"""
        notifications = [
            {
                'code': 'LOW_STOCK',
                'name': 'Low Stock Alert',
                'trigger': 'low_stock',
                'channel': 'both',
                'subject_template': 'Low Stock Alert: {product_name}',
                'message_template': 'Product {product_name} (SKU: {sku}) has reached low stock level. Current stock: {current_stock}, Minimum level: {min_level}.'
            },
            {
                'code': 'PAYMENT_DUE',
                'name': 'Payment Due Reminder',
                'trigger': 'payment_due',
                'channel': 'email',
                'subject_template': 'Payment Due: Invoice {invoice_number}',
                'message_template': 'Invoice {invoice_number} for {customer_name} is due on {due_date}. Amount: {amount}.'
            },
            {
                'code': 'PAYMENT_OVERDUE',
                'name': 'Payment Overdue Alert',
                'trigger': 'payment_overdue',
                'channel': 'both',
                'subject_template': 'OVERDUE: Invoice {invoice_number}',
                'message_template': 'Invoice {invoice_number} for {customer_name} is overdue by {days_overdue} days. Amount: {amount}.'
            },
            {
                'code': 'ORDER_STATUS',
                'name': 'Order Status Update',
                'trigger': 'order_status',
                'channel': 'system',
                'subject_template': 'Order {order_number} Status Changed',
                'message_template': 'Order {order_number} status has been changed from {old_status} to {new_status}.'
            },
            {
                'code': 'APPROVAL_PENDING',
                'name': 'Approval Pending',
                'trigger': 'approval_pending',
                'channel': 'both',
                'subject_template': 'Approval Required: {document_type} {document_number}',
                'message_template': '{document_type} {document_number} requires your approval. Amount: {amount}. Requested by: {requested_by}.'
            },
            {
                'code': 'APPROVAL_DONE',
                'name': 'Approval Completed',
                'trigger': 'approval_completed',
                'channel': 'system',
                'subject_template': '{document_type} {document_number} {status}',
                'message_template': 'Your {document_type} {document_number} has been {status} by {approved_by}.'
            },
        ]
        for notif in notifications:
            NotificationType.objects.get_or_create(code=notif['code'], defaults=notif)
        self.stdout.write(f'  → Created {len(notifications)} notification types')

    def setup_approval_workflows(self):
        """Setup approval workflows"""
        workflows = [
            {'name': 'Sales Order Approval', 'document_type': 'sales_order'},
            {'name': 'Purchase Order Approval', 'document_type': 'purchase_order'},
            {'name': 'Stock Adjustment Approval', 'document_type': 'stock_adjustment'},
            {'name': 'Journal Entry Approval', 'document_type': 'journal_entry'},
            {'name': 'Payment Approval', 'document_type': 'payment'},
        ]
        for wf in workflows:
            workflow, created = ApprovalWorkflow.objects.get_or_create(
                document_type=wf['document_type'],
                defaults={'name': wf['name']}
            )
            if created:
                # Create default approval levels
                ApprovalLevel.objects.create(
                    workflow=workflow,
                    level=1,
                    name='Manager Approval',
                    min_amount=Decimal('0.00'),
                    max_amount=Decimal('50000.00'),
                    approver_role='Manager'
                )
                ApprovalLevel.objects.create(
                    workflow=workflow,
                    level=2,
                    name='Director Approval',
                    min_amount=Decimal('50000.01'),
                    max_amount=None,
                    approver_role='Director'
                )
        self.stdout.write(f'  → Created {len(workflows)} approval workflows with levels')
