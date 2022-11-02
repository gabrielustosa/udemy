from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('', views.QuestionViewSet, basename='question')
router.register('', views.QuestionViewSet, basename='question')

urlpatterns = router.urls
