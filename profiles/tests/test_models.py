from django.contrib.auth.models import User
from django.test import TestCase

from profiles.models import UserProfile


class UserProfileTest(TestCase):
    def setUp(self):
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

