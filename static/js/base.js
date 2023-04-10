const dropdownHoverElems = document.querySelectorAll(".dropdown-hover");
const navbar = document.querySelector(".navbar");
const toggleButton = document.querySelector(".navbar-toggler");

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