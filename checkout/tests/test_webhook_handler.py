from django.core import mail
from django.http import HttpRequest
from django.test import TestCase

from checkout.models import Order
from checkout.webhook_handler import StripeWH_Handler


class TestStripeWebhookHandler(TestCase):
    """
    Test Case for Stripe Wekbooh Handler
    """

    def setUp(self):
        """
        Test Data
        """
        self.request = HttpRequest()
        self.order = Order.objects.create(
            full_name="Test User",
            email="test@test.com",
            phone_number="01234567890",
            country="GB",
            postcode="AB12 3CD",
            town_or_city="Test Town",
            street_address1="Test Street",
            street_address2="",
            grand_total=50.00,
            original_bag='{"1": 1}',
            stripe_pid="stripe_pid",
        )
        self.handler = StripeWH_Handler(self.request)

    def test_handle_event(self):
        # Creating a mock event
        event = {
            "type": "charge.failed",
        }

        # Call the webhook handler
        response = self.handler.handle_event(event)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("Webhook received", response.content.decode())

    def test_send_confirmation_email(self):
        # Call the send_confirmation_email method
        self.handler._send_confirmation_email(self.order)

        # Check confirmation email is sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"BIKE WORLD Confirmation for Order Number "
            f"{self.order.order_number}",
        )
