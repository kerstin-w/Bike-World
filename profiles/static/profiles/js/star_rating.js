// Get all rating containers
const ratingContainers = document.querySelectorAll('.rating');

// Add event listeners to rating containers
ratingContainers.forEach(container => {
    // Get the rating input field and star elements
    const formId = container.querySelector('.fa-star').getAttribute('data-form-id');
    const ratingInput = document.getElementById(`rating-${formId}`);
    const starElems = container.querySelectorAll('.fa-star');

    // Get the parent form element
    const form = ratingInput.closest('form');

    // Get the submit button element
    const submitButton = form.querySelector('button[type="submit"]');

    // Disable the submit button by default
    submitButton.disabled = true;

    // Add an event listener to rating input field to enable/disable submit button
    ratingInput.addEventListener('input', () => {
        submitButton.disabled = !ratingInput.value;
    });

    // Add event listeners to star elements to capture rating value
    starElems.forEach(star => {
        star.addEventListener('click', () => {
            // Update rating input value and checked status for star elements
            const ratingValue = star.getAttribute('data-rating');
            ratingInput.value = ratingValue;
            starElems.forEach((starElem, index) => {
                starElem.classList.toggle('checked', index < ratingValue);
            });

            // Enable the submit button
            submitButton.disabled = false;
        })
    });
});