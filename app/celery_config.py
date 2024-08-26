# app/celery_config.py

from celery import Celery
from app.config import settings
# from app.services import create_and_schedule_alarms_for_next_day
# from app.aws_utils import send_sns_notification, poll_sqs_queue

celery = Celery(
    __name__,
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

@celery.task
def send_notification(event):
    # send_sns_notification(event)
    pass

@celery.task
def poll_sqs_queue_task():
    # poll_sqs_queue()
    pass

@celery.task
def create_and_schedule_alarms_task():
    # create_and_schedule_alarms_for_next_day()
    pass

# Schedule checking SQS queue and creating alarms every 24 hours
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Poll SQS every minute
    # sender.add_periodic_task(60.0, poll_sqs_queue_task.s(), name='poll sqs every minute')
    # Create and schedule alarms every 24 hours
    # sender.add_periodic_task(86400.0, create_and_schedule_alarms_task.s(), name='create alarms daily')
    pass