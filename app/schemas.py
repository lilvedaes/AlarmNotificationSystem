from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import time

# User Schemas
class UserBase(BaseModel):
    username: constr(max_length=50)
    email: EmailStr
    phone_number: constr(max_length=20)
    timezone: constr(max_length=50)

# UserCreate will include all UserBase fields
class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    alarms: List['Alarm'] = []

    class Config:
        orm_mode = True

# Alarm Schemas
class AlarmBase(BaseModel):
    message: str
    time: time
    days_of_week: List[int]  # Monday = 0, Sunday = 6
    is_active: Optional[bool] = True
    send_email: Optional[bool] = False
    send_sms: Optional[bool] = False

# AlarmCreate will include all AlarmBase fields + username
class AlarmCreate(AlarmBase):
    username: str  # Username instead of user_id

class Alarm(AlarmBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
