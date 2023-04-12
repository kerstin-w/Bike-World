from django.urls import path
from .views import BagView, AddToBagView


urlpatterns = [
    path('', BagView.as_view(), name='view_bag'),
    path('add/<item_id>', AddToBagView.as_view(), name='add_to_bag'),
]