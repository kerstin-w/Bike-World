from django.urls import path
from .views import ContactView, FaqView

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("faqs/", FaqView().as_view(), name="faq"),
]
