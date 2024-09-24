from rest_framework.routers import SimpleRouter

from store_api import views

router = SimpleRouter()
router.register(r'', views.UserViewSet)

urlpatterns = router.urls
