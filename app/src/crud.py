import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.src import schemas
from app.src.aws_utils import send_sns_sms_notification, send_sns_email_notification
from app.src.scheduler import schedule_alarm, unschedule_alarm

# Set up logging
logger = logging.getLogger(__name__)

# User CRUD operations
def get_user_by_username(db: Session, username: str) -> schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.username == username))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by username '{username}': {e}")
        raise

def create_user(db: Session, user: schemas.UserCreate) -> schemas.User:
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return schemas.User.model_validate(db_user)
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of an error
        logger.error(f"Error creating user '{user.username}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for user creation: {e}")
        raise

# AlarmJob CRUD operations
def create_alarm_job(db: Session, alarm_job: schemas.AlarmJobCreate) -> schemas.AlarmJob:
    try:
        db_alarm_job = models.AlarmJob(
            alarm_id=alarm_job.alarm_id,
            sms_job_id=alarm_job.sms_job_id,
            email_job_id=alarm_job.email_job_id
        )
        db.add(db_alarm_job)
        db.commit()
        db.refresh(db_alarm_job)
        return schemas.AlarmJob.model_validate(db_alarm_job)
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of an error
        logger.error(f"Error creating alarm job for alarm '{alarm_job.alarm_id}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for alarm job creation: {e}")
        raise

def get_alarm_job(db: Session, alarm_id: int) -> schemas.AlarmJob:
    try:
        result = db.execute(select(models.AlarmJob).filter(models.AlarmJob.alarm_id == alarm_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarm job for alarm ID '{alarm_id}': {e}")
        raise

def delete_alarm_job(db: Session, alarm_id: int) -> None:
    try:
        db.execute(delete(models.AlarmJob).filter(models.AlarmJob.alarm_id == alarm_id))
        db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error deleting alarm job with alarm ID '{alarm_id}': {e}")
        raise

# Alarm CRUD operations
def get_alarm(db: Session, alarm_id: int) -> schemas.Alarm:
    try:
        result = db.execute(select(models.Alarm).filter(models.Alarm.id == alarm_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarm with ID '{alarm_id}': {e}")
        raise

def create_alarm(db: Session, alarm: schemas.AlarmCreate, user: schemas.User) -> schemas.Alarm:
    try:
        # Add alarm to db
        db_alarm = models.Alarm(
            user_id=user.id,
            message=alarm.message,
            time=alarm.time,
            days_of_week=alarm.days_of_week,
            is_active=alarm.is_active,
            send_sms=alarm.send_sms,
            send_email=alarm.send_email
        )
        db.add(db_alarm)
        db.commit()
        db.refresh(db_alarm)

        # Convert to schema
        alarm_schema = schemas.Alarm.model_validate(db_alarm)

        # Schedule alarms with APScheduler
        if alarm_schema.is_active:
            try:
                sms_job_id = None
                email_job_id = None
                if alarm_schema.send_sms:
                    sms_job_id = schedule_alarm(
                        notification_function=send_sns_sms_notification, 
                        contact_info=user.phone_number, 
                        contact_key='phone_number', 
                        alarm=alarm_schema
                    )
                if alarm_schema.send_email:
                    email_job_id = schedule_alarm(
                        notification_function=send_sns_email_notification, 
                        contact_info=user.email, 
                        contact_key='email', 
                        alarm=alarm_schema
                    )

                # Creating alarm job in DB
                create_alarm_job(db, schemas.AlarmJobCreate(
                    alarm_id=alarm_schema.id,
                    sms_job_id=sms_job_id,
                    email_job_id=email_job_id
                ))

            except Exception as e:
                # Rollback if there's an error during scheduling or creating alarm job
                db.rollback()
                logger.error(f"Error scheduling alarm '{db_alarm.id}' for user '{user.id}': {e}")
                raise

        return alarm_schema

    except SQLAlchemyError as e:
        # Rollback on database-related errors
        db.rollback()
        logger.error(f"Error creating alarm for user '{user.id}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for alarm creation: {e}")
        raise

def get_alarms_by_user(db: Session, user_id: int) -> List[schemas.Alarm]:
    try:
        result = db.execute(select(models.Alarm).filter(models.Alarm.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarms for user ID '{user_id}': {e}")
        raise

def delete_alarm(db: Session, alarm_id: int) -> None:
    try:
        # Fetch the alarm job first
        alarm_job = get_alarm_job(db, alarm_id)

        # Unschedule before deleting from the database
        if alarm_job:
            if alarm_job.sms_job_id:
                unschedule_alarm(alarm_job.sms_job_id)
            if alarm_job.email_job_id:
                unschedule_alarm(alarm_job.email_job_id)

        # Delete the alarm and alarm job from the database
        db.execute(delete(models.Alarm).filter(models.Alarm.id == alarm_id))
        delete_alarm_job(db, alarm_id)
        db.commit()

    except SQLAlchemyError as e:
        logger.error(f"Error deleting alarm with ID '{alarm_id}': {e}")
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error when deleting alarm with ID '{alarm_id}': {e}")
        db.rollback()
        raise
