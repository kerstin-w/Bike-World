from django.test import TestCase, RequestFactory, Client
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib.messages import get_messages
from django.db.models import QuerySet

from profiles.models import UserProfile, Wishlist
from checkout.models import Order, OrderLineItem
from products.models import Product, Category
from profiles.forms import UserProfileForm, ProductReviewForm
from profiles.views import ProfileView, ProfileUpdateView, OrderHistoryView


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


class OrderHistoryViewTest(TestCase):
    """
    Test Case for Order History View
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
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
            order_number="12345678",
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

        self.order_line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            lineitem_total=Decimal("499.99"),
        )

    def test_order_history_view_with_valid_order_number(self):
        """
        Test that the view returns a success response with a valid order number
        """
        response = self.client.get(reverse("order_history", args=["12345678"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "checkout/checkout_success.html")
        self.assertEqual(response.context["order"], self.order)
        self.assertTrue(response.context["from_profile"])

    def test_order_history_view_with_invalid_order_number(self):
        """
        Test that the view returns a 404 response with an invalid order number
        """
        response = self.client.get(reverse("order_history", args=["invalid"]))
        self.assertEqual(response.status_code, 404)

    def test_order_history_view_with_unauthenticated_user(self):
        """
        Test that the view redirects to the
        login page with an unauthenticated user
        """
        self.client.logout()
        response = self.client.get(reverse("order_history", args=["12345678"]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/profile/order_history/12345678/"
        )

    def test_order_history_view_with_different_user(self):
        """
        Test that the view returns forbidden with
        a different authenticated user
        """
        another_user = User.objects.create_user(
            username="anotheruser",
            password="anotherpass",
            email="anotheruser@test.com",
        )
        self.client.force_login(another_user)
        response = self.client.get(reverse("order_history", args=["12345678"]))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You do not have permission to access this Order Summary.",
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_order_history_view_template(self):
        """
        Test that the view uses the correct template
        """
        response = self.client.get(reverse("order_history", args=["12345678"]))
        self.assertTemplateUsed(response, "checkout/checkout_success.html")

    def test_order_history_template_contains_order_details(self):
        """
        Test that the template contains the specific order details
        """
        response = self.client.get(reverse("order_history", args=["12345678"]))
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product.retail_price)
        """
        self.order.grand_total and response.context["order"].grand_total
        are being converted to floats with 2 decimal places precision by
        using the quantize method with argument "0.01", before
        comparing them
        """
        self.assertEqual(
            float(self.order.grand_total.quantize(Decimal("0.01"))),
            float(
                response.context["order"].grand_total.quantize(Decimal("0.01"))
            ),
        )


class DeleteAccountViewTest(TestCase):
    """
    Test Case for Delete Account View
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.login(username="testuser", password="testpass")
        self.url = reverse("delete_account")

    def test_delete_account_view_delete_account(self):
        """
        Test that user account is deleted
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("index"))
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_delete_account_view_logout_user(self):
        """
        Test that the user is successfully logged out
        after sending a POST request
        """
        # Check if user is logged in before sending post request
        self.assertTrue(
            self.client.login(username="testuser", password="testpass")
        )
        response = self.client.post(self.url)

        # Check if user is logged out after sending post request
        self.assertFalse("_auth_user_id" in self.client.session)
        self.assertEqual(response.status_code, 302)

    def test_delete_account_view_success_message(self):
        """
        Test that a success message is displayed on the next
        page after account deletion
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "Your Account has been deleted successfully."
        )

    def test_delete_account_view_session_flush(self):
        """
        Test that the client's session is emptied after sending a POST request
        """
        self.client.post(self.url)
        self.client.session.flush()
        self.client.session.load()
        self.assertEqual(len(self.client.session.keys()), 0)


class AddToWishlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
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
        self.url = reverse("add_to_wishlist", args=[self.product.id])

    def test_add_to_wishlist_view_logged_in_user_can_add_to_wishlist(self):
        """
        Test that a user who is logged in can add a product to their wishlist
        """
        self.client.force_login(self.user)
        product_detail_url = reverse("product_detail", args=[self.product.id])
        response = self.client.post(
            self.url, HTTP_REFERER=product_detail_url, follow=True
        )
        messages = get_messages(response.wsgi_request)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_detail.html")
        self.assertIn(
            "<strong>Test Product</strong> added to your wishlist!",
            [str(m) for m in messages],
        )

        # Check if the product was added to the user's wishlist
        wishlist_item = Wishlist.objects.get(
            user=self.user, product=self.product
        )
        self.assertEqual(wishlist_item.user, self.user)
        self.assertEqual(wishlist_item.product, self.product)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, product_detail_url)

    def test_add_to_wishlist_view_logged_out_user_cannot_add_to_wishlist(self):
        """
        Test that a user who is not logged in cannot add a
        product to their wishlist
        """
        self.client.logout()
        response = self.client.post(self.url, follow=True)

        self.assertRedirects(response, "/accounts/login/?next=" + self.url)
        self.assertNotIn(self.product, self.user.wishlist.all())

    def test_add_to_wishlist_view_adds_new_wishlist_item_to_database(self):
        """
        Test that a new Wishlist object is added to the database
        when a product is added to the user's wishlist
        """
        self.client.force_login(self.user)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)

        # Check if a new Wishlist object is added to the database
        self.assertTrue(
            Wishlist.objects.filter(
                user=self.user, product=self.product
            ).exists()
        )


class WishlistViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.force_login(self.user)
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.wishlist1 = Wishlist.objects.create(
            user=self.user,
            product=Product.objects.create(
                title="Product 1",
                category=self.category,
                retail_price=Decimal("499.99"),
            ),
        )
        self.wishlist2 = Wishlist.objects.create(
            user=self.user,
            product=Product.objects.create(
                title="Product 2",
                category=self.category,
                retail_price=Decimal("499.99"),
            ),
        )
        self.wishlist3 = Wishlist.objects.create(
            user=self.user,
            product=Product.objects.create(
                title="Product 3",
                category=self.category,
                retail_price=Decimal("499.99"),
            ),
        )

    def test_wishlist_view_context(self):
        """
        Test context of wishlist view
        """
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile.html")

        wishlist = response.context["wishlist"]
        wishlist_products = [item.product for item in wishlist]

        # Check that the expected number of wishlist
        # items and products are in the context
        self.assertEqual(
            len(wishlist), Wishlist.objects.filter(user=self.user).count()
        )
        self.assertEqual(
            len(wishlist_products),
            Wishlist.objects.filter(user=self.user).count(),
        )

        # Check that the products in the context match
        # the ones in the wishlist queryset
        for product in wishlist_products:
            self.assertIn(
                product.pk,
                Wishlist.objects.values_list("product__pk", flat=True),
            )
