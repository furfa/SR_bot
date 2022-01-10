from . import views

from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = []

router = SimpleRouter()

router.register("", views.PaymentScreenshotViewset, "payments")

urlpatterns += router.urls
