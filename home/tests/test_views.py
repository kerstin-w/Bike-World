from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category


class HomePageViewTest(TestCase):
    """
    Test HomePageView
    """

    def setUp(self):
        """
        Test Data
        """
        self.url = reverse("index")
        self.response = self.client.get(self.url)

        self.category = Category.objects.create(name="Test Category")
        self.product_1 = Product.objects.create(
            title="Product A",
            sku="SKU001",
            category=self.category,
            description="Test description A",
            wheel_size="26 inches",
            retail_price=Decimal("399.00"),
            sale_price=Decimal("349.00"),
            sale=False,
            rating=4,
            image="Image.jpg",
            brand="Scott",
            bike_type="Mountain Bike",
            material="Test Material A",
            derailleur="Test Derailleur A",
            stock=5,
        )
        self.product_2 = Product.objects.create(
            title="Product B",
            sku="SKU002",
            category=self.category,
            description="Test description B",
            wheel_size="28 inches",
            retail_price=Decimal("299.00"),
            sale_price=None,
            sale=False,
            rating=5,
            image="Image.jpg",
            brand="Canyon",
            bike_type="Road Bike",
            material="Test Material B",
            derailleur="Test Derailleur B",
            stock=10,
        )

    def test_home_page_view_returns_200(self):
        """
        Test that the view is returning a status code of 200 OK
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_home_page_view_uses_correct_template(self):
        """
        Test that the view is using the correct template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "home/index.html")

    def test_home_page_view_includes_top_rated_products(self):
        """
        Test that the view includes the top-rated products in the context
        """
        top_rated_products = [self.product_2, self.product_1]
        response = self.client.get(self.url)
        self.assertCountEqual(
            response.context["top_rated_products"], top_rated_products
        )

    def test_home_page_view_displays_top_rated_products(self):
        """
        Test that the view displays the top-rated products correctly
        """
        top_rated_products = [self.product_2, self.product_1]
        response = self.client.get(self.url)
        for i, product in enumerate(top_rated_products):
            self.assertContains(response, product.title)
            self.assertContains(response, str(product.retail_price))
