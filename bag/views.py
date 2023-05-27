from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import (
    HttpResponse,
    get_object_or_404,
    redirect,
    reverse,
)
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

from bag.context_processors import bag_contents
from products.models import Product


class BagView(TemplateView):
    """
    Render the Shopping Bag
    """

    template_name = "bag/bag.html"


class AddToBagView(View):
    """
    View to add items to the shopping bag
    """

    def post(self, request, item_id):
        """
        Add quantity of the product to the shopping bag
        """
        if not Product.objects.filter(id=item_id).exists():
            response_data = {
                'error': 'The product does not exist.',
            }
            return JsonResponse(response_data, status=400)
        quantity = request.POST.get("quantity")

        # Validate the input quantity
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 99:
                raise ValueError('Invalid quantity')
        except ValueError:
            response_data = {
                'error': 'Please enter a valid quantity between 1-99.',
            }
            return JsonResponse(response_data, status=400)

        # get the current bag dictionary from the user's session data
        bag = request.session.get("bag", {})
        # If the item is already in the bag, add the new quantity
        # to the existing quantity
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        # If the item is not yet in the bag, add it with the new quantity
        else:
            bag[item_id] = quantity
        request.session["bag"] = bag

        bag_content = bag_contents(request)
        product_count = bag_content["product_count"]
        response_data = {
            "quantity": bag[item_id],
            "total_quantity": product_count,
            "bag_contents": render_to_string(
                "components/bag_offcanvas.html",
                {"bag": bag_content},
                request=request,
            ),
        }
        return JsonResponse(response_data)


class AdjustBagView(View):
    """
    View to adjust items in the shopping bag
    """

    def post(self, request, item_id):
        """
        Add quantity of the product to the shopping bag
        """

        # get the quantity of the item from the form data
        quantity = int(request.POST.get("quantity"))
        # get the current bag dictionary from the user's session data
        bag = request.session.get("bag", {})
        product = get_object_or_404(Product, pk=item_id)

        # If quantity is greater than zero, update the quantity of
        # the item in the bag
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(
                request,
                f"You updated <strong>{product.title}</strong> quantity to "
                f"<strong>{bag[item_id]}</strong>!",
            )
        # If quantity is zero or less, remove the item from the bag
        else:
            bag.pop(item_id)
            messages.success(
                request, f"You removed <strong>{product.title}</strong>!"
            )

        # Store the updated bag data back into the session
        request.session["bag"] = bag
        return redirect(reverse("view_bag"))


class RemoveItemFromBagView(View):
    """
    View to remove items in the shopping bag
    """

    def post(self, request, item_id):
        """
        Remove item from Shopping Bag
        """
        product = get_object_or_404(Product, pk=item_id)

        try:
            # get the bag dictionary from the session data
            bag = request.session.get("bag", {})
            # remove the item from the bag
            bag.pop(item_id)

            # store the updated bag data back into the session
            request.session["bag"] = bag
            messages.success(
                request, f"You removed <strong>{product.title}</strong>!"
            )
            return HttpResponse(status=200)
        except Exception as e:
            messages.error(request, f"Error removing item: {e}")
            return HttpResponse(status=500)
