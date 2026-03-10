from django.utils.translation import gettext_lazy as _
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.throttling import AnonRateThrottle
from rest_framework.response import Response

from .settings import api_settings


class RegiterAPIView(CreateAPIView):
    """
    New account registration
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = api_settings.REGISTRATION_SERIALIZER
    throttle_classes = (AnonRateThrottle,)


class VerifyEmailAPIView(GenericAPIView):
    """
    Email verification endpoint
    """
    permission_classes = ()
    authentication_classes = ()
    throttle_classes = (AnonRateThrottle,)
    serializer_class = api_settings.VERIFY_SERIALIZER

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": _("Email verified successfully.")})
