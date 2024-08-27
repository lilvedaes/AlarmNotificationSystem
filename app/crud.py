import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, delete
from sqlalchemy.exc import SQLAlchemyError
from app import models, schemas
from app.celery_config import send_sms_notification, send_email_notification
from app.scheduler import schedule_alarm

# Set up logging
logger = logging.getLogger(__name__)

# User CRUD operations
async def get_user_by_username(db: AsyncSession, username: str) -> schemas.User | None:
    try:
        result = await db.execute(select(models.User).filter(models.User.username == username))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by username '{username}': {e}")
        raise

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> schemas.User:
    try:
        db_user = models.User(
            username=user.username,
            email=user.email,
            phone_number=user.phone_number,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return schemas.User.model_validate(db_user)
    except SQLAlchemyError as e:
        logger.error(f"Error creating user '{user.username}': {e}")
        raise
    except ValueError as e:
            logger.error(f"Validation error for user creation: {e}")
            raise

# Alarm CRUD operations
async def get_alarm(db: AsyncSession, alarm_id: int) -> schemas.Alarm | None:
    try:
        result = await db.execute(select(models.Alarm).filter(models.Alarm.id == alarm_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarm with ID '{alarm_id}': {e}")
        raise

async def create_alarm(db: AsyncSession, alarm: schemas.AlarmCreate, user: schemas.User) -> schemas.Alarm:
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
        await db.commit()
        await db.refresh(db_alarm)

        # Convert to schema
        alarm_schema = schemas.Alarm.model_validate(db_alarm)

        # Schedule alarms with APScheduler
        if alarm_schema.is_active:
            try:
                if alarm_schema.send_sms:
                    schedule_alarm(
                        notification_function=send_sms_notification, 
                        contact_info=user.phone_number, 
                        contact_key='phone_number', 
                        alarm=alarm_schema
                    )
                if alarm_schema.send_email:
                    schedule_alarm(
                        notification_function=send_email_notification, 
                        contact_info=user.email, 
                        contact_key='email', 
                        alarm=alarm_schema
                    )
            except Exception as e:
                logger.error(f"Error scheduling alarm '{db_alarm.id}' for user '{user.id}': {e}")
                raise

        return alarm_schema
    except SQLAlchemyError as e:
        logger.error(f"Error creating alarm for user '{user.id}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for alarm creation: {e}")
        raise

async def get_alarms_by_user(db: AsyncSession, user_id: int) -> list[schemas.Alarm]:
    try:
        result = await db.execute(select(models.Alarm).filter(models.Alarm.user_id == user_id))
        return result.scalars().all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarms for user ID '{user_id}': {e}")
        raise

async def delete_alarm(db: AsyncSession, alarm_id: int) -> None:
    try:
        await db.execute(delete(models.Alarm).filter(models.Alarm.id == alarm_id))
        await db.commit()
    except SQLAlchemyError as e:
        logger.error(f"Error deleting alarm with ID '{alarm_id}': {e}")
        raise
