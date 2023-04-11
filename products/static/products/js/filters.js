$(document).ready(function () {

    // Get the "All" category and brand checkboxes
    const categoryAllCheckbox = $('input[name="category_all"]');
    const brandAllCheckbox = $('input[name="brand_all"]');

    // Get the filter forms and selected filters container elements
    const filterForms = $('form[method="get"]');
    const selectedCategoryFiltersContainer = $('#selected-category-filter');
    const selectedBrandFiltersContainer = $('#selected-brand-filter');

    // When the user selects an option in the brand/category dropdown menus
    $('.dropdown-menu input[type="checkbox"]').change(function () {
        const currentCheckbox = $(this);
        const currentName = currentCheckbox.attr('name');

        // If a checkbox is being checked, uncheck all other checkboxes with the same name
        if (currentCheckbox.prop('checked')) {
            $(`.dropdown-menu input[type="checkbox"][name="${currentName}"]:checked`)
                .not(currentCheckbox)
                .prop('checked', false);
        }

        // Construct new URL with selected sort/filter parameters and redirect the user
        const selectedSort = $('#sort-by').val();
        const selectedCategories = $('input[name="category"]:checked').not(categoryAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');
        const selectedBrands = $('input[name="brand"]:checked').not(brandAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');

        const queryParams = {
            sort_by: selectedSort,
            category: selectedCategories,
            brand: selectedBrands
        };

        const url = window.location.pathname + '?' + $.param(queryParams);
        window.location.href = url;
    });

    // When the user clicks the "All" category checkbox
    categoryAllCheckbox.change(function () {
        const isChecked = $(this).prop('checked');
        $('input[name="category"]:checked').not(categoryAllCheckbox).prop('checked', false);

        // Ensure that the "All" checkbox always remains selected
        if (!isChecked) {
            $(this).prop('checked', true);
        }

        // Construct new URL with selected sort/filter parameters and redirect the user
        const selectedSort = $('#sort-by').val();
        const selectedCategories = $('input[name="category"]:checked').not(categoryAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');
        const selectedBrands = $('input[name="brand"]:checked').not(brandAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');

        const queryParams = {
            sort_by: selectedSort,
            category: selectedCategories,
            brand: selectedBrands
        };

        const url = window.location.pathname + '?' + $.param(queryParams);
        window.location.href = url;
    });

    // When the user clicks the "All" brand checkbox
    brandAllCheckbox.change(function () {
        const isChecked = $(this).prop('checked');
        $('input[name="brand"]:checked').not(brandAllCheckbox).prop('checked', false);

        // Ensure that the "All" checkbox always remains selected
        if (!isChecked) {
            $(this).prop('checked', true);
        }

        // Construct new URL with selected sort/filter parameters and redirect the user
        const selectedSort = $('#sort-by').val();
        const selectedCategories = $('input[name="category"]:checked').not(categoryAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');
        const selectedBrands = $('input[name="brand"]:checked').not(brandAllCheckbox).map(function () {
            return $(this).val();
        }).get().join(',');

        const queryParams = {
            sort_by: selectedSort,
            category: selectedCategories,
            brand: selectedBrands
        };

        const url = window.location.pathname + '?' + $.param(queryParams);
        window.location.href = url;
    });

    // When the user selects a different sorting option
    $('#sort-by').on('change', function () {
        // Construct new URL with selected sort/filter parameters and redirect the user
        const selectedSort = $(this).val();
        const queryParams = $.extend({}, getCurrentQueryParams(), {
            sort_by: selectedSort
        });
        const url = window.location.pathname + '?' + $.param(queryParams);
        window.location.href = url;
    });

    // When the user changes a filter
    filterForms.on('change', function () {
        updateSelectedFilters();
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

    // Update the selected filters containers
    const updateSelectedFilters = function () {
        const queryParams = getCurrentQueryParams();
        const selectedCategories = $('input[name="category"][type="checkbox"]:checked')
            .map(function () {
                if ($(this).val() !== 'all') {
                    return $(this).next().text().trim();
                }
            })
            .get();

        const selectedBrands = $('input[name="brand"][type="checkbox"]:checked')
            .map(function () {
                return $(this).next().text().trim();
            })
            .get();

        const selectedCategoryFilters = [];
        const selectedBrandFilters = [];

        // Add selected parameters to selected filters arrays
        if (selectedCategories.length > 0 && selectedCategories.indexOf('All') === -1) {
            for (const category of selectedCategories) {
                selectedCategoryFilters.push(category);
            }
        }

        if (selectedBrands.length > 0 && selectedBrands.indexOf('All') === -1) {
            for (const brand of selectedBrands) {
                selectedBrandFilters.push(brand);
            }
        }

        // Update filter container elements with selected filters
        if (selectedCategoryFilters.length > 0) {
            selectedCategoryFiltersContainer.html(`<span>${selectedCategoryFilters.join(' | ')}</span> `);
        } else {
            selectedCategoryFiltersContainer.empty();
        }

        if (selectedBrandFilters.length > 0) {
            selectedBrandFiltersContainer.html(`<span>${selectedBrandFilters.join(' | ')}</span>`);
        } else {
            selectedBrandFiltersContainer.empty();
        }
    }

    // Reset all filters and selected sorting option
    const resetFilters = function () {
        $('input[type="checkbox"]').prop('checked', false);
        $('#sort-by').prop('selectedIndex', 0);

        window.location.href = '/products/';
    }

    // Set initial filter states on page load
    const queryParams = getCurrentQueryParams();
    const selectedSort = queryParams.sort_by || '';
    $('#sort-by').val(selectedSort);
    $('input[name="category"][value="all"]').prop('checked', true);
    $('input[name="brand"][value="all"]').prop('checked', true);
    updateSelectedFilters();

    // Connect reset button click event to the resetFilters function
    $('#reset').click(resetFilters);
});