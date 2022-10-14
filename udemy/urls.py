from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as views_login

from udemy.apps.user.views import UserRegisterView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/register/', UserRegisterView.as_view(), name='register'),
    path('accounts/login/', views_login.LoginView.as_view(), name='login'),
    path('accounts/logout/', views_login.LogoutView.as_view(), name='logout'),

    path("__reload__/", include("django_browser_reload.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
