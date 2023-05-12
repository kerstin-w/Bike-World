from django.contrib import messages
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import (
    render,
    redirect,
    reverse,
    HttpResponse,
    get_object_or_404,
)
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

        product = get_object_or_404(Product, pk=item_id)
        # get the quantity of the item from the form data
        quantity = int(request.POST.get("quantity"))
        # Get the URL to redirect to after adding to bag from the form data
        redirect_url = request.POST.get("redirect_url")
        # get the current bag dictionary from the user's session data
        bag = request.session.get("bag", {})

        # If the item is already in the bag, add the new quantity
        # to the existing quantity
        if item_id in list(bag.keys()):
            bag[item_id] += quantity
            item_added = True
            messages.success(
                request,
                f"You updated <strong>{product.title}</strong> quantity to "
                f"<strong>{bag[item_id]}</strong>!",
            )
        # If the item is not yet in the bag, add it with the new quantity
        else:
            bag[item_id] = quantity
            item_added = True
            messages.success(
                request, f"You added <strong>{product.title}</strong> to bag!"
            )

        request.session["bag"] = bag
        # Indicate that an item was added to the bag in this request
        request.session["item_added"] = item_added

        """
        Save filters, by getting a copy of the current query parameters,
        generate a Url with ramaining query parameters
        """
        # Get a copy of the current query parameters from the GET data
        current_filters = request.GET.copy()
        # Remove the "category_all" and "brand_all" parameters if present
        current_filters.pop("category_all", None)
        current_filters.pop("brand_all", None)
        # Encode the remaining query parameters into a query string
        query_string = current_filters.urlencode()
        # Construct a URL for the product view that includes
        # remaining query parameters
        redirect_url_with_filters = (
            f"{reverse('products')}?{query_string}"
            if query_string
            else reverse("products")
        )
        """
        Construct a new URL for the View, including only the remaining filters.
        If there are any filters left, they are appended to the base
        URL for the view. if there are no filters left, only the base
        URL is returned.
        """
        if redirect_url:
            redirect_url_with_filters = (
                f"{redirect_url}?{query_string}"
                if query_string
                else redirect_url
            )
        return redirect(redirect_url_with_filters)

    def get(self, request, item_id):
        """
        Save the query parameters when adding item to cart from the CLP
        """

        product = get_object_or_404(Product, pk=item_id)
        # Get a copy of the current query parameters from the GET data
        current_filters = request.GET.copy()
        # Remove the "category_all" and "brand_all" parameters if present
        current_filters.pop("category_all", None)
        current_filters.pop("brand_all", None)

        # Generate Url with current filters
        redirect_url_with_filters = (
            request.reverse("add_to_bag", args=[item_id])
            + "?"
            + current_filters.urlencode()
        )

        messages.success(
            request, f"You added <strong>{product.title}</strong> to bag!"
        )

        return redirect(redirect_url_with_filters)


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
