
from django.contrib import admin
from django.urls import path
from django.urls import include
from fetch import urls
from authentication import auth_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include(urls)),
    path('',include(auth_urls)),
]

