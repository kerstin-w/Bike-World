from django.test import RequestFactory, TestCase
from allauth.account.forms import SignupForm

from profiles.context_processors import login_tag, signup_tag
from profiles.forms import CustomLoginForm


class ContextProcessorTest(TestCase):
    """
    Test Case for Context Processors
    """

    def setUp(self):
        """
        Test Data
        """
        self.factory = RequestFactory()

    def test_login_tag(self):
        """
        Test the login_tag context processor
        """
        request = self.factory.get("/")
        login_form = login_tag(request)["logintag"]
        self.assertIsInstance(login_form, CustomLoginForm)
        self.assertEqual(login_form.auto_id, 'login_id_%s')

    def test_signup_tag(self):
        """
        Test the signup_tag context processor
        """
        request = self.factory.get("/")
        signup_form = signup_tag(request)["signuptag"]
        self.assertIsInstance(signup_form, SignupForm)
        self.assertEqual(signup_form.auto_id, 'signup_id_%s')
