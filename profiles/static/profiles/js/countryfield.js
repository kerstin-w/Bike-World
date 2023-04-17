// Function takes an input element selector as an argument
function updateCountryInputColor(inputSelector) {
    // Get the input element using the selector
    const inputCountry = $(inputSelector);
    // Check if the input element has a value
    const hasValue = inputCountry.val();
    // Set the color of the input element based on whether it has a value or not
    inputCountry.css('color', hasValue ? '#000' : '#6c757d');
}

$(function () {
    updateCountryInputColor('#id_default_country');
    // Set up an event handler for when the input element value changes
    $('#id_default_country').change(function () {
        // Call the function again to update the color of the input element
        // This time, pass in the "this" context to get the input element directly
        updateCountryInputColor(this);
    });
});