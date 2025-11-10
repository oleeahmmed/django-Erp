(function () {
    'use strict';

    function initSalesAdmin() {
        var $ = django.jQuery || jQuery;

        console.log('Sales Admin JS loaded');

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

        // Function to fetch sales quotation details and auto-fill fields
        function autoFillFromSalesQuotation(salesQuotationId) {
            if (!salesQuotationId) {
                console.log('No sales quotation selected');
                return;
            }

            console.log('Fetching sales quotation details for ID:', salesQuotationId);

            $.ajax({
                url: '/erp/api/sales-quotation/' + salesQuotationId + '/details/',
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    console.log('Sales quotation data received:', data);

                    if (data.success) {
                        // Auto-fill customer
                        if (data.customer_id && data.customer_name) {
                            setAutocompleteField('customer', data.customer_id, data.customer_name);
                        }

                        // Auto-fill salesperson
                        if (data.salesperson_id && data.salesperson_name) {
                            setAutocompleteField('salesperson', data.salesperson_id, data.salesperson_name);
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching sales quotation details:', status, error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }

        // Function to fetch sales order details and auto-fill fields
        function autoFillFromSalesOrder(salesOrderId) {
            if (!salesOrderId) {
                console.log('No sales order selected');
                return;
            }

            console.log('Fetching sales order details for ID:', salesOrderId);

            $.ajax({
                url: '/erp/api/sales-order/' + salesOrderId + '/details/',
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    console.log('Sales order data received:', data);

                    if (data.success) {
                        // Auto-fill customer
                        if (data.customer_id && data.customer_name) {
                            setAutocompleteField('customer', data.customer_id, data.customer_name);
                        }

                        // Auto-fill salesperson
                        if (data.salesperson_id && data.salesperson_name) {
                            setAutocompleteField('salesperson', data.salesperson_id, data.salesperson_name);
                        }
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching sales order details:', status, error);
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

        // Setup watchers for sales quotation
        setupFieldWatcher('sales_quotation', autoFillFromSalesQuotation);

        // Setup watchers for sales order
        setupFieldWatcher('sales_order', autoFillFromSalesOrder);

        // Auto-fill on page load if field is already selected
        setTimeout(function () {
            console.log('Checking for pre-selected fields on page load');

            // Check sales quotation
            var $salesQuotationSelect = $('select#id_sales_quotation');
            var salesQuotationId = $salesQuotationSelect.val();

            if (!salesQuotationId) {
                var $hiddenInput = $('input#id_sales_quotation[type="hidden"]');
                if ($hiddenInput.length) {
                    salesQuotationId = $hiddenInput.val();
                }
            }

            if (salesQuotationId) {
                console.log('Sales quotation already selected on load:', salesQuotationId);
                autoFillFromSalesQuotation(salesQuotationId);
            }

            // Check sales order
            var $salesOrderSelect = $('select#id_sales_order');
            var salesOrderId = $salesOrderSelect.val();

            if (!salesOrderId) {
                var $hiddenInput = $('input#id_sales_order[type="hidden"]');
                if ($hiddenInput.length) {
                    salesOrderId = $hiddenInput.val();
                }
            }

            if (salesOrderId) {
                console.log('Sales order already selected on load:', salesOrderId);
                autoFillFromSalesOrder(salesOrderId);
            }
        }, 500);
    }

    // Initialize when DOM is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initSalesAdmin);
    } else if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initSalesAdmin);
    } else {
        window.addEventListener('load', function () {
            setTimeout(initSalesAdmin, 100);
        });
    }
})();
