from django.contrib import admin
from django.urls import path, include

from . import views


urlpatterns = [
    path('login_api_post/', views.authenticate_users.post_api, name='authenticate_user_api'),
    path('login_api_get/', views.authenticate_users.get_api, name='login_api'),
    path('login/', views.authenticate_users.as_view(), name='login_html'),

    path("bots/", include("bots.urls")),
    path('admin/', admin.site.urls),
]
