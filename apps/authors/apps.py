from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthorsConfig(AppConfig):
    name = 'apps.authors'
    verbose_name = _("Authors")

    def ready(self):
        import apps.authors.signals  # noqa
