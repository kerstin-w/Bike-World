from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.context_processors import bag_contents

import stripe


def checkout(request):
    """
    View for Order Checkout
    """
    # Set stripe keys
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # Get basket from session
    bag = request.session.get("bag", {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse("products"))

    # Set current basket
    current_bag = bag_contents(request)
    # Set grand total
    total = current_bag["grand_total"]
    # Set stripe total
    stripe_total = round(total * 100)
    # Set stripe api key
    stripe.api_key = stripe_secret_key
    # Create and set payment intent
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()

    # Check if stripe public key is set
    if not stripe_public_key:
        messages.warning(
            request,
            "Stripe public key is missing. \
            Did you forget to set it in your environment varibables?",
        )

    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
    }

    return render(request, template, context)
