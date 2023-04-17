from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView, ListView
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import UserProfileForm


class ProfileView(LoginRequiredMixin, FormView, ListView):
    """
    View to render the user profile
    """

    template_name = "profiles/profile.html"
    form_class = UserProfileForm
    login_url = "/accounts/login/"
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        """
        Get the UserProfile for the current user using the request object.
        Then, return a queryset of orders related to the retrieved UserProfile.
        """
        profile = get_object_or_404(UserProfile, user=self.request.user)
        return profile.orders.all()

    def get_form_kwargs(self):
        """
        Get and return keyword arguments to be passed to the form class.
        Populate the form with the current user's profile information.
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = get_object_or_404(
            UserProfile, user=self.request.user
        )
        return kwargs

    def form_valid(self, form):
        """
        Called when form submission is successful.
        Save the form data to the corresponding UserProfile model instance.
        """
        form.save()
        return super().form_valid(form)
