from django.test import TestCase
from django.contrib.auth.models import User

from profiles.models import UserProfile
from profiles.forms import UserProfileForm


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