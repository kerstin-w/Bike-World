"""bike_world URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from checkout.admin import DashboardView
from .views import Error403View, Error404View, handler500, robots_txt

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('home.urls')),
    path('products/', include('products.urls')),
    path('bag/', include('bag.urls')),
    path('checkout/', include('checkout.urls')),
    path('profile/', include('profiles.urls')),
    path('support/', include('support.urls')),
    path("robots.txt", robots_txt),
    path('sitemap.xml', TemplateView.as_view(
        template_name='sitemap.xml', content_type='text/xml')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Error Page Handlers
handler403 = Error403View.as_view()
handler404 = Error404View.as_view()
handler500 = handler500
