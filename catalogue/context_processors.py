import re

from django.conf import settings

from .models import Category


def categories(request):
    number = getattr(settings, "WHATSAPP_NUMBER", "")
    phone = getattr(settings, "CONTACT_PHONE", "")
    return {
        "nav_categories": Category.objects.filter(is_active=True),
        "site_whatsapp_link": f"https://wa.me/{number}" if number else "",
        "site_contact_email": getattr(settings, "CONTACT_EMAIL", ""),
        "site_phone": phone,
        "site_phone_href": re.sub(r"[^\d+]", "", phone),
        "site_address": getattr(settings, "CONTACT_ADDRESS", ""),
        "site_hours": getattr(settings, "OPENING_HOURS", ""),
        "site_instagram": getattr(settings, "INSTAGRAM_URL", ""),
        "site_facebook": getattr(settings, "FACEBOOK_URL", ""),
        "site_youtube": getattr(settings, "YOUTUBE_URL", ""),
        "currency": getattr(settings, "CURRENCY_SYMBOL", "\u20b9"),
    }