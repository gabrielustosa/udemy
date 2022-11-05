from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('question', views.QuestionViewSet, basename='question')
router.register('answer', views.AnswerViewSet, basename='answer')

urlpatterns = router.urls
