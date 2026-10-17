from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Category, Product


class ProductRuleTests(TestCase):

    def setUp(self):
        # Runs before every test. Each test gets a fresh, empty test database.
        self.category = Category.objects.create(name="Earrings", slug="earrings")

    def make_product(self, **overrides):
        """Build a valid product WITHOUT saving it.

        Each test passes only the fields it wants to change.
        """
        fields = {
            "name": "Test Hoops",
            "slug": "test-hoops",
            "category": self.category,
        }
        fields.update(overrides)
        return Product(**fields)

    def fake_upload(self):
        """A tiny in-memory file. Nothing is written to disk."""
        return SimpleUploadedFile(
            "test.jpg", b"not-a-real-image", content_type="image/jpeg"
        )

    # --- Validation rules (full_clean runs our clean() method) ---

    def test_sale_price_must_be_below_price(self):
        product = self.make_product(price=1000, sale_price=1200)
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertIn("sale_price", cm.exception.message_dict)

    def test_publishing_requires_main_image(self):
        product = self.make_product(
            publication_status=Product.PublicationStatus.PUBLISHED,
        )
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertIn("main_image", cm.exception.message_dict)

    def test_publishing_requires_alt_text(self):
        product = self.make_product(
            publication_status=Product.PublicationStatus.PUBLISHED,
            main_image=self.fake_upload(),
            main_image_alt="",
        )
        with self.assertRaises(ValidationError) as cm:
            product.full_clean()
        self.assertIn("main_image_alt", cm.exception.message_dict)

    # --- Database rule (save() skips clean(), so only the constraint can stop this) ---

    def test_database_blocks_published_product_without_image(self):
        product = self.make_product(
            publication_status=Product.PublicationStatus.PUBLISHED,
        )
        with self.assertRaises(IntegrityError):
            # atomic() goes INSIDE assertRaises, so the failed write is rolled
            # back before the error is caught, and the test connection stays usable.
            with transaction.atomic():
                product.save()

    # --- What the public is allowed to see ---

    def test_published_excludes_drafts(self):
        self.make_product().save()  # status defaults to draft
        self.assertEqual(Product.objects.published().count(), 0)

    def test_published_excludes_inactive_categories(self):
        # save() runs no validators, so a plain file name is fine here
        self.make_product(
            publication_status=Product.PublicationStatus.PUBLISHED,
            main_image="products/test.jpg",
            main_image_alt="Gold hoop earrings",
        ).save()
        self.assertEqual(Product.objects.published().count(), 1)

        self.category.is_active = False
        self.category.save()
        self.assertEqual(Product.objects.published().count(), 0)