from decimal import Decimal
from django.conf import settings


def bag_contents(request):
    """
    Context of Shopping Bag
    """
    bag_items = []
    total = 0
    product_count = 0

    # Calculate total cost and count of items in the bag
    for item in bag_items:
        total += item["quantity"] * item["product"].price
        product_count += item["quantity"]

    # Calculate amount needed to reach the free delivery threshold
    free_delivery_delta = max(settings.FREE_DELIVERY_THRESHOLD - total, 0)

    # Calculate delivery cost
    delivery = (
        total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        if free_delivery_delta > 0
        else 0
    )

    # Calculate the grand total, which is the sum of the total
    # cost and the delivery cost
    grand_total = delivery + total

    context = {
        "bag_items": bag_items,
        "total": total,
        "product_count": product_count,
        "delivery": delivery,
        "free_delivery_delta": free_delivery_delta,
        "free_delivery_threshold": settings.FREE_DELIVERY_THRESHOLD,
        "grand_total": grand_total,
    }

    return context
