from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.urls import reverse

from .validators import validate_image_size

IMAGE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
    validate_image_size,
]


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=90, unique=True)
    description = models.TextField(blank=True)
    display_order = models.PositiveSmallIntegerField(
        default=0, help_text="Lower numbers appear first in the menu."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def published(self):
        """The one place that decides what the public may see."""
        return self.filter(
            publication_status=Product.PublicationStatus.PUBLISHED,
            category__is_active=True,
        )

class Product(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "available", "Available"
        SOLD_OUT = "sold_out", "Sold out"
        MADE_TO_ORDER = "made_to_order", "Made to order"

    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    sku = models.CharField(
        "product code", max_length=40, unique=True, null=True, blank=True
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    short_description = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    material = models.CharField(max_length=100, blank=True)
    plating = models.CharField(max_length=100, blank=True)
    colour = models.CharField(max_length=60, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    available_sizes = models.CharField(max_length=100, blank=True)

    availability_status = models.CharField(
        max_length=20, choices=Availability.choices, default=Availability.AVAILABLE
    )
    publication_status = models.CharField(
        max_length=20,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
    )

    main_image = models.ImageField(
        upload_to="products/%Y/%m/", blank=True, validators=IMAGE_VALIDATORS
    )
    main_image_alt = models.CharField(max_length=160, blank=True)

    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, editable=False)

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["publication_status", "-published_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__isnull=True) | models.Q(price__gte=0),
                name="product_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(sale_price__isnull=True)
                | models.Q(price__isnull=False, sale_price__lt=models.F("price")),
                name="product_sale_price_below_price",
            ),
            models.CheckConstraint(
                condition=models.Q(publication_status="draft")
                | ~models.Q(main_image=""),
                name="published_requires_main_image",
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    def _normalise_sku(self):
        # Store codes as UPPERCASE, and store "no code" as NULL, not "".
        self.sku = self.sku.strip().upper() if self.sku and self.sku.strip() else None

    def clean(self):
        super().clean()
        self._normalise_sku()
        errors = {}

        if self.sale_price is not None:
            if self.price is None:
                errors["sale_price"] = "Enter a regular price before setting a sale price."
            elif self.sale_price >= self.price:
                errors["sale_price"] = "Sale price must be lower than the regular price."

        if (
            self.publication_status == self.PublicationStatus.PUBLISHED
            and not self.main_image
        ):
            errors["main_image"] = "A published product needs a main image."

        if (
            self.publication_status == self.PublicationStatus.PUBLISHED
            and not self.main_image_alt.strip()
        ):
            errors["main_image_alt"] = (
                "Describe the main image for screen readers before publishing."
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self._normalise_sku()
        if (
            self.publication_status == self.PublicationStatus.PUBLISHED
            and self.published_at is None
        ):
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="products/gallery/%Y/%m/", validators=IMAGE_VALIDATORS
    )
    alt_text = models.CharField(
        max_length=160, 
        help_text="Describe what is visible in the photo."
    )

    display_order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"{self.product.name} image {self.display_order}"