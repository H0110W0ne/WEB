from celery import shared_task
from django.db import transaction

from .models import Registration
from .services import build_registration_text, send_telegram_message


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def send_registration_to_telegram(self, registration_id: int):
    registration = Registration.objects.select_related('direction').get(pk=registration_id)
    text = build_registration_text(registration)
    send_telegram_message(text)
    registration.telegram_sent = True
    registration.telegram_error = ''
    registration.save(update_fields=['telegram_sent', 'telegram_error'])
    return {'ok': True, 'registration_id': registration_id}


def enqueue_registration_notification(registration_id: int):
    transaction.on_commit(lambda: send_registration_to_telegram.delay(registration_id))
