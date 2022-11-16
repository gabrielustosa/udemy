from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('course', views.CourseViewSet, basename='course')

urlpatterns = router.urls
