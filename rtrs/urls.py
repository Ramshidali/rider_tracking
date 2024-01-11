from django.conf.urls import include
from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.urls import path, re_path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('rtrs/main/',include(('main.urls'),namespace='main')), 
    path('rtrs/rides/',include(('rides.urls'),namespace='rides')), 
    # path('rtrs/users/',include(('users.urls'),namespace='users')), 
    path('rtrs/locations/',include(('locations.urls'),namespace='locations')), 
    
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include(('api.v1.authentication.urls','authentication'), namespace='authentication')),
    path('api/v1/rides/', include(('api.v1.rides.urls','api_rides'), namespace='api_rides')),
    path('api/v1/general/', include(('api.v1.general.urls','api_general'), namespace='api_general')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]