from django.urls import path
from .views import BagView


urlpatterns = [
    path('', BagView.as_view(), name='view_bag'),
]