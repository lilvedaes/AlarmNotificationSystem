from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.concurrency import asynccontextmanager
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.crud import user_crud, alarm_crud, alarm_job_crud
from app.schemas import user_schemas, alarm_schemas
from app.db.database import SessionLocal
from app.utils.scheduler import start_scheduler
from app.utils.logger import logger

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
# When specifying req or res as a schema, it runs schema validation and throws RequestValidationError if failed
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error occurred: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors()
        }
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}

# Get user by username
@app.get("/users/{username}", response_model=user_schemas.User)
def get_user(username: str, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, username)
    if db_user is None:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"User with username '{username}' fetched successfully")
    return db_user

# Create user
@app.post("/users/", response_model=user_schemas.User)
def create_user(user_create: user_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, user_create.username)
    if db_user:
        logger.warning(f"Username '{user_create.username}' already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = user_crud.get_user_by_phone_number(db, user_create.phone_number)
    if db_user:
        logger.warning(f"Phone number '{user_create.phone_number}' already registered")
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    created_user = user_crud.create_user(db, user_create)
    logger.info(f"User '{user_create.username}' created successfully")
    return created_user

# Update user by id
@app.put("/users/{user_id}", response_model=user_schemas.User)
def update_user(user_id: int, user_update: user_schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_id(db, user_id)
    if db_user is None:
        logger.warning(f"User with ID '{user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.phone_number == user_update.phone_number and db_user.username == user_update.username:
        return db_user
    
    if user_update.username:
        user_with_new_username = user_crud.get_user_by_username(db, user_update.username)
        if db_user:
            logger.warning(f"Username '{user_update.username}' already registered")
            raise HTTPException(status_code=400, detail="Username already registered")
    
    if user_update.phone_number:
        user_with_new_phone = user_crud.get_user_by_phone_number(db, user_update.phone_number)
        if db_user:
            logger.warning(f"Phone number '{user_update.phone_number}' already registered")
            raise HTTPException(status_code=400, detail="Phone number already registered")
    
    updated_user = user_crud.update_user(db, db_user, user_update)
    logger.info(f"User with ID '{user_id}' updated successfully")
    return updated_user

# Delete user by id
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_id(db, user_id)
    if db_user is None:
        logger.warning(f"User with ID '{user_id}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    user_crud.delete_user_by_id(
        db=db, 
        user=db_user, 
        get_alarms_by_user_func=alarm_crud.get_alarms_by_user_id, 
        delete_alarm_func=alarm_crud.delete_alarm_by_id
    )
    logger.info(f"User with ID '{user_id}' deleted successfully")
    return {"message": "User deleted successfully"}

# Get alarms by username
@app.get("/alarms/user/{username}", response_model=List[alarm_schemas.Alarm])
def get_alarms_by_username(username: str, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, username)
    if not db_user:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    alarms = alarm_crud.get_alarms_by_user_id(db, db_user.id)
    logger.info(f"Fetched {len(alarms)} alarms for user '{username}'")
    return alarms

# Create alarm
@app.post("/alarms/", response_model=alarm_schemas.Alarm)
def create_alarm(alarm_create: alarm_schemas.AlarmCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_username(db, alarm_create.username)
    if not db_user:
        logger.warning(f"User with username '{alarm_create.username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    created_alarm = alarm_crud.create_alarm(
        db=db, 
        alarm_create=alarm_create, 
        user=db_user, 
        create_alarm_job_func=alarm_job_crud.create_alarm_job
    )
    logger.info(f"Alarm with ID '{created_alarm.id}' created successfully for user '{alarm_create.username}'")
    return created_alarm

# Update alarm (activate/deactivate)
@app.put("/alarms/{alarm_id}", response_model=alarm_schemas.Alarm)
def update_alarm(alarm_id: int, alarm_update: alarm_schemas.AlarmUpdate, db: Session = Depends(get_db)):
    db_alarm = alarm_crud.get_alarm_by_id(db, alarm_id)
    if not db_alarm:
        logger.warning(f"Alarm with ID '{alarm_id}' not found")
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    if db_alarm.is_active == alarm_update.is_active:
        return db_alarm
    
    updated_alarm = alarm_crud.update_alarm(
        db=db,
        alarm=db_alarm,
        alarm_update=alarm_update,
        get_user_by_id_func=user_crud.get_user_by_id,
        get_alarm_job_func=alarm_job_crud.get_alarm_job_by_alarm_id
    )
    logger.info(f"Alarm with ID '{alarm_id}' updated successfully")
    return updated_alarm

# Delete alarm
@app.delete("/alarms/{alarm_id}")
def delete_alarm(alarm_id: int, db: Session = Depends(get_db)):
    db_alarm = alarm_crud.get_alarm_by_id(db, alarm_id)
    if not db_alarm:
        logger.warning(f"Alarm with ID '{alarm_id}' not found")
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    alarm_crud.delete_alarm_by_id(
        db=db, 
        alarm_id=alarm_id,
        get_alarm_job_func=alarm_job_crud.get_alarm_job_by_alarm_id,
        delete_alarm_job_func=alarm_job_crud.delete_alarm_job_by_alarm_id
    )
    logger.info(f"Alarm with ID '{alarm_id}' deleted successfully")
    return {"message": "Alarm deleted successfully"}
