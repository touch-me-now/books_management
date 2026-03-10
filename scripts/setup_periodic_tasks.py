from django_celery_beat.models import PeriodicTask, CrontabSchedule


def setup_periodic_tasks():
    daily_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="0",
        hour="8",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )

    PeriodicTask.objects.get_or_create(
        name="Notify users about new books",
        defaults={
            "crontab": daily_schedule,
            "task": "apps.books.tasks.notify_new_books",
        }
    )

    PeriodicTask.objects.get_or_create(
        name="Notify users about anniversary books",
        defaults={
            "crontab": daily_schedule,
            "task": "apps.books.tasks.notify_users_about_anniversary_books",
        }
    )

    print("Periodic tasks created successfully.")


if __name__ == "__main__":
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    setup_periodic_tasks()
