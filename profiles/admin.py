from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Avg

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

    def delete_model(self, request, obj):
        """
        Send email to review author after review was deleted
        and recalculate rating for product
        """
        # capture the user email before the review is deleted
        user_email = obj.user.email
        product = obj.product

        # delete the review
        obj.delete()
        # Update the rating field of the Product instance
        rating = product.reviews.aggregate(Avg("rating"))["rating__avg"]
        product.rating = rating if rating else 0
        product.save()

        # setup the email
        subject = 'Your review has been deleted'
        message = render_to_string(
            "products/emails/review_deleted_mail.txt",
            {"user_name": obj.user.username, "product_name": product.title},
        )
        # Send an email to the user who wrote the review.
        send_mail(
            subject,
            message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True,
            html_message=mark_safe(message),
        )


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

        if user_profile and user_profile.orders.exists():
            inline_instances.append(OrderInline(self.model, self.admin_site))

        return inline_instances
