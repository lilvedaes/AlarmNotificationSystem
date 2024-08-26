# app/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import pytz

scheduler = BackgroundScheduler()

def send_alarm_notification(alarm_id, user_id, message):
    from app.celery_config import send_notification
    send_notification.delay(alarm_id, user_id, message)

def schedule_alarm(alarm):
    timezone = pytz.timezone(alarm.timezone)
    now = datetime.now(timezone)
    scheduled_time = datetime.combine(now.date(), alarm.time)
    
    if scheduled_time < now:
        scheduled_time += timedelta(days=1)

    scheduler.add_job(
        send_alarm_notification,
        'date',
        run_date=scheduled_time,
        args=[alarm.id, alarm.user_id, alarm.message]
    )

def start_scheduler():
    scheduler.start()
