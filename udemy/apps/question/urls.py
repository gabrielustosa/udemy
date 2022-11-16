from django.urls import path, include

from rest_framework.routers import SimpleRouter

from . import views
from udemy.apps.action import views as action_views
from udemy.apps.answer import views as answer_views

router = SimpleRouter()
router.register('', views.QuestionViewSet, basename='question')

app_name = 'question'

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<int:question_id>/action/',
        action_views.QuestionActionViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='action-list'
    ),
    path(
        '<int:question_id>/action/<int:action>/',
        action_views.QuestionActionViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}),
        name='action-detail'
    ),
    path(
        '<int:question_id>/answer/',
        answer_views.QuestionAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answer-list'
    ),
]
