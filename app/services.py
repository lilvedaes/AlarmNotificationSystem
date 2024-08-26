# app/services.py

from sqlalchemy.orm import Session
from app import crud, schemas

def create_and_schedule_alarm(db: Session, alarm: schemas.AlarmCreate):
    # Create alarm
    db_alarm = crud.create_alarm(db, alarm)

    # Schedule alarm using APScheduler (defined in scheduler.py)
    from app.scheduler import schedule_alarm
    schedule_alarm(db_alarm)

    return db_alarm
