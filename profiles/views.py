from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.views.generic import FormView, ListView, TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import UserProfile
from checkout.models import Order
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
        messages.success(
            self.request, "Your Profile has been updated successfully."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """
        Get context wether we are on the profile page and add orders to it
        """
        context = super().get_context_data(**kwargs)
        context["on_profile_page"] = True
        profile = get_object_or_404(UserProfile, user=self.request.user)
        # Add orders related to the profile to the context
        context["orders"] = profile.orders.all()
        return context


class OrderHistoryView(TemplateView):
    """
    View to render Order History
    """

    template_name = "checkout/checkout_success.html"

    def get(self, request, *args, **kwargs):
        # Get the Order with the specified order_number
        order = get_object_or_404(
            Order, order_number=self.kwargs["order_number"]
        )

        messages.info(
            request,
            (
                f"This is a past confirmation for order number "
                f'{self.kwargs["order_number"]}. A confirmation '
                f"email was sent to you on the order date."
            ),
        )

        context = {
            "order": order,
            "from_profile": True,
        }

        return self.render_to_response(context)


class DeleteAccountView(LoginRequiredMixin, LogoutView):
    """
    Delete user account view
    """
    template_name = 'profiles/profile.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        """
        Handles the GET request and deletes the user account on POST request.
        """
        if request.method == 'POST':
            self.logout(request)

            # deletes user account
            user = request.user
            user.delete()
            messages.success(
                self.request, "Your Account has been deleted successfully."
                )
            return redirect(self.success_url)

        return super().dispatch(request, *args, **kwargs)
