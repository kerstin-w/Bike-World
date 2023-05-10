from decimal import Decimal

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from checkout.admin import OrderAdmin, OrderLineItemAdminInline, DashboardView
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

    def test_order_admin_get_queryset(self):
        """
        Test that the get_queryset method correctly filters the orders
        """
        qs = OrderAdmin(Order, self.site).get_queryset(
            request=self.factory.get("/", {"q": "TEST"})
        )
        self.assertEqual(qs.count(), 1)


class DashboardViewTestCase(TestCase):
    """
    Test Case for Admin Dashboard View
    """

    def setUp(self):
        """
        Test Data
        """
        # Create a user with staff permissions
        self.admin = User.objects.create_superuser(
            username="admin",
            password="password",
        )

        # Create a request factory
        self.factory = RequestFactory()

        # Create some test data
        self.order1 = Order.objects.create(
            full_name="John Doe",
            email="johndoe@example.com",
            phone_number="1234567890",
            country="US",
            postcode="12345",
            town_or_city="New York",
            street_address1="123 Main St",
            date=timezone.now(),
            delivery_cost=Decimal("10.00"),
            order_total=Decimal("100.00"),
            grand_total=Decimal("110.00"),
            original_bag="",
            stripe_pid="",
        )
        self.order2 = Order.objects.create(
            full_name="Jane Doe",
            email="janedoe@example.com",
            phone_number="0987654321",
            country="CA",
            postcode="A1A 1A1",
            town_or_city="Toronto",
            street_address1="456 King St",
            date=timezone.now(),
            delivery_cost=Decimal("5.00"),
            order_total=Decimal("50.00"),
            grand_total=Decimal("55.00"),
            original_bag="",
            stripe_pid="",
        )
        self.url = reverse("dashboard")

    def test_dashboard_view_unauthenticated_users(self):
        """
        Test that unauthenticated users can't access the dashboard
        """
        response = self.client.get(self.url)
        login_url = "/admin/login/?next=" + self.url
        self.assertRedirects(response, login_url)

        # Ensure authenticated non-staff users can't access the dashboard
        self.client.login(username="nonstaff", password="password")
        response = self.client.get(self.url)
        login_url = "/admin/login/?next=" + self.url
        self.assertRedirects(response, login_url)

    def test_dashboard_view_authenticated_users(self):
        """
        Test that authenticated staff users can access the dashboard
        """
        self.client.login(username="admin", password="password")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # Check that the expected values are present in the context
        expected_context = {
            "revenue_today": Decimal("165"),
            "revenue_month": Decimal("165"),
            "order_count_today": 2,
            "order_count_month": 2,
            "average_order_total": Decimal("82.5"),
            "daily_revenue": [0, 0, 0, 0, 0, 0, 0, 0, 0, Decimal("165")],
            "country_revenue": (
                '{"Canada": 55.0, '
                '"United States of America": 110.0}'
            ),
        }
        context = response.context[-1]
        self.assertEqual(
            context["revenue_today"], expected_context["revenue_today"]
        )
        self.assertEqual(
            context["revenue_month"], expected_context["revenue_month"]
        )
        self.assertEqual(
            context["order_count_today"], expected_context["order_count_today"]
        )
        self.assertEqual(
            context["order_count_month"], expected_context["order_count_month"]
        )
        self.assertEqual(
            context["average_order_total"],
            expected_context["average_order_total"],
        )
        self.assertEqual(
            context["daily_revenue"], expected_context["daily_revenue"]
        )
        self.assertEqual(
            context["country_revenue"], expected_context["country_revenue"]
        )

    def test_dashboard_view_country_revenue_is_correct(self):
        """
        Test that the get_country_revenue method returns
        the expected country revenue dictionary
        """
        orders_month = Order.objects.filter(date__month=timezone.now().month)
        expected_country_revenue = {"Canada": 55.0,
                                    "United States of America": 110.0}
        country_revenue = DashboardView().get_country_revenue(orders_month)
        self.assertDictEqual(country_revenue, expected_country_revenue)

    def test_dashboard_view_daily_revenue_is_correct(self):
        """
        Test that the get_daily_revenue method returns
        the expected list of daily revenue totals
        """
        today = timezone.localtime().date()
        expected_daily_revenue = [0, 0, 0, 0, 0, 0, 0, 0, 0, Decimal("165")]
        daily_revenue = DashboardView().get_daily_revenue(today)
        self.assertListEqual(daily_revenue, expected_daily_revenue)
