from django.contrib import admin
from .models import Wishlist, ProductReview


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
