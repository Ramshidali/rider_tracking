from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenRefreshView,)
from . import views

app_name = 'rides'

urlpatterns = [
    re_path(r'^ride/(?P<pk>.*)/$', views.ride, name='rides'),
    re_path(r'^rides-list/$', views.rides_list, name='rides_list'),
    re_path(r'^create-ride/$', views.create_ride, name='create_ride'),
    re_path(r'^ride-status-update/(?P<pk>.*)/$', views.update_ride_status, name='update_ride_status'),
    re_path(r'^ride-tracking/(?P<pk>.*)/$', views.ride_tracking, name='ride_tracking'),
    re_path(r'^match-ride-to-driver/(?P<pk>.*)/$', views.match_ride_to_driver, name='match_ride_to_driver'),
    re_path(r'^accept-ride-request/(?P<pk>.*)/$', views.accept_ride_request, name='accept_ride_request'),
]
