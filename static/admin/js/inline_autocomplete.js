(function () {
    'use strict';

    // Wait for jQuery to be available
    function initInlineAutocomplete() {
        var $ = django.jQuery || jQuery;
        
        console.log('Inline autocomplete JS loaded');

        // Function to calculate line total
        function calculateLineTotal(row) {
            var quantity = parseFloat(row.find('input[name$="-quantity"]').val()) || 0;
            var unitPrice = parseFloat(row.find('input[name$="-unit_price"]').val()) || 0;
            var lineTotal = quantity * unitPrice;
            row.find('input[name$="-line_total"]').val(lineTotal.toFixed(2));
        }

        // Function to fetch product price via API
        function setProductPrice(productId, row) {
            if (!productId) {
                console.log('No product ID provided');
                return;
            }

            console.log('Fetching price for product ID:', productId);

            $.ajax({
                url: '/erp/api/product/' + productId + '/price/',
                type: 'GET',
                dataType: 'json',
                success: function (data) {
                    console.log('Product price data received:', data);
                    if (data.success && data.selling_price) {
                        // Always set the price from product
                        row.find('input[name$="-unit_price"]').val(parseFloat(data.selling_price).toFixed(2));
                        console.log('Unit price set to:', data.selling_price);
                        calculateLineTotal(row);
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error fetching product price:', status, error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }

        // Handle autocomplete widget change (Select2 style)
        $(document).on('select2:select', '.field-product select', function (e) {
            console.log('Select2 select event triggered');
            var productId = $(this).val();
            var row = $(this).closest('tr');
            if (productId) {
                setProductPrice(productId, row);
            }
        });

        // Handle regular select change
        $(document).on('change', 'select[name$="-product"]', function () {
            console.log('Regular select change event');
            var productId = $(this).val();
            var row = $(this).closest('tr');
            if (productId) {
                setProductPrice(productId, row);
            }
        });

        // Handle Unfold/Django admin autocomplete - hidden input change
        $(document).on('change', '.field-product input[type="hidden"]', function () {
            console.log('Hidden input change event (autocomplete)');
            var productId = $(this).val();
            var row = $(this).closest('tr');
            if (productId) {
                setTimeout(function () {
                    setProductPrice(productId, row);
                }, 200);
            }
        });

        // Handle text input blur (for autocomplete fields)
        $(document).on('blur', '.field-product input[type="text"]', function () {
            console.log('Text input blur event');
            var row = $(this).closest('tr');
            var hiddenInput = row.find('input[name$="-product"][type="hidden"]');
            var productId = hiddenInput.val();
            if (productId) {
                setTimeout(function () {
                    setProductPrice(productId, row);
                }, 100);
            }
        });

        // Handle quantity and unit price changes
        $(document).on('input change', 'input[name$="-quantity"], input[name$="-unit_price"]', function () {
            var row = $(this).closest('tr');
            calculateLineTotal(row);
        });

        // Initialize existing rows on page load
        setTimeout(function () {
            console.log('Initializing existing rows');
            $('.inline-related:not(.empty-form)').each(function () {
                var row = $(this);
                var productSelect = row.find('select[name$="-product"]');
                var productId = productSelect.val();

                if (!productId) {
                    // Try hidden input for autocomplete
                    var hiddenInput = row.find('input[name$="-product"][type="hidden"]');
                    productId = hiddenInput.val();
                }

                var unitPrice = row.find('input[name$="-unit_price"]').val();

                // If product is selected but no unit price, fetch it
                if (productId && (!unitPrice || parseFloat(unitPrice) === 0)) {
                    console.log('Initializing price for existing row with product:', productId);
                    setProductPrice(productId, row);
                }
            });
        }, 500);

        // Watch for dynamically added rows
        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.addedNodes.length) {
                    $(mutation.addedNodes).filter('.inline-related').each(function () {
                        console.log('New row added, setting up event handlers');
                        var row = $(this);
                        calculateLineTotal(row);
                    });
                }
            });
        });

        // Observe all inline formset containers
        $('.inline-group').each(function () {
            observer.observe(this, {childList: true, subtree: true});
        });
    }

    // Initialize when DOM is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initInlineAutocomplete);
    } else if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initInlineAutocomplete);
    } else {
        // Fallback: wait for window load
        window.addEventListener('load', function() {
            setTimeout(initInlineAutocomplete, 100);
        });
    }
})();
