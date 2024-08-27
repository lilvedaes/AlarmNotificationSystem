import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from typing import List

from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.scheduler import start_scheduler

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Asynchronous version of creating all tables (only necessary if not using Alembic for migrations)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Dependency to get the async DB session
async def get_db():
    async with SessionLocal() as db:
        try:
            # Use yield to "suspend" execution instead of "return" 
            # so that the session closes after the request is done
            yield db
        finally:
            await db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  # Ensure the DB is initialized
    start_scheduler()  # Start the scheduler as usual
    yield

app = FastAPI(lifespan=lifespan)

# Create a custom exception handler for RequestValidationError to throw BAD REQUEST
# When specifying response model as a schema, it runs schema validation and throws RequestValidationError if failed
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(exc: RequestValidationError):
    logger.error(f"Validation error occurred: {exc.errors()} with body: {exc.body}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}

# Create user
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        logger.warning(f"Username '{user.username}' already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    created_user = await crud.create_user(db=db, user=user)
    logger.info(f"User '{user.username}' created successfully")
    return created_user

# Get user by username
@app.get("/users/{username}", response_model=schemas.User)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=username)
    if db_user is None:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    logger.info(f"User with username '{username}' fetched successfully")
    return db_user

# Create alarm
@app.post("/alarms/", response_model=schemas.Alarm)
async def create_alarm(alarm: schemas.AlarmCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=alarm.username)
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
    
    created_alarm = await crud.create_alarm(db=db, alarm=alarm, user=db_user)
    logger.info(f"Alarm with ID '{created_alarm.id}' created successfully for user '{alarm.username}'")
    return created_alarm

# Get alarms by username
@app.get("/alarms/user/{username}", response_model=List[schemas.Alarm])
async def get_alarms_by_username(username: str, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=username)
    if not db_user:
        logger.warning(f"User with username '{username}' not found")
        raise HTTPException(status_code=404, detail="User not found")
    
    alarms = await crud.get_alarms_by_user(db=db, user_id=db_user.id)
    logger.info(f"Fetched {len(alarms)} alarms for user '{username}'")
    return alarms

# Delete alarm
@app.delete("/alarms/{alarm_id}")
async def delete_alarm(alarm_id: int, db: AsyncSession = Depends(get_db)):
    db_alarm = await crud.get_alarm(db, alarm_id=alarm_id)
    if not db_alarm:
        logger.warning(f"Alarm with ID '{alarm_id}' not found")
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    await crud.delete_alarm(db, alarm_id=alarm_id)
    logger.info(f"Alarm with ID '{alarm_id}' deleted successfully")
    return {"message": "Alarm deleted successfully"}
