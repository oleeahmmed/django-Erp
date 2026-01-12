"""
Report Views - Sales, Purchase, and Stock Reports
"""
from django.contrib import admin
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F, Count, Q
from django.http import HttpResponse
from decimal import Decimal
from datetime import datetime

from ..models import (
    SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,
    Product, Customer, Supplier, Category, SalesPerson
)


class SalesReportView(View):
    """Enhanced Sales Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Get filter parameters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        salesperson_id = request.GET.get('salesperson')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        # Base queryset - get sales order items for detailed reporting
        order_items = SalesOrderItem.objects.select_related(
            'sales_order', 'sales_order__customer', 'sales_order__salesperson', 'product'
        ).order_by('-sales_order__order_date', '-sales_order__order_number')
        
        # Apply filters
        if from_date:
            order_items = order_items.filter(sales_order__order_date__gte=from_date)
        if to_date:
            order_items = order_items.filter(sales_order__order_date__lte=to_date)
        if customer_id:
            order_items = order_items.filter(sales_order__customer_id=customer_id)
        if salesperson_id:
            order_items = order_items.filter(sales_order__salesperson_id=salesperson_id)
        if product_id:
            order_items = order_items.filter(product_id=product_id)
        if status:
            order_items = order_items.filter(sales_order__status=status)
        
        # Excel export
        if export_excel:
            return self.export_to_excel(order_items, request)
        
        # Calculate statistics
        total_items = order_items.count()
        total_revenue = order_items.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        total_quantity = order_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        # Get unique orders count
        unique_orders = order_items.values('sales_order').distinct().count()
        
        # Get filter options
        customers = Customer.objects.filter(is_active=True).order_by('name')
        salespersons = SalesPerson.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Sales Report',
            'subtitle': 'Detailed sales analysis with filters',
            'order_items': order_items[:500],  # Limit for performance
            'total_items': total_items,
            'total_revenue': total_revenue,
            'total_quantity': total_quantity,
            'unique_orders': unique_orders,
            'customers': customers,
            'salespersons': salespersons,
            'products': products,
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'salesperson': salesperson_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/sales_report.html', context)
    
    def export_to_excel(self, order_items, request):
        """Export sales report to Excel"""
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sales Report"
        
        # Header style
        header_fill = PatternFill(start_color="C4D82E", end_color="C4D82E", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Headers
        headers = [
            'Order #', 'Order Date', 'Customer', 'Salesperson',
            'Product', 'Quantity', 'Unit Price', 'Line Total', 'Status'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = border
        
        # Data rows
        for row, item in enumerate(order_items, 2):
            ws.cell(row=row, column=1, value=item.sales_order.order_number).border = border
            ws.cell(row=row, column=2, value=item.sales_order.order_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.sales_order.customer.name).border = border
            ws.cell(row=row, column=4, value=item.sales_order.salesperson.name if item.sales_order.salesperson else 'N/A').border = border
            ws.cell(row=row, column=5, value=item.product.name).border = border
            ws.cell(row=row, column=6, value=float(item.quantity)).border = border
            ws.cell(row=row, column=7, value=float(item.unit_price)).border = border
            ws.cell(row=row, column=8, value=float(item.line_total)).border = border
            ws.cell(row=row, column=9, value=item.sales_order.get_status_display()).border = border
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 30
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 12
        ws.column_dimensions['I'].width = 15
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        wb.save(response)
        return response


class PurchaseReportView(View):
    """Enhanced Purchase Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Get filter parameters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        supplier_id = request.GET.get('supplier')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        # Base queryset - get purchase order items for detailed reporting
        order_items = PurchaseOrderItem.objects.select_related(
            'purchase_order', 'purchase_order__supplier', 'product'
        ).order_by('-purchase_order__order_date', '-purchase_order__order_number')
        
        # Apply filters
        if from_date:
            order_items = order_items.filter(purchase_order__order_date__gte=from_date)
        if to_date:
            order_items = order_items.filter(purchase_order__order_date__lte=to_date)
        if supplier_id:
            order_items = order_items.filter(purchase_order__supplier_id=supplier_id)
        if product_id:
            order_items = order_items.filter(product_id=product_id)
        if status:
            order_items = order_items.filter(purchase_order__status=status)
        
        # Excel export
        if export_excel:
            return self.export_to_excel(order_items, request)
        
        # Calculate statistics
        total_items = order_items.count()
        total_amount = order_items.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        total_quantity = order_items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        
        # Get unique orders count
        unique_orders = order_items.values('purchase_order').distinct().count()
        
        # Get filter options
        suppliers = Supplier.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Purchase Report',
            'subtitle': 'Detailed purchase analysis with filters',
            'order_items': order_items[:500],  # Limit for performance
            'total_items': total_items,
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'unique_orders': unique_orders,
            'suppliers': suppliers,
            'products': products,
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'supplier': supplier_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/purchase_report.html', context)
    
    def export_to_excel(self, order_items, request):
        """Export purchase report to Excel"""
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Purchase Report"
        
        # Header style
        header_fill = PatternFill(start_color="C4D82E", end_color="C4D82E", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Headers
        headers = [
            'Order #', 'Order Date', 'Supplier',
            'Product', 'Quantity', 'Unit Price', 'Line Total', 'Status'
        ]
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = border
        
        # Data rows
        for row, item in enumerate(order_items, 2):
            ws.cell(row=row, column=1, value=item.purchase_order.order_number).border = border
            ws.cell(row=row, column=2, value=item.purchase_order.order_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.purchase_order.supplier.name).border = border
            ws.cell(row=row, column=4, value=item.product.name).border = border
            ws.cell(row=row, column=5, value=float(item.quantity)).border = border
            ws.cell(row=row, column=6, value=float(item.unit_price)).border = border
            ws.cell(row=row, column=7, value=float(item.line_total)).border = border
            ws.cell(row=row, column=8, value=item.purchase_order.get_status_display()).border = border
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 30
        ws.column_dimensions['E'].width = 10
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 15
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=purchase_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        wb.save(response)
        return response


class StockReportView(View):
    """Stock/Inventory Report View"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import ProductWarehouseStock
        
        # Get filter parameters
        category_id = request.GET.get('category')
        stock_status = request.GET.get('stock_status')
        
        # Annotate products with total stock from ProductWarehouseStock
        products = Product.objects.select_related('category').filter(is_active=True).annotate(
            total_stock=Sum('warehouse_stocks__quantity')
        ).order_by('name')
        
        # Apply filters
        if category_id:
            products = products.filter(category_id=category_id)
        
        # Filter by stock status using annotated total_stock
        if stock_status == 'low':
            products = products.filter(
                Q(total_stock__lte=F('min_stock_level')) | Q(total_stock__isnull=True)
            )
        elif stock_status == 'out':
            products = products.filter(Q(total_stock=0) | Q(total_stock__isnull=True))
        elif stock_status == 'in':
            products = products.filter(total_stock__gt=F('min_stock_level'))
        
        # Calculate statistics using annotated queryset
        total_products = products.count()
        
        # Calculate total stock value
        total_stock_value = Decimal('0.00')
        for p in products:
            stock_qty = p.total_stock or Decimal('0.00')
            total_stock_value += stock_qty * p.purchase_price
        
        # Low stock and out of stock counts
        low_stock_count = Product.objects.filter(is_active=True).annotate(
            total_stock=Sum('warehouse_stocks__quantity')
        ).filter(
            Q(total_stock__lte=F('min_stock_level')) | Q(total_stock__isnull=True)
        ).count()
        
        out_of_stock_count = Product.objects.filter(is_active=True).annotate(
            total_stock=Sum('warehouse_stocks__quantity')
        ).filter(
            Q(total_stock=0) | Q(total_stock__isnull=True)
        ).count()
        
        # Get limit from request
        limit = request.GET.get('limit', '100')
        if limit == 'all':
            limited_products = products
            showing_limited = False
        else:
            try:
                limit_int = int(limit)
                limited_products = products[:limit_int]
                showing_limited = total_products > limit_int
            except ValueError:
                limited_products = products[:100]
                showing_limited = total_products > 100
                limit = '100'
        
        categories = Category.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Stock Report',
            'subtitle': 'View and filter inventory records',
            'products': limited_products,
            'categories': categories,
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'showing_limited': showing_limited,
            'current_limit': limit,
            'filters': {
                'category': category_id or '',
                'stock_status': stock_status or '',
            }
        }
        
        return render(request, 'admin/erp/stock_report.html', context)


# ==================== SALES QUOTATION REPORT ====================
class SalesQuotationReportView(View):
    """Sales Quotation Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import SalesQuotation, SalesQuotationItem
        
        # Get filter parameters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        salesperson_id = request.GET.get('salesperson')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        # Base queryset
        items = SalesQuotationItem.objects.select_related(
            'sales_quotation', 'sales_quotation__customer', 'sales_quotation__salesperson', 'product'
        ).order_by('-sales_quotation__quotation_date', '-sales_quotation__quotation_number')
        
        # Apply filters
        if from_date:
            items = items.filter(sales_quotation__quotation_date__gte=from_date)
        if to_date:
            items = items.filter(sales_quotation__quotation_date__lte=to_date)
        if customer_id:
            items = items.filter(sales_quotation__customer_id=customer_id)
        if salesperson_id:
            items = items.filter(sales_quotation__salesperson_id=salesperson_id)
        if product_id:
            items = items.filter(product_id=product_id)
        if status:
            items = items.filter(sales_quotation__status=status)
        
        if export_excel:
            return self.export_to_excel(items, request)
        
        # Statistics
        total_items = items.count()
        total_amount = items.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        total_quantity = items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        unique_quotations = items.values('sales_quotation').distinct().count()
        
        # Filter options
        customers = Customer.objects.filter(is_active=True).order_by('name')
        salespersons = SalesPerson.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Sales Quotation Report',
            'subtitle': 'Detailed sales quotation analysis',
            'items': items[:500],
            'total_items': total_items,
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'unique_count': unique_quotations,
            'customers': customers,
            'salespersons': salespersons,
            'products': products,
            'status_choices': [
                ('draft', 'Draft'), ('sent', 'Sent'), ('accepted', 'Accepted'),
                ('converted', 'Converted'), ('rejected', 'Rejected'), ('expired', 'Expired')
            ],
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'salesperson': salesperson_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/sales_quotation_report.html', context)
    
    def export_to_excel(self, items, request):
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sales Quotation Report"
        
        header_fill = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        headers = ['Quotation #', 'Date', 'Valid Until', 'Customer', 'Salesperson', 'Product', 'Quantity', 'Unit Price', 'Line Total', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
        
        for row, item in enumerate(items, 2):
            ws.cell(row=row, column=1, value=item.sales_quotation.quotation_number).border = border
            ws.cell(row=row, column=2, value=item.sales_quotation.quotation_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.sales_quotation.valid_until.strftime('%Y-%m-%d') if item.sales_quotation.valid_until else '').border = border
            ws.cell(row=row, column=4, value=item.sales_quotation.customer.name).border = border
            ws.cell(row=row, column=5, value=item.sales_quotation.salesperson.name if item.sales_quotation.salesperson else 'N/A').border = border
            ws.cell(row=row, column=6, value=item.product.name).border = border
            ws.cell(row=row, column=7, value=float(item.quantity)).border = border
            ws.cell(row=row, column=8, value=float(item.unit_price)).border = border
            ws.cell(row=row, column=9, value=float(item.line_total)).border = border
            ws.cell(row=row, column=10, value=item.sales_quotation.get_status_display()).border = border
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=sales_quotation_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response


# ==================== DELIVERY REPORT ====================
class DeliveryReportView(View):
    """Delivery Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import Delivery, DeliveryItem
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        items = DeliveryItem.objects.select_related(
            'delivery', 'delivery__customer', 'delivery__sales_order', 'product'
        ).order_by('-delivery__delivery_date', '-delivery__delivery_number')
        
        if from_date:
            items = items.filter(delivery__delivery_date__gte=from_date)
        if to_date:
            items = items.filter(delivery__delivery_date__lte=to_date)
        if customer_id:
            items = items.filter(delivery__customer_id=customer_id)
        if product_id:
            items = items.filter(product_id=product_id)
        if status:
            items = items.filter(delivery__status=status)
        
        if export_excel:
            return self.export_to_excel(items, request)
        
        total_items = items.count()
        total_quantity = items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        unique_deliveries = items.values('delivery').distinct().count()
        
        customers = Customer.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Delivery Report',
            'subtitle': 'Detailed delivery analysis',
            'items': items[:500],
            'total_items': total_items,
            'total_quantity': total_quantity,
            'unique_count': unique_deliveries,
            'customers': customers,
            'products': products,
            'status_choices': [('pending', 'Pending'), ('in_transit', 'In Transit'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')],
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/delivery_report.html', context)
    
    def export_to_excel(self, items, request):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Delivery Report"
        
        header_fill = PatternFill(start_color="10B981", end_color="10B981", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        headers = ['Delivery #', 'Date', 'Sales Order', 'Customer', 'Product', 'Quantity', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
        
        for row, item in enumerate(items, 2):
            ws.cell(row=row, column=1, value=item.delivery.delivery_number).border = border
            ws.cell(row=row, column=2, value=item.delivery.delivery_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.delivery.sales_order.order_number if item.delivery.sales_order else 'N/A').border = border
            ws.cell(row=row, column=4, value=item.delivery.customer.name).border = border
            ws.cell(row=row, column=5, value=item.product.name).border = border
            ws.cell(row=row, column=6, value=float(item.quantity)).border = border
            ws.cell(row=row, column=7, value=item.delivery.get_status_display()).border = border
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=delivery_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response


# ==================== INVOICE REPORT ====================
class InvoiceReportView(View):
    """Invoice Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import Invoice, InvoiceItem
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        items = InvoiceItem.objects.select_related(
            'invoice', 'invoice__customer', 'invoice__sales_order', 'product'
        ).order_by('-invoice__invoice_date', '-invoice__invoice_number')
        
        if from_date:
            items = items.filter(invoice__invoice_date__gte=from_date)
        if to_date:
            items = items.filter(invoice__invoice_date__lte=to_date)
        if customer_id:
            items = items.filter(invoice__customer_id=customer_id)
        if product_id:
            items = items.filter(product_id=product_id)
        if status:
            items = items.filter(invoice__status=status)
        
        if export_excel:
            return self.export_to_excel(items, request)
        
        total_items = items.count()
        total_amount = items.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        total_quantity = items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        unique_invoices = items.values('invoice').distinct().count()
        
        customers = Customer.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Invoice Report',
            'subtitle': 'Detailed invoice analysis',
            'items': items[:500],
            'total_items': total_items,
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'unique_count': unique_invoices,
            'customers': customers,
            'products': products,
            'status_choices': [('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid'), ('partial', 'Partial'), ('overdue', 'Overdue'), ('cancelled', 'Cancelled')],
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/invoice_report.html', context)
    
    def export_to_excel(self, items, request):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Invoice Report"
        
        header_fill = PatternFill(start_color="8B5CF6", end_color="8B5CF6", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        headers = ['Invoice #', 'Date', 'Due Date', 'Customer', 'Product', 'Quantity', 'Unit Price', 'Line Total', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
        
        for row, item in enumerate(items, 2):
            ws.cell(row=row, column=1, value=item.invoice.invoice_number).border = border
            ws.cell(row=row, column=2, value=item.invoice.invoice_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.invoice.due_date.strftime('%Y-%m-%d') if item.invoice.due_date else '').border = border
            ws.cell(row=row, column=4, value=item.invoice.customer.name).border = border
            ws.cell(row=row, column=5, value=item.product.name).border = border
            ws.cell(row=row, column=6, value=float(item.quantity)).border = border
            ws.cell(row=row, column=7, value=float(item.unit_price)).border = border
            ws.cell(row=row, column=8, value=float(item.line_total)).border = border
            ws.cell(row=row, column=9, value=item.invoice.get_status_display()).border = border
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=invoice_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response


# ==================== SALES RETURN REPORT ====================
class SalesReturnReportView(View):
    """Sales Return Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import SalesReturn, SalesReturnItem
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        product_id = request.GET.get('product')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        items = SalesReturnItem.objects.select_related(
            'sales_return', 'sales_return__customer', 'sales_return__delivery', 'product'
        ).order_by('-sales_return__return_date', '-sales_return__return_number')
        
        if from_date:
            items = items.filter(sales_return__return_date__gte=from_date)
        if to_date:
            items = items.filter(sales_return__return_date__lte=to_date)
        if customer_id:
            items = items.filter(sales_return__customer_id=customer_id)
        if product_id:
            items = items.filter(product_id=product_id)
        if status:
            items = items.filter(sales_return__status=status)
        
        if export_excel:
            return self.export_to_excel(items, request)
        
        total_items = items.count()
        total_amount = items.aggregate(total=Sum('line_total'))['total'] or Decimal('0.00')
        total_quantity = items.aggregate(total=Sum('quantity'))['total'] or Decimal('0.00')
        unique_returns = items.values('sales_return').distinct().count()
        
        customers = Customer.objects.filter(is_active=True).order_by('name')
        products = Product.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Sales Return Report',
            'subtitle': 'Detailed sales return analysis',
            'items': items[:500],
            'total_items': total_items,
            'total_amount': total_amount,
            'total_quantity': total_quantity,
            'unique_count': unique_returns,
            'customers': customers,
            'products': products,
            'status_choices': [('pending', 'Pending'), ('approved', 'Approved'), ('completed', 'Completed'), ('rejected', 'Rejected')],
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'product': product_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/sales_return_report.html', context)
    
    def export_to_excel(self, items, request):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sales Return Report"
        
        header_fill = PatternFill(start_color="EF4444", end_color="EF4444", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        headers = ['Return #', 'Date', 'Delivery #', 'Customer', 'Product', 'Quantity', 'Unit Price', 'Line Total', 'Reason', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
        
        for row, item in enumerate(items, 2):
            ws.cell(row=row, column=1, value=item.sales_return.return_number).border = border
            ws.cell(row=row, column=2, value=item.sales_return.return_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=item.sales_return.delivery.delivery_number if item.sales_return.delivery else 'N/A').border = border
            ws.cell(row=row, column=4, value=item.sales_return.customer.name).border = border
            ws.cell(row=row, column=5, value=item.product.name).border = border
            ws.cell(row=row, column=6, value=float(item.quantity)).border = border
            ws.cell(row=row, column=7, value=float(item.unit_price)).border = border
            ws.cell(row=row, column=8, value=float(item.line_total)).border = border
            ws.cell(row=row, column=9, value=item.reason or '').border = border
            ws.cell(row=row, column=10, value=item.sales_return.get_status_display()).border = border
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=sales_return_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response


# ==================== INCOMING PAYMENT REPORT ====================
class IncomingPaymentReportView(View):
    """Incoming Payment Report View with Excel Export"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        from ..models import IncomingPayment
        
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        customer_id = request.GET.get('customer')
        payment_method = request.GET.get('payment_method')
        status = request.GET.get('status')
        export_excel = request.GET.get('export') == 'excel'
        
        payments = IncomingPayment.objects.select_related(
            'customer', 'invoice', 'received_by'
        ).order_by('-payment_date', '-payment_number')
        
        if from_date:
            payments = payments.filter(payment_date__gte=from_date)
        if to_date:
            payments = payments.filter(payment_date__lte=to_date)
        if customer_id:
            payments = payments.filter(customer_id=customer_id)
        if payment_method:
            payments = payments.filter(payment_method=payment_method)
        if status:
            payments = payments.filter(status=status)
        
        if export_excel:
            return self.export_to_excel(payments, request)
        
        total_payments = payments.count()
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        customers = Customer.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Incoming Payment Report',
            'subtitle': 'Detailed incoming payment analysis',
            'payments': payments[:500],
            'total_payments': total_payments,
            'total_amount': total_amount,
            'customers': customers,
            'payment_methods': [('cash', 'Cash'), ('bank_transfer', 'Bank Transfer'), ('check', 'Check'), ('card', 'Card'), ('mobile', 'Mobile Payment')],
            'status_choices': [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'customer': customer_id or '',
                'payment_method': payment_method or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/incoming_payment_report.html', context)
    
    def export_to_excel(self, payments, request):
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Border, Side
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Incoming Payment Report"
        
        header_fill = PatternFill(start_color="059669", end_color="059669", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        
        headers = ['Payment #', 'Date', 'Customer', 'Invoice #', 'Amount', 'Payment Method', 'Reference', 'Received By', 'Status']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = border
        
        for row, payment in enumerate(payments, 2):
            ws.cell(row=row, column=1, value=payment.payment_number).border = border
            ws.cell(row=row, column=2, value=payment.payment_date.strftime('%Y-%m-%d')).border = border
            ws.cell(row=row, column=3, value=payment.customer.name).border = border
            ws.cell(row=row, column=4, value=payment.invoice.invoice_number if payment.invoice else 'N/A').border = border
            ws.cell(row=row, column=5, value=float(payment.amount)).border = border
            ws.cell(row=row, column=6, value=payment.get_payment_method_display()).border = border
            ws.cell(row=row, column=7, value=payment.reference or '').border = border
            ws.cell(row=row, column=8, value=payment.received_by.name if payment.received_by else 'N/A').border = border
            ws.cell(row=row, column=9, value=payment.get_status_display()).border = border
        
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=incoming_payment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        wb.save(response)
        return response
