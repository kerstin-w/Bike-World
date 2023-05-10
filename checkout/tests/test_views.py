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
