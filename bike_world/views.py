from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    """
    Create robots.txt file
    """
    lines = [
        "User-Agent: *",
        "Disallow: /accounts/",
        "Disallow: /bag/",
        "Sitemap: https://bike-world.herokuapp.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
