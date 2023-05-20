from django.test import TestCase
from django.contrib.auth.models import User
from allauth.account.forms import LoginForm

from profiles.models import UserProfile
from profiles.forms import UserProfileForm, ProductReviewForm, CustomLoginForm
from products.models import Product


class UserProfileFormTest(TestCase):
    """
    Test Case for User Profile Form
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass", email="testuser@test.com"
        )

        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpass2",
            email="testuser2@test.com",
        )

        # delete existing user_profile instance for testuser
        try:
            self.user_profile = UserProfile.objects.get(user=self.user)
            self.user_profile.delete()
        except UserProfile.DoesNotExist:
            pass

        # create new user_profile instance for testuser
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            default_full_name="John Doe",
            default_email="testuser@test.com",
            default_phone_number="123456789",
            default_country="AT",
            default_postcode="1234",
            default_town_or_city="Vienna",
            default_street_address1="Test Street",
            default_street_address2="Apt 2B",
        )

    def test_user_profile_form_fields(self):
        """
        Test the Form fields
        """
        form = UserProfileForm(instance=self.user_profile)
        expected_fields = [
            "default_full_name",
            "default_email",
            "default_phone_number",
            "default_country",
            "default_postcode",
            "default_town_or_city",
            "default_street_address1",
            "default_street_address2",
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_user_profile_form_initial_data(self):
        """
        Test the initial data for the form fields
        """
        form = UserProfileForm(instance=self.user_profile)
        self.assertEqual(form.initial["default_email"], self.user.email)
        self.assertEqual(
            form.initial["default_full_name"],
            self.user_profile.default_full_name,
        )

    def test_user_profile_form_valid_form(self):
        """
        Test that a form is valid when valid data is entered
        """
        form_data = {
            "default_full_name": "Jane Doe",
            "default_email": "janedoe@test.com",
            "default_phone_number": "123456789",
            "default_country": "SE",
            "default_postcode": "12345",
            "default_town_or_city": "City",
            "default_street_address1": "Test Avenue",
            "default_street_address2": "Unit 2",
        }
        form = UserProfileForm(data=form_data, instance=self.user_profile)
        self.assertTrue(form.is_valid())
        updated_profile = form.save()
        self.assertEqual(updated_profile.default_full_name, "Jane Doe")
        self.assertEqual(updated_profile.default_email, "janedoe@test.com")
        self.assertEqual(updated_profile.default_phone_number, "123456789")
        self.assertEqual(updated_profile.default_country.code, "SE")
        self.assertEqual(updated_profile.default_postcode, "12345")
        self.assertEqual(updated_profile.default_town_or_city, "City")
        self.assertEqual(
            updated_profile.default_street_address1, "Test Avenue"
        )
        self.assertEqual(updated_profile.default_street_address2, "Unit 2")

    def test_user_profile_form_blank_form(self):
        """
        Test that a form returns error when form is blank
        """
        form = UserProfileForm(data={}, instance=self.user_profile)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)
        self.assertIn("default_full_name", form.errors)
        self.assertIn(
            "This field is required.", form.errors["default_full_name"]
        )
        self.assertIn("default_email", form.errors)
        self.assertIn("This field is required.", form.errors["default_email"])

    def test_user_profile_form_email_already_in_use(self):
        """
        Test that from returns error when User tries to updated
        email to and email that is already in use
        """
        # log in as the first user
        self.client.login(
            username=self.user.username, password=self.user.password
        )
        # submit form with a email address already in use by user2
        form_data = {
            "default_full_name": "John Doe",
            "default_email": self.user2.email,
            "default_phone_number": "123456789",
            "default_country": "AT",
            "default_postcode": "1234",
            "default_town_or_city": "Vienna",
            "default_street_address1": "Test Street",
            "default_street_address2": "Apt 2B",
        }
        form = UserProfileForm(data=form_data, instance=self.user_profile)
        self.assertFalse(form.is_valid())
        self.assertTrue("default_email" in form.errors)
        self.assertEqual(
            form.errors["default_email"][0], "Email is already in use."
        )

    def test_user_profile_form_save_user_changes(self):
        """
        Test that save() method correctly saves changes to
        User instance
        """
        form_data = {
            "default_full_name": "John Doe",
            "default_email": "newemail@test.com",
            "default_phone_number": "123456789",
            "default_country": "AT",
            "default_postcode": "1234",
            "default_town_or_city": "Vienna",
            "default_street_address1": "Test Street",
            "default_street_address2": "Apt 2B",
        }
        form = UserProfileForm(data=form_data, instance=self.user_profile)
        self.assertTrue(form.is_valid())
        user = self.user_profile.user
        self.assertEqual(user.email, "testuser@test.com")
        form.save()
        updated_user = User.objects.get(pk=self.user.pk)
        self.assertEqual(updated_user.email, "newemail@test.com")


class ProductReviewFormTest(TestCase):
    """
    Test Case for Product Review Form
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.product = Product.objects.create(
            title="Test Product",
            description="Test Description",
            retail_price=1000.0,
            brand="Test Brand",
            bike_type="Test Type",
            gender=0,
            stock=99,
        )

    def test_product_review_form_valid_form(self):
        """
        Test that the form is valid
        """
        form_data = {
            "review": "This is a test review",
            "rating": 4,
        }
        form = ProductReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_product_review_form_blank_data(self):
        """
        Test that the form returns error when form is blank
        """
        form = ProductReviewForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                "review": ["This field is required."],
                "rating": ["This field is required."],
            },
        )

    def test_product_review_form_save_review(self):
        """
        Test that the form saves review and rating
        """
        form_data = {
            "review": "This is a test review",
            "rating": 4,
        }
        form = ProductReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        review = form.save(commit=False)
        review.product = self.product
        review.user = self.user
        review.save()
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.rating, 4.0)

    def test_product_review_form_invalid_rating(self):
        """
        Test that the form returns an error when the rating is invalid
        """
        data = {
            "rating": 6,
            "review": "Test Review",
        }
        form = ProductReviewForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)
        self.assertEqual(len(form.errors["rating"]), 1)
        self.assertEqual(
            form.errors["rating"][0],
            "Ensure this value is less than or equal to 5.",
        )


class CustomLoginFormTest(TestCase):
    """
    Test Case for Custom Login Form
    """

    def test_autofocus_disabled(self):
        """
        Test form disables autofocus
        """
        form = CustomLoginForm()
        self.assertIsInstance(form, LoginForm)
        self.assertFalse("autofocus" in form.fields["login"].widget.attrs)
