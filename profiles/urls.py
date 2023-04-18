from django.urls import path
from .views import ProfileView, OrderHistoryView, DeleteAccountView

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path(
        "order_history/<order_number>/",
        OrderHistoryView.as_view(),
        name="order_history",
    ),
    path("delete_account/", DeleteAccountView.as_view(), name="delete_account")
]
