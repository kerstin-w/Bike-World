from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from unittest.mock import patch


class SignalsTest(TestCase):
    """
    Test Case for User Profile Form
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = get_user_model().objects.create(
            email='test@test.com',
            password='testpassword',
            username='testuser'
        )

    @patch('profiles.signals.render_to_string')
    def test_send_welcome_email(self, mock_render):
        """
        Test the user_signed_up signal and send welcome email
        """
        mock_render.return_value = "Welcome to BIKE WORLD"
        with self.settings(DEFAULT_FROM_EMAIL='test@test.com'):
            user_signed_up.send(sender=self.user.__class__,
                                request=None, user=self.user)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Welcome to BIKE WORLD")
            self.assertEqual(mail.outbox[0].body, "Welcome to BIKE WORLD")
            self.assertEqual(mail.outbox[0].to, [self.user.email])
        mock_render.assert_called_once_with(
            'emails/welcome_mail.txt', {'user': self.user})
