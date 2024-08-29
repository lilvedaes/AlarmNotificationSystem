from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from typing_extensions import Self
from datetime import time

# Alarm Schemas
class AlarmBase(BaseModel):
    message: str
    time: time
    days_of_week: List[int]  # Monday = 0, Sunday = 6
    is_active: Optional[bool] = True
    send_email: Optional[bool] = False
    send_sms: Optional[bool] = False

    # Validate days of week is a non-empty list
    @field_validator('days_of_week')
    @classmethod
    def check_days_of_week(cls, v: List[int]) -> List[int]:
        if not v:
            raise ValueError('Days of week must contain at least one element.')
        elif any(day < 0 or day > 6 for day in v):
            raise ValueError('Invalid day of the week.')
        return v

    # Validate that at least one of send_email or send_sms is True
    @model_validator(mode='after')
    @classmethod
    def check_notification_flags(cls, self) -> Self:
        if not self.send_email and not self.send_sms:
            raise ValueError('At least one of send_email or send_sms must be True.')
        return self

# AlarmCreate will include all AlarmBase fields + username
class AlarmCreate(AlarmBase):
    username: str  # Username instead of user_id

# AlarmUpdate will include only is_active
class AlarmUpdate(BaseModel):
    is_active: bool

# The Alarm schema will include all AlarmBase fields + id and user_id
class Alarm(AlarmBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True