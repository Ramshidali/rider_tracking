from django.urls import path, re_path
from . import views

app_name = 'general'

urlpatterns = [
    re_path(r'^location-list/$', views.location_list, name='location_list'),
]
