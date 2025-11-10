(function () {
    'use strict';

    function initSalesOrderAdmin() {
        var $ = django.jQuery || jQuery;
        
        console.log('Sales Order Admin JS loaded');
        
        // Any additional custom functionality for sales orders can go here
        // The inline autocomplete functionality is handled by inline_autocomplete.js
    }

    // Initialize when DOM is ready
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).ready(initSalesOrderAdmin);
    } else if (typeof jQuery !== 'undefined') {
        jQuery(document).ready(initSalesOrderAdmin);
    } else {
        // Fallback: wait for window load
        window.addEventListener('load', function() {
            setTimeout(initSalesOrderAdmin, 100);
        });
    }
})();
