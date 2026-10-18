from django.shortcuts import render, get_object_or_404

from .models import Product


def product_list(request):
    products = Product.objects.published().select_related("category")
    context = {"products": products}
    return render(request, "catalogue/product_list.html", context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.published().select_related("category"),
        slug = slug,
    )
    return render(request, "catalogue/product_detail.html", {"product": product})

