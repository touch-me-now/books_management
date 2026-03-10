from datetime import timedelta

from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings


USER_SETTINGS = getattr(settings, "USERS_API_SETTINGS", None)
DEFAULTS = {
    # to provide substitution outside the application, without direct intervention
    "REGISTRATION_SERIALIZER": "apps.users.api.serializers.RegistrationSerializer",
    "CHECK_PASSWORD_SERIALIZER": "apps.users.api.serializers.CheckPasswordSerializer",
}
IMPORT_STRINGS = (
    "REGISTRATION_SERIALIZER",
    "CHECK_PASSWORD_SERIALIZER",
)

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*args, **kwargs) -> None:  # pragma: no cover
    global api_settings

    setting, value = kwargs["setting"], kwargs["value"]

    if setting == "USERS_API_SETTINGS":
        api_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(reload_api_settings)
