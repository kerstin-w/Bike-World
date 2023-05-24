from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model
from django.utils.html import mark_safe


class Category(Model):
    """
    Data Model for Product Categories
    """

    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254)

    def __str__(self):
        return self.friendly_name

    def get_friendly_name(self):
        return self.friendly_name


GENDER = ((0, "Unisex"), (1, "Womens"), (2, "Mens"))


class Product(Model):
    """
    Data Model for Products
    """

    title = models.CharField(max_length=254, unique=True)
    sku = models.CharField(max_length=254, null=True, blank=True, unique=True)
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.TextField()
    wheel_size = models.CharField(max_length=100, null=True, blank=True)
    retail_price = models.DecimalField(max_digits=7, decimal_places=2)
    sale_price = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    sale = models.BooleanField(default=False, null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="products/")
    brand = models.CharField(max_length=100)
    bike_type = models.CharField(max_length=200)
    gender = models.IntegerField(choices=GENDER, default=0)
    material = models.CharField(max_length=100, null=True, blank=True)
    derailleur = models.CharField(max_length=100, null=True, blank=True)
    stock = models.IntegerField(default=99)
    rating = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_gender_display(self):
        """
        Returns the display value of the gender field
        based on the choices defined in GENDER
        """
        return dict(GENDER)[self.gender]

    def image_tag(self):
        """
        Generates an HTML image tag for the product image
        """
        if self.image:
            image_url = f"{settings.MEDIA_URL}{self.image}"
            return mark_safe(
                f'<img src="{image_url}" style="width:150px;height:120px;'
                'object-fit:contain;">'
            )
        else:
            return "No Image Found"

    def get_related_products(self):
        """
        Retrieve all the products that belong to the same category as the
        current product but exclude the current product itself.
        Return only the first 4 related products.
        """
        return Product.objects.filter(category=self.category).exclude(
            id=self.id
        )[:4]

    def clean(self):
        """
        Make sale_price a required field when product is on sale
        """
        super().clean()
        if self.sale and not self.sale_price:
            raise ValidationError("Sale price is required.")

    def save(self, *args, **kwargs):
        """
        Check if the product is on sale and if it is save it in category sale
        """
        if self.sale:
            sale_category = Category.objects.get(name="sale")
            self.category = sale_category
        super().save(*args, **kwargs)
