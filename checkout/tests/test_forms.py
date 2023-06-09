from django.test import TestCase
from django.contrib.auth.models import User

from checkout.forms import OrderForm
from profiles.models import UserProfile


# Import the `TestCase` class from Django
class OrderFormTest(TestCase):
    """
    Test Case for Order Form
    """

    def setUp(self):
        """
        Test Data
        """
        self.user = User.objects.create_user(
            username="testuser", password="testpass"
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

    def test_order_form(self):
        """
        Test that the basic functionality of the OrderForm works correctly
        """
        form_data = {
            "full_name": "Test User",
            "email": "test@test.com",
            "phone_number": "123456789",
            "street_address1": "Test St.",
            "town_or_city": "Test City",
            "postcode": "1234",
            "country": "AT",
        }
        form = OrderForm(data=form_data)
        self.assertTrue(form.is_valid())
        order = form.save(commit=False)
        order.user_profile = self.user_profile
        order.save()
        self.assertEqual(order.full_name, "Test User")
        self.assertEqual(order.email, "test@test.com")
        self.assertEqual(order.phone_number, "123456789")
        self.assertEqual(order.street_address1, "Test St.")
        self.assertEqual(order.town_or_city, "Test City")
        self.assertEqual(order.postcode, "1234")
        self.assertEqual(order.country, "AT")

    def test_order_form_fields_required(self):
        """
        Test that the required fields in the OrderForm are correctly validated
        """
        form = OrderForm(
            {
                "full_name": "",
                "email": "",
                "phone_number": "",
                "street_address1": "",
                "town_or_city": "",
                "country": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["full_name"], ["This field is required."])
        self.assertEqual(form.errors["email"], ["This field is required."])
        self.assertEqual(
            form.errors["phone_number"], ["This field is required."]
        )
        self.assertEqual(
            form.errors["street_address1"], ["This field is required."]
        )
        self.assertEqual(
            form.errors["town_or_city"], ["This field is required."]
        )
        self.assertEqual(form.errors["country"], ["This field is required."])

    def test_order_form_classes(self):
        """
        Test that the classes for the form fields are correctly set
        """
        form = OrderForm()
        self.assertTrue(
            form.fields["full_name"].widget.attrs["class"],
            "stripe-style-input",
        )
        self.assertTrue(
            form.fields["email"].widget.attrs["class"], "stripe-style-input"
        )
        self.assertTrue(
            form.fields["phone_number"].widget.attrs["class"],
            "stripe-style-input",
        )
        self.assertTrue(
            form.fields["postcode"].widget.attrs["class"], "stripe-style-input"
        )
        self.assertTrue(
            form.fields["town_or_city"].widget.attrs["class"],
            "stripe-style-input",
        )
        self.assertTrue(
            form.fields["street_address1"].widget.attrs["class"],
            "stripe-style-input",
        )
        self.assertTrue(
            form.fields["street_address2"].widget.attrs["class"],
            "stripe-style-input",
        )
        self.assertTrue(
            form.fields["country"].widget.attrs["class"], "stripe-style-input"
        )

    def test_order_form_field_placeholders(self):
        """
        Test that the placeholders for the form fields are correctly set
        """
        form = OrderForm()
        self.assertEqual(
            form.fields["full_name"].widget.attrs["placeholder"], "Full Name *"
        )
        self.assertEqual(
            form.fields["email"].widget.attrs["placeholder"], "Email Address *"
        )
        self.assertEqual(
            form.fields["phone_number"].widget.attrs["placeholder"],
            "Phone Number *",
        )
        self.assertEqual(
            form.fields["street_address1"].widget.attrs["placeholder"],
            "Street Address 1 *",
        )
        self.assertEqual(
            form.fields["street_address2"].widget.attrs["placeholder"],
            "Street Address 2",
        )
        self.assertEqual(
            form.fields["town_or_city"].widget.attrs["placeholder"],
            "Town or City *",
        )
        self.assertEqual(
            form.fields["postcode"].widget.attrs["placeholder"], "Postal Code"
        )

    def test_order_form_max_length_street_address2(self):
        """
        Test that the maximum character length for street_address2 field
        is correctly validated
        """
        form_data = {
            "full_name": "Test User",
            "email": "test@test.com",
            "phone_number": "123456789",
            "street_address1": "Test St.",
            "street_address2": "x" * 81,  # Maximum length exceeded
            "town_or_city": "Test City",
            "postcode": "1234",
            "country": "AT",
        }
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["street_address2"],
            ["Ensure this value has at most 80 characters (it has 81)."],
        )

    def test_order_form_invalid_country(self):
        """
        Test that an invalid value for country raises a validation error
        """
        form_data = {
            "full_name": "Test User",
            "email": "test@test.com",
            "phone_number": "123456789",
            "street_address1": "Test St.",
            "street_address2": "",
            "town_or_city": "Test City",
            "postcode": "1234",
            "country": "XX",  # Invalid country name or ISO code entered
        }
        form = OrderForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["country"],
            ["Select a valid choice. XX is not one of the available choices."],
        )
