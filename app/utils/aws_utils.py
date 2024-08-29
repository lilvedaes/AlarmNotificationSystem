import boto3
from app.utils.logger import logger
from app.config import settings

# Initialize AWS services
pinpoint_sms = boto3.client('pinpoint-sms-voice-v2')

# dynamodb = boto3.resource('dynamodb')
# notification_log_table = dynamodb.Table('NotificationLogs')

def send_pinpoint_sms_notification(event):
    logger.info("Send SMS Notification: %s", event)
    try:
        response = pinpoint_sms.send_text_message(
            DestinationPhoneNumber=event['phone_number'],
            OriginationIdentity=settings.end_user_messaging_sender_id_arn,
            MessageBody=event['message'],
            MessageType='TRANSACTIONAL'
        )
        logger.info(f"SMS notification sent successfully: {response}")
    except Exception as e:
        logger.error(f"Error sending SMS notification: {e}")
        raise

# def log_notification_to_dynamodb(event):
#     notification_log_table.put_item(
#         Item={
#             'alarm_id': event['id'],
#             'user_id': event['user_id'],
#             'message': event['message'],
#             'timestamp': datetime.now().isoformat(),
#         }
#     )