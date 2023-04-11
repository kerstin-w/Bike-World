from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from products.admin import ProductAdmin, CategoryAdmin
from products.models import Product, Category


class ProductAdminTestCase(TestCase):
    """
    Test for Product Admin
    """
    def setUp(self):
        """
        Test Data
        """
        self.site = AdminSite()
        self.product_admin = ProductAdmin(Product, self.site)
        self.category = Category.objects.create(
            name="test_category", friendly_name="Test friendly name"
        )
        self.product_with_image = Product.objects.create(
            image='path/to/image.jpg',
            title="Product A",
            sku="SKU001",
            category=self.category,
            description="Test description A",
            wheel_size="26 inches",
            retail_price=15.99,
            sale_price=10.99,
            sale=True,
            rating=4,
            brand="Scott",
            bike_type="Mountain Bike",
            gender=0,
            material="Test Material A",
            derailleur="Test Derailleur A",
            stock=5,
        )
        self.product_without_image = Product.objects.create(
            title="Product B",
            sku="SKU002",
            category=self.category,
            description="Test description B",
            wheel_size="26 inches",
            retail_price=15.99,
            sale_price=10.99,
            sale=True,
            rating=4,
            brand="Scott",
            bike_type="Mountain Bike",
            gender=0,
            material="Test Material B",
            derailleur="Test Derailleur B",
            stock=5,
        )

    def test_list_display(self):
        """
        Test List Display in Admin Panel
        """
        expected = (
            "sku",
            "title",
            "category",
            "rating",
            "stock",
            "image_tag",
        )
        self.assertEqual(self.product_admin.list_display, expected)

    def test_ordering(self):
        """
        Test product order in Admin Panel
        """
        expected = ("sku",)
        self.assertEqual(self.product_admin.ordering, expected)

    def test_list_filter(self):
        """
        Test list filter in Admin Panel
        """
        expected = ("category", "sale", "gender", "brand")
        self.assertEqual(self.product_admin.list_filter, expected)

    def test_search_fields(self):
        """
        Test search fields in Admin Panel
        """
        expected = ["title", "sku"]
        self.assertEqual(self.product_admin.search_fields, expected)


