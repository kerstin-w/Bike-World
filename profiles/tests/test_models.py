from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from profiles.models import UserProfile, Wishlist, ProductReview
from products.models import Product, Category


class UserProfileTest(TestCase):
    """
    Test View for UserProfile
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.user.userprofile.default_full_name = "Test User"
        self.user.userprofile.default_phone_number = "12345"
        self.user.userprofile.default_country = "AT"
        self.user.userprofile.default_postcode = "1234"
        self.user.userprofile.default_town_or_city = "Test City"
        self.user.userprofile.default_street_address1 = "Test Street"
        self.user.userprofile.default_street_address2 = "Apt. 4"
        self.user.userprofile.save()

    def test_create_user_profile(self):
        """
        Test creating a new UserProfile object
        """
        user = User.objects.create_user(
            username="testuser2",
            password="testpass",
            email="testuser2@example.com",
        )
        self.assertIsNotNone(user.userprofile)

    def test_update_user_profile(self):
        """
        Test updating an existing UserProfile object
        """
        self.user.userprofile.default_full_name = "Updated Test User"
        self.user.userprofile.default_phone_number = "56789"
        self.user.userprofile.default_country = "GR"
        self.user.userprofile.default_postcode = "A1B 2C3"
        self.user.userprofile.default_town_or_city = "Updated Test City"
        self.user.userprofile.default_street_address1 = "Updated Test Street"
        self.user.userprofile.default_street_address2 = "Unit 1"
        self.user.userprofile.save()

        # refresh from the database to ensure changes were saved
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(
            updated_profile.default_full_name, "Updated Test User"
        )
        self.assertEqual(updated_profile.default_phone_number, "56789")
        self.assertEqual(updated_profile.default_country, "GR")
        self.assertEqual(updated_profile.default_postcode, "A1B 2C3")
        self.assertEqual(
            updated_profile.default_town_or_city, "Updated Test City"
        )
        self.assertEqual(
            updated_profile.default_street_address1, "Updated Test Street"
        )
        self.assertEqual(updated_profile.default_street_address2, "Unit 1")

    def test_user_profile_string_representation(self):
        """
        Test the string representation of UserProfile object
        """
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(str(profile), self.user.username)


class WishlistTest(TestCase):
    """
    Test Case for Wishlist
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        # create data for testing
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.country_name = "Austria"
        self.country_code = "AT"
        self.product1 = Product.objects.create(
            title="Test Product 1",
            sku="TESTSKU1234",
            category=self.category,
            description="Test description 1",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=4.5,
        )
        self.product2 = Product.objects.create(
            title="Test Product 2",
            sku="TESTSKU1235",
            category=self.category,
            description="Test description 2",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=5,
        )

    def test_add_product_to_wishlist(self):
        """
        Test adding a product to the wishlist
        """
        wishlist_item = Wishlist(user=self.user, product=self.product1)
        wishlist_item.save()
        wishlist_items_count = self.user.wishlist.count()
        self.assertEqual(wishlist_items_count, 1)

    def test_is_product_in_wishlist(self):
        """
        Test the is_product_in_wishlist method
        """

        wishlist_item = Wishlist.objects.create(
            user=self.user, product=self.product1
        )
        # Create a new product that is not in the user's wishlist
        new_product = Product.objects.create(
            title="New Product",
            description="A new product",
            retail_price=Decimal("500.00"),
            stock=10,
            category=self.category,
        )
        # Check that the user's wishlist contains the original product
        self.assertTrue(wishlist_item.is_product_in_wishlist())
        # Check that the user's wishlist does not contain the new product
        self.assertFalse(
            Wishlist.objects.filter(
                user=self.user, product=new_product
            ).exists()
        )


class ProductReviewTest(TestCase):
    """
    Test Case for Product Review
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        # create data for testing
        self.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )
        self.country_name = "Austria"
        self.country_code = "AT"
        self.product = Product.objects.create(
            title="Test Product 1",
            sku="TESTSKU1234",
            category=self.category,
            description="Test description 1",
            retail_price=Decimal("499.99"),
            stock=10,
            rating=4.5,
        )

    def test_product_rating_is_updated(self):
        """
        Test that the product rating is updated after creating these reviews
        """
        ProductReview.objects.create(
            product=self.product,
            user=self.user,
            review="This bike is great!",
            rating=4,
        )
        ProductReview.objects.create(
            product=self.product,
            user=self.user,
            review="This bike is awesome!",
            rating=5,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.rating, 4.5)
