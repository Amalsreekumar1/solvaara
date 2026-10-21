from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import F, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EnquiryForm
from .models import Category, Product

SORT_OPTIONS = [
    ("newest", "Newest", ["-published_at"]),
    ("name", "Name A-Z", ["name"]),
    ("price_low", "Price: low to high", [F("price").asc(nulls_last=True)]),
    ("price_high", "Price: high to low", [F("price").desc(nulls_last=True)]),
]
PAGE_SIZE = 8


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

    category_options = [
        (c.slug, c.name, c.slug == category_slug)
        for c in Category.objects.filter(is_active=True)
    ]
    filter_open = bool(
        request.GET.get("filter") or query or min_price or max_price or category_slug
    )

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
        "category_options": category_options,
        "filter_open": filter_open,
    }
    return render(request, "catalogue/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.published().select_related("category"),
        slug=slug,
    )

    related_products = (
        Product.objects.published()
        .filter(category=product.category)
        .exclude(pk=product.pk)
        .select_related("category")[:4]
    )

    whatsapp_link = None
    if settings.WHATSAPP_NUMBER:
        base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
        message = f"Hi, I'd like to enquire about {product.name}"
        if product.sku:
            message += f" (code {product.sku})"
        message += f". {base}{product.get_absolute_url()}"
        whatsapp_link = (
            f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(message, safe='')}"
        )

    return render(
        request,
        "catalogue/product_detail.html",
        {
            "product": product,
            "whatsapp_link": whatsapp_link,
            "related_products": related_products,
        },
    )


def home(request):
    products = Product.objects.published().select_related("category")

    featured = list(
        products.filter(is_featured=True).order_by("-published_at")[:4]
    )
    if not featured:
        featured = list(products.order_by("-published_at")[:4])

    featured_ids = [product.pk for product in featured]

    new_arrivals = (
        products.exclude(is_featured=True)
        .exclude(pk__in=featured_ids)
        .order_by("-published_at")[:4]
    )

    context = {
        "featured_products": featured,
        "new_arrivals": new_arrivals,
    }
    return render(request, "catalogue/home.html", context)


POLICY_PAGES = {
    "shipping": "Shipping and delivery",
    "returns": "Returns and exchanges",
    "privacy": "Privacy policy",
    "terms": "Terms of use",
}


def policy(request, page):
    title = POLICY_PAGES.get(page)
    if title is None:
        raise Http404
    return render(request, "catalogue/policy.html", {"title": title})


ENQUIRY_LIMIT = 5
ENQUIRY_WINDOW = 60 * 60


def contact(request):
    form = EnquiryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        key = f"enquiry-count:{request.META.get('REMOTE_ADDR', 'unknown')}"
        count = cache.get(key, 0)
        if count >= ENQUIRY_LIMIT:
            form.add_error(
                None,
                "You have sent several enquiries recently. "
                "Please try again later, or message us on WhatsApp.",
            )
        else:
            form.save()
            cache.set(key, count + 1, ENQUIRY_WINDOW)
            messages.success(
                request,
                "Thank you. We have received your enquiry and will reply soon.",
            )
            return redirect("contact")

    return render(request, "catalogue/contact.html", {"form": form})


def about(request):
    return render(request, "catalogue/about.html")