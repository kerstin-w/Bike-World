from django.urls import path
from .views import (
    ContactView,
    FaqView,
    PrivacyPolicyView,
    ReturnPolicyView,
    TermsAndConditionsView,
)

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
    path("faqs/", FaqView.as_view(), name="faq"),
    path(
        "privacy_policy/", PrivacyPolicyView.as_view(), name="privacy_policy"
    ),
    path("return_policy/", ReturnPolicyView.as_view(), name="return_policy"),
    path(
        "terms_and_conditions/",
        TermsAndConditionsView.as_view(),
        name="terms_and_conditions",
    ),
]
