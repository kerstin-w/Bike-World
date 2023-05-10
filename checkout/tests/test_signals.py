from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from profiles.models import UserProfile


class SignalsCheckoutTest(TestCase):
    """
    Test Case for Checkout Signal
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@test.com"
        )
        # delete existing user_profile instance for testuser
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
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.country_name = "Austria"
        self.country_code = "AT"
        self.product = Product.objects.create(
            title="Test Product",
            sku="TESTSKU1234",
            category=self.category,
            description="Test description",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=4.5,
        )

        self.order = Order.objects.create(
            order_number="testorder",
            user_profile=self.user_profile,
            full_name=self.user.get_full_name(),
            email=self.user.email,
            phone_number="1234567890",
            country=self.country_code,
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
        self.line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )

    def test_update_on_save(self):
        """
        Test that the update_on_save signal correctly updates the grand total
        when an instance of OrderLineItem is created or updated.
        """
        self.assertEqual(self.order.grand_total, Decimal("509.99"))
        self.line_item.quantity = 3
        self.line_item.save()
        self.assertEqual(self.order.grand_total, Decimal("1499.97"))

    def test_update_on_delete(self):
        """
        Test that the update_on_delete signal correctly updates the grand total
        when an instance of OrderLineItem is deleted.
        """
        self.assertEqual(self.order.grand_total, Decimal("509.99"))
        self.line_item.delete()
        self.assertEqual(self.order.grand_total, Decimal("0.00"))
