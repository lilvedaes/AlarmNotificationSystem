# app/crud.py

from sqlalchemy.orm import Session
from app import models, schemas

def get_alarm(db: Session, alarm_id: int):
    return db.query(models.Alarm).filter(models.Alarm.id == alarm_id).first()

def create_alarm(db: Session, alarm: schemas.AlarmCreate):
    db_alarm = models.Alarm(**alarm.dict())
    db.add(db_alarm)
    db.commit()
    db.refresh(db_alarm)
    return db_alarm

def delete_alarm(db: Session, alarm_id: int):
    db.query(models.Alarm).filter(models.Alarm.id == alarm_id).delete()
    db.commit()
