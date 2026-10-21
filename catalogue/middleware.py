import os

from django.conf import settings


class IndexingControlMiddleware:
    """Adds noindex headers to the admin and, while indexing is off, to everything."""

    def __init__(self, get_response):
        self.get_response = get_response
        admin = os.environ.get("DJANGO_ADMIN_URL", "admin/").lstrip("/")
        self.admin_prefix = "/" + admin

    def __call__(self, request):
        response = self.get_response(request)
        if not settings.ALLOW_INDEXING or request.path.startswith(self.admin_prefix):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response