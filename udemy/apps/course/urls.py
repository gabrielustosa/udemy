from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('course', views.CourseViewSet, basename='course')
router.register('relation/course', views.CourseRelationViewSet, basename='course_relation')

urlpatterns = router.urls
