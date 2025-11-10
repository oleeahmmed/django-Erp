"""
API Views - JSON endpoints for AJAX requests
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

from ..models import Product, SalesOrder, PurchaseOrder, SalesQuotation, PurchaseQuotation


@require_http_methods(["GET"])
@staff_member_required
def get_product_price(request, product_id):
    """API endpoint to get product selling price"""
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'success': True,
            'product_id': product.id,
            'product_name': product.name,
            'selling_price': str(product.selling_price),
            'purchase_price': str(product.purchase_price),
            'unit': product.unit,
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)


@require_http_methods(["GET"])
@staff_member_required
def get_sales_order_details(request, sales_order_id):
    """API endpoint to get sales order details for auto-filling"""
    try:
        sales_order = SalesOrder.objects.select_related('customer', 'salesperson').get(id=sales_order_id)
        return JsonResponse({
            'success': True,
            'sales_order_id': sales_order.id,
            'order_number': sales_order.order_number,
            'customer_id': sales_order.customer.id,
            'customer_name': sales_order.customer.name,
            'salesperson_id': sales_order.salesperson.id if sales_order.salesperson else None,
            'salesperson_name': sales_order.salesperson.name if sales_order.salesperson else None,
        })
    except SalesOrder.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Sales Order not found'
        }, status=404)


@require_http_methods(["GET"])
@staff_member_required
def get_purchase_order_details(request, purchase_order_id):
    """API endpoint to get purchase order details for auto-filling"""
    try:
        purchase_order = PurchaseOrder.objects.select_related('supplier').get(id=purchase_order_id)
        return JsonResponse({
            'success': True,
            'purchase_order_id': purchase_order.id,
            'order_number': purchase_order.order_number,
            'supplier_id': purchase_order.supplier.id,
            'supplier_name': purchase_order.supplier.name,
        })
    except PurchaseOrder.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Purchase Order not found'
        }, status=404)


@require_http_methods(["GET"])
@staff_member_required
def get_sales_quotation_details(request, sales_quotation_id):
    """API endpoint to get sales quotation details for auto-filling"""
    try:
        sales_quotation = SalesQuotation.objects.select_related('customer', 'salesperson').get(id=sales_quotation_id)
        return JsonResponse({
            'success': True,
            'sales_quotation_id': sales_quotation.id,
            'quotation_number': sales_quotation.quotation_number,
            'customer_id': sales_quotation.customer.id,
            'customer_name': sales_quotation.customer.name,
            'salesperson_id': sales_quotation.salesperson.id if sales_quotation.salesperson else None,
            'salesperson_name': sales_quotation.salesperson.name if sales_quotation.salesperson else None,
        })
    except:
        return JsonResponse({
            'success': False,
            'error': 'Sales Quotation not found'
        }, status=404)


@require_http_methods(["GET"])
@staff_member_required
def get_purchase_quotation_details(request, purchase_quotation_id):
    """API endpoint to get purchase quotation details for auto-filling"""
    try:
        purchase_quotation = PurchaseQuotation.objects.select_related('supplier').get(id=purchase_quotation_id)
        return JsonResponse({
            'success': True,
            'purchase_quotation_id': purchase_quotation.id,
            'quotation_number': purchase_quotation.quotation_number,
            'supplier_id': purchase_quotation.supplier.id,
            'supplier_name': purchase_quotation.supplier.name,
        })
    except:
        return JsonResponse({
            'success': False,
            'error': 'Purchase Quotation not found'
        }, status=404)
