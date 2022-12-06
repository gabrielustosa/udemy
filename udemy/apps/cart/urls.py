from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view({'get': 'list'}), name='list'),
    path('<int:course_id>/', views.CartView.as_view({'post': 'create', 'delete': 'destroy'}), name='detail'),
]
