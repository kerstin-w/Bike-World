from django.test import TestCase
from products.models import Category, Product

class CategoryModelTest(TestCase):
    """
    Test for Category Data Model
    """
    def setUp(self):
        """
        Test Data
        """
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test friendly name'
        )

    def test_category_has_name_attr(self):
        """Test category has 'name' attribute as expected"""
        self.assertEquals(self.category.name, 'test_category')

    def test_category_has_friendly_name_attr(self):
        """
        Test category has friendly_name
        """
        self.assertEquals(self.category.friendly_name, 'Test friendly name')

    def test_category_str_method(self):
        """
        Test the __str__ method of Category model
        """
        self.assertEquals(str(self.category), 'Test friendly name')




class ProductModelTest(TestCase):
    """
    Test for Product Data Model
    """
    def setUp(self):
        """
        Test Data
        """
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test friendly name'
        )
        self.product = Product.objects.create(
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
            stock=5
        )

    def test_product_has_title(self):
        """
        Test product has 'title'
        """
        self.assertEquals(self.product.title, "Product A")

    def test_product_has_sku(self):
        """
        Test product has 'sku'
        """
        self.assertEquals(self.product.sku, 'SKU001')
    
    def test_product_has_category(self):
        """
        Test category of the product
        """
        self.assertEquals(str(self.product.category), "Test friendly name")
    
     def test_product_has_description(self):
        """
        Test product has description
        """
        self.assertEquals(self.product.description, "Test description A")

    def test_product_has_wheel_size(self):
        """
        Test product has wheel_size
        """
        self.assertEquals(self.product.wheel_size, "26 inches")

