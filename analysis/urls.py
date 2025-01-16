from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('visualize/', views.visualize, name='visualize'),    
]
# from . means that the views module is imported from the current package (analysis).