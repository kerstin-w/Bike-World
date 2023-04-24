from django import forms
from .models import UserProfile


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
            "default_email": "Email",
            "default_town_or_city": "Town or City",
            "default_street_address1": "Street Address 1",
            "default_street_address2": "Street Address 2",
            "default_phone_number": "Phone Number",
        }

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
