from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
from app.schemas import alarm_schemas
from app.config import settings
from app.utils.constants import DAY_OF_WEEK_MAP
from app.utils.logger import logger
from app.utils.aws_utils import send_pinpoint_sms_notification

# APScheduler setup
jobstores = {
    'default': SQLAlchemyJobStore(url=settings.database_url)
}
scheduler = BackgroundScheduler(jobstores=jobstores)

# Schedule alarm to be sent at the specified time through sms
# Args:
#   alarm: The alarm object containing scheduling details.
#   phone_number: The contact information (phone number).
def schedule_alarm(
    alarm: alarm_schemas.Alarm,
    phone_number: str
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
        'phone_number': phone_number,
        **alarm.model_dump()
    }
    
    # Schedule the send notification function using APScheduler
    try:
        job_id = f"alarm_sms_{alarm.id}"
        scheduler.add_job(
            func=send_pinpoint_sms_notification,
            args=[event],
            trigger=trigger,
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Successfully scheduled job with ID {job_id}")
    except Exception as e:
        logger.error(f"Error scheduling job with ID {job_id}: {e}")
        raise

    return job_id

# Function to unschedule alarm
def unschedule_alarm(job_id: str):
    try:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
            logger.info(f"Successfully removed job with ID {job_id}")
        else:
            logger.warning(f"No job found with ID {job_id} to unschedule")
    except Exception as e:
        logger.error(f"Error unscheduling job with ID {job_id}: {e}")
        raise


# Function to start scheduler from outside the module
def start_scheduler():
    scheduler.start()