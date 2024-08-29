from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from app.db import models
from app.crud import schemas
from app.utils.logger import logger

# AlarmJob CRUD operations
def get_alarm_job_by_alarm_id(db: Session, alarm_id: int) -> schemas.AlarmJob:
    try:
        result = db.execute(select(models.AlarmJob).filter(models.AlarmJob.alarm_id == alarm_id))
        return result.scalars().first()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching alarm job for alarm ID '{alarm_id}': {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching alarm job for alarm ID '{alarm_id}': {e}")
        raise

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
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error creating alarm job for alarm '{alarm_job.alarm_id}': {e}")
        raise

def delete_alarm_job_by_alarm_id(db: Session, alarm_id: int) -> None:
    try:
        db.execute(delete(models.AlarmJob).filter(models.AlarmJob.alarm_id == alarm_id))
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error deleting alarm job with alarm ID '{alarm_id}': {e}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error deleting alarm job with alarm ID '{alarm_id}': {e}")
        raise