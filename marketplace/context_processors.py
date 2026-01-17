from django.conf import settings


def linkedin(request):
    """
    Expose the LinkedIn Insight Tag partner ID to templates.
    """
    return {
        "linkedin_partner_id": getattr(settings, "LINKEDIN_PARTNER_ID", None),
    }
