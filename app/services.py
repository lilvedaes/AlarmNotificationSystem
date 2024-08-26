# import pytz
from datetime import datetime
from sqlalchemy.orm import Session
# from app import crud
# from app.config import settings
# from app.aws_utils import create_sqs_message, log_event_to_dynamodb

# Handle immediate alarms
def handle_new_alarms(db: Session):
    # now = datetime.now()
    # alarms = crud.get_alarms_due_today(db)
    # for alarm in alarms:
    #     alarm_time = datetime.combine(now.date(), alarm.time)
    #     event = {
    #         'id': alarm.id,
    #         'user_id': alarm.user_id,
    #         'message': alarm.message,
    #         'time': alarm_time.isoformat(),
    #         'email': alarm.email,
    #         'phone_number': alarm.phone_number,
    #         'days_of_week': alarm.days_of_week,
    #         'send_sms': alarm.send_sms,
    #         'send_email': alarm.send_email,
    #     }
    #     log_event_to_dynamodb(event)
    #     create_sqs_message(event)
    pass

# Create and schedule alarms for the next day
def create_and_schedule_alarms_for_next_day(db: Session):
    # users = crud.get_all_users(db)
    # for user in users:
    #     timezone = pytz.timezone(settings.postgres_tz)
    #     today = datetime.now(timezone).date()
    #     tomorrow = today + timedelta(days=1)
    #     alarms = crud.get_alarms_by_user(db, user.id)

    #     for alarm in alarms:
    #         for day in alarm.days_of_week:
    #             if day == tomorrow.weekday():
    #                 alarm_time = datetime.combine(now.date(), alarm.time)
    #                 event = {
    #                     'id': alarm.id,
    #                     'user_id': user.id,
    #                     'message': alarm.message,
    #                     'time': alarm_time.isoformat(),
    #                     'email': user.email,
    #                     'phone_number': user.phone_number,
    #                     'days_of_week': alarm.days_of_week,
    #                     'send_sms': alarm.send_sms,
    #                     'send_email': alarm.send_email,
    #                 }
    #                 log_event_to_dynamodb(event)
    #                 create_sqs_message(event)
    #                 break
    pass
