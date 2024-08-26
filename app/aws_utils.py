# app/aws_utils.py

import boto3

def send_sns_notification(alarm_id, user_id, message):
    sns = boto3.client('sns')
    # Send the SNS notification logic
    sns.publish(
        PhoneNumber='+1234567890',  # Placeholder for actual user phone number
        Message=message,
    )

def log_notification_to_dynamodb(alarm_id, user_id, message):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('NotificationLogs')
    table.put_item(
        Item={
            'alarm_id': alarm_id,
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        }
    )
