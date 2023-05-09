from allauth.account.signals import user_signed_up
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.loader import render_to_string

from profiles.models import ProductReview


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


# Define a receiver function to handle the post_delete signal
@receiver(post_delete, sender=ProductReview)
def send_review_deleted_email_from_list(sender, instance, **kwargs):
    """
    Sends an email to the user when their review is deleted
    """
    # capture the user email before the review is deleted
    user = instance.user
    product = instance.product

    # Update the rating field of the Product instance
    rating = product.reviews.aggregate(Avg("rating"))["rating__avg"]
    product.rating = rating if rating else 0
    product.save()

    # send email to user
    subject = 'Your review has been deleted'
    message = render_to_string(
        "products/emails/review_deleted_mail.txt",
        {"user_name": user.username, "product_name": product.title},
    )
    send_mail(
        subject,
        message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
