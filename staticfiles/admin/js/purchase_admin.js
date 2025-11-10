(function () {
    'use strict';

    function initPurchaseAdmin() {
        var $ = django.jQuery || jQuery;
        
        console.log('Purchase Admin JS loaded');
        
        // Function to set autocomplete field value (for Unfold/Django autocomplete)
        function setAutocompleteField(fieldName, valueId, displayText) {
            var $field = $('#id_' + fieldName);
            
            if ($field.length) {
                console.log('Setting ' + fieldName + ' to:', valueId, displayText);
                
                // Check if it's a select2 field
                if ($field.hasClass('select2-hidden-accessible')) {
                    var newOption = new Option(displayText, valueId, true, true);
                    $field.append(newOption).trigger('change');
                } else if ($field.is('select')) {
                    $field.val(valueId).trigger('change');
                } else {
                    $field.val(valueId);
                    var $textInput = $field.siblings('input[type="text"]');
                    if ($textInput.length) {
                        $textInput.val(displayText);
                    }
                }
            }
        }
        
        // Function to fetch purchase quotation details and auto-fill fields
        function autoFillFromPurchaseQuotation(purchaseQuotationId) {
            if (!purchaseQuotationId) {
                console.log('No purchase quotation selected');
                return;
            }
            
            console.log('Fetching purchase quotation details for ID:', purchaseQuotationId);
            
            $.ajax({
                url: '/erp/api/purchase-quotation/' + purchaseQuotationId + '/details/',
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    console.log('Purchase quotation data received:', data);
                    
                    if (data.success) {
                        // Auto-fill supplier
                        if (data.supplier_id && data.supplier_name) {
                            setAutocompleteField('supplier', data.supplier_id, data.supplier_name);
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching purchase quotation details:', status, error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }
        
        // Function to fetch purchase order details and auto-fill fields
        function autoFillFromPurchaseOrder(purchaseOrderId) {
            if (!purchaseOrderId) {
                console.log('No purchase order selected');
                return;
            }
            
            console.log('Fetching purchase order details for ID:', purchaseOrderId);
            
            $.ajax({
                url: '/erp/api/purchase-order/' + purchaseOrderId + '/details/',
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    console.log('Purchase order data received:', data);
                    
                    if (data.success) {
                        // Auto-fill supplier
                        if (data.supplier_id && data.supplier_name) {
                            setAutocompleteField('supplier', data.supplier_id, data.supplier_name);
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching purchase order details:', status, error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }
        
        // Generic function to handle field changes
        function setupFieldWatcher(fieldName, callback) {
            // Watch for regular select change
            $(document).on('change', 'select#id_' + fieldName, function () {
                var fieldId = $(this).val();
                console.log(fieldName + ' changed (select) to:', fieldId);
                if (fieldId) {
                    callback(fieldId);
                }
            });
            
            // Watch for Select2 change
            $(document).on('select2:select', '#id_' + fieldName, function (e) {
                var fieldId = $(this).val();
                console.log(fieldName + ' changed (select2) to:', fieldId);
                if (fieldId) {
                    callback(fieldId);
                }
            });
            
            // Watch for hidden input change (autocomplete)
            $(document).on('change', 'input#id_' + fieldName + '[type="hidden"]', function () {
                var fieldId = $(this).val();
                console.log(fieldName + ' changed (hidden) to:', fieldId);
                if (fieldId) {
                    setTimeout(function () {
                        callback(fieldId);
                    }, 200);
                }
            });
            
            // Watch for text input blur (autocomplete)
            $(document).on('blur', 'input[id*="' + fieldName + '"][type="text"]', function () {
                console.log(fieldName + ' text input blur');
                var $hiddenInput = $('input#id_' + fieldName + '[type="hidden"]');
                if ($hiddenInput.length) {
                    var fieldId = $hiddenInput.val();
                    if (fieldId) {
                        setTimeout(function () {
                            callback(fieldId);
                        }, 100);
                    }
                }
            });
        }
        
        // Setup watchers for purchase quotation
        setupFieldWatcher('purchase_quotation', autoFillFromPurchaseQuotation);
        
        // Setup watchers for purchase order
        setupFieldWatcher('purchase_order', autoFillFromPurchaseOrder);
        
        // Auto-fill on page load if field is already selected
        setTimeout(function () {
            console.log('Checking for pre-selected fields on page load');
            
            // Check purchase quotation
            var $purchaseQuotationSelect = $('select#id_purchase_quotation');
            var purchaseQuotationId = $purchaseQuotationSelect.val();
            
            if (!purchaseQuotationId) {
                var $hiddenInput = $('input#id_purchase_quotation[type="hidden"]');
                if ($hiddenInput.length) {
                    purchaseQuotationId = $hiddenInput.val();
                }
            }
            
            if (purchaseQuotationId) {
                console.log('Purchase quotation already selected on load:', purchaseQuotationId);
                autoFillFromPurchaseQuotation(purchaseQuotationId);
            }
            
            // Check purchase order
            var $purchaseOrderSelect = $('select#id_purchase_order');
            var purchaseOrderId = $purchaseOrderSelect.val();
            
            if (!purchaseOrderId) {
                var $hiddenInput = $('input#id_purchase_order[type="hidden"]');
                if ($hiddenInput.length) {
                    purchaseOrderId = $hiddenInput.val();
                }
            }
            
            if (purchaseOrderId) {
                console.log('Purchase order already selected on load:', purchaseOrderId);
                autoFillFromPurchaseOrder(purchaseOrderId);
            }
        }, 500);
    }

    // Initialize when DOM is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initPurchaseAdmin);
    } else if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initPurchaseAdmin);
    } else {
        window.addEventListener('load', function() {
            setTimeout(initPurchaseAdmin, 100);
        });
    }
})();
