from django.urls import path
from .views import (
    ProfileView,
    OrderHistoryView,
    DeleteAccountView,
    AddToWishlistView,
    WishlistDeleteView,
)

urlpatterns = [
    path("", ProfileView.as_view(), name="profile"),
    path(
        "order_history/<order_number>/",
        OrderHistoryView.as_view(),
        name="order_history",
    ),
    path(
        "delete_account/", DeleteAccountView.as_view(), name="delete_account"
    ),
    path(
        "add-to-wishlist/<int:product_id>/",
        AddToWishlistView.as_view(),
        name="add-to-wishlist",
    ),
    path('wishlist/<int:pk>/delete/',
         WishlistDeleteView.as_view(), name='wishlist-delete'),
]
