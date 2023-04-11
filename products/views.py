from django.contrib import messages
from django.db.models import Q, Case, When, F, DecimalField
from django.shortcuts import render
from django.views.generic import ListView
from .models import Product, Category


class ProductListView(ListView):
    """
    Displays a list of all products with sorting, filter
    and search
    """
    model = Product
    template_name = 'product_list.html'
    paginate_by = 25
    context_object_name = "products"

    def search_products(self, queryset):
        search_keyword = self.request.GET.get('q')
        if search_keyword:
            # Filter by matching the search keyword
            # against the title, brand and bike_type
            queryset = queryset.filter(
                Q(title__icontains=search_keyword) | 
                Q(brand__icontains=search_keyword) |
                Q(bike_type__icontains=search_keyword)
            )
        return queryset
    
    def sort_queryset(self, queryset):
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_asc':
            # Annotate the queryset with a new field named absolute_price,
            # which will be used for sorting. This field is calculated 
            # based on the sale price (if on sale) or the retail price. 
            # Qqueryset is sorted in ascending order based on 
            # the absolute_price field.
            queryset = queryset.annotate(absolute_price=Case(
                When(sale=True, then=F('sale_price')),
                default=F('retail_price'),
                output_field=DecimalField(),
            )).order_by('absolute_price')
        elif sort_by == 'price_desc':
            # Queryset is sorted in descending order.
            queryset = queryset.annotate(absolute_price=Case(
                When(sale=True, then=F('sale_price')),
                default=F('retail_price'),
                output_field=DecimalField(),
            )).order_by('-absolute_price')
        elif sort_by == 'rating_desc':
            # Sort the queryset by rating.
            queryset = queryset.order_by('-rating')
        else:
            # Default sorting is by stock.
            queryset = queryset.order_by('-stock')

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.search_products(queryset)

        # Check if there are any results or not
        if not queryset.exists():
            # Add an error message
            messages.error(self.request, 'No search results found.')
            # Redirect the user to the products page
            return queryset.none()
        # Return the sorted queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort_by'] = self.request.GET.get('sort_by')
        paginator = context['paginator']
        page_obj = context['page_obj']
        context['products'] = paginator.get_page(page_obj.number)
        return context
