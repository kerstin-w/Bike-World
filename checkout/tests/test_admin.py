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
            inline_admin.readonly_fields, ("lineitem_total",)
        )


class OrderAdminTest(TestCase):
    """
    Test Case for OrderAdmin
    """

    @classmethod
    def setUpTestData(cls):
        """
        Test Data
        """
        # Create a new Order object for tests which need an existing object
        cls.order = Order.objects.create(
            order_number="TEST12345",
            full_name="John Doe",
            email="test@test.com",
            phone_number="1231231234",
            country="AT",
            town_or_city="Innsbruck",
            street_address1="Main St.",
        )

        cls.factory = RequestFactory()

    def setUp(self):
        self.site = AdminSite()

    def test_order_admin_inlines(self):
        """
        Test that the inlines attribute contains only the
        OrderLineItemAdminInline inline.
        """
        self.assertCountEqual(OrderAdmin.inlines, [OrderLineItemAdminInline])
