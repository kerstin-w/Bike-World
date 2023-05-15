from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages import get_messages
from django.test.utils import setup_test_environment
from django.http import JsonResponse
from django.contrib.auth.models import User
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

    def test_add_to_bag_view_existing_item(self):
        """
        Test that an existing item is added correctly to the bag
        and the quantity is updated correctly
        """
        # Add an initial item to the bag
        initial_quantity = 2
        request = self.factory.post(
            reverse("add_to_bag", args=[self.product.id]),
            {"quantity": initial_quantity},
        )
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        response = AddToBagView.as_view()(request, self.product.id)
        # Check if the session bag is updated with the initial quantity
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.__class__, JsonResponse)
        self.assertEqual(
            request.session.get("bag"),
            {self.product.id: initial_quantity},
        )

        # Set the 'bag' key in the session
        request.session["bag"] = {self.product.id: initial_quantity}

        # Add the same item with a different quantity
        existing_item_quantity = request.session["bag"].get(self.product.id, 0)
        new_quantity = 3
        request = self.factory.post(
            reverse("add_to_bag", args=[self.product.id]),
            {"quantity": new_quantity},
        )
        request.user = AnonymousUser()
        middleware.process_request(request)
        request.session.save()

        # Set the 'bag' key in the session
        request.session["bag"] = {self.product.id: initial_quantity}
        # Update existing_item_quantity with the current quantity in the bag
        existing_item_quantity = request.session["bag"].get(self.product.id, 0)
        response = AddToBagView.as_view()(request, self.product.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.__class__, JsonResponse)

        updated_quantity = existing_item_quantity + new_quantity
        # Check if the session bag is updated with the updated quantity
        expected_bag = {self.product.id: updated_quantity}
        self.assertEqual(
            request.session.get("bag"),
            expected_bag,
        )

    def test_add_to_bag_view_with_bag_contents(self):
        """
        Test that bag_contents is updated correctly
        """
        request = self.factory.post(
            reverse("add_to_bag", args=[self.product.id]),
            {"quantity": 1},
        )
        request.user = AnonymousUser()
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        response = AddToBagView.as_view()(request, self.product.id)
        bag_content = bag_contents(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.__class__, JsonResponse)

        response_data = json.loads(response.content.decode("utf-8"))

        self.assertEqual(
            response_data,
            {
                "quantity": 1,
                "total_quantity": 1,
                "bag_contents": render_to_string(
                    "components/bag_offcanvas.html",
                    {"bag": bag_content},
                    request=request,
                ),
            },
        )

    def test_add_to_bag_view_nonexistent_product(self):
        """
        Test adding a non-existent product to the bag
        """
        # Create a request with the necessary data
        item_id = 9999  # ID of a non-existent product
        quantity = 1
        url = reverse("add_to_bag", args=[item_id])
        request = self.factory.post(url, {"quantity": quantity})

        # Call the view
        response = AddToBagView.as_view()(request, item_id)

        # Verify the response
        self.assertEqual(response.status_code, 400)
        expected_data = {"error": "The product does not exist."}
        self.assertJSONEqual(response.content, expected_data)


class AdjustBagViewTest(TestCase):
    """
    Test that a new item is added correctly to the bag
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

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

    def test_adjust_bag_view_add_product_to_bag(self):
        """
        Test that a product already in the bag is added again and
        updates quantity
        """
        response = self.client.post(
            reverse("adjust_bag", args=[self.product.id]), {"quantity": 2}
        )

        # Verify the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("view_bag"))

        # Verify that the bag has been updated
        bag = self.client.session.get("bag", {})
        self.assertEqual(bag.get(str(self.product.id)), 2)

        # Verify success message
        messages = [m.message for m in get_messages(response.wsgi_request)]
        expected_message = f"You updated <strong>{self.product.title}</strong> quantity to <strong>2</strong>!"
        self.assertTrue(
            any(expected_message in message for message in messages)
        )

    def test_adjust_bag_view_update_product_quantity(self):
        """
        Test that the quantity can be updated
        """
        # Add an item to the bag
        self.client.post(
            reverse("adjust_bag", args=[self.product.id]), {"quantity": 2}
        )

        # Send a POST request to update the quantity of the item in the bag
        response = self.client.post(
            reverse("adjust_bag", args=[self.product.id]), {"quantity": 3}
        )

        # Verify the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("view_bag"))

        # Verify that the bag has been updated
        bag = self.client.session.get("bag", {})
        self.assertEqual(bag.get(str(self.product.id)), 3)

        # Verify success message
        messages = [m.message for m in get_messages(response.wsgi_request)]
        expected_message = f"You updated <strong>{self.product.title}</strong> quantity to <strong>3</strong>!"
        self.assertTrue(
            any(expected_message in message for message in messages)
        )

    def test_adjust_bag_view_remove_product_from_bag(self):
        """
        Test that a product can be removed
        """
        # Add an item to the bag
        self.client.post(
            reverse("adjust_bag", args=[self.product.id]), {"quantity": 2}
        )

        # Send a POST request to remove the item from the bag
        response = self.client.post(
            reverse("adjust_bag", args=[self.product.id]), {"quantity": 0}
        )

        # Verify the response status code and redirection
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("view_bag"))

        # Verify that the item has been removed from the bag
        bag = self.client.session.get("bag", {})
        self.assertNotIn(str(self.product.id), bag)

        # Verify success message
        messages = [m.message for m in get_messages(response.wsgi_request)]
        expected_message = (
            f"You removed <strong>{self.product.title}</strong>!"
        )
        self.assertTrue(
            any(expected_message in message for message in messages)
        )
