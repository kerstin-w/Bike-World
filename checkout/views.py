from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.context_processors import bag_contents

import stripe


def checkout(request):
    """
    View for Order Checkout
    """
    # Set stripe keys
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        # Get basket from session
        bag = request.session.get("bag", {})
        # Get form data from session
        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
        }
        # Create an instance of OrderForm from the form data
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            # Save validated form data to a new order
            order = order_form.save()
            # Iterate through items in bag to create OrderLineItem for each
            for item_id, item_data in bag.items():
                try:
                    product = get_object_or_404(Product, pk=item_id)
                    order_line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=item_data,
                    )
                    order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        (
                            "One of the products in your basket wasn't found \
                        in our database. Please call for assistance!"
                        ),
                    )
                    # Delete the order if the product no longer exists
                    order.delete()
                    return redirect(reverse("view_bag"))
            # Update the save_info flag in the session
            request.session["save_info"] = "save-info" in request.POST
            # Redirect to checkout success page with order number as arguments
            return redirect(
                reverse("checkout_success", args=[order.order_number])
            )
        else:
            # Alert user if there is an error with the order form
            messages.error(
                request,
                "There was an error with your form. \
                Please double check your information.",
            )
    else:
        # Get basket from session
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment"
            )
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

    # Load the checkout template with required context
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
    }
    return render(request, template, context)
