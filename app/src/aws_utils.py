import boto3
# from app.models import Alarm
# from app.schemas import AlarmCreate
# from app.scheduler import schedule_alarm
# from app.config import settings

# dynamodb = boto3.resource('dynamodb')
# sns = boto3.client('sns')
# notification_log_table = dynamodb.Table('NotificationLogs')

import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def send_sns_sms_notification(event):
    logger.info("Send SMS Notification: %s", event)

def send_sns_email_notification(event):
    logger.info("Send Email Notification: %s", event)


# def log_notification_to_dynamodb(event):
#     notification_log_table.put_item(
#         Item={
#             'alarm_id': event['id'],
#             'user_id': event['user_id'],
#             'message': event['message'],
#             'timestamp': datetime.now().isoformat(),
#         }
#     )