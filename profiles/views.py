from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic import FormView, ListView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import UserProfile, Wishlist
from products.models import Product
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

    def form_invalid(self, form):
        # handle invalid form submission
        messages.error(
            self.request,
            "Failed to update your profile. Please ensure the form is valid.",
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        """
        Get context wether we are on the profile page and add orders to it
        """
        context = super().get_context_data(**kwargs)
        context["on_profile_page"] = True
        profile = get_object_or_404(UserProfile, user=self.request.user)
        # Add orders related to the profile to the context
        context["orders"] = profile.orders.all()
        # Add wishlist to the context
        context["wishlist"] = Wishlist.objects.filter(user=self.request.user)
        return context


class OrderHistoryView(LoginRequiredMixin, TemplateView):
    """
    View to render Order History
    """

    template_name = "checkout/checkout_success.html"

    def get(self, request, *args, **kwargs):
        # Get the Order with the specified order_number
        order = get_object_or_404(
            Order, order_number=self.kwargs["order_number"]
        )

        # Check if the user who is trying to access this page is the same
        # user who placed the order
        user_profile = UserProfile.objects.get(user=request.user)
        if order.user_profile != user_profile:
            messages.error(
                self.request,
                "You do nt have permssion to access this Order Summary.",
            )
            return HttpResponseRedirect("/")

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


class DeleteAccountView(LoginRequiredMixin, View):
    """
    Delete user account view
    """

    template_name = "profiles/profile.html"
    success_url = reverse_lazy("index")

    def post(self, request, *args, **kwargs):
        # deletes user account
        user = request.user
        user.delete()

        # logout the user
        logout(request)

        messages.success(
            request, "Your Account has been deleted successfully."
        )
        self.request.session.flush()
        return redirect(self.success_url)


class AddToWishlistView(View):
    """
    View to Add Products to the wishlist
    """

    def post(self, request, product_id):
        # Get the product that the user wants to add to their wishlist
        product = get_object_or_404(Product, id=product_id)

        # Get the current user
        user = request.user

        # Check if the product is already in the user's wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            messages.warning(
                request, f'{product} is already in your wishlist!')
        else:
            # Add the product to the user's wishlist
            wishlist_item = Wishlist(user=user, product=product)
            wishlist_item.save()
            messages.success(request, f'{product} added to your wishlist!')

        # Redirect the user back to the same page
        return redirect(request.META.get('HTTP_REFERER', 'home'))


class WishlistView(LoginRequiredMixin, ListView):
    """
    View to display the user's wishlist
    """

    model = Wishlist
    template_name = "profiles/profile.html"
    context_object_name = 'wishlist'

    def get_queryset(self):
        """
        Return the queryset of products in the user's wishlist
        """
        return Wishlist.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Add extra context to the template
        """
        context = super().get_context_data(**kwargs)
        context['products'] = [item.product for item in self.object_list]
        print("test")
        print(context['products'])
        return context
