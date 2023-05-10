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

    def test_order_model_generate_order_number(self):
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

    def test_order_model_update_total(self):
        """
        Test that the order total and grand total are updated correctly
        when a line item is added
        """
        order = Order.objects.create(
            user_profile=self.user_profile,
            full_name="Test User",
            email="test@test.com",
            phone_number="123456789",
            country="SE",
            town_or_city="Test City",
            street_address1="Test St",
            order_total=Decimal("0.00"),
            grand_total=Decimal("0.00"),
            original_bag="",
            stripe_pid="",
        )
        line_item = OrderLineItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            lineitem_total=Decimal("999.98"),
        )
        order.update_total()
        order.refresh_from_db()
        self.assertEqual(order.order_total, line_item.lineitem_total)
        self.assertEqual(order.delivery_cost, Decimal("10.00"))
        self.assertEqual(order.grand_total, Decimal("1009.98"))

    def test_order_model_save(self):
        """
        Test that the order number is set automatically if it hasn't been
        set already
        """
        order = Order(
            user_profile=self.user_profile,
            full_name="Test User",
            email="test@test.com",
            phone_number="123456789",
            country="SE",
            town_or_city="Test City",
            street_address1="Test St",
            order_total=Decimal("10.00"),
            grand_total=Decimal("10.00"),
            original_bag="",
            stripe_pid="",
        )
        order.save()
        self.assertIsNotNone(order.order_number)
        self.assertEqual(len(order.order_number), 10)

    def test_order_model_str_method(self):
        """
        Test the string method
        """
        order = Order(
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
        )
        order.save()
        expected_str = order.order_number
        actual_str = str(order)
        self.assertEqual(actual_str, expected_str)


class OrderLineItemTest(TestCase):
    """
    Test Case for Order Line Item Model
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
        self.order = Order.objects.create(
            user_profile=self.user_profile,
            full_name="Test User",
            email="test@test.com",
            phone_number="1234567890",
            country="AT",
            town_or_city="Test City",
            street_address1="Test St",
            order_total=Decimal("0.00"),
            grand_total=Decimal("0.00"),
            original_bag="",
            stripe_pid="",
        )

    def test_order_line_item_save_updates_lineitem_total(self):
        """
        Test that the lineitem_total field is correctly calculated and
        saved when an OrderLineItem is saved
        """
        # Create an order line item for the test product, with a quantity of 2
        line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        # Check that the lineitem_total has been set correctly
        self.assertEqual(line_item.lineitem_total, Decimal("999.98"))
