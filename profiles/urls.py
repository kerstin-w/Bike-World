from django.urls import path
from .views import ProfileView, OrderHistoryView

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path(
        "order_history/<order_number>",
        OrderHistoryView.as_view(),
        name="order_history",
    ),
]
