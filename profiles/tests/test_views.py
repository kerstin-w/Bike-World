from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django_countries import countries
from decimal import Decimal
from django.contrib.messages import get_messages
from django.db.models import QuerySet

from profiles.models import UserProfile
from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from profiles.forms import UserProfileForm, ProductReviewForm
from profiles.views import ProfileView


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
        Test the get method
        """
        url = reverse("profile")
        request = self.factory.get(url)
        request.user = self.user
        response = ProfileView.as_view()(request)

        self.assertEqual(response.status_code, 200)

        context = response.context_data

        self.assertIn("on_profile_page", context)
        self.assertIn("user_profile_form", context)
        self.assertIn("orders", context)
        self.assertEqual(context["on_profile_page"], True)
        self.assertIsInstance(context["user_profile_form"], UserProfileForm)
        self.assertIsInstance(context["orders"], QuerySet)
        self.assertEqual(str(context["orders"][0]), "testorder")
