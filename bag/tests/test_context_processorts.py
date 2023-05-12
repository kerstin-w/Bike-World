from decimal import Decimal

from django.test import RequestFactory, TestCase
from django.shortcuts import reverse

from django.conf import settings
from products.models import Category, Product
from bag.context_processors import bag_contents


class BagContentsTest(TestCase):
    """
    Test Case for bag contents
    """

    def setUp(self):
        """
        Test Data
        """
        self.factory = RequestFactory()
        self.url = reverse("view_bag")

        self.category = Category.objects.create(
            name="category",
            friendly_name="Friendly category name",
        )
        self.product = Product.objects.create(
            title="product",
            sku="111",
            category=self.category,
            description="product description",
            wheel_size='26"',
            retail_price="100",
            sale_price="50",
            sale=True,
            brand="Brand",
            bike_type="Bike type",
            gender="0",
            material="Material",
            derailleur="Derailleur",
            stock="10",
            rating="4.8",
        )
        self.product_not_on_sale = Product.objects.create(
            title="product not on sale",
            sku="222",
            category=self.category,
            description="product description",
            wheel_size='26"',
            retail_price="80",
            sale_price="0",
            sale=False,
            brand="Brand",
            bike_type="Bike type",
            gender="0",
            material="Material",
            derailleur="Derailleur",
            stock="10",
            rating="4.8",
        )

    def test_bag_contents_basket_was_empty(self):
        """
        Test that if the user's bag was empty, that the context processor
        returns no items and the total is 0.
        """
        request = self.factory.get(self.url)
        request.session = {"bag": {}}
        response = bag_contents(request)

        self.assertEqual(response["bag_items"], [])
        self.assertEqual(response["total"], Decimal(0))
