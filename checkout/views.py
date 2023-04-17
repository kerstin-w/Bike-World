from django.shortcuts import (
    render,
    redirect,
    reverse,
    get_object_or_404,
    HttpResponse,
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
from products.models import Product
from bag.context_processors import bag_contents

import stripe
import json


@require_POST
def cache_checkout_data(request):
    try:
        # Get stripe pid
        pid = request.POST.get("client_secret").split("_secret")[0]
        # Get stripe secret key
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Set stripe payment intent
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "bag": json.dumps(request.session.get("bag", {})),
                "save_info": request.POST.get("save_info"),
                "username": request.user,
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(
            request,
            "Sorry, your payment cannot be \
            processed right now. Please try again later.",
        )
        return HttpResponse(content=e, status=400)


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
            # Save the new Order to the database, but don't commit yet
            order = order_form.save(commit=False)
            # Get Stripe PaymentIntent ID from the POST data
            pid = request.POST.get("client_secret").split("_secret")[0]
            # Save Stripe PaymentIntent ID and bag as JSON to the Order model
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()
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


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # Get save_info flag from the session
    save_info = request.session.get("save_info")
    # Get the order
    order = get_object_or_404(Order, order_number=order_number)

    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the user's profile based on id
        profile = UserProfile.objects.get(user=request.user)

        # Attach the user profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info to their profile
        if save_info:
            # Save the data to a dictionary
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }

            # Create a form instance with the updated profile data
            # and the profile data model instance as arguments
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            # Check if the user's updated profile information is valid
            if user_profile_form.is_valid():
                # Save the updated profile information to the database
                user_profile_form.save()

    # Display a success message to the user with the order number and email
    messages.success(
        request,
        f"Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.",
    )

    # Delete bag from the session
    if "bag" in request.session:
        del request.session["bag"]

    # Render the checkout success template
    template = "checkout/checkout_success.html"
    context = {
        "order": order,
    }
    return render(request, template, context)
