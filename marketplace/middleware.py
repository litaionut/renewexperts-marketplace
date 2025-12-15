from __future__ import annotations

from django.conf import settings
from django.shortcuts import redirect


class SiteLockdownMiddleware:
    """
    Blochează accesul la site (în faza de testing) și permite doar câteva rute publice.

    Control:
      - settings.SITE_LOCKDOWN (bool)
      - settings.SITE_LOCKDOWN_ALLOW_PREFIXES (list[str])

    Comportament:
      - Dacă request.path începe cu unul din prefix-urile permise -> allow
      - Altfel -> redirect către settings.SITE_LOCKDOWN_REDIRECT_TO (default: 'home')
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "SITE_LOCKDOWN", False):
            return self.get_response(request)

        path = request.path or "/"
        allow_paths = set(getattr(settings, "SITE_LOCKDOWN_ALLOW_PATHS", []))
        allow_prefixes = getattr(settings, "SITE_LOCKDOWN_ALLOW_PREFIXES", [])

        if path in allow_paths:
            return self.get_response(request)

        if any(path.startswith(p) for p in allow_prefixes):
            return self.get_response(request)

        redirect_to = getattr(settings, "SITE_LOCKDOWN_REDIRECT_TO", "home")
        return redirect(redirect_to)


