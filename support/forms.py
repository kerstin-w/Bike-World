from django import forms


# These dictionaries represent the common attributes applied to text input
# and textarea tags respectively.
text_input_attrs = {
    "class": "border-black",
    "autofocus": True,
}
textarea_attrs = {
    "class": "border-black",
}


class ContactForm(forms.Form):
    """
    Contact Form
    Defines 4 fields: name, email, subject and message.
    All fields are required.
    """

    # Name field of the form
    name = forms.CharField(
        label="Your name",
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your name",
                # Merge attribute dictionaries to apply common attributes
                **text_input_attrs,
            }
        ),
    )

    # Email field of the form
    email = forms.EmailField(
        label="Your email",
        required=True,
        widget=forms.EmailInput(
            attrs={"id": "email-input",
                   "placeholder": "Enter your email", **text_input_attrs}
        ),
    )

    # Subject field of the form
    subject = forms.CharField(
        label="Subject",
        max_length=200,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter the subject", **text_input_attrs}
        ),
    )

    # Message field of the form
    message = forms.CharField(
        label="Message",
        required=True,
        widget=forms.Textarea(
            attrs={"placeholder": "Enter your message", **textarea_attrs}
        ),
    )
