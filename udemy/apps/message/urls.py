from django.urls import path

from . import views
from udemy.apps.answer import views as answer_views

app_name = 'message'

urlpatterns = [
    path('', views.MessageViewSet.as_view({'post': 'create'}), name='list'),
    path(
        '<int:pk>/',
        views.MessageViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='detail'
    ),
    path(
        '<int:message_id>/answer/',
        answer_views.MessageAnswerViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='answer-list'
    ),
]
