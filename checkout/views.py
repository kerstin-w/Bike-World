from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm
from bag.context_processors import bag_contents

import stripe


def checkout(request):
    """
    View for Order Checkout
    """
    # Get basket from session
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # Set current basket
    current_bag = bag_contents(request)
    # Set grand total
    total = current_bag['grand_total']
    # Set stripe total
    stripe_total = round(total * 100)

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
    }

    return render(request, template, context)
