from apscheduler.schedulers.background import BackgroundScheduler
# from app.celery_config import send_notification
from datetime import datetime, timedelta
# from app.config import settings
# import pytz

scheduler = BackgroundScheduler()

# TODO: Figure out the delay, why is it needed?
# def send_alarm_notification(event):
#     send_notification.delay(event)

# Schedule alarm to be sent at the specified time
def schedule_alarm(alarm):
    # timezone = pytz.timezone(settings.postgres_tz)
    # now = datetime.now(timezone)
    # scheduled_time = datetime.combine(now.date(), alarm.time)
    
    # if scheduled_time < now:
    #     scheduled_time += timedelta(days=1)

    # scheduler.add_job(
    #     send_alarm_notification,
    #     'date',
    #     run_date=scheduled_time,
    #     args=[alarm.dict()]
    # )
    pass

def start_scheduler():
    scheduler.start()
