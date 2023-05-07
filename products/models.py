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

    title = models.CharField(max_length=254)
    sku = models.CharField(max_length=254, null=True, blank=True)
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
    rating = models.FloatField()

    def __str__(self):
        return self.title

    def get_gender_display(self):
        return dict(GENDER)[self.gender]

    def image_tag(self):
        if self.image:
            return mark_safe(
                '<img src="/media/%s" style="width:150px;height:120px;'
                'object-fit:contain;">' % (self.image)
            )
        else:
            return "No Image Found"
