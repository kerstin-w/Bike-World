from django.test import TestCase
from django.urls import reverse

from support.forms import ContactForm


class ContactViewTest(TestCase):
    """
    Test Case for Support Contact View
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("contact")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        """
        Test Data
        """
        self.form_data = {
            "name": "John Doe",
            "email": "johndoe@test.com",
            "subject": "Test message",
            "message": "This is a test.",
        }

    def test_contact_view_url(self):
        """
        Test Contact View URL
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_contact_view_template(self):
        """
        Test Contact View uses correct template
        """
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "support/contact.html")

    def test_contact_view_uses_correct_form(self):
        """
        Test Contact View uses correct form
        """
        response = self.client.get(self.url)
        self.assertIsInstance(response.context["form"], ContactForm)

    def test_contact_view_form_valid(self):
        """
        Test Contact View form is valid
        """
        response = self.client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse("index"))

    def test_contact_view_form_invalid(self):
        """
        Test Contact View form is invalid
        """
        self.form_data["subject"] = ""
        response = self.client.post(self.url, data=self.form_data)
        self.assertEqual(response.status_code, 200)
