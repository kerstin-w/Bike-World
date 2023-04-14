from django.contrib import admin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    Order Line Items Admin
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
