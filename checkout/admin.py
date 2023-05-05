from django.utils import timezone
from django.db.models import Sum, Avg
from django.shortcuts import render
from django.views import View
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
import json

from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    Order Line Items Admin
    """

    model = OrderLineItem
    readonly_fields = ("lineitem_total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Order Admin
    """
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

    def get_country_revenue(self, orders):
        """
        Returns a dictionary mapping country names to revenue totals
        """
        country_revenue = {}
        for order in orders:
            country = order.country.name
            grand_total = float(order.grand_total)
            country_revenue[country] = (
                country_revenue.get(country, 0) + grand_total
            )
        return country_revenue

    def get_today(self):
        """
        Returns the current date in the user's timezone
        """
        return timezone.localtime().date()

    def get_orders_today(self, today):
        """
        Returns a queryset of orders for the given day
        """
        return Order.objects.filter(date__date=today)

    def get_orders_month(self, today):
        """
        Returns a queryset of orders for the current month
        """
        return Order.objects.filter(date__month=today.month)

    def get_revenue(self, orders):
        """
        Returns the total revenue for the given queryset of orders
        """
        return orders.aggregate(Sum("grand_total"))["grand_total__sum"] or 0

    def get_order_count(self, orders):
        """
        Returns the number of orders in the given queryset
        """
        return orders.count()

    def get_average_order_total(self):
        """
        Returns the average order total for all orders
        """
        return (
            Order.objects.all().aggregate(Avg("grand_total"))[
                "grand_total__avg"
            ]
            or 0
        )

    def get_daily_revenue(self, today):
        """
        Returns a list of revenue totals for each day of the current month
        """
        current_month_orders = Order.objects.filter(date__month=today.month)
        daily_revenue = []
        for i in range(1, today.day + 1):
            daily_orders = current_month_orders.filter(date__day=i)
            daily_revenue.append(
                daily_orders.aggregate(Sum("grand_total"))["grand_total__sum"]
                or 0
            )
        return daily_revenue

    def get_context_data(self, request):
        """
        Returns a dictionary of context data for the template
        """
        today = self.get_today()
        orders_today = self.get_orders_today(today)
        orders_month = self.get_orders_month(today)
        revenue_today = self.get_revenue(orders_today)
        revenue_month = self.get_revenue(orders_month)
        order_count_today = self.get_order_count(orders_today)
        order_count_month = self.get_order_count(orders_month)
        average_order_total = self.get_average_order_total()
        daily_revenue = self.get_daily_revenue(today)
        country_revenue = json.dumps(self.get_country_revenue(orders_month))
        return {
            "revenue_today": revenue_today,
            "revenue_month": revenue_month,
            "order_count_today": order_count_today,
            "order_count_month": order_count_month,
            "average_order_total": average_order_total,
            "daily_revenue": daily_revenue,
            "country_revenue": country_revenue,
        }

    def get(self, request):
        """
        Renders the dashboard template with the context data.
        """
        context = self.get_context_data(request)
        return render(request, "admin/dashboard.html", context)
