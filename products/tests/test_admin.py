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
            image="path/to/image.jpg",
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

    def test_product_list_display(self):
        """
        Test List Display in Product Admin Panel
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

    def test_product_ordering(self):
        """
        Test product order in Admin Panel
        """
        expected = ("sku",)
        self.assertEqual(self.product_admin.ordering, expected)

    def test_product_list_filter(self):
        """
        Test list filter in Product Admin Panel
        """
        expected = ("category", "sale", "gender", "brand")
        self.assertEqual(self.product_admin.list_filter, expected)

    def test_product_search_fields(self):
        """
        Test search fields in Product Admin Panel
        """
        expected = ["title", "sku"]
        self.assertEqual(self.product_admin.search_fields, expected)

    def test_product_image_tag_with_image(self):
        """
        Test image_tag in Product Admin Panel
        """
        result = self.product_with_image.image_tag()
        expected = '<img src="/media/path/to/image.jpg" ' \
            'style="width:150px;height:120px;object-fit:contain;">'
        self.assertEqual(result, expected)

    def test_product_image_tag_without_image(self):
        """
        Test image_tag returns 'No Image Found' for product without image
        """
        result = self.product_without_image.image_tag()
        expected = "No Image Found"
        self.assertEqual(result, expected)


class CategoryAdminTestCase(TestCase):
    """
    Test for Category Admin
    """

    def setUp(self):
        """
        Test Data
        """
        self.site = AdminSite()
        self.category_admin = CategoryAdmin(Category, self.site)

    def test_category_list_display(self):
        """
        Test List Display in Category Admin Panel
        """
        expected = ("friendly_name", "pk")
        self.assertEqual(self.category_admin.list_display, expected)

    def test_category_ordering(self):
        """
        Test order Category in Admin Panel
        """
        expected = ("friendly_name",)
        self.assertEqual(self.category_admin.ordering, expected)
