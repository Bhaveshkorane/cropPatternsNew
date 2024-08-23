from django.contrib import admin
from django.urls import path
from FETCH import urls

# For user registraion 
from .views import registeruser
from .views import loginuser
from .views import logouturl


urlpatterns = [ 
# User registrationa and login
    path('register/',registeruser,name='register_url'),
    path('login/',loginuser,name='login_url'),
    path('logout/',logouturl,name='logout_url'),
]
