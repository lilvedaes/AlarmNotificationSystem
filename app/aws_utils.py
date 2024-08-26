from datetime import datetime
import boto3
from app.models import Alarm
from app.schemas import AlarmCreate
from app.scheduler import schedule_alarm
from app import settings

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')
sqs = boto3.client('sqs')
notification_log_table = dynamodb.Table('NotificationLogs')
events_table = dynamodb.Table('Events')

def send_sns_notification(event):
    if event.get('send_sms'):
        sns.publish(
            PhoneNumber=event['phone_number'],
            Message=event['message'],
        )
    if event.get('send_email'):
        sns.publish(
            TopicArn=settings.sns_topic_arn,
            Message=event['message'],
            Subject='Alarm Notification',
        )
    log_notification_to_dynamodb(event)

def log_notification_to_dynamodb(event):
    notification_log_table.put_item(
        Item={
            'alarm_id': event['id'],
            'user_id': event['user_id'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat(),
        }
    )

def log_event_to_dynamodb(event):
    events_table.put_item(
        Item={
            'event_id': event['id'],
            'user_id': event['user_id'],
            'message': event['message'],
            'time': event['time'],
            'email': event['email'],
            'phone_number': event['phone_number'],
            'days_of_week': event['days_of_week'],
            'send_sms': event['send_sms'],
            'send_email': event['send_email'],
            'timestamp': datetime.now().isoformat(),
        }
    )

def create_sqs_message(event):
    sqs.send_message(
        QueueUrl=settings.sqs_queue_url,
        MessageBody=str(event)
    )

def poll_sqs_queue():
    response = sqs.receive_message(
        QueueUrl=settings.sqs_queue_url,
        MaxNumberOfMessages=10
    )
    for message in response.get('Messages', []):
        event = eval(message['Body'])  # Assuming message body is a stringified dict
        process_event(event)
        sqs.delete_message(
            QueueUrl=settings.sqs_queue_url,
            ReceiptHandle=message['ReceiptHandle']
        )

def process_event(event):
    schedule_alarm(AlarmCreate(**event))
    log_event_to_dynamodb(event)
