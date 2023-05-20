// Update quantity on click
$('.update-link').on('click', function (e) {
    e.preventDefault();
    const form = $(this).closest('div').find('.update-form');
    const input = form.find('.qty_input');
    const quantity = parseInt(input.val());
    // Check if Input is within allowed range
    if (quantity >= 1 && quantity <= 99) {
        form.submit();
    } else {
        input[0].setCustomValidity('Please enter a quantity between 1 and 99');
        input[0].reportValidity();
    }
});
// Remove item and reload on click
$('.remove-item').on('click', function (e) {
    e.preventDefault();
    const itemId = $(this).attr('id').split('remove_')[1];
    const url = `/bag/remove/${itemId}/`;
    const data = {
        'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
    };

    $.post(url, data, () => {
        location.reload();
    });
});