from django import forms
from django.db.models.functions import Lower

from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """
    Form to Update and Create Products
    """

    class Meta:
        model = Product
        fields = "__all__"

    image = forms.ImageField(
        label="Image",
        required=False,
        widget=CustomClearableFileInput(attrs={"aria-label": "Select Image"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [
            (category.id, category.get_friendly_name())
            for category in categories
        ]

        self.fields["category"].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "border-black"

    def clean(self):
        """
        Check that a product with a taken title or sku cannot be added
        or a product cannot be edited with a title or sku from another
        product
        """
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        sku = cleaned_data.get("sku")
        # Get the current product instance being edited
        instance = self.instance

        # Check if a product with the same title (case-insensitive)
        # already exists
        if title:
            lower_title = title.lower()
            existing_products = Product.objects.annotate(
                lower_title=Lower("title")
            )

            # Exclude the current product being edited from
            # duplicate title check
            if instance and instance.pk:
                existing_products = existing_products.exclude(pk=instance.pk)

            # Check if any existing product has the same lowercased title
            if existing_products.filter(lower_title=lower_title).exists():
                self.add_error(
                    "title", "A product with this title already exists."
                )

        # Check if a product with the same SKU already exists
        if (
            sku
            and Product.objects.exclude(pk=instance.pk)
            .filter(sku=sku)
            .exists()
        ):
            self.add_error("sku", "A product with this SKU already exists.")

        return cleaned_data
