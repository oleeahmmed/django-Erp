"""
ERP Models - Restructured with Info/Item pattern
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True


# ==================== COMPANY MODEL ====================
class Company(TimeStampedModel):
    """Company/Organization Information"""
    name = models.CharField(_("Company Name"), max_length=200)
    logo = models.ImageField(_("Logo"), upload_to='company/', blank=True, null=True)
    address = models.TextField(_("Address"))
    city = models.CharField(_("City"), max_length=100)
    country = models.CharField(_("Country"), max_length=100)
    phone = models.CharField(_("Phone"), max_length=20)
    email = models.EmailField(_("Email"))
    website = models.URLField(_("Website"), blank=True)
    tax_number = models.CharField(_("Tax Number"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
    
    def __str__(self):
        return self.name


# ==================== WAREHOUSE MODEL ====================
class Warehouse(TimeStampedModel):
    """Warehouse/Location Master"""
    name = models.CharField(_("Warehouse Name"), max_length=100, unique=True)
    code = models.CharField(_("Warehouse Code"), max_length=20, unique=True)
    address = models.TextField(_("Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    manager = models.CharField(_("Manager"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Warehouse")
        verbose_name_plural = _("Warehouses")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


# ==================== CATEGORY MODEL ====================
class Category(TimeStampedModel):
    """Product Category"""
    name = models.CharField(_("Category Name"), max_length=100, unique=True)
    description = models.TextField(_("Description"), blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== PRODUCT MODEL ====================
class Product(TimeStampedModel):
    """Product/Item Master"""
    name = models.CharField(_("Product Name"), max_length=200)
    sku = models.CharField(_("SKU"), max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products', verbose_name=_("Category"))
    description = models.TextField(_("Description"), blank=True)
    unit = models.CharField(_("Unit"), max_length=20, default='PCS')
    
    # Warehouse
    default_warehouse = models.ForeignKey('Warehouse', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_products', verbose_name=_("Default Warehouse"))
    
    # Pricing
    purchase_price = models.DecimalField(_("Purchase Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    selling_price = models.DecimalField(_("Selling Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    
    # Stock (Total across all warehouses)
    current_stock = models.DecimalField(_("Current Stock"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    min_stock_level = models.DecimalField(_("Minimum Stock Level"), max_digits=10, decimal_places=2, default=Decimal('10.00'))
    
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def get_warehouse_stock(self, warehouse):
        """Get stock quantity for a specific warehouse"""
        stock = ProductWarehouseStock.objects.filter(product=self, warehouse=warehouse).first()
        return stock.quantity if stock else Decimal('0.00')
    
    def save(self, *args, **kwargs):
        # Set default warehouse to first warehouse if not set
        if not self.default_warehouse:
            first_warehouse = Warehouse.objects.filter(is_active=True).first()
            if first_warehouse:
                self.default_warehouse = first_warehouse
        super().save(*args, **kwargs)


# ==================== CUSTOMER MODEL ====================
class Customer(TimeStampedModel):
    """Customer Master"""
    name = models.CharField(_("Customer Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=20)
    address = models.TextField(_("Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    tax_number = models.CharField(_("Tax Number"), max_length=50, blank=True)
    credit_limit = models.DecimalField(_("Credit Limit"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== SUPPLIER MODEL ====================
class Supplier(TimeStampedModel):
    """Supplier/Vendor Master"""
    name = models.CharField(_("Supplier Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=20)
    address = models.TextField(_("Address"), blank=True)
    city = models.CharField(_("City"), max_length=100, blank=True)
    country = models.CharField(_("Country"), max_length=100, blank=True)
    tax_number = models.CharField(_("Tax Number"), max_length=50, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Supplier")
        verbose_name_plural = _("Suppliers")
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== SALESPERSON MODEL ====================
class SalesPerson(TimeStampedModel):
    """Sales Person/Representative"""
    name = models.CharField(_("Sales Person Name"), max_length=200)
    email = models.EmailField(_("Email"), blank=True)
    phone = models.CharField(_("Phone"), max_length=20, blank=True)
    employee_id = models.CharField(_("Employee ID"), max_length=50, blank=True)
    commission_rate = models.DecimalField(_("Commission Rate (%)"), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Sales Person")
        verbose_name_plural = _("Sales Persons")
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== SALES QUOTATION ====================
class SalesQuotation(TimeStampedModel):
    """Sales Quotation - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    
    quotation_number = models.CharField(_("Quotation Number"), max_length=50, unique=True, editable=False)
    quotation_date = models.DateField(_("Quotation Date"), default=timezone.now)
    valid_until = models.DateField(_("Valid Until"), null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_quotations', verbose_name=_("Customer"))
    salesperson = models.ForeignKey('SalesPerson', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_quotations', verbose_name=_("Sales Person"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    job_reference = models.CharField(_("Job Reference"), max_length=100, blank=True)
    shipping_method = models.CharField(_("Shipping Method"), max_length=100, blank=True, default="Standard")
    delivery_terms = models.CharField(_("Delivery Terms"), max_length=100, blank=True, default="FOB")
    payment_terms = models.CharField(_("Payment Terms"), max_length=100, blank=True, default="Net 30")
    
    # Amounts (calculated from items)
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(_("Tax Rate (%)"), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Sales Quotation")
        verbose_name_plural = _("Sales Quotations")
        ordering = ['-quotation_date', '-created_at']
    
    def __str__(self):
        return f"{self.quotation_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            # Generate quotation number
            last_quotation = SalesQuotation.objects.order_by('-id').first()
            if last_quotation:
                last_num = int(last_quotation.quotation_number.split('-')[-1])
                self.quotation_number = f"SQ-{last_num + 1:06d}"
            else:
                self.quotation_number = "SQ-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])


class SalesQuotationItem(TimeStampedModel):
    """Sales Quotation Item - Line Item"""
    sales_quotation = models.ForeignKey(SalesQuotation, on_delete=models.CASCADE, related_name='items', verbose_name=_("Sales Quotation"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Sales Quotation Item")
        verbose_name_plural = _("Sales Quotation Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.sales_quotation.quotation_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update parent totals
        self.sales_quotation.calculate_totals()


# ==================== SALES ORDER ====================
class SalesOrder(TimeStampedModel):
    """Sales Order - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('confirmed', _('Confirmed')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    order_number = models.CharField(_("Order Number"), max_length=50, unique=True, editable=False)
    order_date = models.DateField(_("Order Date"), default=timezone.now)
    sales_quotation = models.ForeignKey(SalesQuotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_orders', verbose_name=_("Sales Quotation"))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_orders', verbose_name=_("Customer"))
    salesperson = models.ForeignKey('SalesPerson', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_orders', verbose_name=_("Sales Person"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    job_reference = models.CharField(_("Job Reference"), max_length=100, blank=True)
    shipping_method = models.CharField(_("Shipping Method"), max_length=100, blank=True, default="Standard")
    delivery_terms = models.CharField(_("Delivery Terms"), max_length=100, blank=True, default="FOB")
    delivery_date = models.DateField(_("Delivery Date"), null=True, blank=True)
    payment_terms = models.CharField(_("Payment Terms"), max_length=100, blank=True, default="Net 30")
    due_date = models.DateField(_("Due Date"), null=True, blank=True)
    
    # Amounts (calculated from items)
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(_("Tax Rate (%)"), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Sales Order")
        verbose_name_plural = _("Sales Orders")
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            last_order = SalesOrder.objects.order_by('-id').first()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                self.order_number = f"SO-{last_num + 1:06d}"
            else:
                self.order_number = "SO-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])


class SalesOrderItem(TimeStampedModel):
    """Sales Order Item - Line Item"""
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='items', verbose_name=_("Sales Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Sales Order Item")
        verbose_name_plural = _("Sales Order Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.sales_order.order_number} - {self.product.name}"
    
    @property
    def delivered_quantity(self):
        """Calculate total delivered quantity for this product"""
        from django.db.models import Sum
        total = DeliveryItem.objects.filter(
            delivery__sales_order=self.sales_order,
            product=self.product
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        return total
    
    @property
    def invoiced_quantity(self):
        """Calculate total invoiced quantity for this product"""
        from django.db.models import Sum
        total = InvoiceItem.objects.filter(
            invoice__sales_order=self.sales_order,
            product=self.product
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        return total
    
    @property
    def returned_quantity(self):
        """Calculate total returned quantity for this product"""
        from django.db.models import Sum
        total = SalesReturnItem.objects.filter(
            sales_return__sales_order=self.sales_order,
            product=self.product
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        return total
    
    @property
    def remaining_to_deliver(self):
        """Calculate remaining quantity to deliver"""
        return self.quantity - self.delivered_quantity
    
    @property
    def remaining_to_invoice(self):
        """Calculate remaining quantity to invoice"""
        return self.quantity - self.invoiced_quantity
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # Update parent totals
        self.sales_order.calculate_totals()


# ==================== INVOICE ====================
class Invoice(TimeStampedModel):
    """Invoice - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    invoice_number = models.CharField(_("Invoice Number"), max_length=50, unique=True, editable=False)
    invoice_date = models.DateField(_("Invoice Date"), default=timezone.now)
    due_date = models.DateField(_("Due Date"))
    
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='invoices', verbose_name=_("Sales Order"))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices', verbose_name=_("Customer"))
    salesperson = models.ForeignKey('SalesPerson', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices', verbose_name=_("Sales Person"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    paid_amount = models.DecimalField(_("Paid Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    due_amount = models.DecimalField(_("Due Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")
        ordering = ['-invoice_date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                self.invoice_number = f"INV-{last_num + 1:06d}"
            else:
                self.invoice_number = "INV-000001"
        
        self.due_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.due_amount = self.total_amount - self.paid_amount
        self.save(update_fields=['subtotal', 'total_amount', 'due_amount'])


class InvoiceItem(TimeStampedModel):
    """Invoice Item - Line Item"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', verbose_name=_("Invoice"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Invoice Item")
        verbose_name_plural = _("Invoice Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"
    
    def get_sales_order_item(self):
        """Find matching sales order item by product"""
        if self.invoice.sales_order:
            return self.invoice.sales_order.items.filter(product=self.product).first()
        return None
    
    @property
    def sales_order_item(self):
        """Get sales order item for this product"""
        return self.get_sales_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity from sales order"""
        so_item = self.get_sales_order_item()
        if so_item:
            return so_item.remaining_to_invoice
        return Decimal('0.00')
    
    def clean(self):
        """Validate invoice quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.invoice.sales_order:
            raise ValidationError('Invoice must have a Sales Order.')
        
        # Find matching sales order item
        so_item = self.get_sales_order_item()
        if not so_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Sales Order {self.invoice.sales_order.order_number}.'
            })
        
        # Check if quantity exceeds available
        from django.db.models import Sum
        other_invoices = InvoiceItem.objects.filter(
            invoice__sales_order=self.invoice.sales_order,
            product=self.product
        ).exclude(pk=self.pk).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        total_invoiced = other_invoices + self.quantity
        
        if total_invoiced > so_item.quantity:
            raise ValidationError({
                'quantity': f'Cannot invoice {self.quantity}. Only {so_item.remaining_to_invoice} remaining for this product.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from sales order if not set
        if self.unit_price == Decimal('0.00'):
            so_item = self.get_sales_order_item()
            if so_item:
                self.unit_price = so_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.invoice.calculate_totals()


# ==================== SALES RETURN ====================
class SalesReturn(TimeStampedModel):
    """Sales Return - Header/Info"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    ]
    
    return_number = models.CharField(_("Return Number"), max_length=50, unique=True, editable=False)
    return_date = models.DateField(_("Return Date"), default=timezone.now)
    
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='returns', verbose_name=_("Sales Order"))
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns', verbose_name=_("Invoice"))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_returns', verbose_name=_("Customer"))
    salesperson = models.ForeignKey('SalesPerson', on_delete=models.SET_NULL, null=True, blank=True, related_name='sales_returns', verbose_name=_("Sales Person"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(_("Return Reason"), blank=True)
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    refund_amount = models.DecimalField(_("Refund Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Sales Return")
        verbose_name_plural = _("Sales Returns")
        ordering = ['-return_date', '-created_at']
    
    def __str__(self):
        return f"{self.return_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.return_number:
            last_return = SalesReturn.objects.order_by('-id').first()
            if last_return:
                last_num = int(last_return.return_number.split('-')[-1])
                self.return_number = f"SR-{last_num + 1:06d}"
            else:
                self.return_number = "SR-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal
        self.save(update_fields=['subtotal', 'total_amount'])


class SalesReturnItem(TimeStampedModel):
    """Sales Return Item - Line Item"""
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name='items', verbose_name=_("Sales Return"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Sales Return Item")
        verbose_name_plural = _("Sales Return Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.sales_return.return_number} - {self.product.name}"
    
    def get_sales_order_item(self):
        """Find matching sales order item by product"""
        if self.sales_return.sales_order:
            return self.sales_return.sales_order.items.filter(product=self.product).first()
        return None
    
    @property
    def sales_order_item(self):
        """Get sales order item for this product"""
        return self.get_sales_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity to return (delivered - already returned)"""
        so_item = self.get_sales_order_item()
        if so_item:
            return so_item.delivered_quantity - so_item.returned_quantity
        return Decimal('0.00')
    
    def clean(self):
        """Validate return quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.sales_return.sales_order:
            raise ValidationError('Sales Return must have a Sales Order.')
        
        # Find matching sales order item
        so_item = self.get_sales_order_item()
        if not so_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Sales Order {self.sales_return.sales_order.order_number}.'
            })
        
        # Check if quantity exceeds delivered
        from django.db.models import Sum
        other_returns = SalesReturnItem.objects.filter(
            sales_return__sales_order=self.sales_return.sales_order,
            product=self.product
        ).exclude(pk=self.pk).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        total_returned = other_returns + self.quantity
        delivered = so_item.delivered_quantity
        
        if total_returned > delivered:
            raise ValidationError({
                'quantity': f'Cannot return {self.quantity}. Only {delivered - other_returns} available to return for this product.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from sales order if not set
        if self.unit_price == Decimal('0.00'):
            so_item = self.get_sales_order_item()
            if so_item:
                self.unit_price = so_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.sales_return.calculate_totals()


# ==================== DELIVERY ====================
class Delivery(TimeStampedModel):
    """Delivery - Header/Info"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_transit', _('In Transit')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]
    
    delivery_number = models.CharField(_("Delivery Number"), max_length=50, unique=True, editable=False)
    delivery_date = models.DateField(_("Delivery Date"), default=timezone.now)
    
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, related_name='deliveries', verbose_name=_("Sales Order"))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='deliveries', verbose_name=_("Customer"))
    salesperson = models.ForeignKey('SalesPerson', on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries', verbose_name=_("Sales Person"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery Details
    delivery_address = models.TextField(_("Delivery Address"), blank=True)
    tracking_number = models.CharField(_("Tracking Number"), max_length=100, blank=True)
    carrier = models.CharField(_("Carrier"), max_length=100, blank=True)
    shipping_cost = models.DecimalField(_("Shipping Cost"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")
        ordering = ['-delivery_date', '-created_at']
    
    def __str__(self):
        return f"{self.delivery_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.delivery_number:
            last_delivery = Delivery.objects.order_by('-id').first()
            if last_delivery:
                last_num = int(last_delivery.delivery_number.split('-')[-1])
                self.delivery_number = f"DL-{last_num + 1:06d}"
            else:
                self.delivery_number = "DL-000001"
        super().save(*args, **kwargs)


class DeliveryItem(TimeStampedModel):
    """Delivery Item - Line Item"""
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='items', verbose_name=_("Delivery"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Delivery Item")
        verbose_name_plural = _("Delivery Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.delivery.delivery_number} - {self.product.name}"
    
    def get_sales_order_item(self):
        """Find matching sales order item by product"""
        if self.delivery.sales_order:
            return self.delivery.sales_order.items.filter(product=self.product).first()
        return None
    
    @property
    def sales_order_item(self):
        """Get sales order item for this product"""
        return self.get_sales_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity from sales order"""
        so_item = self.get_sales_order_item()
        if so_item:
            return so_item.remaining_to_deliver
        return Decimal('0.00')
    
    def clean(self):
        """Validate delivery quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.delivery.sales_order:
            raise ValidationError('Delivery must have a Sales Order.')
        
        # Find matching sales order item
        so_item = self.get_sales_order_item()
        if not so_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Sales Order {self.delivery.sales_order.order_number}.'
            })
        
        # Check if quantity exceeds available
        from django.db.models import Sum
        other_deliveries = DeliveryItem.objects.filter(
            delivery__sales_order=self.delivery.sales_order,
            product=self.product
        ).exclude(pk=self.pk).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        total_delivered = other_deliveries + self.quantity
        
        if total_delivered > so_item.quantity:
            raise ValidationError({
                'quantity': f'Cannot deliver {self.quantity}. Only {so_item.remaining_to_deliver} remaining for this product.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from sales order if not set
        if self.unit_price == Decimal('0.00'):
            so_item = self.get_sales_order_item()
            if so_item:
                self.unit_price = so_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ==================== PURCHASE QUOTATION ====================
class PurchaseQuotation(TimeStampedModel):
    """Purchase Quotation (RFQ - Request for Quotation) - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('received', _('Received')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    
    quotation_number = models.CharField(_("Quotation Number"), max_length=50, unique=True, editable=False)
    quotation_date = models.DateField(_("Quotation Date"), default=timezone.now)
    valid_until = models.DateField(_("Valid Until"), null=True, blank=True)
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_quotations', verbose_name=_("Supplier"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Purchase Quotation")
        verbose_name_plural = _("Purchase Quotations")
        ordering = ['-quotation_date', '-created_at']
    
    def __str__(self):
        return f"{self.quotation_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.quotation_number:
            last_quotation = PurchaseQuotation.objects.order_by('-id').first()
            if last_quotation:
                last_num = int(last_quotation.quotation_number.split('-')[-1])
                self.quotation_number = f"PQ-{last_num + 1:06d}"
            else:
                self.quotation_number = "PQ-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])


class PurchaseQuotationItem(TimeStampedModel):
    """Purchase Quotation Item - Line Item"""
    purchase_quotation = models.ForeignKey(PurchaseQuotation, on_delete=models.CASCADE, related_name='items', verbose_name=_("Purchase Quotation"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Purchase Quotation Item")
        verbose_name_plural = _("Purchase Quotation Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_quotation.quotation_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase_quotation.calculate_totals()


# ==================== PURCHASE ORDER ====================
class PurchaseOrder(TimeStampedModel):
    """Purchase Order - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('sent', _('Sent')),
        ('confirmed', _('Confirmed')),
        ('received', _('Received')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    order_number = models.CharField(_("Order Number"), max_length=50, unique=True, editable=False)
    order_date = models.DateField(_("Order Date"), default=timezone.now)
    expected_date = models.DateField(_("Expected Delivery Date"), null=True, blank=True)
    
    purchase_quotation = models.ForeignKey(PurchaseQuotation, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders', verbose_name=_("Purchase Quotation"))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_orders', verbose_name=_("Supplier"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    paid_amount = models.DecimalField(_("Paid Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    due_amount = models.DecimalField(_("Due Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Purchase Order")
        verbose_name_plural = _("Purchase Orders")
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = PurchaseOrder.objects.order_by('-id').first()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                self.order_number = f"PO-{last_num + 1:06d}"
            else:
                self.order_number = "PO-000001"
        
        self.due_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.due_amount = self.total_amount - self.paid_amount
        self.save(update_fields=['subtotal', 'total_amount', 'due_amount'])


class PurchaseOrderItem(TimeStampedModel):
    """Purchase Order Item - Line Item"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name=_("Purchase Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Purchase Order Item")
        verbose_name_plural = _("Purchase Order Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_order.order_number} - {self.product.name}"
    
    @property
    def received_quantity(self):
        """Calculate total received quantity for this product"""
        from django.db.models import Sum
        total = GoodsReceiptItem.objects.filter(
            goods_receipt__purchase_order=self.purchase_order,
            product=self.product
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        return total
    
    @property
    def returned_quantity(self):
        """Calculate total returned quantity for this product"""
        from django.db.models import Sum
        total = PurchaseReturnItem.objects.filter(
            purchase_return__purchase_order=self.purchase_order,
            product=self.product
        ).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        return total
    
    @property
    def remaining_to_receive(self):
        """Calculate remaining quantity to receive"""
        return self.quantity - self.received_quantity
    
    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase_order.calculate_totals()


# ==================== GOODS RECEIPT (GRN) ====================
class GoodsReceipt(TimeStampedModel):
    """Goods Receipt Note (GRN) - Header/Info"""
    RECEIPT_TYPE_CHOICES = [
        ('purchase', _('From Purchase Order')),
        ('return', _('From Sales Return')),
        ('adjustment', _('Stock Adjustment')),
        ('transfer', _('Transfer In')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('received', _('Received')),
        ('inspected', _('Inspected')),
        ('completed', _('Completed')),
        ('rejected', _('Rejected')),
    ]
    
    receipt_number = models.CharField(_("Receipt Number"), max_length=50, unique=True, editable=False)
    receipt_date = models.DateField(_("Receipt Date"), default=timezone.now)
    receipt_type = models.CharField(_("Receipt Type"), max_length=20, choices=RECEIPT_TYPE_CHOICES, default='purchase')
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, null=True, blank=True, related_name='receipts', verbose_name=_("Purchase Order"))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, null=True, blank=True, related_name='receipts', verbose_name=_("Supplier"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Receipt Details
    received_by = models.CharField(_("Received By"), max_length=100, blank=True)
    warehouse_location = models.CharField(_("Warehouse Location"), max_length=100, blank=True, default="Main Warehouse")
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Goods Receipt")
        verbose_name_plural = _("Goods Receipts")
        ordering = ['-receipt_date', '-created_at']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.receipt_type}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_receipt = GoodsReceipt.objects.order_by('-id').first()
            if last_receipt:
                last_num = int(last_receipt.receipt_number.split('-')[-1])
                self.receipt_number = f"GRN-{last_num + 1:06d}"
            else:
                self.receipt_number = "GRN-000001"
        super().save(*args, **kwargs)


class GoodsReceiptItem(TimeStampedModel):
    """Goods Receipt Item - Line Item"""
    goods_receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items', verbose_name=_("Goods Receipt"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Goods Receipt Item")
        verbose_name_plural = _("Goods Receipt Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.goods_receipt.receipt_number} - {self.product.name}"
    
    def get_purchase_order_item(self):
        """Find matching purchase order item by product"""
        if self.goods_receipt.purchase_order:
            return self.goods_receipt.purchase_order.items.filter(product=self.product).first()
        return None
    
    @property
    def purchase_order_item(self):
        """Get purchase order item for this product"""
        return self.get_purchase_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity from purchase order"""
        po_item = self.get_purchase_order_item()
        if po_item:
            return po_item.remaining_to_receive
        return Decimal('0.00')
    
    def clean(self):
        """Validate receipt quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.goods_receipt.purchase_order:
            raise ValidationError('Goods Receipt must have a Purchase Order.')
        
        # Find matching purchase order item
        po_item = self.get_purchase_order_item()
        if not po_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Purchase Order {self.goods_receipt.purchase_order.order_number}.'
            })
        
        # Check if quantity exceeds available
        from django.db.models import Sum
        other_receipts = GoodsReceiptItem.objects.filter(
            goods_receipt__purchase_order=self.goods_receipt.purchase_order,
            product=self.product
        ).exclude(pk=self.pk).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        total_received = other_receipts + self.quantity
        
        if total_received > po_item.quantity:
            raise ValidationError({
                'quantity': f'Cannot receive {self.quantity}. Only {po_item.remaining_to_receive} remaining for this product.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from purchase order if not set
        if self.unit_price == Decimal('0.00'):
            po_item = self.get_purchase_order_item()
            if po_item:
                self.unit_price = po_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ==================== PURCHASE INVOICE (AP INVOICE) ====================
class PurchaseInvoice(TimeStampedModel):
    """Purchase Invoice (AP Invoice) - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('received', _('Received')),
        ('paid', _('Paid')),
        ('partially_paid', _('Partially Paid')),
        ('overdue', _('Overdue')),
        ('cancelled', _('Cancelled')),
    ]
    
    invoice_number = models.CharField(_("Invoice Number"), max_length=50, unique=True, editable=False)
    invoice_date = models.DateField(_("Invoice Date"), default=timezone.now)
    due_date = models.DateField(_("Due Date"))
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='invoices', verbose_name=_("Purchase Order"))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='invoices', verbose_name=_("Supplier"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(_("Tax Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    paid_amount = models.DecimalField(_("Paid Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    due_amount = models.DecimalField(_("Due Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Purchase Invoice")
        verbose_name_plural = _("Purchase Invoices")
        ordering = ['-invoice_date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = PurchaseInvoice.objects.order_by('-id').first()
            if last_invoice:
                last_num = int(last_invoice.invoice_number.split('-')[-1])
                self.invoice_number = f"PINV-{last_num + 1:06d}"
            else:
                self.invoice_number = "PINV-000001"
        
        self.due_amount = self.total_amount - self.paid_amount
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.due_amount = self.total_amount - self.paid_amount
        self.save(update_fields=['subtotal', 'total_amount', 'due_amount'])


class PurchaseInvoiceItem(TimeStampedModel):
    """Purchase Invoice Item - Line Item"""
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='items', verbose_name=_("Purchase Invoice"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Purchase Invoice Item")
        verbose_name_plural = _("Purchase Invoice Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_invoice.invoice_number} - {self.product.name}"
    
    def get_purchase_order_item(self):
        """Find matching purchase order item by product"""
        if self.purchase_invoice.purchase_order:
            return self.purchase_invoice.purchase_order.items.filter(product=self.product).first()
        return None
    
    @property
    def purchase_order_item(self):
        """Get purchase order item for this product"""
        return self.get_purchase_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity from purchase order"""
        po_item = self.get_purchase_order_item()
        if po_item:
            # Calculate how much has been invoiced already
            from django.db.models import Sum
            invoiced = PurchaseInvoiceItem.objects.filter(
                purchase_invoice__purchase_order=self.purchase_invoice.purchase_order,
                product=self.product
            ).exclude(pk=self.pk).aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
            return po_item.quantity - invoiced
        return Decimal('0.00')
    
    def clean(self):
        """Validate invoice quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.purchase_invoice.purchase_order:
            return  # Allow saving without validation
        
        # Find matching purchase order item
        po_item = self.get_purchase_order_item()
        if not po_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Purchase Order {self.purchase_invoice.purchase_order.order_number}.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from purchase order if not set
        if self.unit_price == Decimal('0.00'):
            po_item = self.get_purchase_order_item()
            if po_item:
                self.unit_price = po_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase_invoice.calculate_totals()


# ==================== PURCHASE RETURN ====================
class PurchaseReturn(TimeStampedModel):
    """Purchase Return - Header/Info"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('completed', _('Completed')),
    ]
    
    return_number = models.CharField(_("Return Number"), max_length=50, unique=True, editable=False)
    return_date = models.DateField(_("Return Date"), default=timezone.now)
    
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT, related_name='returns', verbose_name=_("Purchase Order"))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_returns', verbose_name=_("Supplier"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(_("Return Reason"), blank=True)
    
    # Amounts
    subtotal = models.DecimalField(_("Subtotal"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_amount = models.DecimalField(_("Total Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    refund_amount = models.DecimalField(_("Refund Amount"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Purchase Return")
        verbose_name_plural = _("Purchase Returns")
        ordering = ['-return_date', '-created_at']
    
    def __str__(self):
        return f"{self.return_number} - {self.supplier.name}"
    
    def save(self, *args, **kwargs):
        if not self.return_number:
            last_return = PurchaseReturn.objects.order_by('-id').first()
            if last_return:
                last_num = int(last_return.return_number.split('-')[-1])
                self.return_number = f"PR-{last_num + 1:06d}"
            else:
                self.return_number = "PR-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate totals from items"""
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        self.total_amount = self.subtotal
        self.save(update_fields=['subtotal', 'total_amount'])


class PurchaseReturnItem(TimeStampedModel):
    """Purchase Return Item - Line Item"""
    purchase_return = models.ForeignKey(PurchaseReturn, on_delete=models.CASCADE, related_name='items', verbose_name=_("Purchase Return"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Purchase Return Item")
        verbose_name_plural = _("Purchase Return Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.purchase_return.return_number} - {self.product.name}"
    
    def get_purchase_order_item(self):
        """Find matching purchase order item by product"""
        if self.purchase_return.purchase_order:
            return self.purchase_return.purchase_order.items.filter(product=self.product).first()
        return None
    
    @property
    def purchase_order_item(self):
        """Get purchase order item for this product"""
        return self.get_purchase_order_item()
    
    @property
    def available_quantity(self):
        """Get available quantity to return (received quantity)"""
        po_item = self.get_purchase_order_item()
        if po_item:
            return po_item.received_quantity - po_item.returned_quantity
        return Decimal('0.00')
    
    def clean(self):
        """Validate return quantity"""
        from django.core.exceptions import ValidationError
        
        if not self.purchase_return.purchase_order:
            return  # Allow saving without validation
        
        # Find matching purchase order item
        po_item = self.get_purchase_order_item()
        if not po_item:
            raise ValidationError({
                'product': f'Product "{self.product.name}" is not in Purchase Order {self.purchase_return.purchase_order.order_number}.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from purchase order if not set
        if self.unit_price == Decimal('0.00'):
            po_item = self.get_purchase_order_item()
            if po_item:
                self.unit_price = po_item.unit_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.purchase_return.calculate_totals()


# ==================== BILL OF MATERIALS (BOM) ====================
class BillOfMaterials(TimeStampedModel):
    """Bill of Materials - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('obsolete', _('Obsolete')),
    ]
    
    bom_number = models.CharField(_("BOM Number"), max_length=50, unique=True, editable=False)
    name = models.CharField(_("BOM Name"), max_length=200)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='boms', verbose_name=_("Finished Product"))
    version = models.CharField(_("Version"), max_length=20, default='1.0')
    quantity = models.DecimalField(_("Production Quantity"), max_digits=10, decimal_places=2, default=Decimal('1.00'), validators=[MinValueValidator(Decimal('0.01'))])
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Cost tracking
    material_cost = models.DecimalField(_("Material Cost"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    labor_cost = models.DecimalField(_("Labor Cost"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    overhead_cost = models.DecimalField(_("Overhead Cost"), max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_cost = models.DecimalField(_("Total Cost"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Bill of Materials")
        verbose_name_plural = _("Bills of Materials")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.bom_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.bom_number:
            last_bom = BillOfMaterials.objects.order_by('-id').first()
            if last_bom:
                last_num = int(last_bom.bom_number.split('-')[-1])
                self.bom_number = f"BOM-{last_num + 1:06d}"
            else:
                self.bom_number = "BOM-000001"
        super().save(*args, **kwargs)
    
    def calculate_costs(self):
        """Calculate total costs from components"""
        components = self.components.all()
        self.material_cost = sum(comp.line_total for comp in components)
        self.total_cost = self.material_cost + self.labor_cost + self.overhead_cost
        self.save(update_fields=['material_cost', 'total_cost'])


class BOMComponent(TimeStampedModel):
    """BOM Component - Line Item (Raw Materials/Components)"""
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.CASCADE, related_name='components', verbose_name=_("BOM"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Component/Material"))
    
    quantity = models.DecimalField(_("Quantity Required"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_cost = models.DecimalField(_("Unit Cost"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    scrap_percentage = models.DecimalField(_("Scrap %"), max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        verbose_name = _("BOM Component")
        verbose_name_plural = _("BOM Components")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.bom.bom_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Auto-set unit cost from product if not set
        if self.unit_cost == Decimal('0.00'):
            self.unit_cost = self.product.purchase_price
        
        # Calculate with scrap
        quantity_with_scrap = self.quantity * (Decimal('1.00') + (self.scrap_percentage / Decimal('100.00')))
        self.line_total = quantity_with_scrap * self.unit_cost
        super().save(*args, **kwargs)
        # Update parent costs
        self.bom.calculate_costs()


# ==================== PRODUCTION ORDER ====================
class ProductionOrder(TimeStampedModel):
    """Production Order - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('planned', _('Planned')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    order_number = models.CharField(_("Order Number"), max_length=50, unique=True, editable=False)
    order_date = models.DateField(_("Order Date"), default=timezone.now)
    planned_start_date = models.DateField(_("Planned Start Date"), null=True, blank=True)
    planned_end_date = models.DateField(_("Planned End Date"), null=True, blank=True)
    actual_start_date = models.DateField(_("Actual Start Date"), null=True, blank=True)
    actual_end_date = models.DateField(_("Actual End Date"), null=True, blank=True)
    
    bom = models.ForeignKey(BillOfMaterials, on_delete=models.PROTECT, related_name='production_orders', verbose_name=_("Bill of Materials"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='production_orders', verbose_name=_("Product to Produce"))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='production_orders', verbose_name=_("Production Warehouse"))
    
    quantity_to_produce = models.DecimalField(_("Quantity to Produce"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    quantity_produced = models.DecimalField(_("Quantity Produced"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Reference
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_orders', verbose_name=_("Sales Order"))
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Production Order")
        verbose_name_plural = _("Production Orders")
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = ProductionOrder.objects.order_by('-id').first()
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                self.order_number = f"PRO-{last_num + 1:06d}"
            else:
                self.order_number = "PRO-000001"
        
        # Auto-set product from BOM if not set
        if not self.product_id and self.bom:
            self.product = self.bom.product
        
        super().save(*args, **kwargs)
    
    @property
    def remaining_to_produce(self):
        """Calculate remaining quantity to produce"""
        return self.quantity_to_produce - self.quantity_produced


class ProductionOrderComponent(TimeStampedModel):
    """Production Order Component - Required Materials"""
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name='components', verbose_name=_("Production Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Component/Material"))
    
    quantity_required = models.DecimalField(_("Quantity Required"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    quantity_consumed = models.DecimalField(_("Quantity Consumed"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    unit_cost = models.DecimalField(_("Unit Cost"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Production Order Component")
        verbose_name_plural = _("Production Order Components")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.production_order.order_number} - {self.product.name}"
    
    @property
    def remaining_to_consume(self):
        """Calculate remaining quantity to consume"""
        return self.quantity_required - self.quantity_consumed
    
    def save(self, *args, **kwargs):
        # Auto-set unit cost from product if not set
        if self.unit_cost == Decimal('0.00'):
            self.unit_cost = self.product.purchase_price
        
        self.line_total = self.quantity_required * self.unit_cost
        super().save(*args, **kwargs)


# ==================== PRODUCTION RECEIPT ====================
class ProductionReceipt(TimeStampedModel):
    """Production Receipt - Finished Goods Receipt"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('received', _('Received')),
        ('inspected', _('Inspected')),
        ('completed', _('Completed')),
    ]
    
    receipt_number = models.CharField(_("Receipt Number"), max_length=50, unique=True, editable=False)
    receipt_date = models.DateField(_("Receipt Date"), default=timezone.now)
    
    production_order = models.ForeignKey(ProductionOrder, on_delete=models.PROTECT, related_name='receipts', verbose_name=_("Production Order"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Finished Product"))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='production_receipts', verbose_name=_("Warehouse"))
    
    quantity_received = models.DecimalField(_("Quantity Received"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    quantity_rejected = models.DecimalField(_("Quantity Rejected"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Details
    received_by = models.CharField(_("Received By"), max_length=100, blank=True)
    inspected_by = models.CharField(_("Inspected By"), max_length=100, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Production Receipt")
        verbose_name_plural = _("Production Receipts")
        ordering = ['-receipt_date', '-created_at']
    
    def __str__(self):
        return f"{self.receipt_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            last_receipt = ProductionReceipt.objects.order_by('-id').first()
            if last_receipt:
                last_num = int(last_receipt.receipt_number.split('-')[-1])
                self.receipt_number = f"PRR-{last_num + 1:06d}"
            else:
                self.receipt_number = "PRR-000001"
        
        # Auto-set product and warehouse from production order if not set
        if not self.product_id and self.production_order:
            self.product = self.production_order.product
        if not self.warehouse_id and self.production_order:
            self.warehouse = self.production_order.warehouse
        
        super().save(*args, **kwargs)
    
    @property
    def quantity_accepted(self):
        """Calculate accepted quantity"""
        return self.quantity_received - self.quantity_rejected


class ProductionReceiptComponent(TimeStampedModel):
    """Production Receipt Component - Materials Consumed"""
    production_receipt = models.ForeignKey(ProductionReceipt, on_delete=models.CASCADE, related_name='components', verbose_name=_("Production Receipt"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Component/Material"))
    
    quantity_consumed = models.DecimalField(_("Quantity Consumed"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_cost = models.DecimalField(_("Unit Cost"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Production Receipt Component")
        verbose_name_plural = _("Production Receipt Components")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.production_receipt.receipt_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Auto-set unit cost from product if not set
        if self.unit_cost == Decimal('0.00'):
            self.unit_cost = self.product.purchase_price
        
        self.line_total = self.quantity_consumed * self.unit_cost
        super().save(*args, **kwargs)


# ==================== GOODS ISSUE ====================
class GoodsIssue(TimeStampedModel):
    """Goods Issue - Header/Info"""
    ISSUE_TYPE_CHOICES = [
        ('sales', _('For Sales Order')),
        ('production', _('For Production')),
        ('adjustment', _('Stock Adjustment')),
        ('transfer', _('Transfer Out')),
        ('damage', _('Damage/Loss')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('issued', _('Issued')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    issue_number = models.CharField(_("Issue Number"), max_length=50, unique=True, editable=False)
    issue_date = models.DateField(_("Issue Date"), default=timezone.now)
    issue_type = models.CharField(_("Issue Type"), max_length=20, choices=ISSUE_TYPE_CHOICES, default='sales')
    
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.PROTECT, null=True, blank=True, related_name='goods_issues', verbose_name=_("Sales Order"))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True, blank=True, related_name='goods_issues', verbose_name=_("Customer"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Issue Details
    issued_by = models.CharField(_("Issued By"), max_length=100, blank=True)
    warehouse_location = models.CharField(_("Warehouse Location"), max_length=100, blank=True, default="Main Warehouse")
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Goods Issue")
        verbose_name_plural = _("Goods Issues")
        ordering = ['-issue_date', '-created_at']
    
    def __str__(self):
        return f"{self.issue_number} - {self.issue_type}"
    
    def save(self, *args, **kwargs):
        if not self.issue_number:
            last_issue = GoodsIssue.objects.order_by('-id').first()
            if last_issue:
                last_num = int(last_issue.issue_number.split('-')[-1])
                self.issue_number = f"GI-{last_num + 1:06d}"
            else:
                self.issue_number = "GI-000001"
        super().save(*args, **kwargs)


class GoodsIssueItem(TimeStampedModel):
    """Goods Issue Item - Line Item"""
    goods_issue = models.ForeignKey(GoodsIssue, on_delete=models.CASCADE, related_name='items', verbose_name=_("Goods Issue"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Goods Issue Item")
        verbose_name_plural = _("Goods Issue Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.goods_issue.issue_number} - {self.product.name}"
    
    def get_sales_order_item(self):
        """Find matching sales order item by product"""
        if self.goods_issue.sales_order:
            return self.goods_issue.sales_order.items.filter(product=self.product).first()
        return None
    
    @property
    def sales_order_item(self):
        """Get sales order item for this product"""
        return self.get_sales_order_item()
    
    @property
    def available_stock(self):
        """Get available stock for this product"""
        return self.product.current_stock
    
    def clean(self):
        """Validate issue quantity"""
        from django.core.exceptions import ValidationError
        
        # Check if quantity exceeds available stock
        if self.quantity > self.product.current_stock:
            raise ValidationError({
                'quantity': f'Cannot issue {self.quantity}. Only {self.product.current_stock} available in stock.'
            })
        
        # If linked to sales order, validate against order quantity
        if self.goods_issue.sales_order:
            so_item = self.get_sales_order_item()
            if not so_item:
                raise ValidationError({
                    'product': f'Product "{self.product.name}" is not in Sales Order {self.goods_issue.sales_order.order_number}.'
                })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from product if not set
        if self.unit_price == Decimal('0.00'):
            self.unit_price = self.product.selling_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ==================== PRODUCT WAREHOUSE STOCK ====================
class ProductWarehouseStock(TimeStampedModel):
    """Product Stock by Warehouse"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='warehouse_stocks', verbose_name=_("Product"))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='product_stocks', verbose_name=_("Warehouse"))
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        verbose_name = _("Product Warehouse Stock")
        verbose_name_plural = _("Product Warehouse Stocks")
        unique_together = ['product', 'warehouse']
        ordering = ['product', 'warehouse']
    
    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name}: {self.quantity}"


# ==================== INVENTORY TRANSFER ====================
class InventoryTransfer(TimeStampedModel):
    """Inventory Transfer between Warehouses - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('in_transit', _('In Transit')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    transfer_number = models.CharField(_("Transfer Number"), max_length=50, unique=True, editable=False)
    transfer_date = models.DateField(_("Transfer Date"), default=timezone.now)
    
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_out', verbose_name=_("From Warehouse"))
    to_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='transfers_in', verbose_name=_("To Warehouse"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Transfer Details
    transferred_by = models.CharField(_("Transferred By"), max_length=100, blank=True)
    received_by = models.CharField(_("Received By"), max_length=100, blank=True)
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Inventory Transfer")
        verbose_name_plural = _("Inventory Transfers")
        ordering = ['-transfer_date', '-created_at']
    
    def __str__(self):
        return f"{self.transfer_number} - {self.from_warehouse.name} → {self.to_warehouse.name}"
    
    def save(self, *args, **kwargs):
        if not self.transfer_number:
            last_transfer = InventoryTransfer.objects.order_by('-id').first()
            if last_transfer:
                last_num = int(last_transfer.transfer_number.split('-')[-1])
                self.transfer_number = f"IT-{last_num + 1:06d}"
            else:
                self.transfer_number = "IT-000001"
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate transfer"""
        from django.core.exceptions import ValidationError
        
        if self.from_warehouse == self.to_warehouse:
            raise ValidationError({
                'to_warehouse': 'Cannot transfer to the same warehouse.'
            })


class InventoryTransferItem(TimeStampedModel):
    """Inventory Transfer Item - Line Item"""
    inventory_transfer = models.ForeignKey(InventoryTransfer, on_delete=models.CASCADE, related_name='items', verbose_name=_("Inventory Transfer"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=_("Product"))
    
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], default=Decimal('1.00'))
    unit_price = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    line_total = models.DecimalField(_("Line Total"), max_digits=12, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    class Meta:
        verbose_name = _("Inventory Transfer Item")
        verbose_name_plural = _("Inventory Transfer Items")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.inventory_transfer.transfer_number} - {self.product.name}"
    
    @property
    def available_stock(self):
        """Get available stock in source warehouse"""
        return self.product.get_warehouse_stock(self.inventory_transfer.from_warehouse)
    
    def clean(self):
        """Validate transfer quantity"""
        from django.core.exceptions import ValidationError
        
        # Check if quantity exceeds available stock in source warehouse
        available = self.available_stock
        if self.quantity > available:
            raise ValidationError({
                'quantity': f'Cannot transfer {self.quantity}. Only {available} available in {self.inventory_transfer.from_warehouse.name}.'
            })
    
    def save(self, *args, **kwargs):
        # Auto-set unit price from product if not set
        if self.unit_price == Decimal('0.00'):
            self.unit_price = self.product.purchase_price
        
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ==================== STOCK TRANSACTION ====================
class StockTransaction(TimeStampedModel):
    """Stock Movement Tracking"""
    TRANSACTION_TYPES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
        ('adjustment', _('Adjustment')),
        ('transfer_out', _('Transfer Out')),
        ('transfer_in', _('Transfer In')),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Product"))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='transactions', verbose_name=_("Warehouse"))
    transaction_type = models.CharField(_("Transaction Type"), max_length=20, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(_("Quantity"), max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(_("Balance After"), max_digits=10, decimal_places=2, default=Decimal('0.00'))
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Stock Transaction")
        verbose_name_plural = _("Stock Transactions")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name} - {self.get_transaction_type_display()} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Set warehouse to product's default warehouse if not set
        if not self.warehouse_id:
            if self.product.default_warehouse:
                self.warehouse = self.product.default_warehouse
            else:
                # Fallback to first active warehouse
                first_warehouse = Warehouse.objects.filter(is_active=True).first()
                if first_warehouse:
                    self.warehouse = first_warehouse
        super().save(*args, **kwargs)


# ==================== BANKING MODULE ====================

class BankAccount(TimeStampedModel):
    """Bank Account Master"""
    ACCOUNT_TYPE_CHOICES = [
        ('checking', _('Checking Account')),
        ('savings', _('Savings Account')),
        ('credit', _('Credit Card')),
        ('cash', _('Cash Account')),
    ]
    
    account_name = models.CharField(_("Account Name"), max_length=200)
    account_number = models.CharField(_("Account Number"), max_length=50, unique=True)
    account_type = models.CharField(_("Account Type"), max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='checking')
    bank_name = models.CharField(_("Bank Name"), max_length=200, blank=True)
    branch = models.CharField(_("Branch"), max_length=200, blank=True)
    currency = models.CharField(_("Currency"), max_length=10, default='USD')
    
    opening_balance = models.DecimalField(_("Opening Balance"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    current_balance = models.DecimalField(_("Current Balance"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    is_active = models.BooleanField(_("Active"), default=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Bank Account")
        verbose_name_plural = _("Bank Accounts")
        ordering = ['account_name']
    
    def __str__(self):
        return f"{self.account_name} ({self.account_number})"
    
    def save(self, *args, **kwargs):
        # Set current balance to opening balance on first save
        if not self.pk and self.current_balance == Decimal('0.00'):
            self.current_balance = self.opening_balance
        super().save(*args, **kwargs)


class IncomingPayment(TimeStampedModel):
    """Incoming Payment (Money In) - Header/Info"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('online', _('Online Payment')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('received', _('Received')),
        ('cleared', _('Cleared')),
        ('cancelled', _('Cancelled')),
    ]
    
    payment_number = models.CharField(_("Payment Number"), max_length=50, unique=True, editable=False)
    payment_date = models.DateField(_("Payment Date"), default=timezone.now)
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='incoming_payments', verbose_name=_("Customer"))
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='incoming_payments', verbose_name=_("Bank Account"))
    
    payment_method = models.CharField(_("Payment Method"), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Payment Details
    amount = models.DecimalField(_("Amount"), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    check_number = models.CharField(_("Check Number"), max_length=50, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Incoming Payment")
        verbose_name_plural = _("Incoming Payments")
        ordering = ['-payment_date', '-created_at']
    
    def __str__(self):
        return f"{self.payment_number} - {self.customer.name} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            last_payment = IncomingPayment.objects.order_by('-id').first()
            if last_payment:
                last_num = int(last_payment.payment_number.split('-')[-1])
                self.payment_number = f"IP-{last_num + 1:06d}"
            else:
                self.payment_number = "IP-000001"
        super().save(*args, **kwargs)


class IncomingPaymentInvoice(TimeStampedModel):
    """Incoming Payment Invoice Allocation - Line Item"""
    incoming_payment = models.ForeignKey(IncomingPayment, on_delete=models.CASCADE, related_name='invoices', verbose_name=_("Incoming Payment"))
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name='incoming_payments', verbose_name=_("Invoice"))
    
    amount_allocated = models.DecimalField(_("Amount Allocated"), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        verbose_name = _("Incoming Payment Invoice")
        verbose_name_plural = _("Incoming Payment Invoices")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.incoming_payment.payment_number} - {self.invoice.invoice_number} - {self.amount_allocated}"
    
    def clean(self):
        """Validate allocation amount"""
        from django.core.exceptions import ValidationError
        
        if self.amount_allocated > self.invoice.due_amount:
            raise ValidationError({
                'amount_allocated': f'Cannot allocate {self.amount_allocated}. Invoice due amount is {self.invoice.due_amount}.'
            })


class OutgoingPayment(TimeStampedModel):
    """Outgoing Payment (Money Out) - Header/Info"""
    PAYMENT_METHOD_CHOICES = [
        ('cash', _('Cash')),
        ('check', _('Check')),
        ('bank_transfer', _('Bank Transfer')),
        ('credit_card', _('Credit Card')),
        ('online', _('Online Payment')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('cleared', _('Cleared')),
        ('cancelled', _('Cancelled')),
    ]
    
    payment_number = models.CharField(_("Payment Number"), max_length=50, unique=True, editable=False)
    payment_date = models.DateField(_("Payment Date"), default=timezone.now)
    
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='outgoing_payments', verbose_name=_("Supplier"))
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name='outgoing_payments', verbose_name=_("Bank Account"))
    
    payment_method = models.CharField(_("Payment Method"), max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Payment Details
    amount = models.DecimalField(_("Amount"), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    check_number = models.CharField(_("Check Number"), max_length=50, blank=True)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Outgoing Payment")
        verbose_name_plural = _("Outgoing Payments")
        ordering = ['-payment_date', '-created_at']
    
    def __str__(self):
        return f"{self.payment_number} - {self.supplier.name} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.payment_number:
            last_payment = OutgoingPayment.objects.order_by('-id').first()
            if last_payment:
                last_num = int(last_payment.payment_number.split('-')[-1])
                self.payment_number = f"OP-{last_num + 1:06d}"
            else:
                self.payment_number = "OP-000001"
        super().save(*args, **kwargs)


class OutgoingPaymentInvoice(TimeStampedModel):
    """Outgoing Payment Invoice Allocation - Line Item"""
    outgoing_payment = models.ForeignKey(OutgoingPayment, on_delete=models.CASCADE, related_name='invoices', verbose_name=_("Outgoing Payment"))
    purchase_invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.PROTECT, related_name='outgoing_payments', verbose_name=_("Purchase Invoice"))
    
    amount_allocated = models.DecimalField(_("Amount Allocated"), max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        verbose_name = _("Outgoing Payment Invoice")
        verbose_name_plural = _("Outgoing Payment Invoices")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.outgoing_payment.payment_number} - {self.purchase_invoice.invoice_number} - {self.amount_allocated}"
    
    def clean(self):
        """Validate allocation amount"""
        from django.core.exceptions import ValidationError
        
        if self.amount_allocated > self.purchase_invoice.due_amount:
            raise ValidationError({
                'amount_allocated': f'Cannot allocate {self.amount_allocated}. Invoice due amount is {self.purchase_invoice.due_amount}.'
            })


# ==================== ACCOUNTING/FINANCE MODULE ====================

class AccountType(TimeStampedModel):
    """Account Type Classification"""
    TYPE_CHOICES = [
        ('asset', _('Asset')),
        ('liability', _('Liability')),
        ('equity', _('Equity')),
        ('revenue', _('Revenue')),
        ('expense', _('Expense')),
    ]
    
    name = models.CharField(_("Type Name"), max_length=100, unique=True)
    type_category = models.CharField(_("Category"), max_length=20, choices=TYPE_CHOICES)
    is_active = models.BooleanField(_("Active"), default=True)
    
    class Meta:
        verbose_name = _("Account Type")
        verbose_name_plural = _("Account Types")
        ordering = ['type_category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_category_display()})"


class ChartOfAccounts(TimeStampedModel):
    """Chart of Accounts - GL Accounts"""
    account_code = models.CharField(_("Account Code"), max_length=20, unique=True)
    account_name = models.CharField(_("Account Name"), max_length=200)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts', verbose_name=_("Account Type"))
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_accounts', verbose_name=_("Parent Account"))
    
    currency = models.CharField(_("Currency"), max_length=10, default='USD')
    opening_balance = models.DecimalField(_("Opening Balance"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    current_balance = models.DecimalField(_("Current Balance"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Chart of Account")
        verbose_name_plural = _("Chart of Accounts")
        ordering = ['account_code']
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    def save(self, *args, **kwargs):
        if not self.pk and self.current_balance == Decimal('0.00'):
            self.current_balance = self.opening_balance
        super().save(*args, **kwargs)


class CostCenter(TimeStampedModel):
    """Cost Center for expense tracking"""
    code = models.CharField(_("Cost Center Code"), max_length=20, unique=True)
    name = models.CharField(_("Cost Center Name"), max_length=200)
    parent_cost_center = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_cost_centers', verbose_name=_("Parent Cost Center"))
    
    manager = models.CharField(_("Manager"), max_length=100, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Cost Center")
        verbose_name_plural = _("Cost Centers")
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Project(TimeStampedModel):
    """Project for tracking revenues and expenses"""
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    project_code = models.CharField(_("Project Code"), max_length=20, unique=True)
    project_name = models.CharField(_("Project Name"), max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects', verbose_name=_("Customer"))
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField(_("Start Date"), null=True, blank=True)
    end_date = models.DateField(_("End Date"), null=True, blank=True)
    
    project_manager = models.CharField(_("Project Manager"), max_length=100, blank=True)
    budget_amount = models.DecimalField(_("Budget Amount"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    actual_cost = models.DecimalField(_("Actual Cost"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    is_active = models.BooleanField(_("Active"), default=True)
    description = models.TextField(_("Description"), blank=True)
    
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.project_code} - {self.project_name}"
    
    @property
    def budget_variance(self):
        """Calculate budget variance"""
        return self.budget_amount - self.actual_cost
    
    @property
    def budget_utilization_percentage(self):
        """Calculate budget utilization percentage"""
        if self.budget_amount > 0:
            return (self.actual_cost / self.budget_amount) * 100
        return Decimal('0.00')


class JournalEntry(TimeStampedModel):
    """Journal Entry - Header/Info"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('posted', _('Posted')),
        ('cancelled', _('Cancelled')),
    ]
    
    entry_number = models.CharField(_("Entry Number"), max_length=50, unique=True, editable=False)
    entry_date = models.DateField(_("Entry Date"), default=timezone.now)
    posting_date = models.DateField(_("Posting Date"), null=True, blank=True)
    
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default='draft')
    reference = models.CharField(_("Reference"), max_length=100, blank=True)
    
    # Optional links
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name=_("Project"))
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries', verbose_name=_("Cost Center"))
    
    # Totals
    total_debit = models.DecimalField(_("Total Debit"), max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False)
    total_credit = models.DecimalField(_("Total Credit"), max_digits=15, decimal_places=2, default=Decimal('0.00'), editable=False)
    
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")
        ordering = ['-entry_date', '-created_at']
    
    def __str__(self):
        return f"{self.entry_number} - {self.entry_date}"
    
    def save(self, *args, **kwargs):
        if not self.entry_number:
            last_entry = JournalEntry.objects.order_by('-id').first()
            if last_entry:
                last_num = int(last_entry.entry_number.split('-')[-1])
                self.entry_number = f"JE-{last_num + 1:06d}"
            else:
                self.entry_number = "JE-000001"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate total debit and credit"""
        lines = self.lines.all()
        self.total_debit = sum(line.debit for line in lines)
        self.total_credit = sum(line.credit for line in lines)
        self.save(update_fields=['total_debit', 'total_credit'])
    
    @property
    def is_balanced(self):
        """Check if entry is balanced"""
        return self.total_debit == self.total_credit
    
    def clean(self):
        """Validate journal entry"""
        from django.core.exceptions import ValidationError
        
        if self.status == 'posted':
            if not self.is_balanced:
                raise ValidationError('Journal entry must be balanced (Debit = Credit) before posting.')


class JournalEntryLine(TimeStampedModel):
    """Journal Entry Line - Line Item"""
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines', verbose_name=_("Journal Entry"))
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='journal_lines', verbose_name=_("Account"))
    
    description = models.CharField(_("Description"), max_length=200, blank=True)
    debit = models.DecimalField(_("Debit"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    credit = models.DecimalField(_("Credit"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Optional dimensions
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_lines', verbose_name=_("Project"))
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_lines', verbose_name=_("Cost Center"))
    
    class Meta:
        verbose_name = _("Journal Entry Line")
        verbose_name_plural = _("Journal Entry Lines")
        ordering = ['id']
    
    def __str__(self):
        return f"{self.journal_entry.entry_number} - {self.account.account_code}"
    
    def clean(self):
        """Validate journal line"""
        from django.core.exceptions import ValidationError
        
        if self.debit > 0 and self.credit > 0:
            raise ValidationError('A line cannot have both debit and credit amounts.')
        
        if self.debit == 0 and self.credit == 0:
            raise ValidationError('A line must have either debit or credit amount.')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update parent totals
        self.journal_entry.calculate_totals()


class FiscalYear(TimeStampedModel):
    """Fiscal Year"""
    year_name = models.CharField(_("Year Name"), max_length=50, unique=True)
    start_date = models.DateField(_("Start Date"))
    end_date = models.DateField(_("End Date"))
    is_closed = models.BooleanField(_("Closed"), default=False)
    
    class Meta:
        verbose_name = _("Fiscal Year")
        verbose_name_plural = _("Fiscal Years")
        ordering = ['-start_date']
    
    def __str__(self):
        return self.year_name
    
    def clean(self):
        """Validate fiscal year"""
        from django.core.exceptions import ValidationError
        
        if self.start_date >= self.end_date:
            raise ValidationError('End date must be after start date.')


class Budget(TimeStampedModel):
    """Budget Planning"""
    budget_name = models.CharField(_("Budget Name"), max_length=200)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.PROTECT, related_name='budgets', verbose_name=_("Fiscal Year"))
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT, related_name='budgets', verbose_name=_("Account"))
    
    # Optional dimensions
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='budgets', verbose_name=_("Project"))
    cost_center = models.ForeignKey(CostCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name='budgets', verbose_name=_("Cost Center"))
    
    budget_amount = models.DecimalField(_("Budget Amount"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    actual_amount = models.DecimalField(_("Actual Amount"), max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    is_active = models.BooleanField(_("Active"), default=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        verbose_name = _("Budget")
        verbose_name_plural = _("Budgets")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.budget_name} - {self.account.account_code}"
    
    @property
    def variance(self):
        """Calculate budget variance"""
        return self.budget_amount - self.actual_amount
    
    @property
    def utilization_percentage(self):
        """Calculate budget utilization percentage"""
        if self.budget_amount > 0:
            return (self.actual_amount / self.budget_amount) * 100
        return Decimal('0.00')
