from django.views.generic import TemplateView
from products.models import Product
from products.views import WishlistProductsMixin


class HomePageView(WishlistProductsMixin, TemplateView):
    """
    Render the Homepage
    """

    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top_rated_products = Product.objects.filter(
            rating__isnull=False
        ).order_by("-rating")[:4]
        context["top_rated_products"] = top_rated_products
        context["wishlist_products"] = self.get_wishlist_products()
        return context


class Error403View(TemplateView):
    """
    Render 403 Error Page
    """
    template_name = "errors/403.html"


class Error404View(TemplateView):
    """
    Render 404 Error Page
    """
    template_name = "errors/404.html"


class Error405View(TemplateView):
    """
    Render 405 Error Page
    """
    template_name = "errors/405.html"
