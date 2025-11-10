"""
ERP Views Package
"""
from .dashboard import DashboardView
from .reports import SalesReportView, PurchaseReportView, StockReportView
from .print_views import PrintSalesOrderView
from .api_views import (
    get_product_price,
    get_sales_order_details,
    get_purchase_order_details,
    get_sales_quotation_details,
    get_purchase_quotation_details,
)
from .copy_views import (
    copy_sales_quotation_to_order_view,
    copy_sales_order_to_delivery_view,
    copy_sales_order_to_invoice_view,
    copy_sales_order_to_return_view,
    copy_purchase_quotation_to_order_view,
    copy_purchase_order_to_receipt_view,
    copy_purchase_order_to_invoice_view,
    copy_purchase_order_to_return_view,
    copy_bom_to_production_order_view,
    copy_production_order_to_receipt_view,
)

__all__ = [
    'DashboardView',
    'SalesReportView',
    'PurchaseReportView',
    'StockReportView',
    'PrintSalesOrderView',
    'get_product_price',
    'get_sales_order_details',
    'get_purchase_order_details',
    'get_sales_quotation_details',
    'get_purchase_quotation_details',
    'copy_sales_quotation_to_order_view',
    'copy_sales_order_to_delivery_view',
    'copy_sales_order_to_invoice_view',
    'copy_sales_order_to_return_view',
    'copy_purchase_quotation_to_order_view',
    'copy_purchase_order_to_receipt_view',
    'copy_purchase_order_to_invoice_view',
    'copy_purchase_order_to_return_view',
    'copy_bom_to_production_order_view',
    'copy_production_order_to_receipt_view',
]
