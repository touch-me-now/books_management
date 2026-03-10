from datetime import date

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import Book


def get_anviversary_dates() -> list[date]:
    today = timezone.now().date()
    anniversary_years = range(10, 200, 10)  # 10, 20, 30 ...

    anniversary_dates = []
    for years in anniversary_years:
        try:
            anniversary_dates.append(today.replace(year=today.year - years))
        except ValueError:
            # 29 February in a non-leap year
            pass
    return anniversary_dates


@shared_task
def notify_new_books():
    emails = get_user_model().objects.filter(is_active=True).values_list('email', flat=True)
    if not emails:
        return

    day_ago = timezone.now() - timezone.timedelta(days=1)
    books = list(
        Book.objects
        .filter(created_at__gte=day_ago)
        .values_list("title", "publication_date__year")
        .order_by("publication_date")[:20]
    )
    if books:
        context = {
            "title": "Today publicated books",
            "subtitle": "The following books have a publication today:",
            "books": books,
        }
        send_mail(
            subject="📚 Today publicated books",
            message=render_to_string("emails/mail.txt", context),
            html_message=render_to_string("emails/mail.html", context),
            recipient_list=list(emails),
            from_email=None,
            fail_silently=False,
        )



@shared_task
def notify_users_about_anniversary_books():
    emails = get_user_model().objects.filter(is_active=True).values_list('email', flat=True)
    if not emails:
        return

    anniversary_dates = get_anviversary_dates()
    books = list(
        Book.objects
        .filter(publication_date__in=anniversary_dates)
        .values_list("title", "publication_date__year")
        .order_by("publication_date")[:20]
    )

    if books:
        context = {
            "title": "Book Publication Anniversaries Today",
            "subtitle": "The following books have a publication anniversary today:",
            "books": books,
        }
        send_mail(
            subject="📚 Book Publication Anniversaries Today",
            message=render_to_string("emails/mail.txt", context),
            html_message=render_to_string("emails/mail.html", context),
            recipient_list=list(emails),
            from_email=None,
            fail_silently=False,
        )
