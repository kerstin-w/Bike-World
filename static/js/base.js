$(document).ready(function () {
    const dropdownHoverElems = $(".dropdown-hover");
    const navbar = $(".navbar");
    const toggleButton = $(".navbar-toggler");
    const body = $("body");

    // For each dropdown element, add a click event listener
    dropdownHoverElems.click(function () {
        // Toggle the visibility of the dropdown menu for this element
        const dropdownMenu = $(this).find(".dropdown-menu");
        dropdownMenu.toggleClass("show");
    });

    // Add a click event listener to the toggle button
    toggleButton.click(function () {
        // Toggle the "position-absolute" class of the navbar
        navbar.toggleClass("position-absolute");
    });

    // Add a click event listener to the body that closes the category and brand dropdowns when the user clicks outside
    body.click(function (event) {
        if (!$(event.target).closest('.dropdown-hover').length) {
            const dropdownMenusFilter = $('.dropdown-hover > .dropdown-menu');
            dropdownMenusFilter.removeClass('show');
        }
    });
});

// Activate the modal tab on click and store the tab ID in session
$('.login-link, .register-link').click(function () {
    var tabId = $(this).data('tab-target');
    $('.nav-tabs a[href="' + tabId + '"]').tab('show');

    sessionStorage.setItem('activeTabId', tabId);
});

// Clear the stored tab ID whenever the modal is closed
$('#auth-modal').on('hide.bs.modal', function () {
    sessionStorage.removeItem('activeTabId');
});

// Toasts
$(document).ready(function () {
    // Get all the toast elements and create a toast object for each
    const toastElList = $('.toast');
    const toastList = toastElList.map((i, toastEl) => new bootstrap.Toast(toastEl));

    // Function to show all toast messages
    const showAllToasts = () => toastList.each((i, toast) => toast.show());

    // Function to hide all toast messages
    const hideAllToasts = () => toastList.each((i, toast) => toast.hide());

    // Show all toast messages on page load
    showAllToasts();

    // When the user clicks anywhere on the page
    $(document).click(function (event) {
        // Hide all toast messages if the clicked element is not in a toast
        if (!toastElList.is(event.target) && !toastElList.has(event.target).length) {
            hideAllToasts();
        }
    });
});