/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js

    Using google fonts with stripe: 
    https://stackoverflow.com/questions/43824382/custom-font-src-with-stripe/56985340
*/

let stripe_public_key = $('#id_stripe_public_key').text().slice(1, -1);
let client_secret = $('#id_client_secret').text().slice(1, -1);
let stripe = Stripe(stripe_public_key);
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