from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product


def bag_contents(request):
    """
    Context of Shopping Bag
    """
    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    # Calculate total cost and count of items in the bag
    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        # Use sale_price if item is on sale, otherwise retail_price
        if product.sale:
            price = product.sale_price
        else:
            price = product.retail_price

        total += quantity * price
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

    # Calculate amount needed to reach the free delivery threshold
    free_delivery_delta = max(settings.FREE_DELIVERY_THRESHOLD - total, 0)

    # Calculate delivery cost
    delivery = (
        total + Decimal(settings.STANDARD_DELIVERY_COST)
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
