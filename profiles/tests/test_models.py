from django.contrib.auth.models import User
from django.test import TestCase

from profiles.models import UserProfile


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
