from django.contrib import admin
from .models import Product, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin Panel for Products
    """

    list_display = (
        "sku",
        "title",
        "category",
        "rating",
        "image",
    )

    ordering = ("sku",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin Panel for Categories
    """

    list_display = ("friendly_name", "pk")

    ordering = ("friendly_name",)
