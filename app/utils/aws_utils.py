from datetime import datetime
from typing import List
import boto3
from app.utils.logger import logger
from app.config import settings

# Initialize AWS services
pinpoint_sms = boto3.client('pinpoint-sms-voice-v2')
dynamodb = boto3.resource('dynamodb')
notification_log_table = dynamodb.Table('AlarmNotificationSystemNotifications')

def get_pinpoint_verified_phone_numbers() -> List[dict]:
    logger.info("Getting verified phone numbers from Pinpoint")
    try:
        response = pinpoint_sms.describe_verified_destination_numbers(
            MaxResults=10
        )
        logger.info(f"Succcessfully retrieved {len(response['VerifiedDestinationNumbers'])} verified phone numbers from Pinpoint!")
        return response['VerifiedDestinationNumbers']
    except Exception as e:
        logger.error(f"Error getting verified phone numbers from Pinpoint: {e}")
        raise

def add_pinpoint_phone_number(phone_number: str) -> str:
    logger.info(f"Adding phone number to Pinpoint: {phone_number}")
    try:
        response = pinpoint_sms.create_verified_destination_number(
            DestinationPhoneNumber=phone_number
        )
        logger.info(f"Phone number added to Pinpoint: {response['VerifiedDestinationNumberId']}")
        return response['VerifiedDestinationNumberId']
    except Exception as e:
        logger.error(f"Error adding phone number to Pinpoint: {e}")
        raise

def send_pinpoint_verification_code(aws_phone_number_id: str) -> None:
    logger.info(f"Sending verification code to verified destination: {aws_phone_number_id}")
    try:
        response = pinpoint_sms.send_destination_number_verification_code(
            VerifiedDestinationNumberId=aws_phone_number_id,
            VerificationChannel='TEXT',
            LanguageCode='EN_US',
            OriginationIdentity=settings.end_user_messaging_sender_id_arn
        )
        logger.info(f"Verification code sent successfully: {response}")
    except Exception as e:
        logger.error(f"Error sending verification code: {e}")
        raise

def verify_pinpoint_phone_number(aws_phone_number_id: str, verification_code: str) -> None:
    logger.info(f"Verifying phone number: {aws_phone_number_id}")
    try:
        response = pinpoint_sms.verify_destination_number(
            VerifiedDestinationNumberId=aws_phone_number_id,
            VerificationCode=verification_code
        )
        logger.info(f"Phone number verified successfully: {response}")
    except Exception as e:
        logger.error(f"Error verifying phone number: {e}")
        raise

def remove_pinpoint_phone_number(aws_phone_number_id: str) -> None:
    logger.info(f"Removing phone number from Pinpoint: {aws_phone_number_id}")
    try:
        response = pinpoint_sms.delete_verified_destination_number(
            VerifiedDestinationNumberId=aws_phone_number_id
        )
        logger.info(f"Phone number removed from Pinpoint: {response}")
    except Exception as e:
        logger.error(f"Error removing phone number from Pinpoint: {e}")
        raise

def send_pinpoint_sms_notification(event: dict) -> None:
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

def log_notification_to_dynamodb(event):
    notification_log_table.put_item(
        Item={
            'alarm_id': event['id'],
            'user_id': event['user_id'],
            'phone_number': event['phone_number'],
            'message': event['message'],
            'timestamp': datetime.now().isoformat(),
        }
    )