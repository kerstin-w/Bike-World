import uuid

from django.conf import settings
from django.db import models
from django.db.models import Sum


class Order(models.Model):
    """
    Data Model for Order
    """
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(
        max_length=settings.FULL_NAME_MAX_LENGTH, null=False, blank=False
    )
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(
        max_length=settings.PHONE_NUMBER_MAX_LENGTH, null=False, blank=False
    )
    country = models.CharField(
        max_length=settings.COUNTRY_MAX_LENGTH, null=False, blank=False
    )
    postcode = models.CharField(
        max_length=settings.POSTCODE_MAX_LENGTH, null=True, blank=True
    )
    town_or_city = models.CharField(
        max_length=settings.TOWN_OR_CITY_MAX_LENGTH, null=False, blank=False
    )
    street_address1 = models.CharField(
        max_length=settings.STREET_ADDRESS1_MAX_LENGTH, null=False, blank=False
    )
    street_address2 = models.CharField(
        max_length=settings.STREET_ADDRESS2_MAX_LENGTH, null=True, blank=True
    )
    date = models.DateTimeField(auto_now_add=True)

    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        self.order_total = self.lineitems.aggregate(Sum("lineitem_total"))[
            "lineitem_total__sum"
        ]
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            self.delivery_cost = settings.STANDARD_DELIVERY_COST
        else:
            self.delivery_cost = 0
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number
