from django.urls import path
from .views import ContactView, FaqView, PrivacyPolicyView

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("faqs/", FaqView.as_view(), name="faq"),
    path(
        "privacy_policy/", PrivacyPolicyView.as_view(), name="privacy_policy"
    ),
]
