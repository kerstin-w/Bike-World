from django.contrib import admin

from .models import Wishlist, ProductReview, UserProfile


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


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin Panel for UserProfile model with its custom admin configuration
    """

    list_display = (
        "user",
        "default_full_name",
        "default_email",
    )

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
