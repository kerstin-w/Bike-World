from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models import Q, Case, When, F, DecimalField
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.db.models import Avg
from django.urls import reverse, reverse_lazy
from django.conf import settings


from .models import Product, Category
from .forms import ProductForm
from profiles.models import Wishlist, ProductReview


class WishlistProductsMixin:
    """
    A mixin for retrieving the wishlist products of the user.
    """

    def get_wishlist_products(self):
        """
        Returns the list of wishlist products for the logged-in user.
        """
        if self.request.user.is_authenticated:
            return Wishlist.objects.filter(user=self.request.user).values_list(
                "product_id", flat=True
            )
        return []


class ProductListView(WishlistProductsMixin, ListView):
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
            return queryset.none()
        # Return the sorted/filtered queryset
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

        # Add the wishlist_products list to the context
        context["wishlist_products"] = self.get_wishlist_products()
        return context


class ProductDetailView(WishlistProductsMixin, DetailView):
    """
    Displays the details of a product
    """

    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get product title for template title
        context["title"] = self.object.title

        # Get the user's wishlist products
        wishlist_products = self.get_wishlist_products()

        # Get the reviews for the current product
        reviews = ProductReview.get_reviews_for_product(self.object)

        # Add the wishlist_products list to the context
        context["wishlist_products"] = wishlist_products
        # Add reviews to context
        context["reviews"] = reviews
        return context


class ProductReviewDeleteView(UserPassesTestMixin, DeleteView):
    """
    View to delete a product review
    """

    model = ProductReview

    def test_func(self):
        """
        Test if user is superuser.
        Only superusers can delete reviews.
        """
        return self.request.user.is_superuser

    def get_object(self):
        """
        Get the review based on the pk
        """
        review_pk = self.kwargs.get("pk")
        return get_object_or_404(ProductReview, pk=review_pk)

    def handle_no_permission(self):
        """
        Redirect the user to the index page with an error
        message if they don't have permission
        """
        messages.error(
            self.request, "You do not have permission to delete reviews."
        )
        return redirect("index")

    def delete(self, request, *args, **kwargs):
        """
        Delete the review and associated rating
        """
        # Get the review instance
        review = self.get_object()
        # Get the product instance
        product = review.product
        # Delete the review
        response = super().delete(request, *args, **kwargs)
        # Update the rating field of the Product instance
        rating = product.reviews.aggregate(Avg("rating"))["rating__avg"]
        product.rating = rating if rating else 0
        product.save()
        # Show a success message
        messages.success(
            self.request,
            "The review and associated rating have been deleted successfully.",
        )
        return response

    def get_success_url(self):
        """
        Returns the URL to redirect to after a successful delete.
        """
        return reverse_lazy(
            "product_detail", kwargs={"pk": self.object.product.pk}
        )


class ProductCreateView(UserPassesTestMixin, CreateView):
    """
    View to create Product
    """

    model = Product
    form_class = ProductForm
    template_name = "products/add_product.html"

    def test_func(self):
        """
        restrict access to only superusers
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        handle denied access
        """
        messages.error(
            self.request, "You do not have permission to create products."
        )
        return redirect("products")

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

    def get_success_url(self):
        """
        Get the URL to redirect to product page
        """
        pk = self.object.pk
        return reverse("product_detail", kwargs={"pk": pk})


class ProductEditView(UserPassesTestMixin, UpdateView):
    """
    View to display edit a product
    """

    model = Product
    form_class = ProductForm
    template_name = "products/edit_product.html"
    context_object_name = "product"

    def test_func(self):
        """
        restrict access to only superusers
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        handle denied access
        """
        messages.error(
            self.request, "You do not have permission to edit products."
        )
        return redirect("products")

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


class ProductDeleteView(UserPassesTestMixin, DeleteView):
    """
    View to delete a product
    """

    model = Product
    success_url = reverse_lazy("products")

    def test_func(self):
        """
        restrict access to only superusers
        """
        return self.request.user.is_superuser

    def handle_no_permission(self):
        """
        handle denied access
        """
        messages.error(
            self.request, "You do not have permission to delete products."
        )
        return redirect("products")

    def get_object(self, queryset=None):
        """
        Get the Product
        """
        pk = self.kwargs.get("product_id")
        return get_object_or_404(Product, pk=pk)

    def delete(self, request, *args, **kwargs):
        """
        Delete the product and redirect to success URL
        """
        product = self.get_object()
        messages.success(request, f"{product.title} deleted!")
        return super().delete(request, *args, **kwargs)
