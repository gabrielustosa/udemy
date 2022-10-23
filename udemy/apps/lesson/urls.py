from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('', views.LessonViewSet, basename='lesson')

urlpatterns = router.urls
