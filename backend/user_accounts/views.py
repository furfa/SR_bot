import logging

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, parsers
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError, APIException
from rest_framework.decorators import action

from . import serializers
from . import models
from event_bus.utils import publish

logger = logging.getLogger(__name__)


class BotUserViewset(viewsets.ModelViewSet):
    queryset = models.BotUser.objects.all()
    serializer_class = serializers.BotUserSerializer

    @action(detail=True, methods=["POST"])
    def make_referral(self, request, pk=None):
        user = self.get_object()
        if user.inviting_user:
            raise ParseError('This user have inviting_user')

        inviter = models.BotUser.objects.get(id=request.data["id"])
        if not inviter:
            raise ParseError('No inviter user')
        if inviter.id == user.id:
            raise ParseError('inviter = inviting')
        if inviter.inviting_user and inviter.inviting_user.id == user.id:
            raise ParseError('Circular invite')

        user.inviting_user = inviter
        user.save()

        return Response( self.serializer_class(user).data )

    @action(detail=True, methods=["PATCH"])
    def update_last_usage(self, request, pk=None):
        user = self.get_object()
        user.last_usage_at = timezone.now()
        user.telegram_meta = request.data
        user.save()
        return Response( self.serializer_class(user).data )


class UserSupportQuestionViewset(viewsets.ModelViewSet):
    queryset = models.UserSupportQuestion.objects.filter(status=models.UserSupportQuestion.StatusChoices.CREATED)
    serializer_class = serializers.UserSupportQuestionSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type']

    def perform_update(self, serializer):
        serializer.save(status=models.UserSupportQuestion.StatusChoices.ANSWERED)


class GirlFormViewset(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet
    ):
    queryset = models.GirlForm.objects.all()
    serializer_class = serializers.GirlFormSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_object(self):
        user = models.BotUser.objects.get(pk=self.kwargs["pk"])
        forms = user.girl_profile.forms.filter(
            ~Q(status=models.GirlForm.StatusChoices.DELETED)
        )
        if not forms:
            raise NotFound()
        form = forms.latest('id')

        if not form:
            raise NotFound()
        return form

    @action(detail=True, methods=["POST"])
    def set_filled(self, request, pk=None):
        obj = self.get_object()
        obj.status = models.GirlForm.StatusChoices.FILLED
        obj.save()

        return Response( self.serializer_class(obj).data )

    @action(detail=False, methods=["POST"])
    def create_by_user(self, request, pk=None):
        try:
            user_id = request.data.get("user")
            user = models.BotUser.objects.get(id=user_id)
            profile = models.GirlProfile.objects.get(user=user)
            obj = models.GirlForm.objects.create(profile=profile)
        except Exception:
            raise NotFound()

        return Response( self.serializer_class(obj).data)


class GirlFormPhotoViewset(viewsets.ModelViewSet):
    queryset = models.GirlFormPhoto.objects.all()
    serializer_class = serializers.GirlFormPhotoSerializer
    parser_classes = (parsers.MultiPartParser, )
