from django.conf import settings
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string


# Define a receiver function to handle the user_signed_up signal
@receiver(user_signed_up)
def send_welcome_email(sender, **kwargs):
    """
    Function to handle user_signed_up signal and send welcome mail
    """
    user = kwargs["user"]
    subject = "Welcome to BIKE WORLD"
    message = render_to_string(
        'emails/welcome_mail.txt', {'user': user})
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list, fail_silently=True)
