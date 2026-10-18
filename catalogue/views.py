from django.shortcuts import render, get_object_or_404

from .models import Product
from urllib.parse import quote
from django.conf import settings
from django.db.models import Q


def product_list(request):
    products = Product.objects.published().select_related("category")

    category_slug = request.GET.get("category", "")
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(sku__icontains=query)
        )

    context = {
        "products": products,
        "current_category": category_slug,
        "query": query,
    }
    return render(request, "catalogue/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.published().select_related("category"),
        slug = slug,
    )

    whatsapp_link = None
    if settings.WHATSAPP_NUMBER:
        message = f"Hi, I'd like to enquire about {product.name}"
        if product.sku:
            message += f" (code {product.sku})"
        message += f". {request.build_absolute_uri(product.get_absolute_url())}"
        whatsapp_link = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(message, safe='')}"

        return render(
        request,
        "catalogue/product_detail.html",
        {"product": product, "whatsapp_link": whatsapp_link},
    )

