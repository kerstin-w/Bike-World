from django.shortcuts import render
from django.views.generic import ListView
from .models import Product


class ProductListView(ListView):
    """
    Displays a list of all products
    """
    model = Product
    template_name = 'product_list.html'
    paginate_by = 25
    context_object_name = "products"
    queryset = Product.objects.all()
