from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    first_name = models.CharField(_("first name"), max_length=50)
    last_name = models.CharField(_("last name"), max_length=50)
    biography = models.TextField(_("biography"), validators=[MinLengthValidator(10)])
    date_of_birth = models.DateField(_("date of birth"), db_index=True)
    date_of_death = models.DateField(
        _("date of death"),
        db_index=True,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = _("Author")
        verbose_name_plural = _("Authors")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_of_death__isnull=True) | models.Q(date_of_birth__lt=models.F('date_of_death')),
                name='date_of_birth_before_date_of_death'
            ),
            models.UniqueConstraint(
                fields=["first_name", "last_name"],
                name='unique_name',
            ),
        ]

    def get_short_name(self) -> str:
        """Return the short name for the author."""
        return "%s. %s" % (self.first_name[0], self.last_name)

    def __str__(self) -> str:
        return self.get_short_name()