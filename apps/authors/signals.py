from django.db.models import ProtectedError, Count
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import Author


@receiver(pre_delete, sender=Author)
def protect_author_with_books(sender, instance, **kwargs):
    # books where this author is the only one
    sole_author_books = instance.books.annotate(
        author_count=Count("authors")
    ).filter(author_count=1)
    
    if sole_author_books.exists():
        raise ProtectedError(
            _("Cannot delete author: they are the sole author of some books."),
            sole_author_books
        )
