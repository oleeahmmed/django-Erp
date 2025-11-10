"""
ERP Admin Configuration with Unfold and Inline Formsets
"""
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import (
    Company, Category, Product, Customer, Supplier, SalesPerson, Warehouse,
    SalesQuotation, SalesQuotationItem,
    SalesOrder, SalesOrderItem,
    Invoice, InvoiceItem,
    SalesReturn, SalesReturnItem,
    Delivery, DeliveryItem,
    PurchaseQuotation, PurchaseQuotationItem,
    PurchaseOrder, PurchaseOrderItem,
    GoodsReceipt, GoodsReceiptItem,
    GoodsIssue, GoodsIssueItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    PurchaseReturn, PurchaseReturnItem,
    BillOfMaterials, BOMComponent,
    ProductionOrder, ProductionOrderComponent,
    ProductionReceipt, ProductionReceiptComponent,
    InventoryTransfer, InventoryTransferItem,
    ProductWarehouseStock, StockTransaction,
    BankAccount, IncomingPayment, IncomingPaymentInvoice,
    OutgoingPayment, OutgoingPaymentInvoice,
    AccountType, ChartOfAccounts, CostCenter, Project,
    JournalEntry, JournalEntryLine, FiscalYear, Budget
)
from .utils import (
    copy_sales_quotation_to_order,
    copy_sales_order_to_delivery, copy_sales_order_to_invoice, copy_sales_order_to_return,
    copy_purchase_quotation_to_order,
    copy_purchase_order_to_receipt, copy_purchase_order_to_invoice, copy_purchase_order_to_return
)


# ==================== INLINE ADMINS ====================

class SalesQuotationItemInline(TabularInline):
    model = SalesQuotationItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']
    autocomplete_fields = ['product']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class SalesOrderItemInline(TabularInline):
    model = SalesOrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'delivered_qty', 'invoiced_qty', 'returned_qty']
    readonly_fields = ['line_total', 'delivered_qty', 'invoiced_qty', 'returned_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Delivered'))
    def delivered_qty(self, obj):
        if obj.pk:
            remaining = obj.remaining_to_deliver
            return f"{obj.delivered_quantity} / {remaining} left"
        return "-"
    
    @display(description=_('Invoiced'))
    def invoiced_qty(self, obj):
        if obj.pk:
            remaining = obj.remaining_to_invoice
            return f"{obj.invoiced_quantity} / {remaining} left"
        return "-"
    
    @display(description=_('Returned'))
    def returned_qty(self, obj):
        if obj.pk:
            return f"{obj.returned_quantity}"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class SalesReturnItemInline(TabularInline):
    model = SalesReturnItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class PurchaseQuotationItemInline(TabularInline):
    model = PurchaseQuotationItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total']
    readonly_fields = ['line_total']
    autocomplete_fields = ['product']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class PurchaseOrderItemInline(TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'received_qty', 'returned_qty']
    readonly_fields = ['line_total', 'received_qty', 'returned_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Received'))
    def received_qty(self, obj):
        if obj.pk:
            remaining = obj.remaining_to_receive
            return f"{obj.received_quantity} / {remaining} left"
        return "-"
    
    @display(description=_('Returned'))
    def returned_qty(self, obj):
        if obj.pk:
            return f"{obj.returned_quantity}"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class GoodsReceiptItemInline(TabularInline):
    model = GoodsReceiptItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class GoodsIssueItemInline(TabularInline):
    model = GoodsIssueItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_stock']
    readonly_fields = ['unit_price', 'line_total', 'available_stock']
    autocomplete_fields = ['product']
    
    @display(description=_('Stock'))
    def available_stock(self, obj):
        if obj.pk:
            return f"{obj.available_stock} in stock"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class InventoryTransferItemInline(TabularInline):
    model = InventoryTransferItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_stock']
    readonly_fields = ['unit_price', 'line_total', 'available_stock']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_stock(self, obj):
        if obj.pk:
            return f"{obj.available_stock} in source"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class BOMComponentInline(TabularInline):
    model = BOMComponent
    extra = 1
    fields = ['product', 'quantity', 'unit_cost', 'scrap_percentage', 'line_total']
    readonly_fields = ['unit_cost', 'line_total']
    autocomplete_fields = ['product']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class ProductionOrderComponentInline(TabularInline):
    model = ProductionOrderComponent
    extra = 1
    fields = ['product', 'quantity_required', 'quantity_consumed', 'unit_cost', 'line_total', 'remaining']
    readonly_fields = ['unit_cost', 'line_total', 'remaining']
    autocomplete_fields = ['product']
    
    @display(description=_('Remaining'))
    def remaining(self, obj):
        if obj.pk:
            return f"{obj.remaining_to_consume} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class ProductionReceiptComponentInline(TabularInline):
    model = ProductionReceiptComponent
    extra = 1
    fields = ['product', 'quantity_consumed', 'unit_cost', 'line_total']
    readonly_fields = ['unit_cost', 'line_total']
    autocomplete_fields = ['product']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class PurchaseInvoiceItemInline(TabularInline):
    model = PurchaseInvoiceItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class PurchaseReturnItemInline(TabularInline):
    model = PurchaseReturnItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class DeliveryItemInline(TabularInline):
    model = DeliveryItem
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'line_total', 'available_qty']
    readonly_fields = ['unit_price', 'line_total', 'available_qty']
    autocomplete_fields = ['product']
    
    @display(description=_('Available'))
    def available_qty(self, obj):
        if obj.pk:
            return f"{obj.available_quantity} left"
        return "-"
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


# ==================== MAIN ADMINS ====================

@admin.register(Warehouse)
class WarehouseAdmin(ModelAdmin):
    list_display = ['name', 'code', 'city', 'country', 'manager', 'is_active']
    list_filter = ['is_active', 'city', 'country']
    search_fields = ['name', 'code', 'city', 'manager']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'code'),
            ),
            'classes': ['tab'],
            'description': _('Warehouse identification'),
        }),
        (_('Location Details'), {
            'fields': (
                ('address',),
                ('city', 'country'),
                ('phone',),
            ),
            'classes': ['tab'],
            'description': _('Warehouse location and contact'),
        }),
        (_('Management'), {
            'fields': (
                ('manager',),
            ),
            'classes': ['tab'],
            'description': _('Warehouse management information'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Warehouse status'),
        }),
    )


@admin.register(Company)
class CompanyAdmin(ModelAdmin):
    list_display = ['name', 'city', 'country', 'phone', 'email']
    search_fields = ['name', 'city', 'email']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name',),
                ('logo',),
            ),
            'classes': ['tab'],
            'description': _('Company identification and branding'),
        }),
        (_('Contact Details'), {
            'fields': (
                ('address',),
                ('city', 'country'),
                ('phone', 'email'),
                ('website',),
            ),
            'classes': ['tab'],
            'description': _('Company contact information'),
        }),
        (_('Tax Information'), {
            'fields': (
                ('tax_number',),
            ),
            'classes': ['tab'],
            'description': _('Tax and legal information'),
        }),
    )


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name',),
            ),
            'classes': ['tab'],
            'description': _('Category name'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Category status'),
        }),
    )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ['name', 'sku', 'category', 'default_warehouse', 'current_stock', 'stock_status', 'purchase_price', 'selling_price', 'is_active']
    list_filter = ['category', 'default_warehouse', 'is_active']
    search_fields = ['name', 'sku', 'description']
    list_editable = ['is_active']
    autocomplete_fields = ['default_warehouse']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'sku'),
                ('category', 'unit'),
                ('description',),
            ),
            'classes': ['tab'],
            'description': _('Product identification and details'),
        }),
        (_('Warehouse & Stock'), {
            'fields': (
                ('default_warehouse',),
                ('current_stock', 'min_stock_level'),
            ),
            'classes': ['tab'],
            'description': _('Warehouse and stock level information'),
        }),
        (_('Pricing'), {
            'fields': (
                ('purchase_price', 'selling_price'),
            ),
            'classes': ['tab'],
            'description': _('Product pricing information'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Product status'),
        }),
    )
    
    @display(description=_('Stock Status'), label=True)
    def stock_status(self, obj):
        if obj.current_stock <= obj.min_stock_level:
            return format_html('<span style="color: red;">⚠ Low Stock</span>')
        return format_html('<span style="color: green;">✓ In Stock</span>')


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country', 'credit_limit', 'is_active']
    list_filter = ['is_active', 'city', 'country']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name',),
                ('email', 'phone'),
            ),
            'classes': ['tab'],
            'description': _('Customer contact information'),
        }),
        (_('Address Details'), {
            'fields': (
                ('address',),
                ('city', 'country'),
            ),
            'classes': ['tab'],
            'description': _('Customer address information'),
        }),
        (_('Business Details'), {
            'fields': (
                ('tax_number',),
                ('credit_limit',),
            ),
            'classes': ['tab'],
            'description': _('Business and financial information'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Customer status'),
        }),
    )


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'city', 'country', 'is_active']
    list_filter = ['is_active', 'city', 'country']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name',),
                ('email', 'phone'),
            ),
            'classes': ['tab'],
            'description': _('Supplier contact information'),
        }),
        (_('Address Details'), {
            'fields': (
                ('address',),
                ('city', 'country'),
            ),
            'classes': ['tab'],
            'description': _('Supplier address information'),
        }),
        (_('Business Details'), {
            'fields': (
                ('tax_number',),
            ),
            'classes': ['tab'],
            'description': _('Business and tax information'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Supplier status'),
        }),
    )


@admin.register(SalesPerson)
class SalesPersonAdmin(ModelAdmin):
    list_display = ['name', 'email', 'phone', 'employee_id', 'commission_rate', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'email', 'phone', 'employee_id']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'employee_id'),
                ('email', 'phone'),
            ),
            'classes': ['tab'],
            'description': _('Sales person contact information'),
        }),
        (_('Commission Details'), {
            'fields': (
                ('commission_rate',),
            ),
            'classes': ['tab'],
            'description': _('Commission rate configuration'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Sales person status'),
        }),
    )


# ==================== SALES MODULE ====================

@admin.register(SalesQuotation)
class SalesQuotationAdmin(ModelAdmin):
    list_display = ['quotation_number', 'quotation_date', 'valid_until', 'customer', 'salesperson', 'status', 'total_amount', 'action_buttons', 'created_at']
    list_filter = ['status', 'quotation_date', 'salesperson']
    search_fields = ['quotation_number', 'customer__name', 'salesperson__name']
    readonly_fields = ['quotation_number', 'subtotal', 'total_amount']
    autocomplete_fields = ['customer', 'salesperson']
    inlines = [SalesQuotationItemInline]
    actions = ['create_sales_order_action']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('quotation_number', 'quotation_date', 'valid_until'),
                ('customer', 'salesperson'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required quotation information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount'),
                ('tax_rate', 'tax_amount', 'total_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('job_reference', 'shipping_method', 'delivery_terms'),
                ('payment_terms',),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional quotation details'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        order_url = reverse('erp:copy-sales-quotation-to-order', args=[obj.id])
        
        return format_html(
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">📋 Create Order</a>',
            order_url
        )
    
    @admin.action(description=_('Create Sales Order from selected'))
    def create_sales_order_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one sales quotation.'), level='warning')
            return
        
        sales_quotation = queryset.first()
        sales_order, error = copy_sales_quotation_to_order(sales_quotation.id)
        
        if sales_order:
            url = reverse('admin:erp_salesorder_change', args=[sales_order.id])
            self.message_user(
                request,
                format_html('Sales Order <a href="{}">{}</a> created successfully!', url, sales_order.order_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')


@admin.register(SalesOrderItem)
class SalesOrderItemAdmin(ModelAdmin):
    list_display = ['sales_order', 'product', 'quantity', 'unit_price', 'line_total']
    list_filter = ['sales_order']
    search_fields = ['sales_order__order_number', 'product__name', 'product__sku']
    autocomplete_fields = ['product']
    
    def has_module_permission(self, request):
        # Hide from admin index
        return False


@admin.register(SalesOrder)
class SalesOrderAdmin(ModelAdmin):
    list_display = ['order_number', 'order_date', 'customer', 'salesperson', 'status', 'total_amount', 'action_buttons', 'created_at']
    list_filter = ['status', 'order_date', 'salesperson']
    search_fields = ['order_number', 'customer__name', 'salesperson__name']
    readonly_fields = ['order_number', 'subtotal', 'total_amount']
    autocomplete_fields = ['customer', 'salesperson', 'sales_quotation']
    inlines = [SalesOrderItemInline]
    actions = ['create_delivery_action', 'create_invoice_action', 'create_return_action']
    
    class Media:
        js = ('admin/js/sales_admin.js',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('order_number', 'order_date'),
                ('sales_quotation',),
                ('customer', 'salesperson'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required order information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount'),
                ('tax_rate', 'tax_amount', 'total_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('job_reference', 'shipping_method', 'delivery_terms'),
                ('delivery_date', 'payment_terms', 'due_date'),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional order details'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()  # This will call the clean() method
            instance.save()
        formset.save_m2m()
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        print_url = reverse('erp:print-sales-order', args=[obj.id])
        delivery_url = reverse('erp:copy-sales-order-to-delivery', args=[obj.id])
        invoice_url = reverse('erp:copy-sales-order-to-invoice', args=[obj.id])
        return_url = reverse('erp:copy-sales-order-to-return', args=[obj.id])
        
        return format_html(
            '<a href="{}" target="_blank" style="background: #4F46E5; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 3px;">🖨️ Print</a>'
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 3px;">📦 Delivery</a>'
            '<a href="{}" style="background: #F59E0B; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 3px;">📄 Invoice</a>'
            '<a href="{}" style="background: #EF4444; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">↩️ Return</a>',
            print_url, delivery_url, invoice_url, return_url
        )
    
    @admin.action(description=_('Create Delivery from selected'))
    def create_delivery_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one sales order.'), level='warning')
            return
        
        sales_order = queryset.first()
        delivery, error = copy_sales_order_to_delivery(sales_order.id)
        
        if delivery:
            url = reverse('admin:erp_delivery_change', args=[delivery.id])
            self.message_user(
                request,
                format_html('Delivery <a href="{}">{}</a> created successfully!', url, delivery.delivery_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')
    
    @admin.action(description=_('Create Invoice from selected'))
    def create_invoice_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one sales order.'), level='warning')
            return
        
        sales_order = queryset.first()
        invoice, error = copy_sales_order_to_invoice(sales_order.id)
        
        if invoice:
            url = reverse('admin:erp_invoice_change', args=[invoice.id])
            self.message_user(
                request,
                format_html('Invoice <a href="{}">{}</a> created successfully!', url, invoice.invoice_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')
    
    @admin.action(description=_('Create Return from selected'))
    def create_return_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one sales order.'), level='warning')
            return
        
        sales_order = queryset.first()
        sales_return, error = copy_sales_order_to_return(sales_order.id)
        
        if sales_return:
            url = reverse('admin:erp_salesreturn_change', args=[sales_return.id])
            self.message_user(
                request,
                format_html('Return <a href="{}">{}</a> created successfully!', url, sales_return.return_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ['invoice_number', 'invoice_date', 'sales_order', 'customer', 'salesperson', 'status', 'total_amount', 'paid_amount', 'due_amount']
    list_filter = ['status', 'invoice_date', 'salesperson']
    search_fields = ['invoice_number', 'customer__name', 'salesperson__name', 'sales_order__order_number']
    readonly_fields = ['invoice_number', 'subtotal', 'total_amount', 'due_amount']
    autocomplete_fields = ['customer', 'salesperson', 'sales_order']
    inlines = [InvoiceItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('invoice_number', 'invoice_date', 'due_date'),
                ('sales_order',),
                ('customer', 'salesperson'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required invoice information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount', 'tax_amount'),
                ('total_amount', 'paid_amount', 'due_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations and payments'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional invoice details'),
        }),
    )
    
    class Media:
        js = ('admin/js/sales_admin.js',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()


@admin.register(SalesReturn)
class SalesReturnAdmin(ModelAdmin):
    list_display = ['return_number', 'return_date', 'sales_order', 'customer', 'salesperson', 'status', 'total_amount', 'refund_amount']
    list_filter = ['status', 'return_date', 'salesperson']
    search_fields = ['return_number', 'customer__name', 'salesperson__name', 'sales_order__order_number']
    readonly_fields = ['return_number', 'subtotal', 'total_amount']
    autocomplete_fields = ['customer', 'salesperson', 'sales_order', 'invoice']
    inlines = [SalesReturnItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('return_number', 'return_date'),
                ('sales_order',),
                ('customer', 'salesperson'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required return information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'total_amount', 'refund_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations and refunds'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('invoice',),
                ('reason',),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional return details'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()
    
    class Media:
        js = ('admin/js/sales_admin.js',)


@admin.register(Delivery)
class DeliveryAdmin(ModelAdmin):
    list_display = ['delivery_number', 'delivery_date', 'sales_order', 'customer', 'salesperson', 'status']
    list_filter = ['status', 'delivery_date', 'salesperson']
    search_fields = ['delivery_number', 'customer__name', 'salesperson__name', 'sales_order__order_number']
    readonly_fields = ['delivery_number']
    autocomplete_fields = ['customer', 'salesperson', 'sales_order']
    inlines = [DeliveryItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('delivery_number', 'delivery_date'),
                ('sales_order',),
                ('customer', 'salesperson'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required delivery information'),
        }),
        (_('Shipping Details'), {
            'fields': (
                ('tracking_number', 'carrier'),
                ('shipping_cost',),
                ('delivery_address',),
            ),
            'classes': ['tab'],
            'description': _('Shipping and tracking information'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional delivery details'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()
    
    class Media:
        js = ('admin/js/sales_admin.js',)


# ==================== PURCHASE MODULE ====================

@admin.register(PurchaseQuotation)
class PurchaseQuotationAdmin(ModelAdmin):
    list_display = ['quotation_number', 'quotation_date', 'valid_until', 'supplier', 'status', 'total_amount', 'action_buttons']
    list_filter = ['status', 'quotation_date']
    search_fields = ['quotation_number', 'supplier__name']
    readonly_fields = ['quotation_number', 'subtotal', 'total_amount']
    autocomplete_fields = ['supplier']
    inlines = [PurchaseQuotationItemInline]
    actions = ['create_purchase_order_action']
    
    fieldsets = (
        (_('Quotation Information'), {
            'fields': (
                ('quotation_number', 'quotation_date', 'valid_until'),
                ('supplier', 'status'),
            ),
            'classes': ['tab'],
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount', 'tax_amount'),
                ('total_amount',),
                ('notes',),
            ),
            'classes': ['tab'],
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        order_url = reverse('erp:copy-purchase-quotation-to-order', args=[obj.id])
        
        return format_html(
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">📋 Create Order</a>',
            order_url
        )
    
    @admin.action(description=_('Create Purchase Order from selected'))
    def create_purchase_order_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one purchase quotation.'), level='warning')
            return
        
        purchase_quotation = queryset.first()
        purchase_order, error = copy_purchase_quotation_to_order(purchase_quotation.id)
        
        if purchase_order:
            url = reverse('admin:erp_purchaseorder_change', args=[purchase_order.id])
            self.message_user(
                request,
                format_html('Purchase Order <a href="{}">{}</a> created successfully!', url, purchase_order.order_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(ModelAdmin):
    list_display = ['order_number', 'order_date', 'supplier', 'status', 'total_amount', 'paid_amount', 'due_amount', 'action_buttons']
    list_filter = ['status', 'order_date']
    search_fields = ['order_number', 'supplier__name']
    readonly_fields = ['order_number', 'subtotal', 'total_amount', 'due_amount']
    autocomplete_fields = ['supplier', 'purchase_quotation']
    inlines = [PurchaseOrderItemInline]
    actions = ['create_receipt_action', 'create_invoice_action', 'create_return_action']
    
    class Media:
        js = ('admin/js/purchase_admin.js',)
    
    fieldsets = (
        (_('Order Information'), {
            'fields': (
                ('order_number', 'order_date', 'expected_date'),
                ('purchase_quotation',),
                ('supplier', 'status'),
            ),
            'classes': ['tab'],
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount', 'tax_amount'),
                ('total_amount', 'paid_amount', 'due_amount'),
                ('notes',),
            ),
            'classes': ['tab'],
        }),
    )
    
    class Media:
        js = ('admin/js/sales_order_admin.js',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        receipt_url = reverse('erp:copy-purchase-order-to-receipt', args=[obj.id])
        invoice_url = reverse('erp:copy-purchase-order-to-invoice', args=[obj.id])
        return_url = reverse('erp:copy-purchase-order-to-return', args=[obj.id])
        
        return format_html(
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 3px;">📦 Receipt</a>'
            '<a href="{}" style="background: #F59E0B; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px; margin-right: 3px;">📄 Invoice</a>'
            '<a href="{}" style="background: #EF4444; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">↩️ Return</a>',
            receipt_url, invoice_url, return_url
        )
    
    @admin.action(description=_('Create Receipt from selected'))
    def create_receipt_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one purchase order.'), level='warning')
            return
        
        purchase_order = queryset.first()
        goods_receipt, error = copy_purchase_order_to_receipt(purchase_order.id)
        
        if goods_receipt:
            url = reverse('admin:erp_goodsreceipt_change', args=[goods_receipt.id])
            self.message_user(
                request,
                format_html('Goods Receipt <a href="{}">{}</a> created successfully!', url, goods_receipt.receipt_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')
    
    @admin.action(description=_('Create Invoice from selected'))
    def create_invoice_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one purchase order.'), level='warning')
            return
        
        purchase_order = queryset.first()
        purchase_invoice, error = copy_purchase_order_to_invoice(purchase_order.id)
        
        if purchase_invoice:
            url = reverse('admin:erp_purchaseinvoice_change', args=[purchase_invoice.id])
            self.message_user(
                request,
                format_html('Purchase Invoice <a href="{}">{}</a> created successfully!', url, purchase_invoice.invoice_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')
    
    @admin.action(description=_('Create Return from selected'))
    def create_return_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one purchase order.'), level='warning')
            return
        
        purchase_order = queryset.first()
        purchase_return, error = copy_purchase_order_to_return(purchase_order.id)
        
        if purchase_return:
            url = reverse('admin:erp_purchasereturn_change', args=[purchase_return.id])
            self.message_user(
                request,
                format_html('Purchase Return <a href="{}">{}</a> created successfully!', url, purchase_return.return_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(ModelAdmin):
    list_display = ['receipt_number', 'receipt_date', 'receipt_type', 'purchase_order', 'supplier', 'status', 'received_by']
    list_filter = ['status', 'receipt_type', 'receipt_date']
    search_fields = ['receipt_number', 'supplier__name', 'purchase_order__order_number', 'reference']
    readonly_fields = ['receipt_number']
    autocomplete_fields = ['supplier', 'purchase_order']
    inlines = [GoodsReceiptItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('receipt_number', 'receipt_date'),
                ('receipt_type',),
                ('purchase_order',),
                ('supplier',),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required receipt information'),
        }),
        (_('Receipt Details'), {
            'fields': (
                ('received_by', 'warehouse_location'),
                ('reference',),
            ),
            'classes': ['tab'],
            'description': _('Receipt and warehouse information'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional receipt details'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()
    
    class Media:
        js = ('admin/js/purchase_admin.js',)


@admin.register(GoodsIssue)
class GoodsIssueAdmin(ModelAdmin):
    list_display = ['issue_number', 'issue_date', 'issue_type', 'sales_order', 'customer', 'status', 'issued_by']
    list_filter = ['status', 'issue_type', 'issue_date']
    search_fields = ['issue_number', 'customer__name', 'sales_order__order_number', 'reference']
    readonly_fields = ['issue_number']
    autocomplete_fields = ['customer', 'sales_order']
    inlines = [GoodsIssueItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('issue_number', 'issue_date'),
                ('issue_type',),
                ('sales_order',),
                ('customer',),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required issue information'),
        }),
        (_('Issue Details'), {
            'fields': (
                ('issued_by', 'warehouse_location'),
                ('reference',),
            ),
            'classes': ['tab'],
            'description': _('Issue and warehouse information'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional issue details'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()
    
    class Media:
        js = ('admin/js/sales_admin.js',)


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(ModelAdmin):
    list_display = ['invoice_number', 'invoice_date', 'purchase_order', 'supplier', 'status', 'total_amount', 'paid_amount', 'due_amount']
    list_filter = ['status', 'invoice_date']
    search_fields = ['invoice_number', 'supplier__name', 'purchase_order__order_number']
    readonly_fields = ['invoice_number', 'subtotal', 'total_amount', 'due_amount']
    autocomplete_fields = ['supplier', 'purchase_order']
    inlines = [PurchaseInvoiceItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('invoice_number', 'invoice_date', 'due_date'),
                ('purchase_order',),
                ('supplier',),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required invoice information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'discount_amount', 'tax_amount'),
                ('total_amount', 'paid_amount', 'due_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations and payments'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional invoice details'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()
    
    class Media:
        js = ('admin/js/purchase_admin.js',)


@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(ModelAdmin):
    list_display = ['return_number', 'return_date', 'purchase_order', 'supplier', 'status', 'total_amount', 'refund_amount']
    list_filter = ['status', 'return_date']
    search_fields = ['return_number', 'supplier__name', 'purchase_order__order_number']
    readonly_fields = ['return_number', 'subtotal', 'total_amount']
    autocomplete_fields = ['supplier', 'purchase_order']
    inlines = [PurchaseReturnItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('return_number', 'return_date'),
                ('purchase_order',),
                ('supplier',),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required return information'),
        }),
        (_('Financial Details'), {
            'fields': (
                ('subtotal', 'total_amount', 'refund_amount'),
            ),
            'classes': ['tab'],
            'description': _('Financial calculations and refunds'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('reason',),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional return details'),
        }),
    )
    
    class Media:
        js = ('admin/js/purchase_admin.js',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()


# ==================== PRODUCTION MODULE ====================

@admin.register(BillOfMaterials)
class BillOfMaterialsAdmin(ModelAdmin):
    list_display = ['bom_number', 'name', 'product', 'version', 'quantity', 'status', 'material_cost', 'total_cost', 'action_buttons']
    list_filter = ['status', 'created_at']
    search_fields = ['bom_number', 'name', 'product__name', 'product__sku']
    readonly_fields = ['bom_number', 'material_cost', 'total_cost']
    autocomplete_fields = ['product']
    inlines = [BOMComponentInline]
    actions = ['create_production_order_action']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('bom_number', 'name'),
                ('product', 'version'),
                ('quantity', 'status'),
            ),
            'classes': ['tab'],
            'description': _('Required BOM information'),
        }),
        (_('Cost Information'), {
            'fields': (
                ('material_cost', 'labor_cost'),
                ('overhead_cost', 'total_cost'),
            ),
            'classes': ['tab'],
            'description': _('Cost breakdown'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional BOM details'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_costs()
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        production_order_url = reverse('erp:copy-bom-to-production-order', args=[obj.id])
        
        return format_html(
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">🏭 Create Production Order</a>',
            production_order_url
        )
    
    @admin.action(description=_('Create Production Order from selected'))
    def create_production_order_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one BOM.'), level='warning')
            return
        
        bom = queryset.first()
        from .utils import copy_bom_to_production_order
        production_order, error = copy_bom_to_production_order(bom.id)
        
        if production_order:
            url = reverse('admin:erp_productionorder_change', args=[production_order.id])
            self.message_user(
                request,
                format_html('Production Order <a href="{}">{}</a> created successfully!', url, production_order.order_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')


@admin.register(ProductionOrder)
class ProductionOrderAdmin(ModelAdmin):
    list_display = ['order_number', 'order_date', 'product', 'bom', 'warehouse', 'quantity_to_produce', 'quantity_produced', 'status', 'action_buttons']
    list_filter = ['status', 'order_date', 'warehouse']
    search_fields = ['order_number', 'product__name', 'bom__bom_number', 'reference']
    readonly_fields = ['order_number', 'product']
    autocomplete_fields = ['bom', 'warehouse', 'sales_order']
    inlines = [ProductionOrderComponentInline]
    actions = ['create_production_receipt_action']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('order_number', 'order_date'),
                ('bom', 'product'),
                ('warehouse', 'status'),
            ),
            'classes': ['tab'],
            'description': _('Required production order information'),
        }),
        (_('Quantity & Schedule'), {
            'fields': (
                ('quantity_to_produce', 'quantity_produced'),
                ('planned_start_date', 'planned_end_date'),
                ('actual_start_date', 'actual_end_date'),
            ),
            'classes': ['tab'],
            'description': _('Production quantities and schedule'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('sales_order', 'reference'),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional production order details'),
        }),
    )
    
    @display(description=_('Actions'), label=True)
    def action_buttons(self, obj):
        production_receipt_url = reverse('erp:copy-production-order-to-receipt', args=[obj.id])
        
        return format_html(
            '<a href="{}" style="background: #10B981; color: white; padding: 4px 8px; border-radius: 3px; text-decoration: none; font-size: 10px;">📦 Create Receipt</a>',
            production_receipt_url
        )
    
    @admin.action(description=_('Create Production Receipt from selected'))
    def create_production_receipt_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, _('Please select exactly one Production Order.'), level='warning')
            return
        
        production_order = queryset.first()
        from .utils import copy_production_order_to_receipt
        production_receipt, error = copy_production_order_to_receipt(production_order.id)
        
        if production_receipt:
            url = reverse('admin:erp_productionreceipt_change', args=[production_receipt.id])
            self.message_user(
                request,
                format_html('Production Receipt <a href="{}">{}</a> created successfully!', url, production_receipt.receipt_number),
                level='success'
            )
        else:
            self.message_user(request, f'Error: {error}', level='error')


@admin.register(ProductionReceipt)
class ProductionReceiptAdmin(ModelAdmin):
    list_display = ['receipt_number', 'receipt_date', 'production_order', 'product', 'warehouse', 'quantity_received', 'quantity_rejected', 'status']
    list_filter = ['status', 'receipt_date', 'warehouse']
    search_fields = ['receipt_number', 'product__name', 'production_order__order_number']
    readonly_fields = ['receipt_number', 'product', 'warehouse']
    autocomplete_fields = ['production_order']
    inlines = [ProductionReceiptComponentInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('receipt_number', 'receipt_date'),
                ('production_order',),
                ('product', 'warehouse'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required receipt information'),
        }),
        (_('Quantity Details'), {
            'fields': (
                ('quantity_received', 'quantity_rejected'),
            ),
            'classes': ['tab'],
            'description': _('Production quantities'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('received_by', 'inspected_by'),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional receipt details'),
        }),
    )


# ==================== INVENTORY TRANSFER ====================

@admin.register(InventoryTransfer)
class InventoryTransferAdmin(ModelAdmin):
    list_display = ['transfer_number', 'transfer_date', 'from_warehouse', 'to_warehouse', 'status', 'transferred_by']
    list_filter = ['status', 'transfer_date', 'from_warehouse', 'to_warehouse']
    search_fields = ['transfer_number', 'reference', 'transferred_by', 'received_by']
    readonly_fields = ['transfer_number']
    autocomplete_fields = ['from_warehouse', 'to_warehouse']
    inlines = [InventoryTransferItemInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('transfer_number', 'transfer_date'),
                ('from_warehouse', 'to_warehouse'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required transfer information'),
        }),
        (_('Transfer Details'), {
            'fields': (
                ('transferred_by', 'received_by'),
                ('reference',),
            ),
            'classes': ['tab'],
            'description': _('Transfer tracking information'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional transfer details'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()


# ==================== PRODUCT WAREHOUSE STOCK ====================

@admin.register(ProductWarehouseStock)
class ProductWarehouseStockAdmin(ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'updated_at']
    list_filter = ['warehouse']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    autocomplete_fields = ['product', 'warehouse']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (_('Stock Information'), {
            'fields': ('product', 'warehouse', 'quantity')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


# ==================== STOCK TRANSACTION ====================

@admin.register(StockTransaction)
class StockTransactionAdmin(ModelAdmin):
    list_display = ['product', 'warehouse', 'transaction_type', 'quantity', 'balance_after', 'reference', 'created_at']
    list_filter = ['transaction_type', 'warehouse', 'created_at']
    search_fields = ['product__name', 'warehouse__name', 'reference']
    readonly_fields = ['created_at', 'balance_after']
    autocomplete_fields = ['product', 'warehouse']
    
    fieldsets = (
        (_('Transaction Details'), {
            'fields': ('product', 'warehouse', 'transaction_type', 'quantity', 'balance_after', 'reference')
        }),
        (_('Additional Information'), {
            'fields': ('notes', 'created_at')
        }),
    )



# ==================== BANKING MODULE ====================

class IncomingPaymentInvoiceInline(TabularInline):
    model = IncomingPaymentInvoice
    extra = 1
    fields = ['invoice', 'amount_allocated']
    autocomplete_fields = ['invoice']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


class OutgoingPaymentInvoiceInline(TabularInline):
    model = OutgoingPaymentInvoice
    extra = 1
    fields = ['purchase_invoice', 'amount_allocated']
    autocomplete_fields = ['purchase_invoice']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


@admin.register(BankAccount)
class BankAccountAdmin(ModelAdmin):
    list_display = ['account_name', 'account_number', 'account_type', 'bank_name', 'currency', 'current_balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'currency']
    search_fields = ['account_name', 'account_number', 'bank_name']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('account_name', 'account_number'),
                ('account_type', 'currency'),
            ),
            'classes': ['tab'],
            'description': _('Bank account identification'),
        }),
        (_('Bank Details'), {
            'fields': (
                ('bank_name', 'branch'),
            ),
            'classes': ['tab'],
            'description': _('Bank information'),
        }),
        (_('Balance'), {
            'fields': (
                ('opening_balance', 'current_balance'),
            ),
            'classes': ['tab'],
            'description': _('Account balance information'),
        }),
        (_('Status & Notes'), {
            'fields': (
                ('is_active',),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Account status and notes'),
        }),
    )


@admin.register(IncomingPayment)
class IncomingPaymentAdmin(ModelAdmin):
    list_display = ['payment_number', 'payment_date', 'customer', 'bank_account', 'payment_method', 'amount', 'status']
    list_filter = ['status', 'payment_method', 'payment_date', 'bank_account']
    search_fields = ['payment_number', 'customer__name', 'reference', 'check_number']
    readonly_fields = ['payment_number']
    autocomplete_fields = ['customer', 'bank_account']
    inlines = [IncomingPaymentInvoiceInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('payment_number', 'payment_date'),
                ('customer', 'bank_account'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required payment information'),
        }),
        (_('Payment Details'), {
            'fields': (
                ('amount',),
                ('payment_method',),
                ('reference', 'check_number'),
            ),
            'classes': ['tab'],
            'description': _('Payment method and details'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional payment notes'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()


@admin.register(OutgoingPayment)
class OutgoingPaymentAdmin(ModelAdmin):
    list_display = ['payment_number', 'payment_date', 'supplier', 'bank_account', 'payment_method', 'amount', 'status']
    list_filter = ['status', 'payment_method', 'payment_date', 'bank_account']
    search_fields = ['payment_number', 'supplier__name', 'reference', 'check_number']
    readonly_fields = ['payment_number']
    autocomplete_fields = ['supplier', 'bank_account']
    inlines = [OutgoingPaymentInvoiceInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('payment_number', 'payment_date'),
                ('supplier', 'bank_account'),
                ('status',),
            ),
            'classes': ['tab'],
            'description': _('Required payment information'),
        }),
        (_('Payment Details'), {
            'fields': (
                ('amount',),
                ('payment_method',),
                ('reference', 'check_number'),
            ),
            'classes': ['tab'],
            'description': _('Payment method and details'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional payment notes'),
        }),
    )
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()



# ==================== ACCOUNTING/FINANCE MODULE ====================

class JournalEntryLineInline(TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ['account', 'description', 'debit', 'credit', 'project', 'cost_center']
    autocomplete_fields = ['account', 'project', 'cost_center']
    
    class Media:
        js = ('admin/js/inline_autocomplete.js',)


@admin.register(AccountType)
class AccountTypeAdmin(ModelAdmin):
    list_display = ['name', 'type_category', 'is_active']
    list_filter = ['type_category', 'is_active']
    search_fields = ['name']
    list_editable = ['is_active']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('name', 'type_category'),
            ),
            'classes': ['tab'],
            'description': _('Account type classification'),
        }),
        (_('Status'), {
            'fields': (
                ('is_active',),
            ),
            'classes': ['tab'],
            'description': _('Account type status'),
        }),
    )


@admin.register(ChartOfAccounts)
class ChartOfAccountsAdmin(ModelAdmin):
    list_display = ['account_code', 'account_name', 'account_type', 'parent_account', 'currency', 'current_balance', 'is_active']
    list_filter = ['account_type', 'is_active', 'currency']
    search_fields = ['account_code', 'account_name', 'description']
    list_editable = ['is_active']
    autocomplete_fields = ['account_type', 'parent_account']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('account_code', 'account_name'),
                ('account_type', 'parent_account'),
                ('currency',),
            ),
            'classes': ['tab'],
            'description': _('Account identification and classification'),
        }),
        (_('Balance'), {
            'fields': (
                ('opening_balance', 'current_balance'),
            ),
            'classes': ['tab'],
            'description': _('Account balance information'),
        }),
        (_('Status & Description'), {
            'fields': (
                ('is_active',),
                ('description',),
            ),
            'classes': ['tab'],
            'description': _('Account status and notes'),
        }),
    )


@admin.register(CostCenter)
class CostCenterAdmin(ModelAdmin):
    list_display = ['code', 'name', 'parent_cost_center', 'manager', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name', 'manager']
    list_editable = ['is_active']
    autocomplete_fields = ['parent_cost_center']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('code', 'name'),
                ('parent_cost_center',),
                ('manager',),
            ),
            'classes': ['tab'],
            'description': _('Cost center identification'),
        }),
        (_('Status & Description'), {
            'fields': (
                ('is_active',),
                ('description',),
            ),
            'classes': ['tab'],
            'description': _('Cost center status and notes'),
        }),
    )


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['project_code', 'project_name', 'customer', 'status', 'project_manager', 'budget_amount', 'actual_cost', 'budget_variance', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['project_code', 'project_name', 'customer__name', 'project_manager']
    list_editable = ['is_active']
    autocomplete_fields = ['customer']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('project_code', 'project_name'),
                ('customer', 'status'),
                ('project_manager',),
            ),
            'classes': ['tab'],
            'description': _('Project identification'),
        }),
        (_('Schedule'), {
            'fields': (
                ('start_date', 'end_date'),
            ),
            'classes': ['tab'],
            'description': _('Project timeline'),
        }),
        (_('Budget'), {
            'fields': (
                ('budget_amount', 'actual_cost'),
            ),
            'classes': ['tab'],
            'description': _('Project budget and costs'),
        }),
        (_('Status & Description'), {
            'fields': (
                ('is_active',),
                ('description',),
            ),
            'classes': ['tab'],
            'description': _('Project status and notes'),
        }),
    )
    
    @display(description=_('Budget Variance'))
    def budget_variance(self, obj):
        variance = obj.budget_variance
        if variance < 0:
            return format_html('<span style="color: red;">{}</span>', variance)
        return format_html('<span style="color: green;">{}</span>', variance)


@admin.register(JournalEntry)
class JournalEntryAdmin(ModelAdmin):
    list_display = ['entry_number', 'entry_date', 'posting_date', 'status', 'total_debit', 'total_credit', 'is_balanced_display', 'project', 'cost_center']
    list_filter = ['status', 'entry_date', 'project', 'cost_center']
    search_fields = ['entry_number', 'reference', 'notes']
    readonly_fields = ['entry_number', 'total_debit', 'total_credit']
    autocomplete_fields = ['project', 'cost_center']
    inlines = [JournalEntryLineInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('entry_number', 'entry_date'),
                ('posting_date', 'status'),
                ('reference',),
            ),
            'classes': ['tab'],
            'description': _('Journal entry identification'),
        }),
        (_('Dimensions'), {
            'fields': (
                ('project', 'cost_center'),
            ),
            'classes': ['tab'],
            'description': _('Optional project and cost center'),
        }),
        (_('Totals'), {
            'fields': (
                ('total_debit', 'total_credit'),
            ),
            'classes': ['tab'],
            'description': _('Entry totals (must be balanced)'),
        }),
        (_('Additional Details'), {
            'fields': (
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Optional notes'),
        }),
    )
    
    @display(description=_('Balanced'), boolean=True)
    def is_balanced_display(self, obj):
        return obj.is_balanced
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_totals()
    
    def save_formset(self, request, form, formset, change):
        """Validate inline items before saving"""
        instances = formset.save(commit=False)
        for instance in instances:
            instance.full_clean()
            instance.save()
        formset.save_m2m()


@admin.register(FiscalYear)
class FiscalYearAdmin(ModelAdmin):
    list_display = ['year_name', 'start_date', 'end_date', 'is_closed']
    list_filter = ['is_closed']
    search_fields = ['year_name']
    list_editable = ['is_closed']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('year_name',),
                ('start_date', 'end_date'),
            ),
            'classes': ['tab'],
            'description': _('Fiscal year period'),
        }),
        (_('Status'), {
            'fields': (
                ('is_closed',),
            ),
            'classes': ['tab'],
            'description': _('Fiscal year status'),
        }),
    )


@admin.register(Budget)
class BudgetAdmin(ModelAdmin):
    list_display = ['budget_name', 'fiscal_year', 'account', 'project', 'cost_center', 'budget_amount', 'actual_amount', 'variance_display', 'utilization_display', 'is_active']
    list_filter = ['fiscal_year', 'is_active', 'account__account_type']
    search_fields = ['budget_name', 'account__account_name', 'project__project_name', 'cost_center__name']
    list_editable = ['is_active']
    autocomplete_fields = ['fiscal_year', 'account', 'project', 'cost_center']
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                ('budget_name', 'fiscal_year'),
                ('account',),
            ),
            'classes': ['tab'],
            'description': _('Budget identification'),
        }),
        (_('Dimensions'), {
            'fields': (
                ('project', 'cost_center'),
            ),
            'classes': ['tab'],
            'description': _('Optional project and cost center'),
        }),
        (_('Budget Amounts'), {
            'fields': (
                ('budget_amount', 'actual_amount'),
            ),
            'classes': ['tab'],
            'description': _('Budget and actual amounts'),
        }),
        (_('Status & Notes'), {
            'fields': (
                ('is_active',),
                ('notes',),
            ),
            'classes': ['tab'],
            'description': _('Budget status and notes'),
        }),
    )
    
    @display(description=_('Variance'))
    def variance_display(self, obj):
        variance = obj.variance
        if variance < 0:
            return format_html('<span style="color: red;">{}</span>', variance)
        return format_html('<span style="color: green;">{}</span>', variance)
    
    @display(description=_('Utilization %'))
    def utilization_display(self, obj):
        utilization = obj.utilization_percentage
        if utilization > 100:
            return format_html('<span style="color: red;">{:.2f}%</span>', utilization)
        elif utilization > 80:
            return format_html('<span style="color: orange;">{:.2f}%</span>', utilization)
        return format_html('<span style="color: green;">{:.2f}%</span>', utilization)
