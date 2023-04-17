from allauth.account.forms import LoginForm, SignupForm


def login_tag(request):
    """
    Context processor that adds a login form to the context
    of every template that's rendered.
    """
    return {"logintag": LoginForm()}


def signup_tag(request):
    """
    Context processor that adds a signup form to the context
    of every template that's rendered.
    """
    return {"signuptag": SignupForm()}
