from django.urls import path
from .views import BagView, AddToBagView, AdjustBagView, RemoveItemFromBagView


urlpatterns = [
    path('', BagView.as_view(), name='view_bag'),
    path('add/<item_id>', AddToBagView.as_view(), name='add_to_bag'),
    path('adjust/<item_id>/', AdjustBagView.as_view(), name='adjust_bag'),
    path('remove/<item_id>/', RemoveItemFromBagView.as_view(),
         name='remove_from_bag'),
]
