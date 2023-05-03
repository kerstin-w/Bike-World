from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite

from profiles.models import Wishlist, ProductReview, UserProfile
from profiles.admin import (
    WishlistAdmin,
    ProductReviewAdmin,
    UserProfileAdmin,
    OrderInline,
)
from products.models import Category, Product
from checkout.models import Order


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

    def test_product_review_admin_search_fields(self):
        """
        Test that the correct search fields are displayed in the list view.
        """
        review_admin = ProductReviewAdmin(ProductReview, self.site)
        self.assertEqual(
            review_admin.search_fields,
            ("product__title", "user__username", "review"),
        )


class UserProfileAdminTest(TestCase):
    """
    Test Case for User Profile Admin
    """

    def setUp(self):
        """
        Test Data
        """
        self.site = AdminSite()
        self.user_profile_admin = UserProfileAdmin(UserProfile, self.site)
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        # delete existing user_profile instance for testuser
        try:
            self.user_profile = UserProfile.objects.get(user=self.user)
            self.user_profile.delete()
        except UserProfile.DoesNotExist:
            pass

        # create new user_profile instance for testuser
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            default_full_name="John Doe",
            default_email="johndoe@test.com",
            default_phone_number="123456789",
            default_country="AT",
            default_postcode="1234",
            default_town_or_city="Vienna",
            default_street_address1="Test Street",
            default_street_address2="Apt 2B",
        )

    def test_user_profile_admin_list_display(self):
        """
        Test User Profile list_display
        """
        expected_admin_list_display = [
            "user",
            "default_full_name",
            "default_email",
            "orders_count",
        ]

        self.assertListEqual(
            list(self.user_profile_admin.list_display),
            expected_admin_list_display,
        )

    def test_user_profile_admin_inlines(self):
        """
        Test the related OrderInline is inside UserProfileAdmin.inlines
        """
        expected_inlines = [OrderInline]
        self.assertListEqual(self.user_profile_admin.inlines, expected_inlines)

    def test_user_profile_admin_search_fields(self):
        """
        Test the search fields in the user profile admin
        """
        expected_search_fields = [
            "user__username",
            "default_email",
            "default_phone_number",
            "default_full_name",
        ]

        self.assertListEqual(
            list(self.user_profile_admin.search_fields),
            expected_search_fields,
        )

    def test_user_profile_admin_fieldsets(self):
        """
        Test the fieldsets in the user profile admin
        """
        expected_fieldsets = [
            (None, {"fields": ("user", "default_full_name", "default_email")}),
            (
                "Delivery Information",
                {
                    "fields": (
                        "default_phone_number",
                        "default_country",
                        "default_postcode",
                        "default_town_or_city",
                        "default_street_address1",
                        "default_street_address2",
                    )
                },
            ),
        ]

        self.assertListEqual(
            list(self.user_profile_admin.fieldsets),
            expected_fieldsets,
        )

    def test_orders_count(self):
        """
        Test the orders_count returns correct count of orders
        """
        # create two orders for the user_profile
        Order.objects.create(
            user_profile=self.user_profile,
            full_name="customer 1",
            email="customer1@test.com",
        )
        Order.objects.create(
            user_profile=self.user_profile,
            full_name="customer 2",
            email="customer2@test.com",
        )

        expected_count = 2
        self.assertEqual(
            self.user_profile_admin.orders_count(self.user_profile),
            expected_count,
        )

    def test_orders(self):
        """
        Test the orders method returns all the orders of a user profile
        """
        order_1 = Order.objects.create(
            user_profile=self.user_profile,
            full_name="customer 1",
            email="customer1@example.com",
        )
        order_2 = Order.objects.create(
            user_profile=self.user_profile,
            full_name="customer 2",
            email="customer2@example.com",
        )

        expected_result = [order_2, order_1]
        self.assertQuerysetEqual(
            self.user_profile_admin.orders(self.user_profile),
            expected_result,
            transform=lambda x: x,
        )
