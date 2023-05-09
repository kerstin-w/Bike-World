from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock

from products.models import Category, Product
from profiles.models import Wishlist
from products.views import WishlistProductsMixin


class WishlistProductsMixinTest(TestCase):
    """
    Test Case for WishlistProductsMixin
    """

    def setUp(self):
        """
        Test Data Setup
        """
        # Set up Request Factory
        self.factory = RequestFactory()

        # create test user
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )

        # create test category
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )

        # create test product
        self.product = Product.objects.create(
            title="Test Product",
            sku="12345",
            category=self.category,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )

        # create test wishlist
        self.wishlist = Wishlist.objects.create(
            user=self.user, product=self.product
        )

    def test_get_wishlist_products_authenticated(self):
        """
        Test that the get_wishlist_products method of
        WishlistProductsMixin for an authenticated user,
        returns a list of the wishlist products
        """
        # Set up the request with an authenticated user
        request = self.factory.get("/")
        request.user = self.user

        # Set up the mixin and assign the request
        mixin = WishlistProductsMixin()
        mixin.request = request

        # Call the get_wishlist_products method of the mixin
        wishlist_products = mixin.get_wishlist_products()

        # Check that the expected wishlist products are returned
        expected_wishlist_products = [self.product.id]
        self.assertEqual(list(wishlist_products), expected_wishlist_products)

    def test_get_wishlist_products_unauthenticated(self):
        """
        Test to assert that the get_wishlist_products method
        of WishlistProductsMixin for an unauthenticated user,
        returns an empty list
        """
        # Set up the request with an unauthenticated user
        request = self.factory.get("/")
        request.user = Mock(is_authenticated=False)

        # Set up the mixin and assign the request
        mixin = WishlistProductsMixin()
        mixin.request = request

        # Call the get_wishlist_products method of the mixin
        wishlist_products = mixin.get_wishlist_products()

        # Check that the expected result is an empty list
        self.assertEqual(list(wishlist_products), [])

    def test_is_product_in_wishlist_true(self):
        """
        Test to assert that the is_product_in_wishlist method of Wishlist
        returns True when the product is already in a wishlist
        """
        # Create a new wishlist object
        wishlist = Wishlist(user=self.user, product=self.product)

        # Assert that the is_product_in_wishlist method for
        # the new wishlist object returns True
        self.assertTrue(wishlist.is_product_in_wishlist())

    def test_is_product_in_wishlist_false(self):
        """
        Test to assert that the is_product_in_wishlist method of Wishlist
        returns False when the product is not in a wishlist
        """
        # Create a new product that is not in the wishlist
        product2 = Product.objects.create(
            title="test product 2",
            sku="12345",
            category=self.category,
            description="Test Description 2",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )

        # Create a new wishlist object with the user and product created above
        wishlist = Wishlist(user=self.user, product=product2)

        # Assert that the is_product_in_wishlist method for
        # the new wishlist object returns False
        self.assertFalse(wishlist.is_product_in_wishlist())
