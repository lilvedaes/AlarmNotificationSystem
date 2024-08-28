from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from app.src import schemas
from app.config import settings
from app.src.constants import DAY_OF_WEEK_MAP
from typing import Callable, Dict

# APScheduler setup
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.database_url)
}
scheduler = BackgroundScheduler(jobstores=jobstores)

# Schedule alarm to be sent at the specified time through sms or email
# Args:
#   notification_function: The function to call.
#   contact_info: The contact information (email or phone number).
#   contact_key: The key in the event dictionary (either 'phone_number' or 'email').
#   alarm: The alarm object containing scheduling details.
def schedule_alarm(
    notification_function: Callable[[Dict], None], 
    contact_info: str, 
    contact_key: str, 
    alarm: schemas.Alarm
):
    # Create the CronTrigger with the correct day and time
    day_of_week_str = ','.join(DAY_OF_WEEK_MAP[day] for day in alarm.days_of_week)
    trigger = CronTrigger(
        day_of_week=day_of_week_str, 
        hour=alarm.time.hour, 
        minute=alarm.time.minute,
        second=alarm.time.second,
        timezone=settings.timezone
    )
    
    # Create the event dictionary
    event = {
        contact_key: contact_info,
        **alarm.model_dump()
    }
    
    # Schedule the send notidication function using APScheduler
    scheduler.add_job(
        func=notification_function,
        args=[event],
        trigger=trigger,
        id=f"alarm_{contact_key}_{alarm.id}",
        replace_existing=True
    )

# Function to start scheduler from outside the module
def start_scheduler():
    scheduler.start()