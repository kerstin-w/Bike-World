$(document).ready(function () {
    // Select the collapse buttons
    let collapseInfoBtn = $('#collapseInfoBtn');
    let collapseHistoryBtn = $('#collapseHistoryBtn');
    let collapseWishlistBtn = $('#collapseWishlistBtn');
    let collapseReviewBtn = $('#collapseReviewBtn');

    // Select all the collapse containers
    let collapseContainers = $('.collapse');

    // Add a click event listener to the collapse info button
    collapseInfoBtn.on('click', function () {
        // Hide all the collapse containers except the one that was clicked on
        collapseContainers.not('#collapseInfo').removeClass('show');
    });

    // Add a click event listener to the collapse history button
    collapseHistoryBtn.on('click', function () {
        // Hide all the collapse containers except the one that was clicked on
        collapseContainers.not('#collapseHistory').removeClass('show');
    });

    // Add a click event listener to the collapse wishlist button
    collapseWishlistBtn.on('click', function () {
        // Hide all the collapse containers except the one that was clicked on
        collapseContainers.not('#collapseWishlist').removeClass('show');
    });

    // Add a click event listener to the collapse review button
    collapseReviewBtn.on('click', function () {
        // Hide all the collapse containers except the one that was clicked on
        collapseContainers.not('#collapseReview').removeClass('show');
    });

    // Scroll Into View for collapseables 
    const buttons = $('button[data-bs-toggle="collapse"]');

    // Add a click event listener to each button
    buttons.on('click', function () {
        // Get the ID of the container to scroll to from the data-bs-target of the button
        const targetId = $(this).data('bs-target');
        const container = $(targetId).get(0);

        // Scroll to the container using the scrollIntoView method
        container.scrollIntoView({
            behavior: 'smooth'
        });
    });
});