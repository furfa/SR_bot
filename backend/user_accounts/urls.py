from rest_framework.routers import SimpleRouter

from . import views

urlpatterns = []

router = SimpleRouter()

router.register("users", views.BotUserViewset, "user")
router.register("girl_forms", views.GirlFormViewset, "girl_form")
router.register("girl_form_photos", views.GirlFormPhotoViewset, "girl_form_photos")
router.register("support_question", views.UserSupportQuestionViewset, "support_question")


urlpatterns += router.urls


