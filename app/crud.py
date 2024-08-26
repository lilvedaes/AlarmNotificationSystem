from sqlalchemy.orm import Session
from app import models, schemas

# List of valid timezones

# User CRUD operations
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Alarm CRUD operations
def get_alarm(db: Session, alarm_id: int):
    return db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()

def create_alarm(db: Session, alarm: schemas.AlarmCreate, user: models.User):
    db_alarm = models.Alarm(
        user_id=user.id,
        message=alarm.message,
        time=alarm.time,
        days_of_week=alarm.days_of_week,
        is_active=alarm.is_active,
        send_sms=alarm.send_sms,
        send_email=alarm.send_email,
        timezone=user.timezone  # Use the user's timezone
    )
    db.add(db_alarm)
    db.commit()
    db.refresh(db_alarm)
    return db_alarm

def get_alarms_by_user(db: Session, user_id: int):
    return db.query(models.Alarm).filter(models.Alarm.user_id == user_id).all()

def delete_alarm(db: Session, alarm_id: int):
    db.query(models.Alarm).filter(models.Alarm.id == alarm_id).delete()
    db.commit()
