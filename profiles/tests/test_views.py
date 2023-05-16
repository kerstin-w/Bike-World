from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse, reverse_lazy

from checkout.models import Order, OrderLineItem
from profiles.forms import UserProfileForm, ProductReviewForm
from profiles.models import UserProfile, Wishlist, ProductReview
from profiles.views import ProfileView, ProfileUpdateView, WishlistView
from products.models import Product, Category


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
    """
    Test Case for AddToWishlist View
    """

    def setUp(self):
        """
        Test Data
        """
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
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"), {"success": True}
        )
        self.assertTrue(
            Wishlist.objects.filter(
                user=self.user, product=self.product
            ).exists()
        )

        # Check if the product was added to the user's wishlist
        wishlist_item = Wishlist.objects.get(
            user=self.user, product=self.product
        )
        self.assertEqual(wishlist_item.user, self.user)
        self.assertEqual(wishlist_item.product, self.product)

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

        self.assertEqual(response.status_code, 200)

        # Check if a new Wishlist object is added to the database
        self.assertTrue(
            Wishlist.objects.filter(
                user=self.user, product=self.product
            ).exists()
        )

    def test_add_to_wishlist_view_warns_if_product_already_in_wishlist(self):
        """
        Test that a warning message is shown if the user tries to add a product
        to their wishlist that is already in their wishlist
        """
        self.client.force_login(self.user)

        # Add the product to the user's wishlist
        wishlist_item = Wishlist(user=self.user, product=self.product)
        wishlist_item.save()

        # Try to add the same product again
        response = self.client.post(self.url)

        # Check that the warning message is displayed
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": False,
                "message": f"{self.product} is already in your wishlist!",
            },
        )

    def test_add_to_wishlist_view_product_not_found(self):
        """
        Test that a JSON response is returned if
        the product does not exist
        """
        self.client.force_login(self.user)
        invalid_product_id = 99999
        response = self.client.post(
            reverse("add_to_wishlist", args=[invalid_product_id]),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)
        json_response = response.json()
        self.assertEqual(json_response.get("success"), False)
        self.assertEqual(json_response.get("message"), "Product was not found")


class WishlistViewTest(TestCase):
    """
    Test Case for Wishlist View
    """

    def setUp(self):
        """
        Test Data
        """
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

    def test_wishlist_view_template(self):
        """
        Test that product names are in template
        """
        response = self.client.get(reverse("profile"))
        self.assertContains(response, "Product 1")
        self.assertContains(response, "Product 2")
        self.assertContains(response, "Product 3")

    def test_wishlist_view_queryset(self):
        """
        Test that WishlistView returns the correct queryset
        """
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

        # Check that the queryset contains the correct number of wishlist items
        queryset = response.context["wishlist"]
        self.assertEqual(
            queryset.count(), Wishlist.objects.filter(user=self.user).count()
        )

        # Check that each wishlist item belongs to the logged-in user
        for item in queryset:
            self.assertEqual(item.user, self.user)

    def test_wishlist_view_product_context(self):
        """
        Test that WishlistView returns the correct product context
        """
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)

        # Check that the context contains the correct number of products
        wishlist = response.context["wishlist"]
        products = [item.product for item in wishlist]
        self.assertEqual(
            len(products), Wishlist.objects.filter(user=self.user).count()
        )

        # Check that each product belongs to the logged-in user's wishlist
        wishlist_products = self.user.wishlist.values(
            "product_id",
            "product__title",
            "product__description",
            "product__image",
            "product__stock",
            "product__retail_price",
        )
        for product in products:
            self.assertIn(
                {
                    "product_id": product.id,
                    "product__title": product.title,
                    "product__description": product.description,
                    "product__image": product.image,
                    "product__stock": product.stock,
                    "product__retail_price": product.retail_price,
                },
                wishlist_products,
            )

    def test_wishlist_view_queryset_filter(self):
        """
        Test that the queryset filtering is correct
        """
        response = self.client.get(reverse("profile"))
        queryset = response.context["wishlist"]
        expected_queryset = Wishlist.objects.filter(user=self.user)
        self.assertQuerysetEqual(queryset, expected_queryset, ordered=False)

    def test__wishlist_view_get_queryset(self):
        """
        Test the get_queryset
        """
        # create a fake request object with the user set
        request = HttpRequest()
        request.user = self.user

        # create the view and call the get_queryset method
        view = WishlistView()
        view.request = request
        queryset = view.get_queryset()

        # assert that the queryset contains the expected item
        self.assertQuerysetEqual(
            queryset, Wishlist.objects.filter(user=self.user), ordered=False
        )


class WishlistDeleteViewTest(TestCase):
    """
    Test Case for WishlistDelete View
    """

    def setUp(self):
        """
        Test Data
        """
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
        self.wishlist = Wishlist.objects.create(
            user=self.user, product=self.product
        )
        self.delete_url = reverse("wishlist-delete", args=[self.wishlist.pk])

    def test_wishlist_delete_view_redirect_if_not_logged_in(self):
        """
        Test that a non-authenticated user is redirected to
        login page when trying to delete a wishlist item
        """
        self.client.logout()
        response = self.client.post(self.delete_url)
        self.assertRedirects(
            response, "/accounts/login/?next=" + self.delete_url
        )

    def test_wishlist_delete_view_delete_wishlist_item(self):
        """
        Test that a wishlist item can be successfully
        deleted by an authenticated user
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, "/profile/")
        self.assertFalse(Wishlist.objects.filter(pk=self.wishlist.pk).exists())

    def test_wishlist_delete_view_only_delete_own_wishlist_items(self):
        """
        Test that an authenticated user can only delete their own
        wishlist items, and not those of other users
        """
        another_user = User.objects.create_user(
            username="anotheruser", password="anotherpass"
        )
        another_wishlist = Wishlist.objects.create(
            user=another_user, product=self.product
        )
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            reverse("wishlist-delete", args=[another_wishlist.pk])
        )
        self.assertEqual(response.status_code, 405)

    def test_message_after_deleting_wishlist_item(self):
        """
        Test that a success message is displayed after deleting a wishlist item
        """
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(self.delete_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "<strong>Test Product</strong> has been "
            "removed from your wishlist!",
        )


class ProductReviewViewTest(TestCase):
    """
    Test Case for Product Review View
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", email="testuser@test.com", password="testpass"
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
        self.url = reverse(
            "product_review",
            kwargs={
                "order_number": self.order.order_number,
                "product_id": self.product.id,
            },
        )

    def test_product_review_view_form_submission(self):
        """
        Test submitting a valid review form
        """
        self.client.force_login(self.user)
        form_data = {"rating": 5, "review": "This is a great product!"}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))
        self.assertTrue(ProductReview.objects.exists())
        product_review = ProductReview.objects.first()
        self.assertEqual(product_review.product, self.product)
        self.assertEqual(product_review.user, self.user)
        self.assertEqual(product_review.review, "This is a great product!")
        self.assertEqual(product_review.rating, 5)

    def test_product_review_view_form_submission_invalid(self):
        """
        Test submitting an invalid review form
        """
        self.client.force_login(self.user)
        form_data = {"rating": 6, "review": ""}
        response = self.client.post(self.url, data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))
        self.assertFalse(ProductReview.objects.exists())

    def test_product_review_view_unauthenticated_user_is_redirected_to_login(
        self,
    ):
        """
        Test that an unauthenticated user is redirected to the login page
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, f"{reverse('account_login')}?next={self.url}"
        )

    def test_product_review_view_user_can_only_review_purchased_products(self):
        """
        Test that users can only review products they have purchased
        """
        # create a new product that the user has not purchased
        new_product = Product.objects.create(
            title="New Product",
            sku="NEWSKU1234",
            category=self.category,
            description="Test description",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=4.5,
        )
        new_url = reverse(
            "product_review",
            kwargs={
                "order_number": self.order.order_number,
                "product_id": new_product.id,
            },
        )
        # submit a review for the new product
        self.client.force_login(self.user)
        form_data = {"rating": 5, "review": "This is a great product!"}
        response = self.client.post(new_url, data=form_data)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(
            ProductReview.objects.filter(product=new_product).exists()
        )

    def test_product_review_view_success_message(self):
        """
        Test that a success message is displayed after submitting a review
        """
        self.client.force_login(self.user)
        form_data = {"rating": 5, "review": "This is a great product!"}
        response = self.client.post(self.url, data=form_data, follow=True)
        self.assertContains(
            response,
            "Your review for <strong>Test Product</strong> "
            "has been submitted!",
        )

    def test_product_review_view_get_context_data(self):
        """
        Test that the order_item is in the context
        and belongs to the current user
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("order_item", response.context)
        order_item = response.context["order_item"]
        self.assertEqual(order_item, self.order_line_item)


class ProductDeleteViewTest(TestCase):
    """
    Test Case for ProductDeleteView
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.category = Category.objects.create(name="test category")
        self.product = Product.objects.create(
            title="test product",
            sku="SK123",
            category=self.category,
            description="test description",
            wheel_size='18"',
            retail_price=500.00,
            brand="Trek",
            bike_type="Mountain Bike",
            gender=0,
        )
        self.url = reverse(
            "delete_product", kwargs={"product_id": self.product.id}
        )
        self.user = User.objects.create_superuser(
            username="admin", email="admin@test.com", password="adminpassword"
        )

    def test_product_delete_view_redirect_unauthendicated_user(self):
        """
        Test that an unauthenticated user gets redirected
        """
        response = self.client.get(self.url)
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_product_delete_view_redirect_if_logged_in_but_not_superuser(self):
        """
        Test that a user which is not superuser gets redirected
        """
        self.client.force_login(
            User.objects.create_user(
                username="user", email="user@test.com", password="testpassword"
            )
        )
        response = self.client.get(self.url)
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        self.assertEqual(response.status_code, 302)

    def test_product_delete_view_delete_product_success(self):
        """
        Test that a superuser can successfully delete a product
        """
        self.client.force_login(self.user)
        response = self.client.post(
            self.url,
        )
        # Test that success message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"{self.product.title} deleted!")
        # Test that user is redirected to correct URL
        self.assertRedirects(
            response, "/products/", fetch_redirect_response=False
        )
        self.assertEqual(response.status_code, 302)
        # Test that product is deleted from database
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_product_delete_view_get_object(self):
        """
        Test that the correct product is returned by get_object method
        """
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context_data["object"], self.product)
