from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.schemas import user_schemas, alarm_schemas, alarm_job_schemas
from app.utils.aws_utils import send_sns_sms_notification, send_sns_email_notification
from app.utils.scheduler import schedule_alarm, unschedule_alarm
from app.utils.logger import logger

# Alarm CRUD operations
def get_alarm_by_id(db: Session, alarm_id: int) -> alarm_schemas.Alarm:
    try:
        result = db.execute(select(models.Alarm).filter(models.Alarm.id == alarm_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarm with ID '{alarm_id}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching alarm with ID '{alarm_id}': {e}")
        raise

def get_alarms_by_user_id(db: Session, user_id: int) -> List[alarm_schemas.Alarm]:
    try:
        result = db.execute(select(models.Alarm).filter(models.Alarm.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarms for user ID '{user_id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred while getting alarms by user with ID '{user_id}': {e}")
        raise

def create_alarm(
        db: Session, 
        alarm_create: alarm_schemas.AlarmCreate, 
        user: user_schemas.User, 
        create_alarm_job_func
    ) -> alarm_schemas.Alarm:
    try:
        # Add alarm to db
        db_alarm = models.Alarm(
            user_id=user.id,
            message=alarm_create.message,
            time=alarm_create.time,
            days_of_week=alarm_create.days_of_week,
            is_active=alarm_create.is_active,
            send_sms=alarm_create.send_sms,
            send_email=alarm_create.send_email
        )
        db.add(db_alarm)
        db.commit()
        db.refresh(db_alarm)

        # Validate schema
        alarm = alarm_schemas.Alarm.model_validate(db_alarm)

        # Schedule alarms with APScheduler
        sms_job_id = None
        email_job_id = None
        if alarm.is_active:
            if alarm.send_sms:
                sms_job_id = schedule_alarm(
                    notification_function=send_sns_sms_notification, 
                    contact_info=user.phone_number, 
                    contact_key='phone_number', 
                    alarm=alarm
                )
            if alarm.send_email:
                email_job_id = schedule_alarm(
                    notification_function=send_sns_email_notification, 
                    contact_info=user.email, 
                    contact_key='email', 
                    alarm=alarm
                )

        # Creating alarm job in DB
        create_alarm_job_func(db, alarm_job_schemas.AlarmJobCreate(
            alarm_id=alarm.id,
            sms_job_id=sms_job_id,
            email_job_id=email_job_id
        ))

        return alarm
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating alarm for user '{user.id}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for alarm creation: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred while creating alarm for user '{user.id}': {e}")
        raise

def update_alarm(
        db: Session, 
        alarm: alarm_schemas.Alarm, 
        alarm_update: alarm_schemas.AlarmUpdate, 
        get_user_by_id_func, 
        get_alarm_job_func
    ) -> alarm_schemas.Alarm:
    try:
        # Validate schema
        alarm = alarm_schemas.Alarm.model_validate(alarm)

        # Update the alarm
        alarm.is_active = alarm_update.is_active
        db.commit()

        sms_job_id = None
        email_job_id = None
        
        # Schedule alarms if active
        if alarm.is_active:
            # Get user information
            user = get_user_by_id_func(db, alarm.user_id)
            if alarm.send_sms:
                sms_job_id = schedule_alarm(
                    notification_function=send_sns_sms_notification, 
                    contact_info=user.phone_number, 
                    contact_key='phone_number', 
                    alarm=alarm
                )
            if alarm.send_email:
                email_job_id = schedule_alarm(
                    notification_function=send_sns_email_notification, 
                    contact_info=user.email, 
                    contact_key='email', 
                    alarm=alarm
                )
        else:
            # Unschedule alarms if inactive
            alarm_job = get_alarm_job_func(db, alarm.id)
            if alarm_job:
                if alarm_job.sms_job_id:
                    unschedule_alarm(alarm_job.sms_job_id)
                if alarm_job.email_job_id:
                    unschedule_alarm(alarm_job.email_job_id)
            sms_job_id = None
            email_job_id = None

        # Update alarm job in DB
        db.execute(
            models.AlarmJob.__table__.update()
            .where(models.AlarmJob.alarm_id == alarm.id)
            .values(sms_job_id=sms_job_id, email_job_id=email_job_id)
        )
        db.commit()

        return alarm_schemas.Alarm.model_validate(alarm)
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating alarm with ID '{alarm.id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred while updating alarm with ID '{alarm.id}': {e}")
        raise

def delete_alarm_by_id(db: Session, alarm_id: int, get_alarm_job_func, delete_alarm_job_func) -> None:
    try:
        # Fetch the alarm job first
        alarm_job = get_alarm_job_func(db, alarm_id)

        # Unschedule before deleting from the database
        if alarm_job:
            if alarm_job.sms_job_id:
                unschedule_alarm(alarm_job.sms_job_id)
            if alarm_job.email_job_id:
                unschedule_alarm(alarm_job.email_job_id)

        # Delete the alarm and alarm job from the database
        db.execute(delete(models.Alarm).filter(models.Alarm.id == alarm_id))
        delete_alarm_job_func(db, alarm_id)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting alarm with ID '{alarm_id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error when deleting alarm with ID '{alarm_id}': {e}")
        raise
