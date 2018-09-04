"""icicle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from . import views
from icicle import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home),
    path('login/', views.login),
    path('admin/', admin.site.urls),
    path('food/', include('foodOrder.urls'), name='foodOrder'),
    path('attendance/', include('attendance.urls'), name='attendance'),
    path('home/', include('home.urls'), name='home'),
    path('logout/', views.logout)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
