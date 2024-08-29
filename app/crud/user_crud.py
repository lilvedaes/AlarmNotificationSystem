from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.crud import schemas
from app.utils.logger import logger

# User CRUD operations
def get_user_by_id(db: Session, id: int) -> schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.id == id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by id '{id}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user by id '{id}': {e}")
        raise

def get_user_by_username(db: Session, username: str) -> schemas.User:
    try:
        result = db.execute(select(models.User).filter(models.User.username == username))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching user by username '{username}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching user by username '{username}': {e}")
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
        db.rollback()
        logger.error(f"Validation error for user creation: {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating user '{user.username}': {e}")
        raise

def update_user(db: Session, user: schemas.User, user_update: schemas.UserUpdate) -> schemas.User:
    try:
        # Validate schema
        user = schemas.User.model_validate(user)

        # Update user
        if user_update.email:
            user.email = user_update.email
        if user_update.phone_number:
            user.phone_number = user_update.phone_number
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

def delete_user_by_id(db: Session, user_id: int, get_alarms_by_user_func, delete_alarm_func) -> None:
    try:
        # Delete all related alarms
        alarms = get_alarms_by_user_func(db, user_id)
        for alarm in alarms:
            delete_alarm_func(db, alarm.id)

        # Delete the user
        db.execute(delete(models.User).filter(models.User.id == user_id))
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting user with ID '{user_id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting user with ID '{user_id}': {e}")
        raise