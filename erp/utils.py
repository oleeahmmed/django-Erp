"""
Utility functions for ERP operations
"""
from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

from .models import (
    SalesQuotation, SalesOrder, Delivery, Invoice, SalesReturn, 
    SalesOrderItem, DeliveryItem, InvoiceItem, SalesReturnItem,
    PurchaseQuotation, PurchaseOrder, PurchaseOrderItem,
    GoodsReceipt, GoodsReceiptItem,
    PurchaseInvoice, PurchaseInvoiceItem,
    PurchaseReturn, PurchaseReturnItem,
    BillOfMaterials, ProductionOrder, ProductionOrderComponent
)

logger = logging.getLogger(__name__)


@transaction.atomic
def copy_sales_quotation_to_order(sales_quotation_id):
    """
    Create a sales order from a sales quotation
    Copies all items from the quotation
    Only ONE sales order can be created from a quotation
    """
    try:
        sales_quotation = SalesQuotation.objects.prefetch_related('items__product').get(id=sales_quotation_id)
        
        # Check if order already exists for this quotation
        existing_order = SalesOrder.objects.filter(sales_quotation=sales_quotation).first()
        if existing_order:
            return None, f"Sales Order '{existing_order.order_number}' already exists for this quotation"
        
        # Check if quotation has items
        items = sales_quotation.items.all()
        if not items.exists():
            return None, "Sales Quotation has no items to copy"
        
        # Create sales order
        sales_order = SalesOrder.objects.create(
            sales_quotation=sales_quotation,
            customer=sales_quotation.customer,
            salesperson=sales_quotation.salesperson,
            status='draft',
            job_reference=sales_quotation.job_reference,
            shipping_method=sales_quotation.shipping_method,
            delivery_terms=sales_quotation.delivery_terms,
            payment_terms=sales_quotation.payment_terms,
            discount_amount=sales_quotation.discount_amount,
            tax_amount=sales_quotation.tax_amount,
            tax_rate=sales_quotation.tax_rate,
        )
        
        # Copy items
        items_created = 0
        for sq_item in items:
            try:
                SalesOrderItem.objects.create(
                    sales_order=sales_order,
                    product=sq_item.product,
                    quantity=sq_item.quantity,
                    unit_price=sq_item.unit_price,
                )
                items_created += 1
            except Exception as item_error:
                logger.error(f"Error copying item {sq_item.id}: {str(item_error)}")
                raise
        
        logger.info(f"Copied {items_created} items from quotation {sales_quotation.quotation_number} to order {sales_order.order_number}")
        
        # Update quotation status to converted
        sales_quotation.status = 'converted'
        sales_quotation.save(update_fields=['status'])
        
        # Calculate totals
        sales_order.calculate_totals()
        
        return sales_order, None
    except SalesQuotation.DoesNotExist:
        return None, "Sales Quotation not found"
    except Exception as e:
        logger.error(f"Error in copy_sales_quotation_to_order: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_sales_order_to_delivery(sales_order_id):
    """
    Create a delivery from a sales order
    Copies all items with remaining quantities
    """
    try:
        sales_order = SalesOrder.objects.prefetch_related('items__product').get(id=sales_order_id)
        
        # Check if order has items
        items = sales_order.items.all()
        if not items.exists():
            return None, "Sales Order has no items to copy"
        
        # Create delivery
        delivery = Delivery.objects.create(
            sales_order=sales_order,
            customer=sales_order.customer,
            salesperson=sales_order.salesperson,
            status='pending',
            delivery_address=sales_order.customer.address if sales_order.customer.address else '',
        )
        
        # Copy items with remaining quantities
        items_created = 0
        for so_item in items:
            remaining = so_item.remaining_to_deliver
            if remaining > 0:
                try:
                    DeliveryItem.objects.create(
                        delivery=delivery,
                        product=so_item.product,
                        quantity=remaining,
                        unit_price=so_item.unit_price,
                    )
                    items_created += 1
                except Exception as item_error:
                    logger.error(f"Error copying delivery item {so_item.id}: {str(item_error)}")
                    raise
        
        if items_created == 0:
            return None, "No items with remaining quantities to deliver"
        
        logger.info(f"Copied {items_created} items from order {sales_order.order_number} to delivery {delivery.delivery_number}")
        
        return delivery, None
    except SalesOrder.DoesNotExist:
        return None, "Sales Order not found"
    except Exception as e:
        logger.error(f"Error in copy_sales_order_to_delivery: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_sales_order_to_invoice(sales_order_id):
    """
    Create an invoice from a sales order
    Copies all items with remaining quantities
    """
    try:
        sales_order = SalesOrder.objects.prefetch_related('items__product').get(id=sales_order_id)
        
        # Check if order has items
        items = sales_order.items.all()
        if not items.exists():
            return None, "Sales Order has no items to copy"
        
        # Create invoice
        invoice = Invoice.objects.create(
            sales_order=sales_order,
            customer=sales_order.customer,
            salesperson=sales_order.salesperson,
            invoice_date=sales_order.order_date,
            due_date=sales_order.due_date if sales_order.due_date else sales_order.order_date,
            status='draft',
            discount_amount=sales_order.discount_amount,
            tax_amount=sales_order.tax_amount,
        )
        
        # Copy items with remaining quantities
        items_created = 0
        for so_item in items:
            remaining = so_item.remaining_to_invoice
            if remaining > 0:
                try:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=so_item.product,
                        quantity=remaining,
                        unit_price=so_item.unit_price,
                    )
                    items_created += 1
                except Exception as item_error:
                    logger.error(f"Error copying invoice item {so_item.id}: {str(item_error)}")
                    raise
        
        if items_created == 0:
            return None, "No items with remaining quantities to invoice"
        
        logger.info(f"Copied {items_created} items from order {sales_order.order_number} to invoice {invoice.invoice_number}")
        
        # Calculate totals
        invoice.calculate_totals()
        
        return invoice, None
    except SalesOrder.DoesNotExist:
        return None, "Sales Order not found"
    except Exception as e:
        logger.error(f"Error in copy_sales_order_to_invoice: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_sales_order_to_return(sales_order_id):
    """
    Create a sales return from a sales order
    Copies all items that have been delivered (and not yet returned)
    """
    try:
        sales_order = SalesOrder.objects.prefetch_related('items__product').get(id=sales_order_id)
        
        # Check if order has items
        items = sales_order.items.all()
        if not items.exists():
            return None, "Sales Order has no items to copy"
        
        # Check if any items have been delivered
        has_delivered_items = False
        for so_item in items:
            if so_item.delivered_quantity > 0:
                has_delivered_items = True
                break
        
        if not has_delivered_items:
            return None, "No items have been delivered yet. Please create a Delivery first and mark it as 'Delivered' before creating a return."
        
        # Create sales return
        sales_return = SalesReturn.objects.create(
            sales_order=sales_order,
            customer=sales_order.customer,
            salesperson=sales_order.salesperson,
            status='pending',
        )
        
        # Copy items that have been delivered (and not yet fully returned)
        items_created = 0
        for so_item in items:
            delivered = so_item.delivered_quantity
            returned = so_item.returned_quantity
            available_to_return = delivered - returned
            
            if available_to_return > 0:
                try:
                    SalesReturnItem.objects.create(
                        sales_return=sales_return,
                        product=so_item.product,
                        quantity=available_to_return,
                        unit_price=so_item.unit_price,
                    )
                    items_created += 1
                except Exception as item_error:
                    logger.error(f"Error copying return item {so_item.id}: {str(item_error)}")
                    raise
        
        if items_created == 0:
            # Delete the empty return
            sales_return.delete()
            return None, "All delivered items have already been returned."
        
        logger.info(f"Copied {items_created} items from order {sales_order.order_number} to return {sales_return.return_number}")
        
        # Calculate totals
        sales_return.calculate_totals()
        
        return sales_return, None
    except SalesOrder.DoesNotExist:
        return None, "Sales Order not found"
    except Exception as e:
        logger.error(f"Error in copy_sales_order_to_return: {str(e)}")
        return None, str(e)



# ==================== PURCHASE MODULE UTILITIES ====================

@transaction.atomic
def copy_purchase_quotation_to_order(purchase_quotation_id):
    """
    Create a purchase order from a purchase quotation
    Copies all items from the quotation
    Only ONE purchase order can be created from a quotation
    """
    try:
        purchase_quotation = PurchaseQuotation.objects.prefetch_related('items__product').get(id=purchase_quotation_id)
        
        # Check if order already exists for this quotation
        existing_order = PurchaseOrder.objects.filter(purchase_quotation=purchase_quotation).first()
        if existing_order:
            return None, f"Purchase Order '{existing_order.order_number}' already exists for this quotation"
        
        # Check if quotation has items
        items = purchase_quotation.items.all()
        if not items.exists():
            return None, "Purchase Quotation has no items to copy"
        
        # Create purchase order
        purchase_order = PurchaseOrder.objects.create(
            purchase_quotation=purchase_quotation,
            supplier=purchase_quotation.supplier,
            status='draft',
            discount_amount=purchase_quotation.discount_amount,
            tax_amount=purchase_quotation.tax_amount,
        )
        
        # Copy items
        items_created = 0
        for pq_item in items:
            try:
                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    product=pq_item.product,
                    quantity=pq_item.quantity,
                    unit_price=pq_item.unit_price,
                )
                items_created += 1
            except Exception as item_error:
                logger.error(f"Error copying item {pq_item.id}: {str(item_error)}")
                raise
        
        logger.info(f"Copied {items_created} items from quotation {purchase_quotation.quotation_number} to order {purchase_order.order_number}")
        
        # Update quotation status to converted
        purchase_quotation.status = 'converted'
        purchase_quotation.save(update_fields=['status'])
        
        # Calculate totals
        purchase_order.calculate_totals()
        
        return purchase_order, None
    except PurchaseQuotation.DoesNotExist:
        return None, "Purchase Quotation not found"
    except Exception as e:
        logger.error(f"Error in copy_purchase_quotation_to_order: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_purchase_order_to_receipt(purchase_order_id):
    """
    Create a goods receipt from a purchase order
    Copies all items with remaining quantities
    """
    try:
        purchase_order = PurchaseOrder.objects.prefetch_related('items__product').get(id=purchase_order_id)
        
        # Check if order has items
        items = purchase_order.items.all()
        if not items.exists():
            return None, "Purchase Order has no items to copy"
        
        # Create goods receipt
        goods_receipt = GoodsReceipt.objects.create(
            purchase_order=purchase_order,
            supplier=purchase_order.supplier,
            status='pending',
        )
        
        # Copy items with remaining quantities
        items_created = 0
        for po_item in items:
            remaining = po_item.remaining_to_receive
            if remaining > 0:
                try:
                    GoodsReceiptItem.objects.create(
                        goods_receipt=goods_receipt,
                        product=po_item.product,
                        quantity=remaining,
                        unit_price=po_item.unit_price,
                    )
                    items_created += 1
                except Exception as item_error:
                    logger.error(f"Error copying receipt item {po_item.id}: {str(item_error)}")
                    raise
        
        if items_created == 0:
            return None, "No items with remaining quantities to receive"
        
        logger.info(f"Copied {items_created} items from order {purchase_order.order_number} to receipt {goods_receipt.receipt_number}")
        
        return goods_receipt, None
    except PurchaseOrder.DoesNotExist:
        return None, "Purchase Order not found"
    except Exception as e:
        logger.error(f"Error in copy_purchase_order_to_receipt: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_purchase_order_to_invoice(purchase_order_id):
    """
    Create a purchase invoice from a purchase order
    Copies all items with remaining quantities
    """
    try:
        purchase_order = PurchaseOrder.objects.prefetch_related('items__product').get(id=purchase_order_id)
        
        # Check if order has items
        items = purchase_order.items.all()
        if not items.exists():
            return None, "Purchase Order has no items to copy"
        
        # Create purchase invoice
        purchase_invoice = PurchaseInvoice.objects.create(
            purchase_order=purchase_order,
            supplier=purchase_order.supplier,
            invoice_date=purchase_order.order_date,
            due_date=purchase_order.order_date + timedelta(days=30),
            status='draft',
            discount_amount=purchase_order.discount_amount,
            tax_amount=purchase_order.tax_amount,
        )
        
        # Copy items
        items_created = 0
        for po_item in items:
            try:
                PurchaseInvoiceItem.objects.create(
                    purchase_invoice=purchase_invoice,
                    product=po_item.product,
                    quantity=po_item.quantity,
                    unit_price=po_item.unit_price,
                )
                items_created += 1
            except Exception as item_error:
                logger.error(f"Error copying invoice item {po_item.id}: {str(item_error)}")
                raise
        
        logger.info(f"Copied {items_created} items from order {purchase_order.order_number} to invoice {purchase_invoice.invoice_number}")
        
        # Calculate totals
        purchase_invoice.calculate_totals()
        
        return purchase_invoice, None
    except PurchaseOrder.DoesNotExist:
        return None, "Purchase Order not found"
    except Exception as e:
        logger.error(f"Error in copy_purchase_order_to_invoice: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_purchase_order_to_return(purchase_order_id):
    """
    Create a purchase return from a purchase order
    Copies all items that have been received
    """
    try:
        purchase_order = PurchaseOrder.objects.prefetch_related('items__product').get(id=purchase_order_id)
        
        # Check if order has items
        items = purchase_order.items.all()
        if not items.exists():
            return None, "Purchase Order has no items to copy"
        
        # Create purchase return
        purchase_return = PurchaseReturn.objects.create(
            purchase_order=purchase_order,
            supplier=purchase_order.supplier,
            status='pending',
        )
        
        # Copy items that have been received
        items_created = 0
        for po_item in items:
            received = po_item.received_quantity
            returned = po_item.returned_quantity
            available_to_return = received - returned
            
            if available_to_return > 0:
                try:
                    PurchaseReturnItem.objects.create(
                        purchase_return=purchase_return,
                        product=po_item.product,
                        quantity=available_to_return,
                        unit_price=po_item.unit_price,
                    )
                    items_created += 1
                except Exception as item_error:
                    logger.error(f"Error copying return item {po_item.id}: {str(item_error)}")
                    raise
        
        if items_created == 0:
            return None, "No received items available to return"
        
        logger.info(f"Copied {items_created} items from order {purchase_order.order_number} to return {purchase_return.return_number}")
        
        # Calculate totals
        purchase_return.calculate_totals()
        
        return purchase_return, None
    except PurchaseOrder.DoesNotExist:
        return None, "Purchase Order not found"
    except Exception as e:
        logger.error(f"Error in copy_purchase_order_to_return: {str(e)}")
        return None, str(e)


# ==================== PRODUCTION MODULE UTILITIES ====================

@transaction.atomic
def copy_bom_to_production_order(bom_id, quantity_to_produce=None, warehouse_id=None, sales_order_id=None):
    """
    Create a production order from a BOM
    Copies all components from the BOM
    """
    try:
        from .models import BOMComponent, Warehouse
        
        bom = BillOfMaterials.objects.prefetch_related('components__product').get(id=bom_id)
        
        # Set default quantity if not provided
        if quantity_to_produce is None:
            quantity_to_produce = bom.quantity
        
        # Get default warehouse if not provided
        warehouse = None
        if warehouse_id:
            warehouse = Warehouse.objects.get(id=warehouse_id)
        else:
            warehouse = Warehouse.objects.filter(is_active=True).first()
        
        # Get sales order if provided
        sales_order = None
        if sales_order_id:
            sales_order = SalesOrder.objects.get(id=sales_order_id)
        
        # Create production order
        production_order = ProductionOrder.objects.create(
            bom=bom,
            product=bom.product,
            warehouse=warehouse,
            quantity_to_produce=quantity_to_produce,
            sales_order=sales_order,
            status='draft',
        )
        
        logger.info(f"Created production order {production_order.order_number} from BOM {bom.bom_number}")
        
        # Copy components from BOM
        items_created = 0
        for bom_component in bom.components.all():
            try:
                # Calculate required quantity based on production quantity
                required_qty = bom_component.quantity * quantity_to_produce
                # Add scrap percentage
                if bom_component.scrap_percentage > 0:
                    scrap_factor = Decimal('1.00') + (bom_component.scrap_percentage / Decimal('100.00'))
                    required_qty = required_qty * scrap_factor
                
                ProductionOrderComponent.objects.create(
                    production_order=production_order,
                    product=bom_component.product,
                    quantity_required=required_qty,
                    unit_cost=bom_component.unit_cost,
                )
                items_created += 1
            except Exception as item_error:
                logger.error(f"Error copying BOM component {bom_component.id}: {str(item_error)}")
                raise
        
        if items_created == 0:
            return None, "No components to copy from BOM"
        
        logger.info(f"Copied {items_created} components from BOM {bom.bom_number} to production order {production_order.order_number}")
        
        return production_order, None
    except BillOfMaterials.DoesNotExist:
        return None, "Bill of Materials not found"
    except Exception as e:
        logger.error(f"Error in copy_bom_to_production_order: {str(e)}")
        return None, str(e)


@transaction.atomic
def copy_production_order_to_receipt(production_order_id, quantity_received=None, quantity_rejected=None):
    """
    Create a production receipt from a production order
    Copies material consumption from production order components
    """
    try:
        from .models import ProductionReceipt, ProductionReceiptComponent
        
        production_order = ProductionOrder.objects.prefetch_related('components__product').get(id=production_order_id)
        
        # Set default quantities if not provided
        if quantity_received is None:
            quantity_received = production_order.quantity_to_produce - production_order.quantity_produced
        if quantity_rejected is None:
            quantity_rejected = Decimal('0.00')
        
        # Create production receipt
        production_receipt = ProductionReceipt.objects.create(
            production_order=production_order,
            product=production_order.product,
            warehouse=production_order.warehouse,
            quantity_received=quantity_received,
            quantity_rejected=quantity_rejected,
            status='draft',
        )
        
        logger.info(f"Created production receipt {production_receipt.receipt_number} from production order {production_order.order_number}")
        
        # Copy material consumption from production order components
        items_created = 0
        for po_component in production_order.components.all():
            try:
                # Calculate consumption based on production ratio
                if production_order.quantity_to_produce > 0:
                    production_ratio = (quantity_received + quantity_rejected) / production_order.quantity_to_produce
                    consumed_qty = po_component.quantity_required * production_ratio
                else:
                    consumed_qty = po_component.quantity_required
                
                ProductionReceiptComponent.objects.create(
                    production_receipt=production_receipt,
                    product=po_component.product,
                    quantity_consumed=consumed_qty,
                    unit_cost=po_component.unit_cost,
                )
                items_created += 1
            except Exception as item_error:
                logger.error(f"Error copying production order component {po_component.id}: {str(item_error)}")
                raise
        
        if items_created == 0:
            return None, "No components to copy from production order"
        
        logger.info(f"Copied {items_created} components from production order {production_order.order_number} to receipt {production_receipt.receipt_number}")
        
        return production_receipt, None
    except ProductionOrder.DoesNotExist:
        return None, "Production Order not found"
    except Exception as e:
        logger.error(f"Error in copy_production_order_to_receipt: {str(e)}")
        return None, str(e)
