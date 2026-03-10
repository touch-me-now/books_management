from rest_framework.generics import CreateAPIView
from rest_framework.throttling import AnonRateThrottle

from .settings import api_settings


class RegiterAPIView(CreateAPIView):
    """
    New account registration
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = api_settings.REGISTRATION_SERIALIZER
    throttle_classes = (AnonRateThrottle,)
