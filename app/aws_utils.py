from datetime import datetime
import boto3
# from app.models import Alarm
# from app.schemas import AlarmCreate
# from app.scheduler import schedule_alarm
# from app.config import settings

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
notification_log_table = dynamodb.Table('NotificationLogs')

def send_sns_sms_notification(event):
    print("Send SMS Notification")

def send_sns_email_notification(event):
    print("Send Email Notification")

def log_notification_to_dynamodb(event):
    notification_log_table.put_item(
        Item={
            'alarm_id': event['id'],
            'user_id': event['user_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat(),
        }
    )