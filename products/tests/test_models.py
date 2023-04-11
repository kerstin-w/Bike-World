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

    def test_category_has_name(self):
        """Test category has 'name' attribute as expected"""
        self.assertEquals(self.category.name, 'test_category')

    def test_category_has_friendly_name(self):
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

    def test_product_has_retail_price(self):
        """
        Test product has retail_price
        """
        self.assertAlmostEqual(float(self.product.retail_price), 15.99)

    def test_product_has_sale_price(self):
        """
        Test product has sale_price
        """
        self.assertAlmostEqual(float(self.product.sale_price), 10.99)

    def test_product_has_sale(self):
        """
        Test product has sale 
        """
        self.assertTrue(self.product.sale)
    
    def test_product_has_rating(self):
        """
        Test product has rating
        """
        self.assertEquals(self.product.rating, 4)

    def test_product_has_brand(self):
        """
        Test product has brand
        """
        self.assertEquals(self.product.brand, "Scott")

    def test_product_has_bike_type(self):
        """
        Test product has bike_type
        """
        self.assertEquals(self.product.bike_type, "Mountain Bike")
    
    def test_product_has_gender(self):
        """
        Test product has gender
        """
        self.assertEquals(self.product.get_gender_display(), "Unisex")

    def test_product_has_material(self):
        """
        Test product has material
        """
        self.assertEquals(self.product.material, "Test Material A")
        
    def test_product_has_derailleur(self):
        """
        Test product has derailleur
        """
        self.assertEquals(self.product.derailleur, "Test Derailleur A")
    
    def test_product_has_stock(self):
        """
        Test product has stock
        """
        self.assertEquals(self.product.stock, 5)

