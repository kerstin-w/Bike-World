from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.test.utils import setup_test_environment
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
import json
from decimal import Decimal


from bag.context_processors import bag_contents
from bag.views import AddToBagView
from bag.context_processors import bag_contents
from products.models import Product, Category


class BagViewTest(TestCase):
    """
    Test Case for Bag View
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()

    def test_bag_view_returns_200(self):
        """
        Test that the response status code is 200
        """
        response = self.client.get(reverse("view_bag"))
        self.assertEqual(response.status_code, 200)

    def test_bag_view_uses_correct_template(self):
        """
        Test that the correct tempalte is used
        """
        response = self.client.get(reverse("view_bag"))
        self.assertTemplateUsed(response, "bag/bag.html")


class AddToBagViewTest(TestCase):
    """
    Test Case for Add To Bag View
    """

    def setUp(self):
        """
        Test Data
        """
        self.factory = RequestFactory()
        self.category = Category.objects.create(
            name="category",
            friendly_name="Friendly category name",
        )
        self.product = Product.objects.create(
            title="product",
            sku="111",
            category=self.category,
            description="product description",
            wheel_size='26"',
            retail_price="100",
            sale_price="50",
            sale=True,
            brand="Brand",
            bike_type="Bike type",
            gender="0",
            material="Material",
            derailleur="Derailleur",
            stock="10",
            rating="4.8",
        )

    def test_add_to_bag_view_new_item(self):
        """
        Test that a new item is added correctly to the bag
        """
        # Create a session with a new item
        request = self.factory.post(
            reverse("add_to_bag", args=[self.product.id]),
            {"quantity": 3},
        )
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        # Add the new item
        response = AddToBagView.as_view()(request, self.product.id)
        # Check if the session bag is updated with the new item quantity
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.__class__, JsonResponse)
        self.assertEqual(
            request.session.get("bag"),
            {(self.product.id): 3},
        )
