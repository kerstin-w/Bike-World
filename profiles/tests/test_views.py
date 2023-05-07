from django.test import TestCase, RequestFactory, Client
from django.http import HttpRequest
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.messages import get_messages
from django.db.models import QuerySet

from profiles.models import UserProfile
from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from profiles.forms import UserProfileForm, ProductReviewForm
from profiles.views import ProfileView, ProfileUpdateView


class ProfileViewTest(TestCase):
    """
    Test Case for Profile View
    """

    def setUp(self):
        """
        Test Datat
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@test.com"
        )
        self.client.login(username="testuser", password="testpass")
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
        self.order_lines = []

        # create data for testing
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

        order_line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            lineitem_total=Decimal("499.99"),
        )
        self.order_lines.append(order_line_item)

        self.order.lineitems.add(*self.order_lines)

    def tearDown(self):
        # Clean up
        pass

    def test_profile_view_get(self):
        """
        Test that a GET request to the profile view returns a status code
        of 200, and that the response contains the expected context data
        """
        url = reverse("profile")
        request = self.factory.get(url)
        request.user = self.user
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        context = response.context_data

        self.assertIn("user_profile_form", context)
        self.assertIn("orders", context)
        self.assertIsInstance(context["user_profile_form"], UserProfileForm)
        self.assertIsInstance(context["orders"], QuerySet)
        self.assertEqual(str(context["orders"][0]), "testorder")

    def test_profile_view_get_context_data(self):
        """
        Test the context data
        """
        url = reverse("profile")
        request = self.factory.get(url)
        request.user = self.user
        response = ProfileView.as_view()(request)
        # test expected context content
        context = response.context_data
        self.assertIn("user_profile_form", context)
        self.assertIn("orders", context)
        self.assertIn("wishlist", context)
        self.assertIn("order_item_ids", context)
        # test order_item_ids context content
        order_item_ids = context["order_item_ids"]
        self.assertEqual(len(order_item_ids), 1)
        self.assertEqual(
            order_item_ids[0]["product"].title, self.product.title
        )
        self.assertEqual(
            order_item_ids[0]["order_number"], self.order.order_number
        )
        self.assertIsInstance(
            order_item_ids[0]["review_form"], ProductReviewForm
        )

    def test_profile_view_get_queryset(self):
        """
        Test that the get_queryset method returns the
        orders for the current user's UserProfile
        """
        url = reverse("profile")
        request = self.factory.get(url)
        request.user = self.user
        view = ProfileView()
        view.request = request
        queryset = view.get_queryset()
        self.assertEqual(
            list(queryset),
            list(Order.objects.filter(user_profile=self.user_profile)),
        )

    def test_profile_view_not_logged_in(self):
        """
        Test that a user who is not logged in is redirected to the login page
        if they attempt to access the profile page
        """
        self.client.logout()
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/accounts/login/?next={url}",
            status_code=302,
            target_status_code=200,
        )

    def test_profile_view_logged_in(self):
        """
        Test that a user who is logged in can access the profile page
        """
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class ProfileUpdateViewTest(TestCase):
    """
    Test Case for Profile Update View
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.url = reverse("profile_update")
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
        self.client.login(username="testuser", password="testpass")

    def test_profile_update_view_get_form_kwargs(self):
        """
        Test that the get_form_kwargs method of the ProfileUpdateView
        returns a dictionary containing the user profile instance
        as the instance key, and the user email as the initial key
        """
        view = ProfileUpdateView()
        view.request = HttpRequest()
        view.request.user = self.user
        view.kwargs = {}
        kwargs = view.get_form_kwargs()
        self.assertEqual(kwargs["instance"], self.user_profile)
        self.assertEqual(kwargs["initial"], {"default_email": self.user.email})

    def test_profile_update_view_get(self):
        """
        Test that a GET request to the profile update view returns
        a status code of 200
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_profile_update_view_post_valid_form(self):
        """
        Test that a POST request to the profile update view with
        valid form data updates the user profile and user account,
        and redirects the user to the profile page
        """
        data = {
            "default_full_name": "Test User",
            "default_email": "newemail@test.com",
            "default_phone_number": "1234567890",
            "default_country": "AT",
            "default_postcode": "12345",
            "default_town_or_city": "Test City",
            "default_street_address1": "123 Test St",
            "default_street_address2": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse_lazy("profile"),
            status_code=302,
            target_status_code=200,
        )

        user_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(user_profile.default_full_name, "Test User")
        self.assertEqual(user_profile.default_email, "newemail@test.com")
        self.assertEqual(user_profile.default_phone_number, "1234567890")
        self.assertEqual(user_profile.default_country, "AT")
        self.assertEqual(user_profile.default_postcode, "12345")
        self.assertEqual(user_profile.default_town_or_city, "Test City")
        self.assertEqual(user_profile.default_street_address1, "123 Test St")
        self.assertEqual(user_profile.default_street_address2, None)

        user = User.objects.get(username=self.user.username)
        self.assertEqual(user.email, "newemail@test.com")

    def test_profile_update_view_form_invalid(self):
        """
        Test that a POST request to the profile update view with
        invalid form data returns a message indicating that
        the profile update failed.
        """
        data = {
            "default_full_name": "Test User",
            "default_email": "invalidmail",
            "default_phone_number": "1234567890",
            "default_country": "AT",
            "default_postcode": "12345",
            "default_town_or_city": "Test City",
            "default_street_address1": "123 Test St",
            "default_street_address2": "Apt. 4",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Failed to update your profile.")

    def test_profile_update_view_get_context_data(self):
        """
        Test that the get_context_data method of the ProfileUpdateView
        returns a dictionary containing a user profile form instance
        as the "user_profile_form" key, and that the instance of the
        form is the same as the user profile instance for the current user
        """
        request = HttpRequest()
        request.user = self.user
        view = ProfileUpdateView()
        view.request = request
        context = view.get_context_data()
        self.assertIn("user_profile_form", context)
        self.assertIsInstance(context["user_profile_form"], UserProfileForm)
        self.assertEqual(
            context["user_profile_form"].instance, self.user_profile
        )
