from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import Wishlist, ProductReview, UserProfile
from checkout.models import Order


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """
    Admin Panel for ProductReview model with its custom admin configuration
    """

    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("product", "user", "created_at")
    search_fields = ("product__title", "user__username", "review")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Admin Panel for WishList model with its custom admin configuration
    """

    list_display = ("user", "product", "is_product_in_wishlist")
    list_filter = ("user",)
    search_fields = ("user__username", "product__title")


class OrderInline(admin.TabularInline):
    """
    Create a new inline class that will be embedded in the UserProfileAdmin
    and show the Order summary
    """

    model = Order
    fields = (
        "view_order",
        "date",
        "order_total",
        "delivery_cost",
        "grand_total",
    )
    readonly_fields = (
        "order_number",
        "date",
        "order_total",
        "delivery_cost",
        "grand_total",
        "view_order",
    )
    can_delete = False
    extra = 0

    def view_order(self, order):
        """
        Return a link to an individual order
        """
        url = reverse("admin:checkout_order_change", args=[order.id])
        return format_html('<a href="{}">{}</a>', url, order.order_number)

    view_order.short_description = "Order Number"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin Panel for UserProfile model with its custom admin configuration
    """

    list_display = (
        "user",
        "default_full_name",
        "default_email",
        "orders_count",
    )
    inlines = [OrderInline]
    search_fields = (
        "user__username",
        "default_email",
        "default_phone_number",
        "default_full_name",
    )
    fieldsets = (
        (None, {"fields": ("user", "default_full_name", "default_email")}),
        (
            "Delivery Information",
            {
                "fields": (
                    "default_phone_number",
                    "default_country",
                    "default_postcode",
                    "default_town_or_city",
                    "default_street_address1",
                    "default_street_address2",
                )
            },
        ),
    )

    def orders_count(self, user_profile):
        """
        Define orders_count field that returns the
        count of orders for each UserProfile
        """
        return user_profile.orders.count()

    def orders(self, user_profile):
        """
        Define a field that returns all orders for each UserProfile object
        """
        return user_profile.orders.all()

    orders.short_description = "Orders"

    def get_inline_instances(self, request, user_profile=None):
        """
        Ensure that the OrderInline is only displayed
        if the userProfile has a related Order
        """
        inline_instances = []
        if user_profile:
            inline_instances.append(OrderInline(self.model, self.admin_site))
        return inline_instances
