from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas

# User CRUD operations
async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# Alarm CRUD operations
async def get_alarm(db: AsyncSession, alarm_id: int):
    result = await db.execute(select(models.Alarm).filter(models.Alarm.id == alarm_id))
    return result.scalars().first()

async def create_alarm(db: AsyncSession, alarm: schemas.AlarmCreate, user: models.User):
    db_alarm = models.Alarm(
        user_id=user.id,
        message=alarm.message,
        time=alarm.time,
        days_of_week=alarm.days_of_week,
        is_active=alarm.is_active,
        send_sms=alarm.send_sms,
        send_email=alarm.send_email
    )
    db.add(db_alarm)
    await db.commit()
    await db.refresh(db_alarm)
    return db_alarm

async def get_alarms_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Alarm).filter(models.Alarm.user_id == user_id))
    return result.scalars().all()

async def delete_alarm(db: AsyncSession, alarm_id: int):
    await db.execute(delete(models.Alarm).filter(models.Alarm.id == alarm_id))
    await db.commit()
