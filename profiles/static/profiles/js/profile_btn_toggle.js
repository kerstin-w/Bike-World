$(document).ready(function () {
    // Select the collapse buttons
    let collapseButtons = $('button[data-bs-toggle="collapse"]');

    // Select all the collapse containers
    let collapseContainers = $('.collapse');

    // Add a click event listener to each button
    collapseButtons.on('click', function () {
        const targetId = $(this).data('bs-target');
        const container = $(targetId).get(0);
        const isOpen = $(targetId).hasClass('show');

        // Hide all the collapse containers except the one that was clicked on
        collapseContainers.not(targetId).removeClass('show');

        if (!isOpen) {
            scrollToContent(container);
        } else {
            // If the collapsible is already open, scroll to the top of the container
            scrollToTop(container);
        }
    });

    function scrollToContent(container) {
        // Scroll to the container using the scrollIntoView method
        container.scrollIntoView({
            behavior: 'smooth'
        });
    }

    function scrollToTop(container) {
        // Scroll to the top of the container
        container.scrollTop = 0;
    }
    // Check if the collapseWishlist parameter is present in the URL
    const urlParams = new URLSearchParams(window.location.search);
    const collapseWishlist = urlParams.get('collapseWishlist');
    if (collapseWishlist === 'true') {
        // Open the wishlist collapsible
        $('#collapseWishlist').addClass('show');
    }
});