from django.urls import path

from . import views

app_name = 'answer'

urlpatterns = [
    path(
        '<int:answer_id>/', views.AnswerViewSet.as_view(
            {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='detail'
    ),
]
