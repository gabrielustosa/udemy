from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/', include('udemy.apps.user.urls')),

    path('api/course/', include('udemy.apps.course.urls')),
    path('api/category/', include('udemy.apps.category.urls')),
    path('api/rating/', include('udemy.apps.rating.urls')),
    path('api/module/', include('udemy.apps.module.urls')),
    path('api/lesson/', include('udemy.apps.lesson.urls')),
    path('api/content/', include('udemy.apps.content.urls')),
    path('api/question/', include('udemy.apps.question.urls')),
    path('api/note/', include('udemy.apps.note.urls')),
    path('api/answer/', include('udemy.apps.answer.urls')),
    path('api/message/', include('udemy.apps.message.urls')),

    path("__reload__/", include("django_browser_reload.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
