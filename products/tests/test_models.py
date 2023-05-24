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
            name="test_category", friendly_name="Test friendly name"
        )

    def test_category_has_name(self):
        """Test category has 'name' attribute as expected"""
        self.assertEquals(self.category.name, "test_category")

    def test_category_has_friendly_name(self):
        """
        Test category has friendly_name
        """
        self.assertEquals(self.category.friendly_name, "Test friendly name")

    def test_category_str_method(self):
        """
        Test the __str__ method of Category model
        """
        self.assertEquals(str(self.category), "Test friendly name")


class ProductModelTest(TestCase):
    """
    Test for Product Data Model
    """

    def setUp(self):
        """
        Test Data
        """
        self.category = Category.objects.create(
            name="sale", friendly_name="Sale"
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
            stock=5,
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
        self.assertEquals(self.product.sku, "SKU001")

    def test_product_has_category(self):
        """
        Test category of the product
        """
        self.assertEquals(str(self.product.category), "Sale")

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

    def test_product_str_(self):
        """
        Test the __str__ method of Product model
        """
        self.assertEquals(str(self.product), "Product A")

    def test_get_gender_display(self):
        """
        Test the genders are displayed
        """
        self.assertEquals(self.product.get_gender_display(), "Unisex")

    def test_get_related_products(self):
        """
        Test that related products are retrieved successfully.
        """
        # Create a different category for related_product_1
        category2 = Category.objects.create(
            name="test_category_2", friendly_name="Test friendly name 2"
        )

        related_product_1 = Product.objects.create(
            title="Related Product 1",
            sku="SKU002",
            category=category2,
            description="Test description B",
            wheel_size="24 inches",
            retail_price=10.99,
            sale_price=5.99,
            sale=False,
            rating=3,
            brand="Trek",
            bike_type="Road Bike",
            gender=1,
            material="Test Material B",
            derailleur="Test Derailleur B",
            stock=3,
        )

        related_product_2 = Product.objects.create(
            title="Related Product 2",
            sku="SKU003",
            category=self.category,
            description="Test description C",
            wheel_size="27 inches",
            retail_price=20.99,
            sale_price=15.99,
            sale=False,
            rating=5,
            brand="Giant",
            bike_type="Hybrid Bike",
            gender=2,
            material="Test Material C",
            derailleur="Test Derailleur C",
            stock=7,
        )

        related_product_3 = Product.objects.create(
            title="Related Product 3",
            sku="SKU004",
            category=category2,
            description="Test description C",
            wheel_size="27 inches",
            retail_price=20.99,
            sale_price=15.99,
            sale=False,
            rating=5,
            brand="Giant",
            bike_type="Hybrid Bike",
            gender=2,
            material="Test Material C",
            derailleur="Test Derailleur C",
            stock=7,
        )

        # Test that related products are retrieved for the given product
        related_products = self.product.get_related_products()
        self.assertEqual(related_products.count(), 1)
        self.assertIn(related_product_2, related_products)

        # Test that the method excludes the current product from the results
        related_products = related_product_1.get_related_products()
        self.assertEqual(related_products.count(), 1)
        self.assertIn(related_product_3, related_products)
        self.assertNotIn(related_product_1, related_products)

    def test_get_related_products_returns_only_4_products(self):
        """
        Test that only the first 4 related products are returned
        """
        # Create additional products in the same category
        for i in range(5):
            Product.objects.create(
                title=f"Product B{i}",
                sku=f"SKU000{i}",
                category=self.category,
                description=f"Test description B{i}",
                wheel_size="26 inches",
                retail_price=15.99,
                sale_price=10.99,
                sale=False,
                rating=4,
                brand="Scott",
                bike_type="Mountain Bike",
                gender=0,
                material="Test Material B",
                derailleur="Test Derailleur B",
                stock=5,
            )

        # Call get_related_products method for the test product
        related_products = self.product.get_related_products()

        # Check that only 4 products are returned
        self.assertEqual(len(related_products), 4)

        # Check that the related products belong to the same category
        for product in related_products:
            self.assertEqual(product.category, self.category)

        # Check that the test product is not in the related products list
        self.assertNotIn(self.product, related_products)
