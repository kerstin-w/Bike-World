$(document).ready(function () {
    // Get the wishlist form element using its ID
    const form = $("#add-to-wishlist-form");

    // Check if wishlist form element is present on the DOM
    if (form.length) {
        // Get the URL for adding the item to the wishlist
        const url = form.attr("data-url");
        // Get the wishlist button element inside the form
        const wishlistButton = form.find(".btn-wishlist");
        const errorMessage = $("#wishlist-error-message");

        // Submit Wishlist Form
        form.submit(function (event) {
            // Prevent the form from submitting normally
            event.preventDefault();

            // Send an AJAX request to the server to add the item to the wishlist
            $.ajax({
                url: url,
                type: "POST",
                headers: {
                    // Set the CSRF token in the header to secure the request
                    "X-CSRFToken": getCookie("csrftoken")
                },
                success: function (data) {
                    // If item added to wishlist successfully...
                    if (data.success) {
                        // Update button appearance to show the item is already in wishlist
                        wishlistButton.addClass("disabled");
                        wishlistButton.attr("aria-label", "Item is already in your Wishlist");
                        wishlistButton.html('<i class="fa-solid fa-check fa-lg"></i>');

                        // Disable the wishlist button
                        wishlistButton.prop("disabled", true);
                    } else {
                        // Display error message
                        errorMessage.text(data.message);
                        errorMessage.show();
                    }
                },
                error: function (error) {
                    // Log any error occurred during adding item to wishlist
                    console.error("Error:", error);
                }
            });
        });
    }
});

// Function to get the value of a cookie by name
function getCookie(name) {
    const cookieValue = document.cookie.match(
        "(^|;)\\s*" + name + "\\s*=\\s*([^;]+)"
    );
    return cookieValue ? cookieValue.pop() : "";
}