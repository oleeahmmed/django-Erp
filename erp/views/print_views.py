"""
Print Views - For printing documents
"""
from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from ..models import SalesOrder, Company


class PrintSalesOrderView(View):
    """Print Sales Order View"""
    
    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, order_id, *args, **kwargs):
        order = SalesOrder.objects.prefetch_related('items__product').select_related('customer').get(id=order_id)
        
        try:
            company = Company.objects.first()
        except:
            company = None
        
        context = {
            'order': order,
            'company': company,
        }
        
        return render(request, 'admin/erp/print_sales_order.html', context)
