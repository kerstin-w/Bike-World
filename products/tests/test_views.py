from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from unittest.mock import Mock

from products.models import Category, Product
from profiles.models import Wishlist
from products.views import WishlistProductsMixin


class WishlistProductsMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
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
        self.wishlist = Wishlist.objects.create(
            user=self.user, product=self.product
        )

    def test_get_wishlist_products_authenticated(self):
        request = self.factory.get("/")
        request.user = self.user
        mixin = WishlistProductsMixin()
        mixin.request = request

        wishlist_products = mixin.get_wishlist_products()

        expected_wishlist_products = [self.product.id]
        self.assertEqual(list(wishlist_products), expected_wishlist_products)

    def test_get_wishlist_products_unauthenticated(self):
        request = self.factory.get("/")
        request.user = Mock(is_authenticated=False)
        mixin = WishlistProductsMixin()
        mixin.request = request

        wishlist_products = mixin.get_wishlist_products()

        self.assertEqual(list(wishlist_products), [])
