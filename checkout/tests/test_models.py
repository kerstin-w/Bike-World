from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from profiles.models import UserProfile


class OrderModelTest(TestCase):
    """
    Test Case for Order Model
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        try:
            self.user_profile = UserProfile.objects.get(user=self.user)
            self.user_profile.delete()
        except UserProfile.DoesNotExist:
            pass
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            default_full_name=self.user.get_full_name(),
            default_email=self.user.email,
        )
        # create data for testing
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.product = Product.objects.create(
            title="Test Product",
            sku="TESTSKU1234",
            category=self.category,
            description="Test description",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=4.5,
        )

    def test__order_model_generate_order_number(self):
        """
        Test that the order number generated is 10 characters long and unique
        """
        order = Order.objects.create(
            user_profile=self.user_profile,
            full_name="Test User",
            email="test@test.com",
            phone_number="1234567890",
            country="AT",
            town_or_city="Test City",
            street_address1="Test St",
            order_total=Decimal("10.00"),
            grand_total=Decimal("10.00"),
            original_bag="",
            stripe_pid="",
        )
        self.assertEqual(len(order.order_number), 10)
        self.assertNotEqual(
            Order.objects.create(
                user_profile=self.user_profile,
                full_name="Test User",
                email="test@test.com",
                phone_number="123456789",
                country="AT",
                town_or_city="Test City",
                street_address1="Test St",
                order_total=Decimal("10.00"),
                grand_total=Decimal("10.00"),
                original_bag="",
                stripe_pid="",
            ).order_number,
            order.order_number,
        )
