from django.urls import path
from . import views

urlpatterns = [
       path('', views.index, name='index'),
       path('getinfo', views.fetch_info, name='getinfo'),
       path('delete_file', views.delete_file, name='delete_file'),
       path('download', views.download, name='download'),
       path('download/<str:filename>/', views.download_file, name='download_file'),
]