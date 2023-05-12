from django.test import TestCase, Client
from django.urls import reverse


class BagViewTest(TestCase):
    """
    Test Case for Bag View
    """

    def setUp(self):
        """
        Test Data
        """
        self.client = Client()

    def test_bag_view_returns_200(self):
        """
        Test that the response status code is 200
        """
        response = self.client.get(reverse('view_bag'))
        self.assertEqual(response.status_code, 200)

    def test_bag_view_uses_correct_template(self):
        """
        Test that the correct tempalte is used
        """
        response = self.client.get(reverse('view_bag'))
        self.assertTemplateUsed(response, 'bag/bag.html')
