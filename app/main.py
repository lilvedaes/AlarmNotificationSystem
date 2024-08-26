import pytz
from app.scheduler import start_scheduler
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas, crud
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}

# Create user
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return crud.create_user(db=db, user=user)

# Get user by username
@app.get("/users/{username}", response_model=schemas.User)
def get_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Create alarm
@app.post("/alarms/", response_model=schemas.Alarm)
def create_alarm(alarm: schemas.AlarmCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=alarm.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    alarm_data = schemas.AlarmCreate(**alarm.dict(), username=db_user.username)

    # Validate the days_of_week field
    for day in alarm_data.days_of_week:
        if day < 0 or day > 6:
            raise HTTPException(status_code=400, detail="Invalid day of the week")
    
    return crud.create_alarm(db=db, alarm=alarm_data, user=db_user)

# Get alarms by username
@app.get("/alarms/user/{username}", response_model=List[schemas.Alarm])
def get_alarms_by_username(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_alarms_by_user(db=db, user_id=db_user.id)

# Delete alarm
@app.delete("/alarms/{alarm_id}")
def delete_alarm(alarm_id: int, db: Session = Depends(get_db)):
    db_alarm = crud.get_alarm(db, alarm_id=alarm_id)
    if not db_alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    crud.delete_alarm(db, alarm_id=alarm_id)
    return {"message": "Alarm deleted successfully"}