# app/schemas.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import time

class AlarmBase(BaseModel):
    user_id: int
    message: str
    time: time
    days_of_week: List[str]
    timezone: str
    send_email: Optional[bool] = False
    send_sms: Optional[bool] = False

class AlarmCreate(AlarmBase):
    pass

class Alarm(AlarmBase):
    id: int

    class Config:
        orm_mode = True
