from django.test import TestCase
from django.urls import reverse


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
