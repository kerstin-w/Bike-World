from django.urls import path
from . import views

urlpatterns = [
    path("", views.ProductListView.as_view(), name="products"),
    path(
        "<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"
    ),
    path("add/", views.ProductCreateView.as_view(), name="add_product"),
    path(
        "edit/<int:product_id>/",
        views.ProductEditView.as_view(),
        name="edit_product",
    ),
]
