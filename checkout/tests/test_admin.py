from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from checkout.admin import OrderAdmin, OrderLineItemAdminInline
from checkout.models import Order, OrderLineItem


class OrderLineItemAdminInlineTest(TestCase):
    """
    Test Case for OrderLineItemAdminInline
    """

    def test_order_line_item_admin_inline_model(self):
        """
        Test that the model attribute is set to OrderLineItem
        """
        self.assertEqual(OrderLineItemAdminInline.model, OrderLineItem)

    def test_order_line_item_admin_inline_readonly_fields(self):
        """
        Test that the readonly_fields attribute contains only the
        field lineitem_total
        """
        inline_admin = OrderLineItemAdminInline(Order, AdminSite())
        self.assertCountEqual(
            inline_admin.readonly_fields, ("lineitem_total",))
