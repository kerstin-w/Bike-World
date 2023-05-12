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

    def test_bag_contents_basket_has_items(self):
        """
        Test that if the user has items in their bag, that they the response
        contains the items and their respective quantity.
        """
        request = self.factory.get(self.url)
        request.session = {"bag": {"1": 2}}
        response = bag_contents(request)

        self.assertEqual(response["bag_items"][0]["product"], self.product)
        self.assertEqual(response["bag_items"][0]["quantity"], 2)

    def test_bag_contents_prices_are_calculated(self):
        """
        Test that the processor calculates the total and delivery charges.
        """
        request = self.factory.get(self.url)
        request.session = {"bag": {"1": 2}}
        response = bag_contents(request)

        expected_total = Decimal(self.product.sale_price) * 2
        expected_delivery_cost = settings.STANDARD_DELIVERY_COST

        self.assertEqual(response["total"], expected_total)
        self.assertEqual(response["delivery"], expected_delivery_cost)

    def test_bag_contents_free_delivery_threshold(self):
        """
        Test that the free delivery threshold is correctly calculated.
        """
        request = self.factory.get(self.url)
        request.session = {"bag": {"1": 1}}
        response = bag_contents(request)

        self.assertEqual(
            response["free_delivery_delta"],
            settings.FREE_DELIVERY_THRESHOLD - int(self.product.sale_price),
        )

    def test_bag_contents_grand_total(self):
        """
        Test that the grand total is correctly calculated.
        """
        request = self.factory.get(self.url)
        request.session = {"bag": {"1": 2}}
        response = bag_contents(request)

        expected_grand_total = (
            int(self.product.sale_price) * 2
        ) + settings.STANDARD_DELIVERY_COST
        self.assertEqual((response["grand_total"]), (expected_grand_total))

    def test_bag_contents_with_product_not_on_sale(self):
        """
        Test that price is calculated correctly with retail price.
        """
        session = self.client.session
        session["bag"] = {str(self.product_not_on_sale.id): 1}
        session.save()

        request = self.factory.get(self.url)
        request.session = session
        response = bag_contents(request)

        self.assertEqual(response["total"], 80)
