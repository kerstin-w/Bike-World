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

    def test_contact_from_name_field_required(self):
        """
        Test that the name field is required
        """
        form_data = {
            "email": "john@test.com",
            "subject": "Test",
            "message": "How are you doing?",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["name"], ["This field is required."])

    def test_contact_from_subject_field_required(self):
        """
        Test that the subject field is required
        """
        form_data = {
            "name": "John Doe",
            "email": "john@test.com",
            "message": "How are you doing?",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["subject"], ["This field is required."])

    def test_contact_from_message_field_required(self):
        """
        Test that the message field is required
        """
        form_data = {
            "name": "John Doe",
            "email": "john@test.com",
            "subject": "Test",
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["message"], ["This field is required."])
