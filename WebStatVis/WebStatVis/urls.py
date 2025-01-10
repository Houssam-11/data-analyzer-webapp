"""
URL configuration for WebStatVis project.

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
from django.contrib import admin
from django.urls import path , include

from django.conf import settings
from django.conf.urls.static import static

from django.http import HttpResponse

from analysis.views import homepage

def home_view(request):
    return HttpResponse("<h1>Welcome to the Data Analysis Project</h1>")


urlpatterns = [
    path('admin/', admin.site.urls), # standard for including the Django admin interface. 
                                    # allowing access to the admin interface at http://<domain>/admin/
    path('', homepage, name='homepage'), # Set the homepage as the default

    path('', include('analysis.urls')),  # Include analysis app URLs

]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # ensures media files are served during development.

'''
  this code configures the URL patterns for the Django admin interface 
 and sets up the ability to serve media files from the specified directory during development.
'''
