from django.views import View
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from .forms import ContactForm


class ContactView(View):
    """
    Contact View that displays the contact from
    and handles the from
    """

    # handle the GET request for the contact page
    def get(self, request, *args, **kwargs):
        # Get the current URL of the page
        request.session["previous_page"] = request.META.get("HTTP_REFERER")
        form = ContactForm()
        # Render the contact page with an empty ContactForm
        return render(request, "support/contact.html", {"form": form})

    # handle the POST request for the contact page
    def post(self, request, *args, **kwargs):
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
