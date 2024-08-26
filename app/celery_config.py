# app/celery_config.py

from celery import Celery

celery = Celery(
    __name__,
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task
def send_notification(alarm_id, user_id, message):
    # Logic to send notification using AWS SNS
    from app.aws_utils import send_sns_notification
    send_sns_notification(alarm_id, user_id, message)
