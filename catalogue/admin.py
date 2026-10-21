from django.contrib import admin

from .models import Category, Enquiry, Product, ProductImage


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
    no_image = 0
    no_alt = 0

    for product in queryset:
        if not product.main_image:
            no_image += 1
            continue
        if not product.main_image_alt.strip():
            no_alt += 1
            continue
        product.publication_status = Product.PublicationStatus.PUBLISHED
        product.save()
        published += 1

    message = f"{published} product(s) published."
    if no_image:
        message += f" {no_image} skipped (no main image)."
    if no_alt:
        message += f" {no_alt} skipped (no image description)."
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


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ["customer_name", "email", "phone", "status", "created_at"]
    list_filter = ["status", "created_at"]
    list_editable = ["status"]
    search_fields = ["customer_name", "email", "phone", "message"]
    readonly_fields = ["customer_name", "email", "phone", "message", "created_at"]