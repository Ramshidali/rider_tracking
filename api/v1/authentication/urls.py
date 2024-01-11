from django.urls import path, re_path
from rest_framework_simplejwt.views import (TokenRefreshView,)
from . import views

app_name = 'authentication'

urlpatterns = [

    re_path(r'^token/$', views.UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),

    re_path(r'^create-user/$', views.create_user, name='create_user'),
    re_path(r'^login/$', views.login, name='login'),
    
    re_path(r'^users-list/$', views.users_list, name='users_list'),

]
