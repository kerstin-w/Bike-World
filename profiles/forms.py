from django import forms
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import UserProfile, ProductReview


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ("user",)

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        super().__init__(*args, **kwargs)
        placeholders = {
            "default_full_name": "Your Full Name",
            "default_postcode": "Postal Code",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_phone_number": "Phone Number",
        }
        if self.instance:
            placeholders["default_email"] = self.instance.user.email
        else:
            placeholders["default_email"] = "Email"

        # Set autofocus on the first field
        self.fields["default_street_address1"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "default_country":
                if self.fields[field].required:
                    # Add a required asterisk to the placeholder
                    placeholder = f"{placeholders[field]} *"
                else:
                    placeholder = placeholders[field]
                self.fields[field].widget.attrs["placeholder"] = placeholder
            # Add a class for styling
            self.fields[field].widget.attrs["class"] = "border-black"
            # Remove auto-generated labels
            self.fields[field].label = False

    def clean_default_email(self):
        """
        Ensure that the email is not already taken ba another user.
        """
        # Get the email address entered by the user from the form data
        email = self.cleaned_data.get("default_email")
        # Check if the entered email address is already taken by another user
        if (
            email != self.instance.user.email
            and User.objects.filter(email=email).exists()
        ):
            # If the email address is already taken, raise a validation error
            raise forms.ValidationError("Email is already in use.")
        # If the email address is not already taken, return it
        return email

    def save(self, commit=True):
        """
        Save the form data to UserProfile model instance.
        If commit is True, save changes to the database.
        """
        # Create a new UserProfile model instance from the form data
        profile = super().save(commit=False)
        # Get the User instance associated with the UserProfile instance
        user = profile.user
        # Update the email address of the User instance with
        # the entered email address from the form data
        user.email = self.cleaned_data["default_email"]
        # If commit is True, save the changes to the database
        if commit:
            user.save()
            profile.save()
        # Return the UserProfile instance
        return profile


class ProductReviewForm(forms.ModelForm):
    """
    Form to write a Product Review
    """

    rating = forms.IntegerField(widget=forms.HiddenInput(), validators=[
                                MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        model = ProductReview
        fields = (
            "review",
            "rating",
        )

        widgets = {
            "review": forms.Textarea(
                attrs={"class": "form-control, border-black"}
            ),
        }
