const dropdownHoverElems = document.querySelectorAll(".dropdown-hover");
const navbar = document.querySelector(".navbar");
const toggleButton = document.querySelector(".navbar-toggler");
const body = document.querySelector("body");

// For each dropdown element, add a click event listener
dropdownHoverElems.forEach(function (dropdownHoverElem) {
    dropdownHoverElem.addEventListener("click", function (event) {

        // Toggle the visibility of the dropdown menu for this element
        const dropdownMenu = this.querySelector(".dropdown-menu");
        dropdownMenu.classList.toggle("show");
    });
});

// Add a click event listener to the toggle button
toggleButton.addEventListener("click", function () {
    // Toggle the "position-absolute" class of the navbar
    if (navbar.classList.contains("position-absolute")) {
        navbar.classList.remove("position-absolute");
    } else {
        navbar.classList.add("position-absolute");
    }
});

// Add a click event listener to the body that closes the category and brand dropdowns when the user clicks outside
body.addEventListener("click", function (event) {
    if (!event.target.closest('.dropdown-hover')) {
        const dropdownMenusFilter = document.querySelectorAll('.dropdown-hover > .dropdown-menu');
        dropdownMenusFilter.forEach(function (dropdownMenusFilter) {
            dropdownMenusFilter.classList.remove('show');
        });
    }
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
document.addEventListener('DOMContentLoaded', () => {
    // Get all the toast elements and create a toast object for each
    const toastElList = Array.from(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(toastEl => new bootstrap.Toast(toastEl));

    // Function to show all toast messages
    const showAllToasts = () => toastList.forEach(toast => toast.show());

    // Function to hide all toast messages
    const hideAllToasts = () => toastList.forEach(toast => toast.hide());

    // Show all toast messages on page load
    showAllToasts();

    // When the user clicks anywhere on the page
    document.addEventListener('click', event => {
        // Hide all toast messages if the clicked element is not in a toast
        if (!toastElList.some(toastEl => toastEl.contains(event.target))) {
            hideAllToasts();
        }
    });
});