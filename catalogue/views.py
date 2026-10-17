from django.shortcuts import render

from .models import Product


def product_list(request):
    products = Product.objects.published().select_related("category")
    context = {"products": products}
    return render(request, "catalogue/product_list.html", context)