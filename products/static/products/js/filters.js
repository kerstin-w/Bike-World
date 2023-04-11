$(document).ready(function () {

    // When the user selects a different sorting option
    $('#sort-by').on('change', function () {
        // Construct new URL with selected sort parameters and redirect the user
        const selectedSort = $(this).val();
        const queryParams = $.extend({}, getCurrentQueryParams(), {
            sort_by: selectedSort
        });
        const url = window.location.pathname + '?' + $.param(queryParams);
        window.location.href = url;
    });


    // Get the current query parameters
    const getCurrentQueryParams = function () {
        const currentQueryParams = window.location.search.substring(1).split('&');
        const queryParams = {};
        for (let i = 0; i < currentQueryParams.length; ++i) {
            const paramParts = currentQueryParams[i].split('=');
            if (paramParts.length === 2) {
                queryParams[paramParts[0]] = decodeURIComponent(paramParts[1].replace(/\+/g, ' '));
            }
        }
        return queryParams;
    }

});