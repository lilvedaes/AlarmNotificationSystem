from celery import Celery
from app.config import settings
from app.aws_utils import send_sns_sms_notification, send_sns_email_notification

celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)
celery.conf.timezone = settings.timezone  # Set the timezone for the celery app

# Celery task to send SMS notification
@celery.task
def send_sms_notification(event):
    send_sns_sms_notification(event)

# Celery task to send email notification
@celery.task
def send_email_notification(event):
    send_sns_email_notification(event)