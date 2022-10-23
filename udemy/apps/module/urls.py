from rest_framework.routers import SimpleRouter

from . import views

router = SimpleRouter()
router.register('', views.ModuleViewSet, basename='module')

urlpatterns = router.urls
