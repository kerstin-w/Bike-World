from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator

from django_countries.fields import CountryField

from products.models import Product


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_full_name = models.CharField(
        max_length=settings.FULL_NAME_MAX_LENGTH, null=False, blank=False
    )
    default_email = models.EmailField(max_length=254, null=False, blank=False)
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True
    )
    default_country = CountryField(
        blank_label="Country", null=True, blank=True
    )
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_town_or_city = models.CharField(
        max_length=40, null=True, blank=True
    )
    default_street_address1 = models.CharField(
        max_length=80, null=True, blank=True
    )
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True
    )

    def __str__(self):
        return self.user.username


class Wishlist(models.Model):
    """
    A Wishlist data Model
    Users can add a product to their wishlist
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def is_product_in_wishlist(self):
        """
        Return a boolean indicating whether the product
        is in the user's wishlist
        """
        return Wishlist.objects.filter(
            user=self.user, product=self.product
        ).exists()


class ProductReview(models.Model):
    """
    Data Model for Product Reviews
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.TextField()
    rating = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"

    def save(self, *args, **kwargs):
        """
        Call the superclass's save() method to save the new review.
        """
        super(ProductReview, self).save(*args, **kwargs)

        # Update the rating field of the Product instance
        # with the average rating.
        self.product.rating = self.product.reviews.aggregate(Avg("rating"))[
            "rating__avg"
        ]

        # Save the Product instance with the new rating.
        self.product.save()

    @classmethod
    def get_reviews_for_product(cls, product):
        """
        Method to get review of a specific product
        """
        return cls.objects.filter(product=product).order_by('-created_at')


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile

    When a User is saved (created or updated), this function will be called and
    will create a new UserProfile object if the User was just created,
    or update the existing UserProfile object if the User was just updated.
    """
    if created:
        # If the User was just created, create a new UserProfile object
        UserProfile.objects.create(user=instance)
    # Whether the User was just created or updated, save the UserProfile object
    instance.userprofile.save()
