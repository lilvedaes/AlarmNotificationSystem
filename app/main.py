import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from app.src import schemas, crud
from app.db.database import SessionLocal
from app.src.scheduler import start_scheduler

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Dependency to get the synchronous DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()  # Start the scheduler as usual
    yield

app = FastAPI(lifespan=lifespan)

# Create a custom exception handler for RequestValidationError to throw BAD REQUEST
# When specifying response model as a schema, it runs schema validation and throws RequestValidationError if failed
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc: RequestValidationError):
    logger.error(f"Validation error occurred: {exc.errors()}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors()
        }
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}

# Create user
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"Username '{user.username}' already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    created_user = crud.create_user(db=db, user=user)
    logger.info(f"User '{user.username}' created successfully")
    return created_user

# Get user by username
@app.get("/users/{username}", response_model=schemas.User)
def get_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User with username '{username}' fetched successfully")
    return db_user

# Update user by id
@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        logger.warning(f"User with ID '{user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.phone_number == user_update.phone_number and db_user.email == user_update.email:
        return db_user
    
    updated_user = crud.update_user(db, db_user, user_update)
    logger.info(f"User with ID '{user_id}' updated successfully")
    return updated_user

# Create alarm
@app.post("/alarms/", response_model=schemas.Alarm)
def create_alarm(alarm: schemas.AlarmCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=alarm.username)
    if not db_user:
        logger.warning(f"User with username '{alarm.username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Additional validation
    if not alarm.days_of_week:
        logger.warning(f"Alarm creation failed for '{alarm.username}': days_of_week is empty")
        raise HTTPException(status_code=400, detail="Days of week must contain at least one element")
    if any(day < 0 or day > 6 for day in alarm.days_of_week):
        logger.warning(f"Alarm creation failed for '{alarm.username}': Invalid day of the week in {alarm.days_of_week}")
        raise HTTPException(status_code=400, detail="Invalid day of the week")
    if not alarm.send_email and not alarm.send_sms:
        logger.warning(f"Alarm creation failed for '{alarm.username}': Both send_email and send_sms are False")
        raise HTTPException(status_code=400, detail="At least one of send_email or send_sms must be True")
    
    created_alarm = crud.create_alarm(db=db, alarm_create=alarm, user=db_user)
    logger.info(f"Alarm with ID '{created_alarm.id}' created successfully for user '{alarm.username}'")
    return created_alarm

# Get alarms by username
@app.get("/alarms/user/{username}", response_model=List[schemas.Alarm])
def get_alarms_by_username(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    alarms = crud.get_alarms_by_user(db=db, user_id=db_user.id)
    logger.info(f"Fetched {len(alarms)} alarms for user '{username}'")
    return alarms

# Update alarm (activate/deactivate)
@app.put("/alarms/{alarm_id}", response_model=schemas.Alarm)
def update_alarm(alarm_id: int, alarm_update: schemas.AlarmUpdate, db: Session = Depends(get_db)):
    db_alarm = crud.get_alarm(db, alarm_id=alarm_id)
    if not db_alarm:
        logger.warning(f"Alarm with ID '{alarm_id}' not found")
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    if db_alarm.is_active == alarm_update.is_active:
        return db_alarm
    
    updated_alarm = crud.update_alarm(db, db_alarm, alarm_update)
    logger.info(f"Alarm with ID '{alarm_id}' updated successfully")
    return updated_alarm

# Delete alarm
@app.delete("/alarms/{alarm_id}")
def delete_alarm(alarm_id: int, db: Session = Depends(get_db)):
    db_alarm = crud.get_alarm(db, alarm_id=alarm_id)
    if not db_alarm:
        logger.warning(f"Alarm with ID '{alarm_id}' not found")
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    crud.delete_alarm(db, alarm_id=alarm_id)
    logger.info(f"Alarm with ID '{alarm_id}' deleted successfully")
    return {"message": "Alarm deleted successfully"}
