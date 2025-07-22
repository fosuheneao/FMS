"""
URL configuration for yugep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('yuapp.urls')),
    path('', include('coworker.urls')),
    path('', include('fieldmate.urls')),
    path('', include('edo.urls')),
    path('', include('buyer.urls')),
    path('', include('aic.urls')),
    path('', include('sales.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
