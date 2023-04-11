from django.views.generic import TemplateView


class BagView(TemplateView):
    """
    Render the Shopping Bag
    """
    template_name = 'bag/bag.html'
