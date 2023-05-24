from decimal import Decimal

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.admin.sites import AdminSite
from django.utils.html import format_html

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
            sale=False,
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
            sale=False,
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

        # Create two orders associated with the user_profile
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
        # Use assertQuerysetEqual to compare the expected and actual queryset
        # The transform parameter is used to convert the objects in queryset
        # to strings
        self.assertQuerysetEqual(
            self.user_profile_admin.orders(self.user_profile),
            expected_result,
            transform=lambda x: x,
        )

    def test_get_inline_instances_with_orders(self):
        """
        Ensure that get_inline_instances returns inline instances when
        user_profile object has related orders
        """

        # Create an order associated with the user_profile
        Order.objects.create(
            user_profile=self.user_profile,
            full_name="customer 1",
            email="customer1@test.com",
        )
        # Create a request and set the user attribute to self.user
        request = self.factory.get("/admin")
        request.user = self.user
        # Call get_inline_instances method with created request & user_profile
        inline_instances = self.user_profile_admin.get_inline_instances(
            request, user_profile=self.user_profile
        )
        self.assertEqual(len(inline_instances), 1)
        self.assertIsInstance(inline_instances[0], OrderInline)

    def test_get_inline_instances_without_orders(self):
        """
        Ensure that get_inline_instances returns empty list when
        user_profile object has no related orders
        """

        # Call the get_inline_instances method with None request & user_profile
        inline_instances = self.user_profile_admin.get_inline_instances(
            request=None, user_profile=self.user_profile
        )

        # Assert that the OrderInline is not displayed
        self.assertListEqual(inline_instances, [])

    def test_orders_short_description(self):
        """
        Test the short description is set as expected for orders function
        """
        self.assertEqual(
            self.user_profile_admin.orders.short_description, "Orders"
        )


class OrderInlineTest(TestCase):
    """
    Test Case for Order Inline Admin
    """

    def setUp(self):
        """
        Test Data
        """
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
        self.order = Order.objects.create(
            order_number="12345678",
            user_profile=self.user_profile,
            full_name=self.user.get_full_name(),
            email=self.user.email,
            phone_number="1234567890",
            country="AT",
            postcode="12345",
            town_or_city="Test Town",
            street_address1="Test Street 12",
            street_address2="Test Apt 123",
            delivery_cost=Decimal("10.00"),
            order_total=Decimal("499.99"),
            grand_total=Decimal("509.99"),
            original_bag="{}",
            stripe_pid="TestStripePID",
        )
        self.inline = OrderInline(UserProfile, AdminSite())

    def test_order_inline_view_order(self):
        """
        Test that the returned value of the view_order method matches
        the HTML link that points to the change page for the Order
        """
        result = self.inline.view_order(self.order)
        url = reverse("admin:checkout_order_change", args=[self.order.id])
        expected_output = format_html(
            '<a href="{}">{}</a>', url, self.order.order_number
        )
        self.assertEqual(result, expected_output)
