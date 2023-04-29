from django.test import TestCase
from support.forms import ContactForm


class ContactFormTestCase(TestCase):
    """
    Test Case for Support ContactForm
    """

    def test_contact_from_valid(self):
        """
        Test that the form is valid when
        all fields are provided with input values
        """
        form_data = {
            "name": "John Doe",
            "email": "john@test.com",
            "subject": "Test",
            "message": "How are you doing?",
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_from_invalid(self):
        """ "
        Test that the form is invalid when any field is blank
        """
        form_data = {
            "name": "",
            "email": "",
            "subject": "",
            "message": "",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
