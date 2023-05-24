from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.test import TestCase

from allauth.account.signals import user_signed_up

from products.models import Category, Product
from profiles.models import ProductReview


class SignalsTest(TestCase):
    """
    Test Case for User Profile Form
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = get_user_model().objects.create(
            email="test@test.com", password="testpassword", username="testuser"
        )
        self.product = Product.objects.create(
            title="Test Product",
            sku="test_sku",
            category=Category.objects.create(
                name="Test Category", friendly_name="Test Category"
            ),
            description="Test Product Description",
            wheel_size="26 inches",
            retail_price=999.99,
            sale_price=799.99,
            sale=False,
            image="path/to/test/image.jpg",
            brand="Test Brand",
            bike_type="Test Bike Type",
            gender=0,
            material="Test Material",
            derailleur="Test Derailleur",
            stock=10,
            rating=4.5,
        )
        self.review = ProductReview.objects.create(
            product=self.product,
            user=self.user,
            review="Test Review",
            rating=5,
        )

    @patch("profiles.signals.render_to_string")
    def test_send_welcome_email(self, mock_render):
        """
        Test the user_signed_up signal and send welcome email
        """
        mock_render.return_value = "Welcome to BIKE WORLD"
        with self.settings(DEFAULT_FROM_EMAIL="test@test.com"):
            user_signed_up.send(
                sender=self.user.__class__, request=None, user=self.user
            )
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "Welcome to BIKE WORLD")
            self.assertEqual(mail.outbox[0].body, "Welcome to BIKE WORLD")
            self.assertEqual(mail.outbox[0].to, [self.user.email])
        mock_render.assert_called_once_with(
            "emails/welcome_mail.txt", {"user": self.user}
        )

    def test_send_review_deleted_email_from_list_signal(self):
        """
        Test if email is sent when a product review is deleted
        """
        # Setup signal
        signal_was_called = False

        @receiver(post_delete, sender=ProductReview)
        def signal_receiver(sender, instance, **kwargs):
            nonlocal signal_was_called
            signal_was_called = True

        message = render_to_string(
            "products/emails/review_deleted_mail.txt",
            {
                "user_name": self.user.username,
                "product_name": self.product.title,
                "message": "Your review for {} has been deleted".format(
                    self.product.title
                ),
            },
        )
        # Delete review and test signal
        self.review.delete()
        self.assertTrue(signal_was_called)

        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject, "Your review has been deleted"
        )
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertIn(message, mail.outbox[0].body)
