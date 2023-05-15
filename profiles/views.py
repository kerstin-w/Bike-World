from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    View,
)

from checkout.models import Order, OrderLineItem
from products.models import Product

from .forms import ProductReviewForm, UserProfileForm
from .models import ProductReview, UserProfile, Wishlist


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View to render the user profile
    """

    template_name = "profiles/profile.html"
    login_url = "/accounts/login/"

    def get_queryset(self):
        """
        Get the UserProfile for the current user using the request object.
        Then, return a queryset of orders related to the retrieved UserProfile.
        """
        profile = get_object_or_404(UserProfile, user=self.request.user)
        return profile.orders.all()

    def get_context_data(self, **kwargs):
        """
        Get context wether we are on the profile page and add orders to it
        """
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(UserProfile, user=self.request.user)
        # Create an instance of the UserProfileForm with the current
        # user's profile info
        user_profile_form = UserProfileForm(instance=profile)
        context["user_profile_form"] = user_profile_form
        # Add orders related to the profile to the context
        context["orders"] = profile.orders.all()
        # Add wishlist to the context
        context["wishlist"] = Wishlist.objects.filter(user=self.request.user)
        # Get a queryset of all product reviews for this user's UserProfile
        user_reviews = ProductReview.objects.filter(user=self.request.user)
        # Filter out any line items that have a corresponding review
        order_line_items = (
            OrderLineItem.objects.filter(order__user_profile=profile)
            .exclude(product__reviews__in=user_reviews)
            .distinct()
        )

        # Create a list of order item IDs and product titles
        order_item_ids = []
        reviewed_products = []
        for item in order_line_items:
            # Only add the product to the context if it hasn't been reviewed
            # and hasn't been listed before
            if item.product not in reviewed_products:
                reviewed_products.append(item.product)
                order_item_ids.append(
                    {
                        "order_number": item.order.order_number,
                        "product": item.product,
                        "review_form": ProductReviewForm(),
                    }
                )
        context["order_item_ids"] = order_item_ids

        return context


class ProfileUpdateView(ProfileView, FormView):
    """
    View to handle updating of user profile
    """

    form_class = UserProfileForm
    template_name = "profiles/profile.html"
    success_url = reverse_lazy("profile")

    def get_context_data(self, **kwargs):
        """
        Get the user_profile_form instance by calling
        and add it to the context data dictionary
        """
        context = super().get_context_data(**kwargs)
        context["user_profile_form"] = self.get_form()
        return context

    def get_form_kwargs(self):
        """
        Get and return keyword arguments to be passed to the form class.
        Populate the form with the current user's profile information.
        """
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = get_object_or_404(
            UserProfile, user=self.request.user
        )
        kwargs["initial"] = {"default_email": self.request.user.email}
        return kwargs

    def form_valid(self, form):
        """
        Called when form submission is successful.
        Save the form data to the corresponding UserProfile model instance.
        """
        form.save()
        messages.success(
            self.request, "Your profile has been updated successfully."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submissions and render the form again.
        """
        messages.error(
            self.request,
            "Failed to update your profile. Please ensure the form is valid.",
        )
        return super().form_invalid(form)


class OrderHistoryView(LoginRequiredMixin, TemplateView):
    """
    View to render Order History
    """

    template_name = "checkout/checkout_success.html"

    def get(self, request, *args, **kwargs):
        # Try to get the order and render it if successful
        try:
            order = self.get_order()
            if not self.has_permission(order):
                # If user does not have permission to access the order
                return self.handle_permission_denied()
            # Add success and confirmation messages and
            # render the template with the order details
            self.add_confirmation_message(order)
            context = {
                "order": order,
                "from_profile": True,
            }

            return self.render_to_response(context)
        except Http404:
            return self.handle_not_found()

    def get_order(self):
        """
        Get the order with the order_number specified in the URL
        """
        return get_object_or_404(Order, order_number=self.kwargs["order_number"])

    def has_permission(self, order):
        """
        Check if the user has permission to view the order
        """
        user_profile = UserProfile.objects.get(user=self.request.user)
        return order.user_profile == user_profile

    def handle_permission_denied(self):
        """
        Handle cases where user does not have permission to access the order
        """
        messages.error(
            self.request,
            "You do not have permission to access this Order Summary.",
        )
        return HttpResponseRedirect("/")

    def add_confirmation_message(self, order):
        """
        Add a confirmation message to the response
        """
        confirmation_message = (
            f"This is a past confirmation for order number "
            f'{self.kwargs["order_number"]}. A confirmation '
            f"email was sent to you on the order date."
        )
        messages.info(self.request, confirmation_message)

    def handle_not_found(self):
        """
        Handle cases where the order is not found
        """
        messages.error(
            self.request,
            "The order you are trying to access does not exist.",
        )
        return HttpResponseNotFound()


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


class AddToWishlistView(LoginRequiredMixin, View):
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
                request, f"{product} is already in your wishlist!"
            )
        else:
            # Add the product to the user's wishlist
            wishlist_item = Wishlist(user=user, product=product)
            wishlist_item.save()
            messages.success(
                request, f"<strong>{product}</strong> added to your wishlist!"
            )

        # Redirect the user back to the same page
        return redirect(request.META.get("HTTP_REFERER", "index"))


class WishlistView(LoginRequiredMixin, ListView):
    """
    View to display the user's wishlist
    """

    model = Wishlist
    template_name = "profiles/profile.html"
    context_object_name = "wishlist"

    def get_queryset(self):
        """
        Return the queryset of products in the user's wishlist
        """
        return Wishlist.objects.filter(user=self.request.user)


class WishlistDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to handle deleting a product from the wishlist
    """

    model = Wishlist
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        """
        Return the queryset of products in the user's wishlist
        that belong to the current user
        """
        return Wishlist.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Handle delete request to delete a product from the wishlist
        """
        self.object = self.get_object()
        product = self.object.product.title
        messages.success(
            request,
            f"<strong>{product}</strong> has been removed from your wishlist!",
        )
        return super().delete(request, *args, **kwargs)


class ProductReviewView(ProfileView, LoginRequiredMixin, FormView):
    """
    View for Users to write a review about purchased products
    """

    template_name = "profiles/profile.html"
    form_class = ProductReviewForm

    def get_context_data(self, **kwargs):
        """
        Retrieve order number and product ID from URL parameters and
        add the order item to the context
        """
        context = super().get_context_data(**kwargs)
        context["order_item"] = self.get_order_item()
        return context

    def get_order_item(self):
        """
        Retrieve the order item, ensuring it belongs to the current user
        """
        order_number = self.kwargs["order_number"]
        product_id = self.kwargs["product_id"]
        return get_object_or_404(
            OrderLineItem,
            order__order_number=order_number,
            product__id=product_id,
            order__user_profile__user=self.request.user,
        )

    def form_valid(self, form):
        """
        Process valid form data
        """
        review = form.save(commit=False)
        review.user = self.request.user
        review.product = self.get_order_item().product
        review.order_item = self.get_order_item()
        review.save()
        # Display a success message and redirect to the profile page
        messages.success(
            self.request,
            f"Your review for <strong>{review.product}</strong> "
            "has been submitted!",
        )
        return redirect(reverse("profile"))

    def form_invalid(self, form):
        """
        Handle invalid form submissions
        """
        messages.error(
            self.request,
            "Failed to submit your Review. Please ensure the form is valid.",
        )
        return redirect(reverse("profile"))
