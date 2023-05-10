from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from decimal import Decimal
from unittest.mock import patch
import json

from checkout.models import Order
from checkout.forms import OrderForm
from bag.context_processors import bag_contents
from products.models import Product, Category
from profiles.models import UserProfile


class CheckoutViewsTest(TestCase):
    """
    Test Case for checkout view
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.checkout_url = reverse("checkout")
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.product = Product.objects.create(
            title="Test Product",
            sku="TESTSKU1234",
            category=self.category,
            description="Test description",
            retail_price=10,
            stock=10,
            rating=4.5,
        )
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
            default_full_name="Test User",
            default_email=self.user.email,
        )
        # Set up session and bag variables for the tests
        self.bag = {str(self.product.id): 1}
        self.session = self.client.session
        self.session["bag"] = self.bag
        self.session.save()

    def test_checkout_view_get(self):
        """
        Test GET request to checkout view
        """
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "checkout/checkout.html")

    def test_checkout_view_post_valid_order_form(self):
        """
        Test POST request to checkout view with valid order form
        """
        # Define variables for the Stripe transaction
        stripe_total = (
            Decimal(self.bag[str(self.product.id)]) * self.product.retail_price
        )
        stripe_total_in_cents = int(stripe_total * 100)
        # Use mock object to test fake Stripe transaction
        with patch("stripe.PaymentIntent.create") as stripe_create_mock:
            # Set return values for the mock object
            stripe_create_mock.return_value.client_secret = "test_client"
            stripe_create_mock.return_value.amount = stripe_total_in_cents
            stripe_create_mock.return_value.currency = "EUR"
            stripe_create_mock.return_value.status = "succeeded"
            # Make the request to the checkout view with fake data
            response = self.client.post(
                self.checkout_url,
                {
                    "full_name": "Test User",
                    "email": "testuser@example.com",
                    "phone_number": "1234567890",
                    "country": "US",
                    "postcode": "12345",
                    "town_or_city": "Test City",
                    "street_address1": "Test Street 1",
                    "street_address2": "Test Street 2",
                    "client_secret": "test_client_secret_secret",
                },
            )
            # Assert that the response contains the correct status code,
            # redirect URL, and creates a new order object with the
            # correct data
            self.assertEqual(response.status_code, 302)
            self.assertEqual(
                response.url,
                reverse(
                    "checkout_success",
                    args=[Order.objects.latest("id").order_number],
                ),
            )
            self.assertEqual(Order.objects.count(), 1)
            order = Order.objects.first()
            self.assertEqual(order.full_name, "Test User")
            self.assertEqual(order.email, "testuser@example.com")
            self.assertEqual(order.phone_number, "1234567890")
            self.assertEqual(order.country, "US")
            self.assertEqual(order.postcode, "12345")
            self.assertEqual(order.town_or_city, "Test City")
            self.assertEqual(order.street_address1, "Test Street 1")
            self.assertEqual(order.street_address2, "Test Street 2")
            bag_dict = json.loads(order.original_bag)
            self.assertEqual(bag_dict, self.session["bag"])
            self.assertEqual(order.stripe_pid, "test_client")
