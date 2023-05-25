from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
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


class Error403View(TemplateView):
    """
    Render 403 Error Page
    """

    template_name = "errors/403.html"


class Error404View(TemplateView):
    """
    Render 404 Error Page
    """

    template_name = "errors/404.html"


class Error405View(TemplateView):
    """
    Render 405 Error Page
    """

    template_name = "errors/405.html"


def handler500(request, *args, **argv):
    """
    Render 500 Error Page
    """
    return render(request, "errors/500.html", status=500)
