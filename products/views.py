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
    template_name = "product_list.html"
    paginate_by = 25
    context_object_name = "products"

    def filter_by_category(self, queryset):
        # Filter the queryset by the category name
        category_name = self.request.GET.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset

    def filter_by_brand(self, queryset):
        # Filter the queryset by brand name
        brand_name = self.request.GET.get("brand")
        if brand_name:
            queryset = queryset.filter(brand__iexact=brand_name)
        return queryset

    def search_products(self, queryset):
        # Filter by matching the search keyword
        # against the title, brand and type
        search_keyword = self.request.GET.get("q")
        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword)
                | Q(brand__icontains=search_keyword)
                | Q(type__icontains=search_keyword)
            )
        return queryset

    def sort_queryset(self, queryset):
        """
        Annotate the queryset with a new field named absolute_price,
        which will be used for sorting. This field is calculated
        based on the sale price (if on sale) or the retail price.
        Qqueryset is sorted in ascending order based on
        the absolute_price field.
        """
        sort_by = self.request.GET.get("sort_by")
        if sort_by == "price_asc":
            queryset = queryset.annotate(
                absolute_price=Case(
                    When(sale=True, then=F("sale_price")),
                    default=F("retail_price"),
                    output_field=DecimalField(),
                )
            ).order_by("absolute_price")
        elif sort_by == "price_desc":
            # Queryset is sorted in descending order.
            queryset = queryset.annotate(
                absolute_price=Case(
                    When(sale=True, then=F("sale_price")),
                    default=F("retail_price"),
                    output_field=DecimalField(),
                )
            ).order_by("-absolute_price")
        elif sort_by == "rating_desc":
            # Sort the queryset by rating.
            queryset = queryset.order_by("-rating")
        else:
            # Default sorting is by stock.
            queryset = queryset.order_by("-stock")

        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        # Apply filters to the queryset
        queryset = self.filter_by_category(queryset)
        queryset = self.filter_by_brand(queryset)
        queryset = self.search_products(queryset)
        queryset = self.sort_queryset(queryset)

        # Check if there are any results or not
        if not queryset.exists():
            # Add an error message
            messages.error(self.request, "No search results found.")
            # Redirect the user to the products page
            return queryset.none()
        # Return the sorted queryset
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add filter values to the context
        context["selected_category"] = self.request.GET.get("category")
        context["selected_brand"] = self.request.GET.get("brand")

        # Add sorting value to the context
        context["sort_by"] = self.request.GET.get("sort_by")

        # Set up pagination
        paginator = context["paginator"]
        page_obj = context["page_obj"]
        context["products"] = paginator.get_page(page_obj.number)

        # Add available categories and brands to the context
        context["categories"] = Category.objects.all()
        context["brands"] = Product.objects.values_list(
            "brand", flat=True
        ).distinct()

        return context
