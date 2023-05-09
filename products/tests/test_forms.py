from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from io import BytesIO
from PIL import Image

from products.forms import ProductForm
from products.models import Category, Product


class ProductFormTest(TestCase):
    """
    Test Case for Product Form
    """

    @classmethod
    def setUpTestData(cls):
        # create a category for the test products
        cls.category = Category.objects.create(
            name="TestCategory", friendly_name="Test Category"
        )

    def setUp(self):
        """
        Test Data
        """
        self.form_data = {
            "title": "Test Title",
            "sku": "12345",
            "category": self.category.id,
            "description": "Test Description",
            "wheel_size": "Test Wheel Size",
            "retail_price": 50.00,
            "sale_price": 45.00,
            "sale": True,
            "brand": "Test Brand",
            "bike_type": "Test Bike Type",
            "gender": 0,
            "material": "Test Material",
            "derailleur": "Test Derailleur",
            "stock": 100,
            "rating": 3.5,
        }
        # create an image to use for file uploads
        self.image = self.generate_image()

    def generate_image(self):
        """
        Utility function to generate a test image for form file uploads
        """
        file = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "test_image.png"
        file.seek(0)
        return SimpleUploadedFile(
            file.name, file.read(), content_type="image/png"
        )

    def test_product_form_valid_form(self):
        """
        Test that form is valid
        """
        form = ProductForm(data=self.form_data, files={"image": self.image})
        self.assertTrue(form.is_valid())

    def test_product_form_category_choices(self):
        """
        Test that the category field has the expected choices
        """
        form = ProductForm()
        self.assertIn(
            (self.category.id, self.category.friendly_name),
            form.fields["category"].choices,
        )

    def test_product_form_field_widgets(self):
        """
        Test that all fields have proper widget
        """
        form = ProductForm()
        for field_name, field in form.fields.items():
            self.assertEqual(
                field.widget.attrs["class"],
                "border-black",
                f"{field_name} widget is wrong.",
            )
