/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js

    Using google fonts with stripe: 
    https://stackoverflow.com/questions/43824382/custom-font-src-with-stripe/56985340
*/

let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
console.log(stripePublicKey)
let clientSecret = $('#id_client_secret').text().slice(1, -1);
console.log(clientSecret)
let stripe = Stripe(stripePublicKey);
console.log(stripe)
let elements = stripe.elements({
    fonts: [{
        // integrate Google Fonts Montserrat into stripe
        cssSrc: 'https://fonts.googleapis.com/css?family=Roboto:400;500;700;900',
    }]
});
let style = {
    base: {
        color: '#000',
        fontFamily: 'Roboto, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#717171'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
let card = elements.create('card', {
    style: style
});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    let errorDiv = document.getElementById('card-errors');
    // If there is an error
    if (event.error) {
        let html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        // Update errorDiv with error
        $(errorDiv).html(html);
    } else {
        // Update errorDiv with blank string
        errorDiv.textContent = '';
    }
});

// Handle form submit
let form = document.getElementById('payment-form');

form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    card.update({
        'disabled': true
    });
    $('#submit-button').attr('disabled', true);
    //Fade out payment form
    $('#payment-form').fadeToggle(100);
    // Fade in loader overlay
    $('#loading-overlay').fadeToggle(100);

    // Get save_info checkbox value
    let saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // Set post data
    let postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // Set url
    let url = '/checkout/cache_checkout_data/';

    $.post(url, postData).done(function () {
        // Confirm card payment
        stripe.confirmCardPayment(clientSecret, {
            // Set payment method
            payment_method: {
                card: card,
                // Set billing details
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                    }
                }
            },
            // Set shipping details
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                }
            },
        }).then(function (result) {
            // Display any card errors
            if (result.error) {
                let errorDiv = document.getElementById('card-errors');
                let html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                // Fade in payment form
                $('#payment-form').fadeToggle(100);
                // Fade out loader overlay
                $('#loading-overlay').fadeToggle(100);
                card.update({
                    'disabled': false
                });
                // Enable submit button
                $('#submit-button').attr('disabled', false);
            } else {
                // Submit form if payment intent is succesfull
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    })
});