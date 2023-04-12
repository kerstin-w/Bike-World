from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect, reverse, HttpResponse


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

        quantity = int(request.POST.get("quantity"))
        redirect_url = request.POST.get("redirect_url")
        bag = request.session.get("bag", {})

        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

        request.session["bag"] = bag

        """
        Save filters, by getting a copy of the current query parameters,
        generate a Url with ramaining query parameters
        """
        current_filters = request.GET.copy()
        current_filters.pop("category_all", None)
        current_filters.pop("brand_all", None)
        query_string = current_filters.urlencode()
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
        else:
            return redirect(redirect_url_with_filters)

    def get(self, request, item_id):
        """
        Save the query parameters when adding item to cart from the CLP
        """

        current_filters = request.GET.copy()
        current_filters.pop("category_all", None)
        current_filters.pop("brand_all", None)

        # Generate Url with current filters
        redirect_url_with_filters = (
            request.reverse("add_to_bag", args=[item_id])
            + "?"
            + current_filters.urlencode()
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

        quantity = int(request.POST.get("quantity"))
        bag = request.session.get("bag", {})

        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop(item_id)

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
        try:
            bag = request.session.get("bag", {})
            bag.pop(item_id)

            request.session["bag"] = bag
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(status=500)
