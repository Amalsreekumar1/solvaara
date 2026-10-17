from django.contrib import admin
from django.utils import timezone
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "display_order", "is_active"]
    list_editable = ["display_order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.action(description="Publish selected products")
def publish_products(modeladmin, request, queryset):
    published = 0
    skipped = 0

    for product in queryset:
        if not product.main_image:
            skipped += 1
            continue
        product.publication_status = Product.PublicationStatus.PUBLISHED
        product.save()
        published += 1

    message = f"{published} product(s) published."
    if skipped:
        message += f" {skipped} skipped (no main image)."
    modeladmin.message_user(request, message)


@admin.action(description="Unpublish selected products")
def unpublish_products(modeladmin, request, queryset):
    count = 0

    for product in queryset:
        product.publication_status = Product.PublicationStatus.DRAFT
        product.save()
        count += 1

    modeladmin.message_user(request, f"{count} product(s) unpublished.")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "category",
        "price",
        "availability_status",
        "publication_status",
        "is_featured",
    ]
    list_filter = [
        "category",
        "availability_status",
        "publication_status",
        "is_featured",
    ]
    list_editable = ["availability_status", "is_featured"]
    search_fields = ["name", "sku"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "published_at"]
    inlines = [ProductImageInline]
    actions = [publish_products, unpublish_products]

    fieldsets = (
        ("Basics", {
            "fields": (
                "name", "slug", "sku", "category",
                "short_description", "description",
            ),
        }),
        ("Pricing", {
            "fields": ("price", "sale_price"),
        }),
        ("Product details", {
            "fields": (
                "material", "plating", "colour",
                "dimensions", "available_sizes",
            ),
        }),
        ("Images", {
            "fields": ("main_image", "main_image_alt"),
        }),
        ("Status", {
            "fields": (
                "availability_status",
                "publication_status",
                "is_featured",
            ),
        }),
        ("Dates", {
            "fields": ("created_at", "updated_at", "published_at"),
        }),
    )