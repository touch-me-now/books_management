from celery import shared_task
from django.core.mail import send_mail

from .verify import EmailVerificationCode, verify_msg


@shared_task
def send_verification_code(email: str):
    verification = EmailVerificationCode.generate(email)
    verification.save()  # saving in cache
    send_mail(
        subject="Welcome to our Library API",
        message=verify_msg.format(code=verification.code),
        recipient_list=[email],
        from_email=None,
        fail_silently=False,
    )
