from allauth.account.forms import LoginForm, SignupForm


class CustomLoginForm(LoginForm):
    """
    Custom Login Form to turn of the auto focus
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.pop('autofocus', None)


def login_tag(request):
    """
    Context processor that adds a login form to the context
    of every template that's rendered.
    """
    return {"logintag": CustomLoginForm()}


def signup_tag(request):
    """
    Context processor that adds a signup form to the context
    of every template that's rendered.
    """
    return {"signuptag": SignupForm()}
