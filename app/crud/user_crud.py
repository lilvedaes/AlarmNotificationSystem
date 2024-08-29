from app.utils.aws_utils import add_pinpoint_phone_number, get_pinpoint_verified_phone_numbers, remove_pinpoint_phone_number, send_pinpoint_verification_code, verify_pinpoint_phone_number
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.schemas import user_schemas
from app.utils.logger import logger

# User CRUD operations
def get_user_by_id(db: Session, id: int) -> user_schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.id == id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by id '{id}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user by id '{id}': {e}")
        raise

def get_user_by_username(db: Session, username: str) -> user_schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.username == username))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by username '{username}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user by username '{username}': {e}")
        raise

def get_user_by_phone_number(db: Session, phone_number: str) -> user_schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.phone_number == phone_number))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by id '{phone_number}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user by id '{phone_number}': {e}")
        raise

def create_user(db: Session, user: user_schemas.UserCreate) -> user_schemas.User:
    try:
        # Check that you're below 10 verified phone numbers
        aws_verified_phone_numbers = get_pinpoint_verified_phone_numbers()
        if len(aws_verified_phone_numbers) >= 10:
            raise ValueError("You have reached the maximum number of verified phone numbers")
        
        # Add phone number to Pinpoint
        aws_phone_number_id = add_pinpoint_phone_number(user.phone_number)
        send_pinpoint_verification_code(aws_phone_number_id)

        # Add user to db
        db_user = models.User(
            username=user.username,
            phone_number=user.phone_number,
            aws_phone_number_id=aws_phone_number_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return user_schemas.User.model_validate(db_user)
    except SQLAlchemyError as e:
        db.rollback()  # Rollback in case of an error
        logger.error(f"Error creating user '{user.username}': {e}")
        raise
    except ValueError as e:
        db.rollback()
        logger.error(f"Validation error for user creation: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user '{user.username}': {e}")
        raise

def update_user(db: Session, user: user_schemas.User, user_update: user_schemas.UserUpdate) -> user_schemas.User:
    try:
        # Validate schema
        user = user_schemas.User.model_validate(user)

        # Update user
        if user_update.username:
            user.username = user_update.username
        if user_update.phone_number:
            # Delete old number from Pinpoint if it exists
            aws_verified_phone_numbers = get_pinpoint_verified_phone_numbers()
            for phone_number in aws_verified_phone_numbers:
                if phone_number['DestinationPhoneNumber'] == user.phone_number:
                    remove_pinpoint_phone_number(user.aws_phone_number_id)

            # Check that you're below 10 verified phone numbers
            if len(aws_verified_phone_numbers) >= 10:
                raise ValueError("You have reached the maximum number of verified phone numbers")

            # Add new phone number to Pinpoint
            aws_phone_number_id = add_pinpoint_phone_number(user_update.phone_number)
            send_pinpoint_verification_code(aws_phone_number_id)
            user.phone_number = user_update.phone_number
            user.aws_phone_number_id = aws_phone_number_id
        db.execute(
            update(models.User)
            .where(models.User.id == user.id)
            .values(username=user.username, phone_number=user.phone_number, aws_phone_number_id=user.aws_phone_number_id)
        )
        db.commit()

        return user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating user with ID '{user.id}': {e}")
        raise
    except ValueError as e:
        logger.error(f"Validation error for user update: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating user with ID '{user.id}': {e}")
        raise

def delete_user_by_id(db: Session, user: user_schemas.User, get_alarms_by_user_func, delete_alarm_func) -> None:
    try:
        # Delete verified number from Pinpoint if it exists
        verified_phone_numbers = get_pinpoint_verified_phone_numbers()
        for phone_number in verified_phone_numbers:
            if phone_number['DestinationPhoneNumber'] == user.phone_number:
                remove_pinpoint_phone_number(user.aws_phone_number_id)

        # Delete all related alarms
        alarms = get_alarms_by_user_func(db, user.id)
        for alarm in alarms:
            delete_alarm_func(db, alarm.id)

        # Delete the user
        db.execute(delete(models.User).filter(models.User.id == user.id))
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user with ID '{user.id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting user with ID '{user.id}': {e}")
        raise

def verify_phone_number(aws_phone_number_id: str, verification_code: str) -> None:
    try:
        # Verify phone number
        verify_pinpoint_phone_number(aws_phone_number_id, verification_code)
    except Exception as e:
        logger.error(f"Error verifying phone number: {e}")
        raise