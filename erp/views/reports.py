"""
Report Views - Sales, Purchase, and Stock Reports
"""
from django.contrib import admin
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, F
from decimal import Decimal

from ..models import (
    SalesOrder, SalesOrderItem, Invoice, PurchaseOrder, Product, 
    Customer, Supplier, Category, SalesPerson
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
            'Product', 'Quantity', 'Unit Price', 'Discount', 'Tax', 'Line Total', 'Status'
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
            ws.cell(row=row, column=8, value=float(item.discount_amount)).border = border
            ws.cell(row=row, column=9, value=float(item.tax_amount)).border = border
            ws.cell(row=row, column=10, value=float(item.line_total)).border = border
            ws.cell(row=row, column=11, value=item.sales_order.get_status_display()).border = border
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 25
        ws.column_dimensions['D'].width = 20
        ws.column_dimensions['E'].width = 30
        ws.column_dimensions['F'].width = 10
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 10
        ws.column_dimensions['I'].width = 10
        ws.column_dimensions['J'].width = 12
        ws.column_dimensions['K'].width = 15
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=sales_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        wb.save(response)
        return response


class PurchaseReportView(View):
    """Purchase Report View - Shows Purchase Orders"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Get filter parameters
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        supplier_id = request.GET.get('supplier')
        status = request.GET.get('status')
        
        # Default queryset
        purchases = PurchaseOrder.objects.select_related('supplier').prefetch_related('items').order_by('-order_date')
        
        # Apply filters
        if from_date:
            purchases = purchases.filter(order_date__gte=from_date)
        if to_date:
            purchases = purchases.filter(order_date__lte=to_date)
        if supplier_id:
            purchases = purchases.filter(supplier_id=supplier_id)
        if status:
            purchases = purchases.filter(status=status)
        
        # Calculate statistics
        total_purchases = purchases.count()
        total_amount = purchases.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        total_paid = purchases.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0.00')
        total_due = purchases.aggregate(total=Sum('due_amount'))['total'] or Decimal('0.00')
        
        # Status breakdown
        draft_count = purchases.filter(status='draft').count()
        sent_count = purchases.filter(status='sent').count()
        confirmed_count = purchases.filter(status='confirmed').count()
        received_count = purchases.filter(status='received').count()
        completed_count = purchases.filter(status='completed').count()
        
        # Get limit from request
        limit = request.GET.get('limit', '100')
        if limit == 'all':
            limited_purchases = purchases
            showing_limited = False
        else:
            try:
                limit_int = int(limit)
                limited_purchases = purchases[:limit_int]
                showing_limited = total_purchases > limit_int
            except ValueError:
                limited_purchases = purchases[:100]
                showing_limited = total_purchases > 100
                limit = '100'
        
        # Get all suppliers for filter
        suppliers = Supplier.objects.filter(is_active=True).order_by('name')
        
        context = {
            **admin.site.each_context(request),
            'title': 'Purchase Report',
            'subtitle': 'View and filter purchase order records',
            'purchases': limited_purchases,
            'suppliers': suppliers,
            'total_purchases': total_purchases,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'draft_count': draft_count,
            'sent_count': sent_count,
            'confirmed_count': confirmed_count,
            'received_count': received_count,
            'completed_count': completed_count,
            'showing_limited': showing_limited,
            'current_limit': limit,
            'filters': {
                'from_date': from_date or '',
                'to_date': to_date or '',
                'supplier': supplier_id or '',
                'status': status or '',
            }
        }
        
        return render(request, 'admin/erp/purchase_report.html', context)


class StockReportView(View):
    """Stock/Inventory Report View"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        # Get filter parameters
        category_id = request.GET.get('category')
        stock_status = request.GET.get('stock_status')
        
        # Default queryset
        products = Product.objects.select_related('category').filter(is_active=True).order_by('name')
        
        # Apply filters
        if category_id:
            products = products.filter(category_id=category_id)
        
        if stock_status == 'low':
            products = products.filter(current_stock__lte=F('min_stock_level'))
        elif stock_status == 'out':
            products = products.filter(current_stock=0)
        elif stock_status == 'in':
            products = products.filter(current_stock__gt=F('min_stock_level'))
        
        # Calculate statistics
        total_products = products.count()
        total_stock_value = sum(
            float(p.current_stock * p.purchase_price) for p in products
        )
        low_stock_count = Product.objects.filter(
            current_stock__lte=F('min_stock_level'),
            is_active=True
        ).count()
        out_of_stock_count = Product.objects.filter(
            current_stock=0,
            is_active=True
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
