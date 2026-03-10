from datetime import date

from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

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
    books = Book.objects.filter(created_at__gte=day_ago).values_list("title", flat=True)[:10]
    if books:
        book_list = "\n".join(f"* {book}" for book in books)

        send_mail(
            'New Books Added',
            f'New books have been added in the last day: {book_list}',
            recipient_list=emails,
            from_email=None,  # Use default from email
            fail_silently=False,
        )
        print(f"New books added in the last day: {book_list}")


@shared_task
def notify_users_about_anniversary_books():
    emails = get_user_model().objects.filter(is_active=True).values_list('email', flat=True)
    if not emails:
        return

    anniversary_dates = get_anviversary_dates()
    books = Book.objects.filter(publication_date__in=anniversary_dates).values_list("title", flat=True)
    if books:
        book_list = "\n".join(f"* {book}" for book in books)
        send_mail(
            'Book Publication Anniversary',
            f'Today is the publication anniversary of the following books: {book_list}',
            recipient_list=emails,
            from_email=None,  # Use default from email
            fail_silently=False,
        )
        print(f"Books with publication anniversary today: {book_list}")
