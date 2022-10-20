from django.urls import path

from udemy.apps.user import views

app_name = 'user'

urlpatterns = [
    path('teste/', views.A.as_view(), name='teste'),
    path('create/', views.CreateUserView.as_view(), name='create'),
]
