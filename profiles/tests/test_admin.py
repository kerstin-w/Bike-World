from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite

from profiles.models import Wishlist, ProductReview
from profiles.admin import WishlistAdmin, ProductReviewAdmin
from products.models import Category, Product


class WishlistAdminTest(TestCase):
    """
    Test Case for WishList Admin
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.product = Product.objects.create(
            title="Test Product",
            sku="test_sku",
            category=Category.objects.create(
                name="Test Category", friendly_name="Test Category"
            ),
            description="Test Product Description",
            wheel_size="26 inches",
            retail_price=999.99,
            sale_price=799.99,
            sale=True,
            image="path/to/test/image.jpg",
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=10,
            rating=4.5,
        )
        self.wishlist = Wishlist.objects.create(
            user=self.user, product=self.product
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass")
        self.site = AdminSite()

    def test_wishlist_admin_list_display(self):
        """
        Test that the correct fields are displayed in the list view.
        """
        wishlist_admin = WishlistAdmin(Wishlist, self.site)
        self.assertEqual(
            wishlist_admin.list_display,
            ("user", "product", "is_product_in_wishlist"),
        )

    def test_wishlist_admin_list_filter(self):
        """
        Test that the correct filters are displayed in the list view.
        """
        wishlist_admin = WishlistAdmin(Wishlist, self.site)
        self.assertEqual(wishlist_admin.list_filter, ("user",))

    def test_wishlist_admin_search_fields(self):
        """
        Test that the correct search fields are displayed in the list view.
        """
        wishlist_admin = WishlistAdmin(Wishlist, self.site)
        self.assertEqual(
            wishlist_admin.search_fields, ("user__username", "product__title")
        )


class ProductReviewAdminTest(TestCase):
    """
    Test Case for Product Review Admin
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.product = Product.objects.create(
            title="Test Product",
            sku="test_sku",
            category=Category.objects.create(
                name="Test Category", friendly_name="Test Category"
            ),
            description="Test Product Description",
            wheel_size="26 inches",
            retail_price=999.99,
            sale_price=799.99,
            sale=True,
            image="path/to/test/image.jpg",
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=10,
            rating=4.5,
        )
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            review="Test Review",
            rating=5,
        )
        self.client = Client()
        self.client.login(username="testuser", password="testpass")
        self.site = AdminSite()

    def test_product_review_admin_list_display(self):
        """
        Test that the correct fields are displayed in the list view.
        """
        review_admin = ProductReviewAdmin(ProductReview, self.site)
        self.assertEqual(
            review_admin.list_display,
            ("product", "user", "rating", "created_at"),
        )
