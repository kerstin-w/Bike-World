from django.contrib.auth.models import User
from django.db.models import Avg
from django.test import RequestFactory, TestCase, Client
from django.urls import reverse, resolve
from django.contrib.messages import get_messages
from unittest.mock import Mock, patch
from decimal import Decimal

from products.models import Category, Product
from profiles.models import Wishlist, ProductReview
from products.views import (
    WishlistProductsMixin,
    ProductReviewDeleteView,
    PermissionRequiredMixin,
)


class WishlistProductsMixinTest(TestCase):
    """
    Test Case for WishlistProductsMixin
    """

    def setUp(self):
        """
        Test Data Setup
        """
        # Set up Request Factory
        self.factory = RequestFactory()

        # create test user
        self.user = User.objects.create_user(
            username="testuser", password="password"
        )

        # create test category
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )

        # create test product
        self.product = Product.objects.create(
            title="Test Product",
            sku="12345",
            category=self.category,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )

        # create test wishlist
        self.wishlist = Wishlist.objects.create(
            user=self.user, product=self.product
        )

    def test_get_wishlist_products_authenticated(self):
        """
        Test that the get_wishlist_products method of
        WishlistProductsMixin for an authenticated user,
        returns a list of the wishlist products
        """
        # Set up the request with an authenticated user
        request = self.factory.get("/")
        request.user = self.user

        # Set up the mixin and assign the request
        mixin = WishlistProductsMixin()
        mixin.request = request

        # Call the get_wishlist_products method of the mixin
        wishlist_products = mixin.get_wishlist_products()

        # Check that the expected wishlist products are returned
        expected_wishlist_products = [self.product.id]
        self.assertEqual(list(wishlist_products), expected_wishlist_products)

    def test_get_wishlist_products_unauthenticated(self):
        """
        Test to assert that the get_wishlist_products method
        of WishlistProductsMixin for an unauthenticated user,
        returns an empty list
        """
        # Set up the request with an unauthenticated user
        request = self.factory.get("/")
        request.user = Mock(is_authenticated=False)

        # Set up the mixin and assign the request
        mixin = WishlistProductsMixin()
        mixin.request = request

        # Call the get_wishlist_products method of the mixin
        wishlist_products = mixin.get_wishlist_products()

        # Check that the expected result is an empty list
        self.assertEqual(list(wishlist_products), [])

    def test_is_product_in_wishlist_true(self):
        """
        Test to assert that the is_product_in_wishlist method of Wishlist
        returns True when the product is already in a wishlist
        """
        # Create a new wishlist object
        wishlist = Wishlist(user=self.user, product=self.product)

        # Assert that the is_product_in_wishlist method for
        # the new wishlist object returns True
        self.assertTrue(wishlist.is_product_in_wishlist())

    def test_is_product_in_wishlist_false(self):
        """
        Test to assert that the is_product_in_wishlist method of Wishlist
        returns False when the product is not in a wishlist
        """
        # Create a new product that is not in the wishlist
        product2 = Product.objects.create(
            title="test product 2",
            sku="12345",
            category=self.category,
            description="Test Description 2",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )

        # Create a new wishlist object with the user and product created above
        wishlist = Wishlist(user=self.user, product=product2)

        # Assert that the is_product_in_wishlist method for
        # the new wishlist object returns False
        self.assertFalse(wishlist.is_product_in_wishlist())


class ProductListViewTest(TestCase):
    """
    Tests for product list view
    """

    def setUp(self):
        """
        Test Data Setup
        """
        # create test category
        self.category1 = Category.objects.create(
            name="TestCategory1", friendly_name="Test Category1"
        )

        # create test product
        self.product1 = Product.objects.create(
            title="Test Product1",
            sku="12345",
            category=self.category1,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand1",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )

        self.category2 = Category.objects.create(
            name="TestCategory2", friendly_name="Test Category2"
        )

        self.product2 = Product.objects.create(
            title="Test Product2",
            sku="12345",
            category=self.category2,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=150.00,
            sale_price=145.00,
            sale=True,
            brand="Test Brand2",
            bike_type="Test Bike Type",
            gender=1,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=90,
            rating=4.2,
        )

    def test_product_list_view_template(self):
        """
        Test to check the existence of template and its content
        """
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "products/product_list.html")

    def test_product_list_view_with_filters(self):
        """
        Test that all filters work as expected
        """
        url = (
            reverse("products")
            + "?category=TestCategory1&brand=Test%20Brand1&gender=0&"
            + "sort_by=rating_desc"
        )
        response = self.client.get(url)
        self.assertIn(self.product1, response.context["products"])
        self.assertNotIn(self.product2, response.context["products"])

    def test_product_list_view_filter_by_brand(self):
        """
        Test that products are filtered by brand
        """
        response = self.client.get("/products/?brand=Test%20Brand2")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product2")
        self.assertNotContains(response, "Test Product1")

    def test_product_list_view_filter_by_gender(self):
        """
        Test that products are filtered by gender
        """
        response = self.client.get("/products/?gender=Womens")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product2")
        self.assertNotContains(response, "Test Product1")

    def test_product_list_view_filter_by_category(self):
        """
        Test that products are filtered by category
        """
        response = self.client.get("/products/?category=TestCategory1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Product1")
        self.assertNotContains(response, "Test Product2")

    def test_product_list_view_search(self):
        """
        Test that search keyword filter work as expected
        """
        url = reverse("products") + "?q=Test%20Product2"
        response = self.client.get(url)
        self.assertIn(self.product2, response.context["products"])
        self.assertNotIn(self.product1, response.context["products"])

        url = reverse("products") + "?q=Test"
        response = self.client.get(url)
        self.assertIn(self.product1, response.context["products"])
        self.assertIn(self.product2, response.context["products"])

    def test_product_list_view_sorting(self):
        """
        Test to check sorting feature works as expected
        """
        # Sorted by Price Descending
        url = reverse("products") + "?sort_by=price_desc"
        response = self.client.get(url)
        sorted_products = response.context["products"]
        self.assertEqual(sorted_products[0], self.product2)
        # Sorted by Price Ascending
        url = reverse("products") + "?sort_by=price_asc"
        response = self.client.get(url)
        sorted_products = response.context["products"]
        self.assertEqual(sorted_products[0], self.product1)
        # Sorted by Rating Descending
        url = reverse("products") + "?sort_by=rating_desc"
        response = self.client.get(url)
        sorted_products = response.context["products"]
        self.assertEqual(sorted_products[0], self.product2)
        # Default Sorting is by stock
        url = reverse("products")
        response = self.client.get(url)
        default_sorted_products = response.context["products"]
        self.assertEqual(default_sorted_products[0], self.product1)

    def test_product_list_view_no_products_found(self):
        """
        Test to check 0 products scenario
        """
        Product.objects.all().delete()
        url = (
            reverse("products")
            + "?category=TestCategory1"
            + "&brand=Test%20Brand1"
            + "&gender=0"
            + "&sort_by=rating_desc"
        )
        response = self.client.get(url)
        self.assertEqual(len(response.context["products"]), 0)

    def test__product_list_view_pagination(self):
        """
        Test the pagination feature
        """
        response = self.client.get(reverse("products"))
        self.assertTrue("is_paginated" in response.context)
        self.assertFalse(response.context["is_paginated"])

        # Create 25 more products
        for i in range(25):
            Product.objects.create(
                title=f"Test Product {i+3}",
                sku="12345",
                category=self.category2,
                description="Test Description",
                wheel_size="Test Wheel Size",
                retail_price=Decimal(50 + i),
                sale_price=Decimal(45 + i),
                sale=False,
                brand="Test Brand",
                bike_type="Test Bike Type",
                gender=1,
                material="Test Material",
                derailleur="Test Derailleur",
                stock=100,
                rating=Decimal(3.5 + i / 10),
            )

        response = self.client.get(reverse("products"))
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])

        self.assertTrue(len(response.context["products"]), 25)

        response = self.client.get(reverse("products") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])

        self.assertTrue(len(response.context["products"]), 2)

    @patch("products.views.WishlistProductsMixin.get_wishlist_products")
    def test_wishlist_products_mixin(self, mock_wishlist):
        """
        Test to check the WishlistProductMixin
        """
        response = self.client.get(reverse("products"))
        self.assertTrue(mock_wishlist.called)
        self.assertEqual(
            response.context["wishlist_products"], mock_wishlist()
        )


class ProductDetailViewTest(TestCase):
    """
    Test Case for ProductDetailView
    """

    @classmethod
    def setUpTestData(cls):
        # create test user
        cls.user = User.objects.create_user(
            username="testuser", password="password"
        )
        # Create a product for testing
        cls.category1 = Category.objects.create(
            name="TestCategory1", friendly_name="Test Category1"
        )
        cls.product = Product.objects.create(
            title="Test Product1",
            sku="12345",
            category=cls.category1,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand1",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )
        # Create a product review for testing
        cls.review = ProductReview.objects.create(
            product=cls.product,
            rating=5,
            review="Test review text",
            user=cls.user,
        )

    def test_product_detail_view_get_context_data(self):
        """
        Test the context data
        """
        # Create a mock request and response
        response = self.client.get(
            reverse("product_detail", kwargs={"pk": self.product.pk})
        )

        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)

        # Assert that the product and review are in the context
        self.assertIn("product", response.context)
        self.assertEqual(response.context["product"], self.product)
        self.assertIn("reviews", response.context)
        self.assertEqual(response.context["reviews"][0], self.review)

        # Assert that the title is set correctly
        self.assertIn("title", response.context)
        self.assertEqual(response.context["title"], self.product.title)

        # Assert that the wishlist_products are set correctly
        with patch(
            "products.views.ProductDetailView.get_wishlist_products"
        ) as mock_wishlist_products:
            mock_wishlist_products.return_value = []
            response = self.client.get(
                reverse("product_detail", kwargs={"pk": self.product.pk})
            )
            self.assertIn("wishlist_products", response.context)
            self.assertEqual(response.context["wishlist_products"], [])
            mock_wishlist_products.assert_called_once()


class ProductReviewDeleteViewTest(TestCase):
    """
    Test Case for ProductReviewDeleteView
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="12345"
        )
        self.admin = User.objects.create_superuser(
            username="admin", password="admin"
        )
        self.other_user = User.objects.create_user(
            username="Other User", email="other@test.com", password="password"
        )
        # create test category
        self.category1 = Category.objects.create(
            name="TestCategory1", friendly_name="Test Category1"
        )
        # create test product
        self.product = Product.objects.create(
            title="Test Product1",
            sku="12345",
            category=self.category1,
            description="Test Description",
            wheel_size="Test Wheel Size",
            retail_price=50.00,
            sale_price=45.00,
            sale=True,
            brand="Test Brand1",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=100,
            rating=3.5,
        )
        self.review = ProductReview.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            review="This is a test review.",
        )
        self.url = reverse("review_delete", kwargs={"pk": self.review.pk})

    def test_product_review_delete_view_permissions(self):
        """
        Test that the view extends from PermissionRequiredMixin
        """
        resolved_view = resolve(self.url)
        self.assertEqual(
            resolved_view.func.__name__,
            ProductReviewDeleteView.as_view().__name__,
        )
        self.assertEqual(
            resolved_view.func.view_class, ProductReviewDeleteView
        )
        self.assertEqual(
            resolved_view.func.__module__, ProductReviewDeleteView.__module__
        )
        self.assertTrue(
            issubclass(ProductReviewDeleteView, PermissionRequiredMixin)
        )

    def test_product_review_delete_view_handle_no_permission(self):
        """
        Test that checks if the handle_no_permission returns
        the expected error message and redirects to the homepage
        """
        self.client.force_login(self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        storage = get_messages(response.wsgi_request)
        self.assertIn(
            "You do not have permission to access this page.",
            [msg.message for msg in storage],
        )

    def test_product_review_delete_view_get_object(self):
        """
        Test that get_object returns the expected object
        instance based on the kwargs
        """
        view = ProductReviewDeleteView()
        view.kwargs = {"pk": self.review.pk}
        obj = view.get_object()
        self.assertEqual(obj, self.review)

    def test_product_review_delete_view_delete(self):
        """
        Test that a review and its rating is deleted successfully
        """
        self.client.force_login(self.admin)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 302)
        # Recalculate the product's rating after deleting the review
        product = Product.objects.get(id=self.product.id)
        rating = product.reviews.aggregate(Avg("rating"))["rating__avg"]
        product.rating = rating if rating else 0
        self.assertEqual(ProductReview.objects.count(), 0)
        self.assertAlmostEqual(product.rating, 0, places=4)
        storage = get_messages(response.wsgi_request)
        self.assertIn(
            "The review and associated rating have been deleted successfully.",
            [msg.message for msg in storage],
        )
