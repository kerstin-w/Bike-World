from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect, reverse


class BagView(TemplateView):
    """
    Render the Shopping Bag
    """
    template_name = 'bag/bag.html'


class AddToBagView(View):
    """
    View to add items to the shopping bag
    """
    def post(self, request, item_id):
        """
        Add quantity of the product to the shopping bag
        """

        quantity = int(request.POST.get('quantity'))
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})

        if item_id in list(bag.keys()):
            bag[item_id] += quantity
        else:
            bag[item_id] = quantity

        request.session['bag'] = bag
        return redirect(redirect_url)

class AdjustBagView(View):
    """
    View to adjust items in the shopping bag
    """
    def post(self, request, item_id):
        """
        Add quantity of the product to the shopping bag
        """

        quantity = int(request.POST.get('quantity'))
        bag = request.session.get('bag', {})

        if quantity > 0:
            bag[item_id] = quantity
        else:
            bag.pop['item_id']

        request.session['bag'] = bag
        return redirect(reverse('view_bag'))
