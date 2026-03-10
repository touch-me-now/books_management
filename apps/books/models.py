from typing import TypeVar

from django.apps import apps
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class Genre(models.Model):
    name = models.CharField(_("name"), max_length=50, unique=True)

    class Meta:
        ordering = ("id",)
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField(_("title"), max_length=100)
    summary = models.TextField(_("summary"))
    # ISBN-10 - old ex: 0-306-40615-2, 0-19-853453-X
    # ISBN-13 - new (starts from 978 or 979) ex: 978-3-16-148410-0, 979-0-2600-0043-8
    # hyphens don't carry any meaning, so only numbers will be stored.
    isbn = models.CharField(
        max_length=13,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{9}[\dX]$|^\d{13}$',
                message=_('Enter a valid ISBN-10 or ISBN-13.'),
                code='invalid_isbn'
            )
        ]
    )
    # It's worth ensuring that the author's deletion is checked at the signal level
    #  to prevent deletion if this is the only author of the book
    authors = models.ManyToManyField(settings.AUTHOR_MODEL, verbose_name=_("authors"), related_name="books")
    publication_date = models.DateField(_("publication date"), db_index=True)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, verbose_name=_("genre"))
    created_at = models.DateTimeField(_("created time"), auto_now_add=True)

    class Meta:
        ordering = ("-publication_date",)
        verbose_name = _("Book")
        verbose_name_plural = _("Books")

    def __str__(self) -> str:
        return self.title


class UserFavoriteBook(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="favorite_books",
        verbose_name=_("user")
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="user_favorites",
        verbose_name=_("book")
    )
    added_at = models.DateTimeField(_("added time"), auto_now_add=True)

    class Meta:
        verbose_name = _("User favorite book")
        verbose_name_plural = _("User favorite books")

    def __str__(self) -> str:
        user_id = getattr(self, "user_id")
        book_id = getattr(self, "book_id")
        return str(
            _('User: %(user)s Book: %(book)s.') % {'user': user_id, 'book': book_id}
        )

A = TypeVar("A", bound=models.Model)

def get_author_model() -> A:
    return apps.get_model(settings.AUTHOR_MODEL)
