from django.urls import path, include

from rest_framework.routers import SimpleRouter

from . import views
from udemy.apps.answer import views as answer_views

router = SimpleRouter()
router.register('', views.MessageViewSet, basename='message')

app_name = 'message'

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<int:message_id>/answer/',
        answer_views.MessageAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answer-list'
    ),
]
