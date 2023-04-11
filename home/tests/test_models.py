from django.test import TestCase
from products.models import Category, Product

class CategoryModelTest(TestCase):
    """
    Test for Category Data Model
    """
    def setUp(self):
        """
        Test Data
        """
        self.category = Category.objects.create(
            name='test_category',
            friendly_name='Test friendly name'
        )

    def test_category_has_name_attr(self):
        """Test category has 'name' attribute as expected"""
        self.assertEquals(self.category.name, 'test_category')

    def test_category_has_friendly_name_attr(self):
        """
        Test category has friendly_name
        """
        self.assertEquals(self.category.friendly_name, 'Test friendly name')

    def test_category_str_method(self):
        """
        Test the __str__ method of Category model
        """
        self.assertEquals(str(self.category), 'Test friendly name')
