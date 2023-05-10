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

    def test_order_admin_readonly_fields(self):
        """
        Test that the readonly_fields attribute contains all the
        expected fields that should be read-only.
        """
        self.assertCountEqual(
            OrderAdmin.readonly_fields,
            (
                "order_number",
                "date",
                "delivery_cost",
                "order_total",
                "grand_total",
                "original_bag",
                "stripe_pid",
            ),
        )

    def test_order_admin_fields(self):
        """
        Test that the fields attribute contains all the expected fields
        """
        self.assertCountEqual(
            OrderAdmin.fields,
            (
                "order_number",
                "user_profile",
                "date",
                "full_name",
                "email",
                "phone_number",
                "country",
                "postcode",
                "town_or_city",
                "street_address1",
                "street_address2",
                "delivery_cost",
                "order_total",
                "grand_total",
                "original_bag",
                "stripe_pid",
            ),
        )

    def test_order_admin_list_display(self):
        """
        Test that  the list_display attribute contains all the
        expected fields to be displayed in the list view
        """
        self.assertCountEqual(
            OrderAdmin.list_display,
            (
                "order_number",
                "date",
                "full_name",
                "order_total",
                "delivery_cost",
                "grand_total",
            ),
        )

    def test_order_admin_ordering(self):
        """
        Test that the ordering attribute specifies that orders
        should be ordered by descending order of date
        """
        self.assertCountEqual(OrderAdmin.ordering, ("-date",))
