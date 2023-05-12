from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from .forms import ContactForm
from profiles.models import UserProfile


class ContactView(FormView):
    template_name = "support/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        # Get the form data
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]
        # Send email
        send_mail(
            subject,
            f"{name} wrote, \n\n{message}",
            email,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        # Add a success message to be displayed after the redirect
        messages.success(
            self.request, "Thanks for contacting us! We will be in touch soon."
        )
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Check if the user is authenticated
        if self.request.user.is_authenticated:
            # Get the UserProfile object of the logged-in user (if exists)
            try:
                user_profile = UserProfile.objects.get(user=self.request.user)
                # Set the form's initial values to the user's name and email
                kwargs["initial"] = {
                    "name": user_profile.default_full_name,
                    "email": self.request.user.email,
                }
            except UserProfile.DoesNotExist:
                pass
        return kwargs

    def get_success_url(self):
        # Redirect to the previous page
        return self.request.session.get("previous_page", self.success_url)

    def get(self, request, *args, **kwargs):
        # Store the previous page URL in the session
        request.session["previous_page"] = request.META.get("HTTP_REFERER")
        return super().get(request, *args, **kwargs)


class FaqView(TemplateView):
    """
    Render the FAQs Page
    """
    template_name = 'support/faq.html'


class PrivacyPolicyView(TemplateView):
    """
    Render the Privacy Policy Page
    """
    template_name = 'support/privacy_policy.html'
