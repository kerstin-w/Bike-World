from django.utils import timezone
from django.db.models import Sum, Avg
from django.shortcuts import render
from django.views import View
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    Order Line Items Admin
    """

    model = OrderLineItem
    readonly_fields = ("lineitem_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = (
        "order_number",
        "date",
        "delivery_cost",
        "order_total",
        "grand_total",
        "original_bag",
        "stripe_pid",
    )

    fields = (
        "order_number",
        "user_profile",
        "date",
        "full_name",
        "email",
        "phone_number",
        "country",
        "postcode",
        "town_or_city",
        "street_address1",
        "street_address2",
        "delivery_cost",
        "order_total",
        "grand_total",
        "original_bag",
        "stripe_pid",
    )

    list_display = (
        "order_number",
        "date",
        "full_name",
        "order_total",
        "delivery_cost",
        "grand_total",
    )

    ordering = ("-date",)


class DashboardView(View):
    """
    Display a Dashboard in the Admin Panel
    """

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Get the current date in the user's timezone
        today = timezone.localtime().date()

        # Query the database for the revenue for today and the current month
        orders_today = Order.objects.filter(date__date=today)
        orders_month = Order.objects.filter(date__month=today.month)

        revenue_today = orders_today.aggregate(Sum("grand_total"))[
            "grand_total__sum"] or 0
        revenue_month = orders_month.aggregate(Sum("grand_total"))[
            "grand_total__sum"] or 0

        # Query the database for number of orders for today and current month
        order_count_today = orders_today.count()
        order_count_month = orders_month.count()

        # Query the database for the average order total for all orders
        average_order_total = Order.objects.all().aggregate(
            Avg("grand_total"))["grand_total__avg"] or 0

        # Add all the data to a context dictionary
        context = {
            "revenue_today": revenue_today,
            "revenue_month": revenue_month,
            "order_count_today": order_count_today,
            "order_count_month": order_count_month,
            "average_order_total": average_order_total,
        }

        # Render template with the context data and return response
        return render(request, "admin/dashboard.html", context)
