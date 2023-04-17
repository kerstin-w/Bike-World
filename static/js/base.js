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

// Initialize bootstrap tabs
$(function () {
    $('#authTabs a').on('click', function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
});