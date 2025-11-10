(function () {
    'use strict';

    function initSalesQuotationAdmin() {
        var $ = django.jQuery || jQuery;

        console.log('Sales Quotation Admin JS loaded');

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

        // Watch for sales quotation selection change (regular select)
        $(document).on('change', 'select#id_sales_quotation', function () {
            var salesQuotationId = $(this).val();
            console.log('Sales quotation changed (select) to:', salesQuotationId);
            if (salesQuotationId) {
                autoFillFromSalesQuotation(salesQuotationId);
            }
        });

        // Watch for sales quotation autocomplete change (Select2)
        $(document).on('select2:select', '#id_sales_quotation', function (e) {
            var salesQuotationId = $(this).val();
            console.log('Sales quotation changed (select2) to:', salesQuotationId);
            if (salesQuotationId) {
                autoFillFromSalesQuotation(salesQuotationId);
            }
        });

        // Watch for sales quotation autocomplete change (hidden input)
        $(document).on('change', 'input#id_sales_quotation[type="hidden"]', function () {
            var salesQuotationId = $(this).val();
            console.log('Sales quotation changed (hidden) to:', salesQuotationId);
            if (salesQuotationId) {
                setTimeout(function () {
                    autoFillFromSalesQuotation(salesQuotationId);
                }, 200);
            }
        });

        // Watch for sales quotation text input blur (for autocomplete)
        $(document).on('blur', 'input[id*="sales_quotation"][type="text"]', function () {
            console.log('Sales quotation text input blur');
            var $hiddenInput = $('input#id_sales_quotation[type="hidden"]');
            if ($hiddenInput.length) {
                var salesQuotationId = $hiddenInput.val();
                if (salesQuotationId) {
                    setTimeout(function () {
                        autoFillFromSalesQuotation(salesQuotationId);
                    }, 100);
                }
            }
        });

        // Auto-fill on page load if sales quotation is already selected
        setTimeout(function () {
            console.log('Checking for pre-selected sales quotation on page load');

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
        }, 500);
    }

    // Initialize when DOM is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initSalesQuotationAdmin);
    } else if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initSalesQuotationAdmin);
    } else {
        window.addEventListener('load', function () {
            setTimeout(initSalesQuotationAdmin, 100);
        });
    }
})();
