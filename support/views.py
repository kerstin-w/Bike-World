from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings

from .forms import ContactForm
from profiles.models import UserProfile


class ContactView(View):
    """
    Contact View that displays the contact from
    and handles the from
    """

    def get(self, request, *args, **kwargs):
        """
        handle the GET request for the contact page
        """
        # Get the current URL of the page
        request.session["previous_page"] = request.META.get("HTTP_REFERER")
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the UserProfile object of the logged-in user (if exists)
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                user_profile = None
            # If a user profile exists, pre-fill the form fields
            # with the stored data
            if user_profile:
                form = ContactForm(
                    initial={
                        "name": user_profile.default_full_name,
                        "email": request.user.email,
                    }
                )
            else:
                form = ContactForm()
        else:
            form = ContactForm()
        # Render the contact page with the initialized ContactForm
        return render(request, "support/contact.html", {"form": form})

    def post(self, request, *args, **kwargs):
        """
        handle the POST request for the contact page
        """
        form = ContactForm(request.POST)
        # Check if the submitted form data is valid
        if form.is_valid():
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
                request, "Thanks for contacting us! We will be in touch soon."
            )
            # Redirect to the previous page
            return redirect(request.session.get("previous_page", "/"))
        # Render the contact page with the invalid form and error messages
        return render(request, "support/contact.html", {"form": form})
