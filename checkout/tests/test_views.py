from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from unittest.mock import patch

import json
import stripe

from checkout.models import Order
from checkout.forms import OrderForm
from products.models import Product, Category
from profiles.models import UserProfile


class CacheCheckoutDataViewTest(TestCase):
    """
    Test case for cache_checkout_data view
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.url = reverse("cache_checkout_data")
        self.stripe_secret_key = settings.STRIPE_SECRET_KEY
        self.original_modify = stripe.PaymentIntent.modify

    def test_cache_checkout_data_with_valid_data_returns_200(self):
        """
        Test that the view returns an HTTP 200 response code when
        valid data is passed
        """
        # Set up test data
        bag = {"test_product": {"quantity": 1}}
        save_info = True
        user = {"username": "testuser"}

        # Construct POST data
        post_data = {
            "client_secret": "pi_1A2BCDEFGHIJKLMNOPQRS_secret_abcdefghij",
            "save_info": save_info,
        }
        session = self.client.session
        session["bag"] = bag
        session.save()

        # Mock PaymentIntent.modify() method
        stripe.PaymentIntent.modify = lambda *args, **kwargs: None

        # Make a POST request to the view
        response = self.client.post(
            self.url,
            {
                **post_data,
                **{
                    "metadata": json.dumps(
                        {
                            "bag": json.dumps(bag),
                            "save_info": save_info,
                            "username": user,
                        }
                    )
                },
            },
        )

        # Assert that the response has status code 200
        self.assertEqual(response.status_code, 200)

    def test_cache_checkout_data_with_invalid_data_returns_400(self):
        """
        Test that the view returns an HTTP 400 response code when
        invalid data is passed to it
        """
        # Construct POST data with missing client_secret key
        post_data = {"save_info": True}

        # Make a POST request to the view
        response = self.client.post(self.url, post_data)

        # Assert that the response has status code 400
        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        """
        Reset mock PaymentIntent.modify method
        """
        stripe.PaymentIntent.modify = self.original_modify


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

    def test_checkout_view_populate_order_form_with_user_profile(self):
        """
        Test if authenticated users have their profile information
        pre-populated in the order form
        """
        self.client.force_login(self.user)
        # Make a GET request to the checkout page and assert that the
        # correct data is pre-filled in the form
        response = self.client.get(self.checkout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "checkout/checkout.html")
        order_form = response.context["order_form"]
        self.assertEqual(order_form["full_name"].value(), "Test User")
        self.assertEqual(order_form["email"].value(), "testuser@test.com")

    @patch("checkout.views.UserProfile.objects.get")
    def test_checkout_view_authenticated_user_with_no_profile(
        self, mock_get_user_profile
    ):
        """
        Test that checks if order form is empty for users without profile
        """
        # Set up a user and log in
        user2 = User.objects.create_user(
            username="testuser2", password="testpass"
        )
        self.client.login(username=user2.username, password=user2.password)
        # Mock the UserProfile.objects.get() method to
        # raise the UserProfile.DoesNotExist exception
        mock_get_user_profile.side_effect = UserProfile.DoesNotExist()
        # Make a GET request to the checkout view
        response = self.client.get(reverse("checkout"))
        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)
        # Assert that the order_form context variable
        # is an instance of OrderForm
        self.assertIsInstance(response.context["order_form"], OrderForm)

    def test_checkout_view_missing_stripe_public_key(self):
        """
        Test if a warning message is displayed if the Stripe public
        key is not set in the environment variables
        """
        # Delete the Stripe public key from environment variables
        with self.settings(STRIPE_PUBLIC_KEY=""):
            response = self.client.get(self.checkout_url)
            self.assertEqual(response.status_code, 200)
            messages = list(response.context["messages"])
            self.assertEqual(len(messages), 1)
            self.assertEqual(
                str(messages[0]),
                "Stripe public key is missing. "
                "Did you forget to set it in your environment variables?",
            )
