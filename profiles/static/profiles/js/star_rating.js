// Get all rating containers
const ratingContainers = document.querySelectorAll('.rating');

// Add a click event listener to each star icon to capture the rating value
if (ratingContainers.length > 0) {
    ratingContainers.forEach(container => {
        const formId = container.querySelector('.fa-star').getAttribute('data-form-id');
        const ratingInput = document.getElementById(`rating-${formId}`);
        const starElems = container.querySelectorAll('.fa-star');
        starElems.forEach(star => {
            star.addEventListener('click', event => {
                // Get the rating value from the clicked star's data-rating attribute
                const ratingValue = event.target.getAttribute('data-rating');
                // Update the value of the hidden input field with the new rating value
                ratingInput.value = ratingValue;
                // Update the "checked" status for each star element based on the new rating value
                for (let i = 1; i <= 5; i++) {
                    const starElem = container.querySelector(`.fa-star.star-${i}`);
                    if (i <= ratingValue) {
                        starElem.classList.add('checked');
                    } else {
                        starElem.classList.remove('checked');
                    }
                }
            });
        });

        // Update the "checked" status for the first star when the page loads
        const firstStarElem = container.querySelector('.fa-star.star-1');
        firstStarElem.classList.add('checked');
    });
}