from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q, Case, When, F, DecimalField
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from .models import Product, Category
from .forms import ProductForm


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
        """
        Filter the queryset by the category name
        """
        category_name = self.request.GET.get("category")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        return queryset

    def filter_by_brand(self, queryset):
        """
        Filter the queryset by brand name
        """
        brand_name = self.request.GET.get("brand")
        if brand_name:
            queryset = queryset.filter(brand__iexact=brand_name)
        return queryset

    def filter_by_gender(self, queryset):
        """
        Filter the queryset by gender
        """
        gender = self.request.GET.get("gender", None)
        if gender == "Womens":
            queryset = queryset.filter(gender=1)
        elif gender == "Mens":
            queryset = queryset.filter(gender=2)
        else:
            queryset = queryset.all()
        return queryset

    def search_products(self, queryset):
        """
        Filter by matching the search keyword
        against the title, brand and type
        """
        search_keyword = self.request.GET.get("q")
        if search_keyword:
            queryset = queryset.filter(
                Q(title__icontains=search_keyword)
                | Q(brand__icontains=search_keyword)
                | Q(bike_type__icontains=search_keyword)
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
        queryset = self.filter_by_gender(queryset)
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


class ProductDetailView(DetailView):
    """
    Displays the details of a product
    """

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_object(self):
        """
        Get the product object based on the pk
        """
        pk = self.kwargs.get("pk")
        return get_object_or_404(Product, pk=pk)


class ProductCreateView(UserPassesTestMixin, CreateView):
    """
    View to create Product
    """

    model = Product
    form_class = ProductForm
    template_name = "products/add_product.html"
    success_url = reverse_lazy("products")

    def test_func(self):
        """
        restrict access to only superusers
        """
        return self.request.user.is_superuser

    def form_valid(self, form):
        """
        handle successful form submission
        """
        messages.success(self.request, "Successfully added product!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        handle invalid form submission
        """
        messages.error(
            self.request,
            "Failed to add product. Please ensure the form is valid.",
        )
        return super().form_invalid(form)


class ProductEditView(UpdateView):
    """
    View to display edit a product
    """

    model = Product
    form_class = ProductForm
    template_name = "products/edit_product.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        """
        Get the Product
        """
        pk = self.kwargs.get("product_id")
        return get_object_or_404(Product, pk=pk)

    def form_valid(self, form):
        """
        handle successful form submission
        """
        messages.success(self.request, "Successfully updated product!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        handle invalid form submission
        """
        messages.error(
            self.request,
            "Failed to update product. Please ensure the form is valid.",
        )
        return super().form_invalid(form)

    def get_success_url(self):
        """
        Get the URL to redirect to product page
        """
        pk = self.kwargs.get("product_id")
        return reverse("product_detail", kwargs={"pk": pk})
