from urllib.parse import quote

from django.conf import settings
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator
from .models import Product
from decimal import Decimal, InvalidOperation

SORT_OPTIONS = [
    ("newest", "Newest", ["-published_at"]),
    ("name", "Name A-Z", ["name"]),
    ("price_low", "Price: low to high", [F("price").asc(nulls_last=True)]),
    ("price_high", "Price: high to low", [F("price").desc(nulls_last=True)]),
]
PAGE_SIZE = 12

def parse_price(value):
    try:
        number = Decimal(value)
    except InvalidOperation:
        return None
    return number if number >= 0 else None

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

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    min_value = parse_price(min_price)
    max_value = parse_price(max_price)
    if min_value is not None:
        products = products.filter(price__gte=min_value)
    if max_value is not None:
        products = products.filter(price__lte=max_value)

    sort = request.GET.get("sort", "newest")
    ordering = {key: order for key, label, order in SORT_OPTIONS}
    if sort not in ordering:
        sort = "newest"
    products = products.order_by(*ordering[sort])

    paginator = Paginator(products, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "querystring": querystring,
        "current_category": category_slug,
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
        "sort_options": [
            (key, label, key == sort) for key, label, order in SORT_OPTIONS
        ],
    }
    return render(request, "catalogue/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.published().select_related("category"),
        slug=slug,
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