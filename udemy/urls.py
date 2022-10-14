from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),

    # path('accounts/register/', UserRegisterView.as_view(), name='register'),
    # path('accounts/login/', views_login.LoginView.as_view(), name='login'),
    # path('accounts/logout/', views_login.LogoutView.as_view(), name='logout'),

    path("__reload__/", include("django_browser_reload.urls")),

    path('api/user/', include('udemy.apps.user.api.urls'))

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
