"""
URL configuration for erp app
"""
from django.urls import path
from .views import (
    DashboardView, SalesReportView, PurchaseReportView, StockReportView,
    PrintSalesOrderView, get_product_price, get_sales_order_details, get_purchase_order_details,
    get_sales_quotation_details, get_purchase_quotation_details,
    # Copy/Create views
    copy_sales_quotation_to_order_view, copy_sales_order_to_delivery_view,
    copy_sales_order_to_invoice_view, copy_sales_order_to_return_view,
    copy_purchase_quotation_to_order_view, copy_purchase_order_to_receipt_view,
    copy_purchase_order_to_invoice_view, copy_purchase_order_to_return_view,
    copy_bom_to_production_order_view, copy_production_order_to_receipt_view
)

app_name = 'erp'

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('reports/purchases/', PurchaseReportView.as_view(), name='purchase-report'),
    path('reports/stock/', StockReportView.as_view(), name='stock-report'),
    path('sales-order/<int:order_id>/print/', PrintSalesOrderView.as_view(), name='print-sales-order'),
    
    # API Endpoints
    path('api/product/<int:product_id>/price/', get_product_price, name='get-product-price'),
    path('api/sales-order/<int:sales_order_id>/details/', get_sales_order_details, name='get-sales-order-details'),
    path('api/purchase-order/<int:purchase_order_id>/details/', get_purchase_order_details, name='get-purchase-order-details'),
    path('api/sales-quotation/<int:sales_quotation_id>/details/', get_sales_quotation_details, name='get-sales-quotation-details'),
    path('api/purchase-quotation/<int:purchase_quotation_id>/details/', get_purchase_quotation_details, name='get-purchase-quotation-details'),
    
    # Copy/Create Actions - Sales Module
    path('sales-quotation/<int:quotation_id>/create-order/', copy_sales_quotation_to_order_view, name='copy-sales-quotation-to-order'),
    path('sales-order/<int:order_id>/create-delivery/', copy_sales_order_to_delivery_view, name='copy-sales-order-to-delivery'),
    path('sales-order/<int:order_id>/create-invoice/', copy_sales_order_to_invoice_view, name='copy-sales-order-to-invoice'),
    path('sales-order/<int:order_id>/create-return/', copy_sales_order_to_return_view, name='copy-sales-order-to-return'),
    
    # Copy/Create Actions - Purchase Module
    path('purchase-quotation/<int:quotation_id>/create-order/', copy_purchase_quotation_to_order_view, name='copy-purchase-quotation-to-order'),
    path('purchase-order/<int:order_id>/create-receipt/', copy_purchase_order_to_receipt_view, name='copy-purchase-order-to-receipt'),
    path('purchase-order/<int:order_id>/create-invoice/', copy_purchase_order_to_invoice_view, name='copy-purchase-order-to-invoice'),
    path('purchase-order/<int:order_id>/create-return/', copy_purchase_order_to_return_view, name='copy-purchase-order-to-return'),
    
    # Copy/Create Actions - Production Module
    path('bom/<int:bom_id>/create-production-order/', copy_bom_to_production_order_view, name='copy-bom-to-production-order'),
    path('production-order/<int:order_id>/create-receipt/', copy_production_order_to_receipt_view, name='copy-production-order-to-receipt'),
]
