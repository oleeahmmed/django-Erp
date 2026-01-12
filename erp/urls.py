"""
URL configuration for erp app
"""
from django.urls import path
from .views import (
    DashboardView, SalesReportView, PurchaseReportView, StockReportView,
    SalesQuotationReportView, DeliveryReportView, InvoiceReportView,
    SalesReturnReportView, IncomingPaymentReportView,
    PrintSalesOrderView, PrintSalesQuotationView, PrintDeliveryView,
    PrintInvoiceView, PrintSalesReturnView, PrintIncomingPaymentView,
    PrintQuickSaleView, StockMovementGuideView,
    # Purchase print views
    PrintPurchaseQuotationView, PrintPurchaseOrderView, PrintGoodsReceiptView,
    PrintGoodsReceiptPOView, PrintPurchaseInvoiceView, PrintPurchaseReturnView,
    PrintOutgoingPaymentView,
    # Manufacturing print views
    PrintBOMView, PrintProductionOrderView, PrintProductionReceiptView,
    get_product_price, get_product_by_sku, get_sales_order_details, get_purchase_order_details,
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
    path('stock-movement-guide/', StockMovementGuideView.as_view(), name='stock-movement-guide'),
    path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
    path('reports/purchases/', PurchaseReportView.as_view(), name='purchase-report'),
    path('reports/stock/', StockReportView.as_view(), name='stock-report'),
    path('reports/sales-quotations/', SalesQuotationReportView.as_view(), name='sales-quotation-report'),
    path('reports/deliveries/', DeliveryReportView.as_view(), name='delivery-report'),
    path('reports/invoices/', InvoiceReportView.as_view(), name='invoice-report'),
    path('reports/sales-returns/', SalesReturnReportView.as_view(), name='sales-return-report'),
    path('reports/incoming-payments/', IncomingPaymentReportView.as_view(), name='incoming-payment-report'),
    
    # Print URLs - Sales
    path('sales-order/<int:order_id>/print/', PrintSalesOrderView.as_view(), name='print-sales-order'),
    path('sales-quotation/<int:quotation_id>/print/', PrintSalesQuotationView.as_view(), name='print-sales-quotation'),
    path('delivery/<int:delivery_id>/print/', PrintDeliveryView.as_view(), name='print-delivery'),
    path('invoice/<int:invoice_id>/print/', PrintInvoiceView.as_view(), name='print-invoice'),
    path('sales-return/<int:return_id>/print/', PrintSalesReturnView.as_view(), name='print-sales-return'),
    path('incoming-payment/<int:payment_id>/print/', PrintIncomingPaymentView.as_view(), name='print-incoming-payment'),
    path('quick-sale/<int:sale_id>/print/', PrintQuickSaleView.as_view(), name='print-quick-sale'),
    
    # Print URLs - Purchase
    path('purchase-quotation/<int:quotation_id>/print/', PrintPurchaseQuotationView.as_view(), name='print-purchase-quotation'),
    path('purchase-order/<int:order_id>/print/', PrintPurchaseOrderView.as_view(), name='print-purchase-order'),
    path('goods-receipt/<int:receipt_id>/print/', PrintGoodsReceiptView.as_view(), name='print-goods-receipt'),
    path('goods-receipt-po/<int:receipt_id>/print/', PrintGoodsReceiptPOView.as_view(), name='print-goods-receipt-po'),
    path('purchase-invoice/<int:invoice_id>/print/', PrintPurchaseInvoiceView.as_view(), name='print-purchase-invoice'),
    path('purchase-return/<int:return_id>/print/', PrintPurchaseReturnView.as_view(), name='print-purchase-return'),
    path('outgoing-payment/<int:payment_id>/print/', PrintOutgoingPaymentView.as_view(), name='print-outgoing-payment'),
    
    # Print URLs - Manufacturing
    path('bom/<int:bom_id>/print/', PrintBOMView.as_view(), name='print-bom'),
    path('production-order/<int:order_id>/print/', PrintProductionOrderView.as_view(), name='print-production-order'),
    path('production-receipt/<int:receipt_id>/print/', PrintProductionReceiptView.as_view(), name='print-production-receipt'),
    
    # API Endpoints
    path('api/product/<int:product_id>/price/', get_product_price, name='get-product-price'),
    path('api/product/by-sku/', get_product_by_sku, name='get-product-by-sku'),
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
