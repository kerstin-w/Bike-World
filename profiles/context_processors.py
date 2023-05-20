from allauth.account.forms import SignupForm
from .forms import CustomLoginForm


def login_tag(request):
    """
    Context processor that adds a login form to the context
    of every template that's rendered.
    """
    return {"logintag": CustomLoginForm(auto_id="login_id_%s")}


def signup_tag(request):
    """
    Context processor that adds a signup form to the context
    of every template that's rendered.
    """
    return {"signuptag": SignupForm(auto_id="signup_id_%s")}
