from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.scheduler import start_scheduler

# Asynchronous version of creating all tables (only necessary if not using Alembic for migrations)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Dependency to get the async DB session
async def get_db() -> AsyncSession:
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()  # Ensure the DB is initialized
    start_scheduler()  # Start the scheduler as usual

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Alarm Notification System!"}

# Create user
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return await crud.create_user(db=db, user=user)

# Get user by username
@app.get("/users/{username}", response_model=schemas.User)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Create alarm
@app.post("/alarms/", response_model=schemas.Alarm)
async def create_alarm(alarm: schemas.AlarmCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=alarm.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    alarm_data = schemas.AlarmCreate(**alarm.dict(), username=db_user.username)

    # Validate the days_of_week field
    for day in alarm_data.days_of_week:
        if day < 0 or day > 6:
            raise HTTPException(status_code=400, detail="Invalid day of the week")
    
    return await crud.create_alarm(db=db, alarm=alarm_data, user=db_user)

# Get alarms by username
@app.get("/alarms/user/{username}", response_model=List[schemas.Alarm])
async def get_alarms_by_username(username: str, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.get_alarms_by_user(db=db, user_id=db_user.id)

# Delete alarm
@app.delete("/alarms/{alarm_id}")
async def delete_alarm(alarm_id: int, db: AsyncSession = Depends(get_db)):
    db_alarm = await crud.get_alarm(db, alarm_id=alarm_id)
    if not db_alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    await crud.delete_alarm(db, alarm_id=alarm_id)
    return {"message": "Alarm deleted successfully"}
