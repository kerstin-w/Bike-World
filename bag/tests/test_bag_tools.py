from django.test import TestCase
from django.template import Template, Context


class BagToolsTest(TestCase):
    """
    Test Case for bag tools
    """

    def test_multiply_price_by_quantity(self):
        expected_result = "50"
        template = Template("{% load bag_tools %}"
                            "{{ price|multiply_price_by_quantity:quantity }}")
        context = Context({"price": 10, "quantity": 5})
        self.assertEqual(template.render(context), expected_result)

        expected_result = "0"
        template = Template("{% load bag_tools %}"
                            "{{ price|multiply_price_by_quantity:quantity }}")
        context = Context({"price": 100, "quantity": 0})
        self.assertEqual(template.render(context), expected_result)
